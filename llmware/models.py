
# Copyright 2023 llmware

# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.  You
# may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.

import logging
import json
import numpy as np
import os
import re
import requests
import tempfile
import ast
from collections import OrderedDict
from tqdm.auto import trange
import time

import torch
from torch import Tensor, nn
from tqdm.autonotebook import trange
import math

import torch.utils.checkpoint

#   start - imports for ctransformers
from functools import partial
import platform
from ctypes import CDLL, c_bool, c_int, c_float, c_char_p, c_void_p, POINTER, Structure
from pathlib import Path
#   end - imports for ctransformers


from llmware.util import Utilities
from llmware.configs import LLMWareConfig
from llmware.resources import CloudBucketManager
from llmware.exceptions import (ModelNotFoundException, DependencyNotInstalledException, ModuleNotFoundException,
                                ModelCardNotRegisteredException)

from llmware.model_configs import (global_model_repo_catalog_list, global_model_finetuning_prompt_wrappers_lookup,
                                   global_default_prompt_catalog)


# api model imports
import openai, anthropic, ai21, cohere


class _ModelRegistry:

    """ ModelRegistry class is wrapper class around the global_model_repo_catalog_list for easy dynamic updating """

    #   notes:
    #   --held out as internal global cls to keep options to adapt implementation over time
    #   --shifted to internal class - not to be directly accessed -> make changes through ModelCatalog

    #   pulls default model list from model_configs.py
    registered_models = global_model_repo_catalog_list

    model_classes = ["HFGenerativeModel", "LLMWareModel", "GGUFGenerativeModel",
                     "LLMWareSemanticModel", "HFEmbeddingModel", "OpenChatModel", "OllamaModel",
                     "OpenAIGenModel", "ClaudeModel", "GoogleGenModel",
                     "CohereGenModel", "JurassicModel", "AIBReadGPTModel",
                     "OpenAIEmbeddingModel", "CohereEmbeddingModel","GoogleEmbeddingModel"]

    #   model card validation for registering new model - required attributes
    min_required_fields = ["model_name", "model_family", "model_category"]

    #   most fine-tuned models require a specific prompt wrapping that was used in the fine-tuning process
    #   we are treating these "prompt_wrappers" as core attributes of the model
    prompt_wrappers = ["alpaca", "human_bot", "chatgpt", "<INST>", "open_chat", "hf_chat", "chat_ml"]
    registered_wrappers = global_model_finetuning_prompt_wrappers_lookup

    @classmethod
    def get_model_list(cls):
        """ List current view of registered models """
        return cls.registered_models

    @classmethod
    def get_wrapper_list(cls):
        """ List current registered wrapper formats """
        return cls.registered_wrappers

    @classmethod
    def add_wrapper(cls, wrapper_name, wrapper_dict):

        """ Adds a new prompter wrapper to the registered list """

        cls.registered_wrappers.update({wrapper_name:wrapper_dict})
        cls.prompt_wrappers.append(wrapper_name)

        return wrapper_dict

    @classmethod
    def validate(cls, model_card_dict):

        """ Provides minimal validation of structure of a new model card """

        for keys in cls.min_required_fields:
            if keys not in model_card_dict:
                return False

        if "model_family" not in model_card_dict:
            return False

        if model_card_dict["model_family"] not in cls.model_classes:
            return False

        if "prompt_wrapper" in model_card_dict:

            pwrap = model_card_dict["prompt_wrapper"]

            if pwrap:

                # ok if prompt_wrapper = ""

                if pwrap not in cls.get_wrapper_list():

                    # permits registering of new model card but issues warning

                    print(f"update: this prompt wrapper - {pwrap} - is not registered which may lead to unpredictable "
                      f"results in inference - you should register this prompt format for better results.")

        return True

    @classmethod
    def add_model(cls, model_card_dict):

        """ Adds a model to the registry """

        if cls.validate(model_card_dict):
            cls.registered_models.append(model_card_dict)
        else:
            raise ModelCardNotRegisteredException("New-Model-Card-Missing-Keys")

        return model_card_dict

    @classmethod
    def update_model(cls, model_name_lookup, new_model_card_dict):

        """ Updates model in the registry """

        if not cls.validate(new_model_card_dict):
            raise ModelCardNotRegisteredException("New-Model-Card-Missing-Keys")

        updated=False

        for i, models in enumerate(cls.registered_models):
            if models["model_name"] == model_name_lookup:
                del cls.registered_models[i]
                cls.registered_models.append(new_model_card_dict)
                updated = True
                break

        return updated

    def delete_model(cls, model_name):

        """ Removes model from Model Registry list """

        model_found=False

        for i, models in enumerate(cls.registered_models):
            if models["model_name"] == model_name:
                del cls.registered_models[i]
                model_found = True
                break

        if not model_found:
            raise ModelNotFoundException(model_name)

        return model_found


class ModelCatalog:

    """ ModelCatalog is the main class responsible for model lookup of (1) Model Card and (2) Finding Model Class.
    In most cases, ModelCatalog is the interface for all facets of interacting with the model classes.
    """

    def __init__(self):

        #   ModelCatalog is simple, flexible mechanism to track registered models
        #   Easy to create "model repo" with mix of model types and instantiation approaches
        #   Builds on standard model classes with standard inference

        self.model_classes = [
                                # generative model classes
                                "OpenAIGenModel", "ClaudeModel", "GoogleGenModel",
                                "CohereGenModel", "JurassicModel", "AIBReadGPTModel",
                                "HFGenerativeModel", "LLMWareModel", "GGUFGenerativeModel",
                                "OpenChatModel", "OllamaModel",

                                # embedding model classes
                                "LLMWareSemanticModel",
                                "OpenAIEmbeddingModel", "CohereEmbeddingModel",
                                "GoogleEmbeddingModel", "HFEmbeddingModel"
                             ]

        self.open_source_model_classes = ["HFGenerativeModel", "LLMWareModel", "GGUFGenerativeModel",
                                          "LLMWareSemanticModel","HFEmbeddingModel", "OpenChatModel",
                                          "OllamaModel"]

        self.global_model_list = _ModelRegistry().get_model_list()

        self.account_name = None
        self.library_name= None

    def pull_latest_manifest(self):
        """ Not implemented currently """
        # will add to check manifest in global repo and make available for pull down
        return 0

    def save_model_registry(self, fp, fn="llmware_supported_models_manifest.json"):

        """ Utility method to export global model list to json file """

        json_dict = json.dumps(self.global_model_list, indent=1)
        with open(os.path.join(fp, fn), "w", encoding='utf-8') as outfile:
            outfile.write(json_dict)

        return 0

    def register_new_model_card(self, model_card_dict):

        """ Registers a new model card directly in the model catalog """

        # register new model
        _ModelRegistry().add_model(model_card_dict)
        # self.global_model_list.append(model_card_dict)

        return 0

    def delete_model_card(self, model_name):

        """ Removes a model card from the registry """

        _ModelRegistry().delete_model(model_name)

        return 0

    def register_new_finetune_wrapper(self, name, main_start="", main_stop="", llm_start="",
                                      system_start="", system_stop=""):

        new_dict = {"main_start": main_start, "main_stop": main_stop, "start_llm_response": llm_start,
                    "system_start": system_start, "system_stop": system_stop}

        _ModelRegistry().add_wrapper(name, new_dict)

        return 0

    def get_list_registered_finetune_wrappers(self):
        return _ModelRegistry().get_wrapper_list()

    def register_new_hf_generative_model(self, hf_model_name=None, context_window=2048, prompt_wrapper="<INST>",
                                         display_name=None, temperature=0.3, trailing_space="", link=""):

        if not display_name:
            display_name = hf_model_name

        model_card = {"model_name": hf_model_name,
                      "context_window": context_window,
                      "prompt_wrapper": prompt_wrapper,

                      "display_name": display_name, "temperature": temperature, "trailing_space": trailing_space,
                      "model_family": "HFGenerativeModel", "model_category": "generative_local",
                      "model_location": "hf_repo", "instruction_following": False,
                      "link": link,
                      "custom_model_files": [], "custom_model_repo": ""}

        _ModelRegistry().add_model(model_card)

        return model_card

    def register_sentence_transformer_model(self, model_name, embedding_dims, context_window,
                                            display_name=None, link=""):

        if not display_name:
            display_name = model_name

        new_model_card_dict = {"model_name": model_name, "context_window": context_window,
                               "embedding_dims": embedding_dims,

                               # pre-populated parameters for sentence transformer
                               "model_family": "LLMWareSemanticModel", "model_category": "embedding",
                               "display_name": display_name, "link": link,
                               "model_location": "st_repo",
                               "custom_model_files": [], "custom_model_repo":""
                               }

        _ModelRegistry().add_model(new_model_card_dict)

        return new_model_card_dict

    def register_gguf_model(self, model_name, gguf_model_repo, gguf_model_file_name, prompt_wrapper=None,
                            eos_token_id=0, display_name=None,trailing_space="", temperature=0.3,
                            context_window=2048, instruction_following=False):

        """ Registers a new GGUF model in model catalog - alternative to adding directly in the ModelRegistry """

        if not display_name:
            display_name = model_name

        new_model_card_dict = {"model_name": model_name, "display_name": display_name,
                               "model_family": "GGUFGenerativeModel", "model_category": "generative_local",
                               "model_location": "llmware_repo", "context_window": context_window,
                               "instruction_following": instruction_following, "prompt_wrapper": prompt_wrapper,
                               "temperature": temperature, "trailing_space": trailing_space,
                               "eos_token_id": eos_token_id,
                               "gguf_file": gguf_model_file_name,
                               "gguf_repo": gguf_model_repo,
                               "link": "", "custom_model_files": [], "custom_model_repo":""
                               }

        _ModelRegistry().add_model(new_model_card_dict)
        # self.global_model_list.append(new_model_card_dict)

        return new_model_card_dict

    def register_open_chat_model(cls, model_name, api_base=None, model_type="chat", display_name=None,
                            context_window=4096, instruction_following=True, prompt_wrapper="",
                            temperature=0.5):

        """ Add any open chat model into Model Registry, e.g.,

         _ModelRegistry().add_open_chat_model("my_open_chat_model1",
                                            api_base="http://localhost:1234/v1",
                                            prompt_wrapper="<INST>",
                                            model_type="chat")

         To invoke the model:

         my_open_chat_model = ModelCatalog().load_model("my_open_chat_model1")

         Or from a prompt:

         prompter = Prompt().load_model("my_open_chat_model1")

         """

        if not display_name:
            display_name = model_name

        new_model_card_dict = {"model_name": model_name, "model_type": model_type, "prompt_wrapper": prompt_wrapper,
                               "display_name": display_name,
                               "model_family": "OpenChatModel", "model_category": "generative-api",
                               "model_location": "api", "context_window": context_window,
                               "instruction_following": instruction_following,
                               "temperature": temperature, "trailing_space": "",
                               "api_base": api_base
                               }

        _ModelRegistry().add_model(new_model_card_dict)

        return 0

    def register_ollama_model(cls, model_name,
                              host="localhost",
                              port=11434,
                              model_type="chat",
                              raw=False,
                              stream=False,
                              display_name=None,
                              context_window=4096,
                              instruction_following=True,
                              prompt_wrapper="",
                              temperature=0.5):

        """ Add any Ollama model into Model Registry - key parameters:

        Assumes -
        1.  default host/port configs of "localhost:11434"
        2.  supports 'completion' ollama api, but uses "chat" by default
        3.  assumes raw=False & stream=False -> more options will be supported over time

        If you are using the ollama default settings, then you can register a model card by
        simply providing the model name,

        e.g., ModelCatalog().register_ollama_model("llama2")

         """

        if not display_name:
            display_name = model_name

        #   note: both raw_mode and stream_mode are set to False

        new_model_card_dict = {"model_name": model_name, "model_type": model_type,
                               "host": host, "port": port,
                               "prompt_wrapper": prompt_wrapper,
                               "display_name": display_name,
                               "model_family": "OllamaModel", "model_category": "generative-api",
                               "model_location": "api", "context_window": context_window,
                               "instruction_following": instruction_following,
                               "temperature": temperature, "trailing_space": "",
                               "raw_mode": False, "stream_mode": False
                               }

        _ModelRegistry().add_model(new_model_card_dict)

        return 0

    def setup_custom_llmware_inference_server(self, uri_string, secret_key=None):

        """ Sets up and registers a custom llmware inference server """

        #   Examples:
        #       os.environ["LLMWARE_GPT_URI"] = "http://111.111.1.111:8080"
        #       os.environ["USER_MANAGED_LLMWARE_GPT_API_KEY"] = "demo-pass-test-key"

        # set environ variables with the URL and password key
        os.environ["LLMWARE_GPT_URI"] = uri_string
        os.environ["USER_MANAGED_LLMWARE_GPT_API_KEY"] = secret_key

        return 1

    def lookup_model_card (self, selected_model_name):

        """ Looks up a model card by model name - the model card has the key configuration and lookup information """

        model_card = None

        # first check in the global_model_repo + confirm location
        for models in self.global_model_list:
            if models["model_name"] == selected_model_name:
                model_card = models
                model_card.update({"standard":True})
                break

        #   if model not found, then return None, and downstream calling function responsible for handling

        # print("update: lookup_model_card - ", model_card)

        return model_card

    def locate_and_retrieve_model_bits (self, model_card):

        """ For models requiring instantiation locally, this utility method retrieves the model bits using the
        instructions provided in the model card entry. """

        # check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):
            # if not explicitly set up by user, then create folder directory structure
            LLMWareConfig.setup_llmware_workspace()

        model_folder_name = model_card["model_name"]

        if model_card["model_family"] == "GGUFGenerativeModel":
            model_folder_name = model_folder_name.split("/")[-1]

        if not os.path.exists(LLMWareConfig.get_model_repo_path()):
            os.mkdir(LLMWareConfig.get_model_repo_path())

        model_location = os.path.join(LLMWareConfig.get_model_repo_path(), model_folder_name)

        if os.path.exists(model_location):
            model_parts_in_folder = os.listdir(model_location)
            if len(model_parts_in_folder) > 0:

                # print("update: found model parts - ", model_parts_in_folder)

                return model_location

        logging.info("update: ModelCatalog - this model - %s - is not in local repo - %s, so pulling "
                        "from global repo - please note that this may take a little time to load "
                        "for the first time.", model_folder_name, LLMWareConfig.get_model_repo_path())

        logging.info("update: ModelCatalog - pulling model from global repo - %s ", model_folder_name)

        if model_card["model_family"] != "GGUFGenerativeModel":

            CloudBucketManager().pull_single_model_from_llmware_public_repo(model_folder_name)
        else:
            #   GGUF models pulled directly from HF repos
            logging.info("update: pulling GGUF model from HF - %s - %s", model_location, model_card)

            self.pull_model_from_hf(model_card, model_location)

        logging.info("update: ModelCatalog - done pulling model into local folder - %s ", model_location)

        if os.path.exists(model_location):
            return model_location
        
        raise ModelNotFoundException(model_folder_name)

    def _instantiate_model_class_from_string(self, model_class, model_name, model_card, api_key=None):

        """ Internal utility method to instantiate model classes from strings. """

        # by default - if model not found - return None
        my_model = None
        context_window= 2048    # used in generative models - use 2048 as default safe backup
        embedding_dims = None   # used in embedding models

        if "context_window" in model_card:
            context_window = model_card["context_window"]

        if model_class in self.model_classes:

            # generative models
            if model_class == "ClaudeModel": my_model = ClaudeModel(model_name=model_name,
                                                                    context_window=context_window,
                                                                    api_key=api_key)

            if model_class == "OpenAIGenModel": my_model = OpenAIGenModel(model_name=model_name,
                                                                          context_window=context_window,
                                                                          api_key=api_key)

            if model_class == "CohereGenModel": my_model = CohereGenModel(model_name=model_name,
                                                                          context_window=context_window,
                                                                          api_key=api_key)

            if model_class == "JurassicModel": my_model = JurassicModel(model_name=model_name,
                                                                        context_window=context_window,
                                                                        api_key=api_key)

            if model_class == "GoogleGenModel": my_model = GoogleGenModel(model_name=model_name,
                                                                          context_window=context_window,
                                                                          api_key=api_key)

            if model_class == "OpenChatModel": my_model = OpenChatModel(model_name=model_name,
                                                                        context_window=context_window,
                                                                        api_key=api_key, model_card=model_card)

            if model_class == "OllamaModel": my_model = OllamaModel(model_name=model_name,
                                                                    context_window=context_window,
                                                                    api_key=api_key, model_card=model_card)

            # stub for READ GPT provided -> will add other 3rd party models too
            if model_class == "AIBReadGPTModel": my_model = AIBReadGPTModel(model_name=model_name,api_key=api_key)

            # *new* - stub for LLMWare Model
            if model_class == "LLMWareModel":
                my_model = LLMWareModel(model_name=model_name,api_key=api_key)

            # embedding models

            if "embedding_dims" in model_card:
                embedding_dims = model_card["embedding_dims"]

            if model_class == "OpenAIEmbeddingModel": my_model = OpenAIEmbeddingModel(model_name=model_name,
                                                                                      embedding_dims=embedding_dims,
                                                                                      api_key=api_key)

            if model_class == "CohereEmbeddingModel": my_model = CohereEmbeddingModel(model_name=model_name,
                                                                                      embedding_dims=embedding_dims,
                                                                                      api_key=api_key)

            if model_class == "GoogleEmbeddingModel": my_model = GoogleEmbeddingModel(model_name=model_name,
                                                                                      embedding_dims=embedding_dims,
                                                                                      api_key=api_key)

            if model_class == "LLMWareSemanticModel": my_model = LLMWareSemanticModel(model_name=model_name,
                                                                                      embedding_dims=embedding_dims,
                                                                                      api_key=api_key,
                                                                                      model_card=model_card)

            # HF models
            if model_class == "HFGenerativeModel":
                my_model = HFGenerativeModel(model_name=model_name,api_key=api_key, trust_remote_code=True,
                                             model_card=model_card)

                # set specific parameters associated with custom models

                if "instruction_following" in model_card:
                    my_model.instruction_following = model_card["instruction_following"]
                else:
                    my_model.instruction_following = False

                if "prompt_wrapper" in model_card:
                    my_model.prompt_wrapper = model_card["prompt_wrapper"]
                else:
                    my_model.prompt_wrapper = "human_bot"

                if "temperature" in model_card:
                    my_model.temperature = model_card["temperature"]
                else:
                    my_model.temperature = 0.3
                
                if "trailing_space" in model_card:
                    my_model.trailing_space = model_card["trailing_space"]

            if model_class == "GGUFGenerativeModel":

                my_model = GGUFGenerativeModel(model_name=model_name, api_key=api_key, model_card=model_card)

                if "prompt_wrapper" in model_card:
                    my_model.prompt_wrapper = model_card["prompt_wrapper"]
                else:
                    my_model.prompt_wrapper = "human_bot"

                if "temperature" in model_card:
                    my_model.temperature = model_card["temperature"]
                else:
                    my_model.temperature = 0.3

                if "trailing_space" in model_card:
                    my_model.trailing_space = model_card["trailing_space"]

            if model_class == "HFEmbeddingModel": my_model = HFEmbeddingModel(model_name=model_name,
                                                                              api_key=api_key,
                                                                              model_card=model_card)

        return my_model

    def load_model (self, selected_model, api_key=None):

        """ Main method for loading and fully instantiating a model based solely on the model's name """

        # completes all preparatory steps, and returns 'ready-for-inference' model

        # step 1- lookup model card from the catalog
        model_card = self.lookup_model_card(selected_model)
        if not model_card:
            logging.error("error: ModelCatalog - unexpected - could not identify model card for "
                          "selected model - %s ", selected_model)

            raise ModelNotFoundException(selected_model)

        # step 2- instantiate the right model class
        my_model = self.get_model_by_name(model_card["model_name"], api_key=api_key)
        if not my_model:
            logging.error("error: ModelCatalog - unexpected - could not identify the model - %s ", selected_model)
            raise ModelNotFoundException(selected_model)

        # step 3- if physical model, then find the location on local server, and if not available, then pull from s3
        if model_card["model_location"] == "llmware_repo":
            loading_directions = self.locate_and_retrieve_model_bits(model_card)
            my_model = my_model.load_model_for_inference(loading_directions, model_card=model_card)
        else:
            # if api_key passed, save as environ variable
            # TODO - look at this
            if api_key:
                my_model.set_api_key(api_key)
                os.environ[selected_model] = api_key

            # pass model name to the model directly
            my_model.model_name = selected_model

        return my_model

    def add_api_key (self, selected_model_name, api_key):

        """ Convenience method to apply an api_key to a pass to a model """

        # step 1- lookup model card from the catalog
        model_card = self.lookup_model_card(selected_model_name)

        if not model_card:

            logging.error("error: ModelCatalog - could not identify model card for "
                          "selected model - %s ", selected_model_name)

            raise ModelNotFoundException(selected_model_name)

        # step 2 - save api key as environmental variable
        model_name = model_card["model_name"]
        os.environ[model_name] = api_key

        return self

    def load_sentence_transformer_model(self,model, model_name):

        """ Loads a sentence transformer model """

        model = LLMWareSemanticModel(model=model,model_name=model_name)
        return model

    def load_hf_embedding_model(self, model, tokenizer):

        """ Loads and integrates a Huggingface embedding model """

        model = HFEmbeddingModel(model, tokenizer)
        return model

    def load_hf_generative_model(self, model,tokenizer,prompt_wrapper=None,
                                 instruction_following=False):

        """ Loads and integrates a Huggingface generative decoder-based 'causal' model with limited options
        to control model preprocessing prompt behavior """

        model = HFGenerativeModel(model, tokenizer, prompt_wrapper=prompt_wrapper,
                                  instruction_following=instruction_following)

        return model

    def load_embedding_model (self, model_name=None,
                              model=None, tokenizer=None,from_hf=False,
                              from_sentence_transformers=False):

        """ Loads embedding model by name -
        main handler used by any calling function to instantiate embedding model. """

        loaded_model = None

        # if user passed a 'loaded model' object, then apply directly
        if model:

            # first, check for 'from_hf' flag and load as HuggingFace model
            if from_hf:
                loaded_model = ModelCatalog().load_hf_embedding_model(model,tokenizer)
            else:
                # second, check for 'from_sentence_transformer' flag and load as SBERT model
                if from_sentence_transformers:
                    loaded_model = ModelCatalog().load_sentence_transformer_model(model,model_name)

            if not loaded_model:
                logging.error("error: ModelCatalog load_embedding_model could not identify the "
                              "passed model - if model is from HuggingFace, then mark optional "
                              "'from_hf' flag to True.  If model is from Sentence Transformers, "
                              " then mark optional 'from_sentence_transformers' flag "
                              "to True.  Note: setting search mode to text search, in absence of embedding "
                              "model.")
        else:
            # main case - load embedding model from Catalog
            loaded_model = ModelCatalog().load_model(selected_model=model_name)

        return loaded_model

    def list_open_source_models(self):

        """ Lists the open source models in the ModelCatalog. """

        open_source_models = []

        for x in self.global_model_list:

            if x["model_family"] in self.open_source_model_classes:
                open_source_models.append(x)

        return open_source_models

    def list_embedding_models(self):

        """ Lists the embedding models in the ModelCatalog. """

        embedding_models = []

        for x in self.global_model_list:
            if x["model_category"] == "embedding":
                embedding_models.append(x)

        return embedding_models

    def list_generative_models(self):

        """ Lists the generative models in the ModelCatalog. """

        gen_models = []

        for x in self.global_model_list:
            if x["model_category"].startswith("generative"):
                gen_models.append(x)

        gen_models = sorted(gen_models, key=lambda x: x["model_name"], reverse=False)

        return gen_models

    def list_generative_local_models(self):

        """ Lists the generative local models in the ModelCatalog. """

        gen_local_models = []

        for x in self.global_model_list:
            if x["model_category"] == "generative_local":
                gen_local_models.append(x)

        gen_local_models = sorted(gen_local_models, key=lambda x:x["model_name"], reverse=False)

        return gen_local_models

    def list_all_models(self):

        """ Lists all models in the ModelCatalog. """

        all_models = []
        for x in self.global_model_list:
            all_models.append(x)

        all_models = sorted(all_models, key=lambda x: x["model_category"], reverse=False)

        return all_models

    def model_lookup(self,model_name):

        """ Looks up model by model_name. """

        my_model = None

        for models in self.global_model_list:
            if models["model_name"] == model_name:
                my_model = models
                break

        return my_model

    def get_model_by_name(self, model_name, api_key=None):

        """ Gets and instantiates model by name. """

        my_model = None

        for models in self.global_model_list:

            if models["model_name"] == model_name:
                selected_model = models
                my_model = self._instantiate_model_class_from_string(selected_model["model_family"],
                                                                     model_name, models,api_key=api_key)
                break

        return my_model

    def pull_model_from_hf(self, model_card, local_model_repo_path, api_key=None):

        """ Pulls a specific model file from Huggingface repository into local model repo path """

        from huggingface_hub import hf_hub_download

        model_name = model_card["model_name"].split("/")[-1]

        gguf_file = model_card["gguf_file"]     # e.g., "ggml-model-q4_k_m.gguf",
        gguf_repo = model_card["gguf_repo"]     # e.g., "llmware/dragon-mistral-7b-v0-gguf"

        # model_path = os.path.join(local_model_repo_path, self.model_name)

        logging.info("update: pull_model_from_repo - %s - %s", local_model_repo_path, model_name)

        if not os.path.exists(local_model_repo_path):
            os.mkdir(local_model_repo_path)

        downloader = hf_hub_download(gguf_repo,
                                     gguf_file,
                                     local_dir=local_model_repo_path,
                                     # note: change to save bits in local model repo, not symlink to HF .cache
                                     local_dir_use_symlinks=False,
                                     token=api_key)

        return local_model_repo_path

    def pull_snapshot_from_hf(self, model_name, local_model_repo_path, api_key=None):

        """ Pulls snapshot of HF model repository and saves into local folder path. """

        from huggingface_hub import snapshot_download

        model_name = "llmware/" + model_name

        snapshot = snapshot_download(model_name, local_dir=local_model_repo_path, token=api_key,
                                     local_dir_use_symlinks=False)

        return local_model_repo_path



class PromptCatalog:
    """ PromptCatalog manages prompt styles and prompt wrappers. """

    def __init__(self):

        self.prompt_catalog = global_default_prompt_catalog
        self.prompt_wrappers = _ModelRegistry().prompt_wrappers
        self.prompt_wrapper_lookup = _ModelRegistry().get_wrapper_list()

        self.prompt_list = self.list_all_prompts()

    def lookup_prompt(self, prompt_name):

        for prompts in self.prompt_catalog:
            if prompts["prompt_name"] == prompt_name:
                return prompts

        return None

    def get_all_prompts(self):
        return self.prompt_catalog

    def list_all_prompts(self):
        prompt_list = []
        for prompt in self.prompt_catalog:
            if "prompt_name" in prompt:
                prompt_list.append(prompt["prompt_name"])
        return prompt_list

    def parse_instruction_for_user_vars(self, prompt_card, inference_dict=None):

        # if no user vars key in prompt_card, then return instruction unchanged

        if "user_vars" not in prompt_card:
            return prompt_card["instruction"]

        if not prompt_card["user_vars"]:
            return prompt_card["instruction"]

        # if no inference_dict, then define as empty dictionary
        if not inference_dict:
            inference_dict = {}

        # in this case, will 'parameterize' and dynamically update instruction
        tokens = prompt_card["instruction"].split(" ")
        updated_instruction = ""

        for i, t in enumerate(tokens):

            if t.startswith("{{") and t.endswith("}}"):

                t_core = t[2:-2]

                # if value found for key in the inference dict, then apply as true 'user_vars'
                if t_core in inference_dict:
                    new_inserted_token = inference_dict[t_core]
                    updated_instruction += str(new_inserted_token) + " "
                else:
                    # apply default value found in the prompt card as back-up
                    if t_core in prompt_card["user_vars"]:
                        new_inserted_token = prompt_card["user_vars"][t_core]
                        updated_instruction += str(new_inserted_token) + " "

            else:
                updated_instruction += t + " "

        logging.info(f"update: prompt catalog - constructed dynamic instruction - {updated_instruction}")

        return updated_instruction.strip()

    def build_core_prompt(self, prompt_card=None, prompt_name=None, separator="\n", query=None, context=None,
                          inference_dict=None):

        if not context:  context = ""
        if not query: query = ""

        if not prompt_card and not prompt_name:
            # error - returning query
            logging.error("error: no prompt selected in PromptCatalog().build_core_prompt")
            prompt_dict = {"core_prompt": context + "\n" + query, "prompt_card": {}}
            return prompt_dict

        if not prompt_card:
            prompt_card = PromptCatalog().lookup_prompt(prompt_name)

        logging.info(f"update: prompt_card - {prompt_card}")

        core_prompt = ""

        if prompt_card:
            for keys in prompt_card["run_order"]:

                if keys == "instruction":
                    # special handler
                    instruction = self.parse_instruction_for_user_vars(prompt_card, inference_dict=inference_dict)
                    core_prompt += instruction + separator
                else:
                    if not keys.startswith("$"):
                        core_prompt += prompt_card[keys] + separator
                    else:
                        if keys == "$query":
                            core_prompt += query + separator
                        if keys == "$context":
                            core_prompt += context + separator

        # update instruction, if user_vars accepted in instruction
        """
        if "instruction" in prompt_card:
            prompt_card["instruction"] = self.parse_instruction_for_user_vars(prompt_card,inference_dict=inference_dict)
            print("update: prompt_card instruction - ", prompt_card)
            core_prompt += prompt_card["instruction"]
        """

        prompt_dict = {"core_prompt": core_prompt, "prompt_card": prompt_card}

        # print("update - core prompt built - ", core_prompt)

        logging.info(f"update: prompt created - {prompt_dict}")

        return prompt_dict

    def add_custom_prompt_card(self, prompt_name, run_order_list, prompt_dict, prompt_description=None):

        new_prompt_card = {"prompt_name": prompt_name,
                           "prompt_description": prompt_description,
                           "run_order": run_order_list}

        for keys, values in prompt_dict.items():
            new_prompt_card.update({keys: values})

        self.prompt_catalog.append(new_prompt_card)

        return new_prompt_card

    def apply_prompt_wrapper(self, text, prompt_wrapper, separator="\n", instruction=None):

        output_text = text

        if prompt_wrapper not in self.prompt_wrappers:
            logging.info("update: selected wrapper - %s - could not be identified -"
                         "returning text prompt without any special format wrapping", prompt_wrapper)

            return output_text

        if prompt_wrapper == "chatgpt":
            return self.wrap_chatgpt_sample(text, instruction)

        else:
            wrapped_prompt = self.wrap_custom(text, prompt_wrapper, instruction=instruction)
            # print("update: wrapped prompt - ", wrapped_prompt)
            return wrapped_prompt

    #   deprecated - replaced by wrap_custom builder function
    def wrap_chat_ml_sample(self, text, separator, instruction):

        if not instruction:
            instruction = "You are a helpful assistant."

        output_text = "<|im_start|>system\n" + instruction + "<|im_end|>\n" + \
                      "<|im_start|>user" + text + "<|im_end|>\n" + \
                      "<|im_start|>assistant"

        return output_text

    #   wip - create ability to customize template
    def wrap_custom(self, text, wrapper_type, instruction=None):

        # print("update: wrapper_type - ", wrapper_type)

        prompt_out = ""

        if wrapper_type in self.prompt_wrapper_lookup:

            prompt_template = self.prompt_wrapper_lookup[wrapper_type]

            # print("update: found prompt template - ", prompt_template)

            if "system_start" in prompt_template:

                if prompt_template["system_start"] != "":

                    prompt_out += prompt_template["system_start"]
                    if instruction:
                        prompt_out += instruction
                    else:
                        prompt_out += "You are a helpful assistant."

                    if "system_stop" in prompt_template:
                        prompt_out += prompt_template["system_stop"]

            if "main_start" in prompt_template:

                prompt_out += prompt_template["main_start"]
                prompt_out += text

                if "main_stop" in prompt_template:
                    prompt_out += prompt_template["main_stop"]

            if "start_llm_response" in prompt_template:
                prompt_out += prompt_template["start_llm_response"]

        else:
            prompt_out = text

        return prompt_out

    def wrap_chatgpt_sample(self, text, instruction):

        if not instruction:
            instruction = "You are a helpful assistant."

        new_sample = [{"role": "system", "content": instruction},
                      {"role": "user", "content": text}]

        return new_sample

    # deprecated - replaced by wrap_custom builder function
    def wrap_human_bot_sample(self, text, user_separator="<human>: ", response_separator="<bot>:"):
        content = user_separator + text + "\n" + response_separator
        return content

    #   deprecated
    def wrap_llama2_chat_sample(self, text, separator):
        content = "<INST> " + text + "</INST>"
        return content

    #   deprecated
    def wrap_alpaca_sample(self, text, separator="\n"):
        content = "### Instruction: " + text + separator + "### Response: "
        return content

    #   deprecated
    def wrap_openchat_sample(self, text, separator="\n"):
        content = "GPT4 User: " + text + "<|endofturn|>" + "GPT4 Assistant:"
        return content

    #   deprecated
    def wrap_hf_chat_zephyr_sample(self, text, separator="\n"):
        content = "<|system|>You are a helpful assistant.\n</s>" + \
                  "<|user|>" + text + "\n</s>" + \
                  "<|assistant|>"
        return content


class OpenChatModel:

    """ OpenChatModel class implements the OpenAI prompt API and is intended for use with OpenChat compatible
    inference servers """

    def __init__(self, model_name=None,  model_card=None, context_window=4000,prompt_wrapper=None, api_key="not_used"):

        #   expected to take config parameters from model card
        self.api_key = api_key
        self.model_name = model_name
        self.model_card = model_card

        #   by default, will use the 'chat' open interface, but alternative is 'completion' api
        self.model_type = "chat"

        #   assume that prompt_wrapper is set in the model card configuration
        self.prompt_wrapper = prompt_wrapper

        #   this is the key parameter that needs to be configured to pass to open chat inference server
        self.api_base = ""

        if self.model_card:

            if "model_type" in self.model_card:
                self.model_type = self.model_card["model_type"]

            if "api_base" in self.model_card:
                self.api_base = self.model_card["api_base"]

            if "prompt_wrapper" in self.model_card:
                self.prompt_wrapper = self.model_card["prompt_wrapper"]

        self.error_message = "\nUnable to connect to OpenChat Model. Please try again later."

        self.separator = "\n"

        # assume input (50%) + output (50%)
        self.max_total_len = context_window
        self.max_input_len = int(context_window * 0.5)
        self.llm_max_output_len = int(context_window * 0.5)

        # inference settings
        self.temperature = 0.7
        self.target_requested_output_tokens = 100
        self.add_prompt_engineering = False
        self.add_context = ""

    def set_api_key (self, api_key, env_var="USER_MANAGED_OPEN_CHAT_API_KEY"):

        # set api_key
        os.environ[env_var] = api_key
        logging.info("update: added and stored OpenChat api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key (self, env_var="USER_MANAGED_OPEN_CHAT_API_KEY"):

        #   not expected to use api_key - so may be empty - handled in inference separately
        self.api_key = os.environ.get(env_var)

        return self.api_key

    def token_counter(self, text_sample):

        #   open ai recommends using the open source gpt2 tokenizer to count tokens
        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids

        return len(toks)

    def prompt_engineer_chat(self, query, context, inference_dict=None):

        if not self.add_prompt_engineering:
            if context:
                selected_prompt = "default_with_context"
            else:
                selected_prompt = "default_no_context"
        else:
            selected_prompt = self.add_prompt_engineering

        prompt_dict = PromptCatalog().build_core_prompt(prompt_name=selected_prompt,
                                                        separator=self.separator,
                                                        query=query, context=context,
                                                        inference_dict=inference_dict)

        system_message = prompt_dict["prompt_card"]["system_message"]
        if not system_message:
            system_message = "You are a helpful assistant."

        core_prompt = prompt_dict["core_prompt"]

        #   final wrapping, based on model-specific instruct training format
        #   --provides a final 'wrapper' around the core prompt text, based on model expectations

        if self.prompt_wrapper:
            core_prompt = PromptCatalog().apply_prompt_wrapper(core_prompt, self.prompt_wrapper, instruction=None)

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": core_prompt}
            ]

        return messages

    def prompt_engineer_completion (self, query, context, inference_dict=None):

        if not self.add_prompt_engineering:
            if context:
                selected_prompt = "default_with_context"
            else:
                selected_prompt = "default_no_context"

        else:
            selected_prompt = self.add_prompt_engineering

        prompt_dict = PromptCatalog().build_core_prompt(prompt_name=selected_prompt,
                                                        separator=self.separator,
                                                        query=query, context=context,
                                                        inference_dict=inference_dict)

        core_prompt = prompt_dict["core_prompt"]

        #   final wrapping, based on model-specific instruct training format
        #   --provides a final 'wrapper' around the core prompt text, based on model expectations

        if self.prompt_wrapper:
            core_prompt = PromptCatalog().apply_prompt_wrapper(core_prompt, self.prompt_wrapper, instruction=None)

        return core_prompt

    def inference(self, prompt, add_context=None, add_prompt_engineering=None, inference_dict=None,
                  api_key=None):

        if add_context:
            self.add_context = add_context

        if add_prompt_engineering:
            self.add_prompt_engineering = add_prompt_engineering

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

        # api_key
        if api_key:
            self.api_key = api_key

        if not self.api_key:
            self.api_key = self._get_api_key()

        # expect that .api_base will route to local open chat inference server
        #   -- assumed that *** api_key likely not used ***
        if not self.api_key:
            openai.api_key = "not-used"
        else:
            openai.api_key = self.api_key

        # default case - pass the prompt received without change
        prompt_enriched = prompt

        usage = {}
        time_start = time.time()

        # save current state of openai.api_base
        openai_api_base_entering_state = openai.api_base

        # set api_base based on configs
        openai.api_base = self.api_base

        try:

            if self.model_type == "chat":

                messages = self.prompt_engineer_chat(prompt_enriched, self.add_context, inference_dict)

                response = openai.ChatCompletion.create(model=self.model_name,messages=messages,
                                                        max_tokens=self.target_requested_output_tokens)

                """ assume 'minimal' api output conformance with OpenAI """

                text_out = response["choices"][0]["message"]["content"]

                """ note: some openchat api do not support providing usage output consistent with OpenAI API """

                pt = 0
                ct = 0
                tt = 0

                """ best effort to gather usage data if conforms with OpenAI """

                if "usage" in response:

                    if "prompt_tokens" in response["usage"]:
                        pt = response["usage"]["prompt_tokens"]

                    if "completion_tokens" in response["usage"]:
                        ct = response["usage"]["completion_tokens"]

                    if "total_tokens" in response["usage"]:
                        tt = response["usage"]["total_tokens"]

                usage = {"input": pt,
                         "output": ct,
                         "total": tt,
                         "metric": "tokens",
                         "processing_time": time.time() - time_start}

            else:

                # traditional completion 'instruct gpt' models

                prompt_enriched = self.prompt_engineer_completion(prompt_enriched,
                                                                  self.add_context,
                                                                  inference_dict=inference_dict)

                prompt_final = prompt_enriched

                text_prompt = prompt_final + self.separator

                response = openai.Completion.create(model=self.model_name, prompt=text_prompt,
                                                    temperature=self.temperature,
                                                    max_tokens=self.target_requested_output_tokens)

                """ assume 'minimal' api output conformance with OpenAI """

                text_out = response["choices"][0]["text"]

                """ note: some openchat api do not support providing usage output consistent with OpenAI API """

                pt = 0
                ct = 0
                tt = 0

                """ best effort to gather usage data if conforms with OpenAI API """

                if "usage" in response:

                    if "prompt_tokens" in response["usage"]:
                        pt = response["usage"]["prompt_tokens"]

                    if "completion_tokens" in response["usage"]:
                        ct = response["usage"]["completion_tokens"]

                    if "total_tokens" in response["usage"]:
                        tt = response["usage"]["total_tokens"]

                usage = {"input": pt,
                         "output": ct,
                         "total": tt,
                         "metric": "tokens",
                         "processing_time": time.time() - time_start}

        except Exception as e:

            text_out = "/***ERROR***/"
            usage = {"input":0, "output":0, "total":0, "metric": "tokens",
                     "processing_time": time.time() - time_start}

            logging.error("error: Open Chat model inference produced error - %s ", e)

        # reset openai.api_base
        openai.api_base = openai_api_base_entering_state

        output_response = {"llm_response": text_out, "usage": usage}

        return output_response



class OllamaModel:

    """ OllamaModel class implements the Ollama model prompt API and is intended for use in building
     RAG pipelines while using a Ollama endpoint primarily for rapid local prototyping. """

    def __init__(self, model_name=None,  model_card=None, context_window=4000,prompt_wrapper=None, api_key="not_used"):

        # default ollama specific settings
        # self.uri = "http://localhost:11434/api/"
        self.host = "localhost"
        self.port = 11434
        self.model_name = "llama2"
        self.model_type = "chat"
        self.stream_mode = False
        self.raw_mode = False

        #   expected to take config parameters from model card
        self.api_key = api_key
        self.model_name = model_name
        self.model_card = model_card

        #   assume that prompt_wrapper is set in the model card configuration
        self.prompt_wrapper = prompt_wrapper

        if self.model_card:

            if "model_name" in self.model_card:
                self.model_name = self.model_card["model_name"]

            if "model_type" in self.model_card:
                self.model_type = self.model_card["model_type"]

            if "host" in self.model_card:
                self.host = self.model_card["host"]

            if "port" in self.model_card:
                self.port = self.model_card["port"]

            if "prompt_wrapper" in self.model_card:
                self.prompt_wrapper = self.model_card["prompt_wrapper"]

            if "raw_mode" in self.model_card:
                self.raw_mode = self.model_card["raw_mode"]

            if "stream_mode" in self.model_card:
                self.stream_mode = self.model_card["stream_mode"]

        self.error_message = f"\nUnable to connect to Ollama Model. Please check that Ollama is running"\
                             f"at {self.host}:{self.port}"

        self.separator = "\n"

        # assume input (50%) + output (50%)
        self.max_total_len = context_window
        self.max_input_len = int(context_window * 0.5)
        self.llm_max_output_len = int(context_window * 0.5)

        # inference settings -> not used as generation handled by Ollama inference
        self.temperature = 0.7
        self.target_requested_output_tokens = 100
        self.add_prompt_engineering = False
        self.add_context = ""

        # self.uri = "http://localhost:11434/api/"
        self.uri = f"http://{self.host}:{self.port}/api/"

    def set_api_key (self, api_key, env_var="USER_MANAGED_OLLAMA_API_KEY"):

        # set api_key
        os.environ[env_var] = api_key
        logging.info("update: added and stored Ollama api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key (self, env_var="USER_MANAGED_OLLAMA_API_KEY"):

        #   not expected to use api_key - so may be empty - handled in inference separately
        self.api_key = os.environ.get(env_var)

        return self.api_key

    def token_counter(self, text_sample):

        #   note: this is an approximation for counting the input tokens using a default tokenizer
        #   --to get 100% accurate, need to use the tokenizer being applied on the 'ollama' decoding

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids

        return len(toks)

    def prompt_engineer (self, query, context, inference_dict=None):

        #   by default, this will construct a very basic prompt, concatenating the
        #   query + context with a basic instruction

        if not self.add_prompt_engineering:
            if context:
                selected_prompt = "default_with_context"
            else:
                selected_prompt = "default_no_context"
        else:
            selected_prompt = self.add_prompt_engineering

        prompt_dict = PromptCatalog().build_core_prompt(prompt_name=selected_prompt,
                                                        separator=self.separator,
                                                        query=query, context=context,
                                                        inference_dict=inference_dict)

        core_prompt = prompt_dict["core_prompt"]

        #   Ollama will handle the prompt wrap templating, unless self.raw_mode = True
        if self.raw_mode:
            if self.prompt_wrapper:
                core_prompt = PromptCatalog().apply_prompt_wrapper(core_prompt, self.prompt_wrapper,
                                                                   instruction=None)

        return core_prompt

    def discover_models(self):

        """ Calls Ollama endpoint for discovery of available models and their locations. """

        response = requests.get(self.uri+"tags")

        logging.info("update: OllamaModel - discover_models - %s ", response.text)

        output = json.loads(response.text)

        return output

    def inference(self, prompt, add_context=None, add_prompt_engineering=None, inference_dict=None,
                  api_key=None):

        """ In typical case with raw_mode = False, then no prompt engineering, just apply a basic
        assembly of the prompt and context. """

        if add_context:
            self.add_context = add_context

        if add_prompt_engineering:
            self.add_prompt_engineering = add_prompt_engineering

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

        # default case - pass the prompt received without change
        prompt_enriched = prompt

        usage = {}

        time_start = time.time()

        try:

            #   assumes 'chat' api by default

            if self.model_type == "chat":

                full_prompt = self.prompt_engineer(prompt_enriched, self.add_context, inference_dict)

                messages = [{"role": "user", "content": full_prompt}]
                uri = self.uri + "chat"

                # print("messages: ", messages, uri)

                response = requests.post(uri,
                                         json={"model": self.model_name,
                                               "messages": messages, "stream": self.stream_mode})

                logging.info("update: OllamaModel response - chat - %s ", response.text)

                output = json.loads(response.text)

                text_out = output["message"]["content"]

                # print("text only - ", output["message"]["content"])

                pt = 0
                ct = 0
                tt = 0

                """ best effort to gather usage data  """

                if "eval_count" in output:
                    ct = output["eval_count"]
                    tt += ct

                pt = self.token_counter(full_prompt)

                tt += pt

                usage = {"input": pt,
                         "output": ct,
                         "total": tt,
                         "metric": "tokens",
                         "processing_time": time.time() - time_start}

            else:

                # traditional completion 'instruct gpt' api

                prompt_enriched = self.prompt_engineer(prompt_enriched, self.add_context,
                                                       inference_dict=inference_dict)

                prompt_final = prompt_enriched + self.separator

                params = {"model": self.model_name, "prompt": prompt_final, "stream": self.stream_mode}

                # response = requests.post("http://localhost:11434/api/generate", json=params)
                response = requests.post(self.uri+"generate", json=params)

                output = json.loads(response.text)

                text_out = output["response"]

                # print("response - generate - ", text_out)

                pt = 0
                ct = 0
                tt = 0

                """ best effort to gather usage data if conforms with OpenAI API """

                if "eval_count" in output:

                    ct = output["eval_count"]
                    tt += ct

                pt = self.token_counter(prompt_final)
                tt += pt

                usage = {"input": pt,
                         "output": ct,
                         "total": tt,
                         "metric": "tokens",
                         "processing_time": time.time() - time_start}

        except Exception as e:

            text_out = "/***ERROR***/"
            usage = {"input":0, "output":0, "total":0, "metric": "tokens",
                     "processing_time": time.time() - time_start}

            logging.error("error: Ollama model inference produced error - %s ", e)

        output_response = {"llm_response": text_out, "usage": usage}

        return output_response


class OpenAIGenModel:

    """ OpenAIGenModel class implements the OpenAI API for its generative decoder models. """

    def __init__(self, model_name=None, api_key=None, context_window=4000):

        self.api_key = api_key
        self.model_name = model_name

        self.error_message = "\nUnable to connect to OpenAI. Please try again later."

        self.separator = "\n"

        # assume input (50%) + output (50%)
        self.max_total_len = context_window
        self.max_input_len = int(context_window * 0.5)
        self.llm_max_output_len = int(context_window * 0.5)

        # inference settings
        self.temperature = 0.7
        self.target_requested_output_tokens = 100
        self.add_prompt_engineering = False
        self.add_context = ""

    def set_api_key (self, api_key, env_var="USER_MANAGED_OPENAI_API_KEY"):

        # set api_key
        os.environ[env_var] = api_key
        logging.info("update: added and stored OpenAI api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key (self, env_var="USER_MANAGED_OPENAI_API_KEY"):

        self.api_key = os.environ.get(env_var)

        if not self.api_key:
            logging.error("error: _get_api_key could not successfully retrieve value from: %s ", env_var)

        return self.api_key

    def token_counter(self, text_sample):

        #   open ai recommends using the open source gpt2 tokenizer to count tokens
        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids

        return len(toks)

    def prompt_engineer_chatgpt3(self, query, context, inference_dict=None):

        if not self.add_prompt_engineering:
            if context:
                selected_prompt = "default_with_context"
            else:
                selected_prompt = "default_no_context"
        else:
            selected_prompt = self.add_prompt_engineering

        prompt_dict = PromptCatalog().build_core_prompt(prompt_name=selected_prompt,
                                                        separator=self.separator,
                                                        query=query, context=context,
                                                        inference_dict=inference_dict)

        system_message = prompt_dict["prompt_card"]["system_message"]
        if not system_message:
            system_message = "You are a helpful assistant."

        core_prompt = prompt_dict["core_prompt"]

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": core_prompt}
            ]

        return messages

    def prompt_engineer (self, query, context, inference_dict=None):

        if not self.add_prompt_engineering:
            if context:
                selected_prompt = "default_with_context"
            else:
                selected_prompt = "default_no_context"

        else:
            selected_prompt = self.add_prompt_engineering

        prompt_dict = PromptCatalog().build_core_prompt(prompt_name=selected_prompt,
                                                        separator=self.separator,
                                                        query=query, context=context,
                                                        inference_dict=inference_dict)

        core_prompt = prompt_dict["core_prompt"]

        return core_prompt

    def inference(self, prompt, add_context=None, add_prompt_engineering=None, inference_dict=None,
                  api_key=None):

        if add_context:
            self.add_context = add_context

        if add_prompt_engineering:
            self.add_prompt_engineering = add_prompt_engineering

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

        # api_key
        if api_key:
            self.api_key = api_key

        if not self.api_key:
            self.api_key = self._get_api_key()

        if not self.api_key:
            logging.error("error: invoking OpenAI Generative model with no api_key")

        # default case - pass the prompt received without change
        prompt_enriched = prompt

        # set as default openai base
        openai_api_base_entering_state = openai.api_base
        openai.api_base = "https://api.openai.com/v1"

        usage = {}
        time_start = time.time()

        try:

            if self.model_name in ["gpt-3.5-turbo","gpt-4","gpt-4-1106-preview","gpt-3.5-turbo-1106"]:

                messages = self.prompt_engineer_chatgpt3(prompt_enriched, self.add_context, inference_dict)

                # different api for "chat completion" -> only applies to ChatGPT = 'gpt-3.5-turbo'
                openai.api_key = self.api_key
                response = openai.ChatCompletion.create(model=self.model_name,messages=messages,
                                                        max_tokens=self.target_requested_output_tokens)

                text_out = response["choices"][0]["message"]["content"]

                usage = {"input": response["usage"]["prompt_tokens"],
                         "output": response["usage"]["completion_tokens"],
                         "total": response["usage"]["total_tokens"],
                         "metric": "tokens",
                         "processing_time": time.time() - time_start}

                # logging.info("update: open ai response: %s ", response)

            else:
                # 'instruct gpt' models

                prompt_enriched = self.prompt_engineer(prompt_enriched, self.add_context, inference_dict=inference_dict)

                prompt_final = prompt_enriched

                text_prompt = prompt_final + self.separator
                logging.info("update: openai model - FINAL PROMPT: %s %s ", self.model_name, prompt_final)
                openai.api_key = self.api_key
                response = openai.Completion.create(model=self.model_name, prompt=text_prompt,
                                                    temperature=self.temperature,
                                                    max_tokens=self.target_requested_output_tokens)

                logging.info("update: open ai response: %s ", response["choices"])
                text_out = response["choices"][0]["text"]
                # openai response "usage" dict - {"completion_tokens" | "prompt_tokens" | total_tokens"}

                usage = {"input": response["usage"]["prompt_tokens"],
                         "output": response["usage"]["completion_tokens"],
                         "total": response["usage"]["total_tokens"],
                         "metric": "tokens",
                         "processing_time": time.time() - time_start}

        except Exception as e:
            # this is special error code that will be picked and handled in AIModels().inference handler
            text_out = "/***ERROR***/"
            usage = {"input":0, "output":0, "total":0, "metric": "tokens",
                     "processing_time": time.time() - time_start}

            # raise LLMInferenceResponseException(e)
            logging.error("error: OpenAI model inference produced error - %s ", e)

        # reset openai api_base
        openai.api_base = openai_api_base_entering_state

        # will look to capture usage metadata
        #   "usage" = {"completion_tokens", "prompt_tokens", "total_tokens"}

        output_response = {"llm_response": text_out, "usage": usage}

        return output_response


class ClaudeModel:

    """ ClaudeModel class implements the Anthropic Claude API for calling Anthropic models. """

    def __init__(self, model_name=None, api_key=None, context_window=8000):

        self.api_key = api_key
        self.model_name = model_name

        self.error_message = "\nUnable to connect to Anthropic/Claude. Please try again later."

        self.separator = "\n"

        #   Claude/Anthropic model - 8000 max token context window
        self.max_total_len = context_window
        self.max_input_len = int(context_window * 0.5)
        self.llm_max_output_len = int(context_window * 0.5)

        # inference settings
        self.temperature = 0.7
        self.target_requested_output_tokens = 100
        self.add_prompt_engineering = False
        self.add_context = ""

    def set_api_key(self, api_key, env_var="USER_MANAGED_ANTHROPIC_API_KEY"):

        # set api_key
        os.environ[env_var] = api_key
        logging.info("update: added and stored ANTHROPIC api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_ANTHROPIC_API_KEY"):

        self.api_key = os.environ.get(env_var)

        if not self.api_key:
            logging.error("error: _get_api_key could not successfully retrieve value from: %s ", env_var)

        return self.api_key

    def token_counter(self, text_sample):

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids
        return len(toks)

    def prompt_engineer (self, query, context, inference_dict=None):

        # default case -> prompt = input query

        prompt_engineered = ""

        if not self.add_prompt_engineering:
            if context:
                selected_prompt = "default_with_context"
            else:
                selected_prompt = "default_no_context"
        else:
            selected_prompt = self.add_prompt_engineering

        prompt_dict = PromptCatalog().build_core_prompt(prompt_name=selected_prompt,
                                                        separator=self.separator,
                                                        query=query,context=context,
                                                        inference_dict=inference_dict)

        if prompt_dict:

            core_prompt = prompt_dict["core_prompt"]

            # prototype prompt for Anthropic:
            # "\n\nHuman:" + {text} + "\n\nAssistant:"
            # per Anthropic docs, usually best to include the query at the END, rather than the Beginning

            prompt_engineered = "\n\nHuman: " + core_prompt + "\n\nAssistant:"

        return prompt_engineered

    def inference(self, prompt, add_context=None, add_prompt_engineering=None, inference_dict=None,
                  api_key=None):

        if add_context:
            self.add_context = add_context

        if add_prompt_engineering:
            self.add_prompt_engineering = add_prompt_engineering

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

        if api_key:
            self.api_key = api_key

        if not self.api_key:
            self.api_key = self._get_api_key()

        if not self.api_key:
            logging.error("error: invoking Anthropic Claude Generative model with no api_key")

        client = anthropic.Client(api_key=self.api_key)

        # prototype prompt sample:   prompt_enriched = "\n\nHuman:" + " please read the following- " +
        # self.add_context + " Based on these materials, " + prompt["prompt"] + "\n\nAssistant:"

        prompt_enriched = self.prompt_engineer(prompt,self.add_context, inference_dict=inference_dict)

        # preferred model = "claude-instant-v1"

        time_start = time.time()

        try:
            response = client.completions.create(prompt=prompt_enriched,
                                                stop_sequences=[anthropic.HUMAN_PROMPT],
                                                max_tokens_to_sample=self.target_requested_output_tokens,
                                                model=self.model_name,
                                                stream=False,
                                                temperature=self.temperature)

            #text_out = list(response)[-1].completion
            text_out = response.completion

            input_count = client.count_tokens(prompt_enriched)
            output_count = client.count_tokens(text_out)

            usage = {"input": input_count, "output": output_count, "total": input_count + output_count,
                     "metric": "tokens", "processing_time": time.time() - time_start}

        except Exception as e:
            # this is special error code that will be picked and handled by calling function
            text_out = "/***ERROR***/"
            usage = {"input":0, "output":0, "total":0, "metric": "tokens",
                     "processing_time": time.time() - time_start}

            # raise LLMInferenceResponseException(e)
            logging.error("error: Anthropic model inference produced error - %s ", e)

        output_response = {"llm_response": text_out, "usage": usage}

        logging.info(f"update: output_response - anthropic: {output_response}")
     
        return output_response


class GoogleGenModel:

    """ GoogleGenModel class implements the Google Vertex API for Google's generative models.
    Note: to use GoogleModels does require a separate import of Google SDKs - vertexai and google.cloud.platform """

    def __init__(self, model_name=None, api_key=None, context_window=8192):

        try:
            from vertexai.preview.language_models import TextGenerationModel, TextEmbeddingModel
            from vertexai import init
            import google.cloud.aiplatform as aiplatform
        except:
            raise DependencyNotInstalledException("google-cloud-aiplatform")

        self.api_key = api_key
        self.model_name = model_name
        self.model = None
        self.error_message = "\nUnable to connect to Google/PALM Model. Please try again later."
        self.separator = "\n"

        # need to confirm max input and output
        #   set max_total_len -> adjust input and output based on use case
        self.max_total_len = context_window
        self.max_input_len = int(context_window*0.5)

        # need to check max output for Google - may be asymmetrical cap
        self.llm_max_output_len = 1024

        # inference settings
        self.temperature = 0.7
        self.target_requested_output_tokens = 100
        self.add_prompt_engineering = False
        self.add_context = ""

    def set_api_key(self, api_key, env_var="USER_MANAGED_GOOGLE_API_KEY"):

        # set api_key
        os.environ[env_var] = api_key
        logging.info("update: added and stored GOOGLE api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_GOOGLE_API_KEY"):

        self.api_key = os.environ.get(env_var)
        return self.api_key

    def token_counter(self, text_sample):

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids

        return len(toks)

    def prompt_engineer (self, query, context, inference_dict=None):

        if not self.add_prompt_engineering:
            if context:
                selected_prompt = "default_with_context"
            else:
                selected_prompt = "default_no_context"
        else:
            selected_prompt = self.add_prompt_engineering

        prompt_dict = PromptCatalog().build_core_prompt(prompt_name=selected_prompt,
                                                        separator=self.separator,
                                                        query=query,
                                                        context=context,
                                                        inference_dict=inference_dict)

        if prompt_dict:
            prompt_engineered = prompt_dict["core_prompt"]

        else:
            # default case -> prompt = input query
            prompt_engineered = "Please read the following text: " + context + \
                                " and answer the question: " + query

        return prompt_engineered

    def inference(self, prompt, add_context=None, add_prompt_engineering=None, inference_dict=None,
                  api_key=None):
 
        if add_context:
            self.add_context = add_context

        if add_prompt_engineering:
            self.add_prompt_engineering = add_prompt_engineering

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

        # api_key
        if api_key:
            self.api_key = api_key

        if not self.api_key:
            self.api_key = self._get_api_key()

        if not self.api_key:
            logging.error("error: invoking Google Generative model with no api_key")

        prompt_enriched = self.prompt_engineer(prompt,self.add_context, inference_dict=inference_dict)

        self.target_requested_output_tokens= 2000
        # note: google api is not well-documented

        time_start = time.time()

        try:

            # Important: Before calling the model, we need to ensure the contents of the
            # api_key (the json dict string) have been persisted to a file
            # and the environment variable GOOGLE_APPLICATION_CREDENTIALS points to that file path

            google_json_credentials = self.api_key_to_json()
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_json_credentials

            self.model = TextGenerationModel.from_pretrained("text-bison@001")
            response = self.model.predict(prompt=prompt_enriched,
                                          temperature=0.7)

            logging.info(f"google model response: {response.text}")
         
            text_out = response.text

            input_count = len(prompt_enriched)
            output_count = len(text_out)

            usage = {"input": input_count, "output": output_count, "total": input_count + output_count,
                     "metric": "characters","processing_time": time.time() - time_start}

        except Exception as e:

            # this is special error code that will be picked and handled in AIModels().inference handler
            text_out = "/***ERROR***/"
            usage = {"input":0, "output":0, "total":0, "metric": "characters",
                     "processing_time": time.time() - time_start}

            # raise LLMInferenceResponseException(e)
            logging.error("error: Google model inference produced error:  %s", e)

        finally:
            # Close the credentials json which automatically deletes it (since it is a NamedTemporaryFile)
            os.remove(google_json_credentials)
        
        output_response = {"llm_response": text_out, "usage": usage}

        logging.info("update: output_response - google: %s ", output_response)

        return output_response
    
    def api_key_to_json(self):

        # Google authentication key is an entire json dictionary which we have the user pass in as an env var
        # We write out the json and we need to escape newlines which seem to be always present in
        # google auth json files

        temp_json_path = tempfile.NamedTemporaryFile(prefix="googlecreds", delete=False).name

        with open(temp_json_path, "w", encoding='utf-8') as f:
            f.write(self.api_key.replace("\n", "\\n"))

        return temp_json_path


class JurassicModel:

    """ JurassicModel class implements the AI21 Jurassic API. """

    def __init__(self, model_name=None, api_key=None, context_window=2048):

        self.api_key = api_key
        self.model_name = model_name

        self.error_message = "\nUnable to connect to Jurassic. Please try again later."

        self.separator = " -- "

        #   set max_total_len -> adjust input and output based on use case
        self.max_total_len = context_window
        self.max_input_len = int(context_window * 0.5)

        self.llm_max_output_len = int(context_window * 0.5)

        # inference settings
        self.temperature = 0.7
        self.target_requested_output_tokens = 100
        self.add_prompt_engineering = False
        self.add_context = ""

        # 'j2-jumbo-instruct', 'j2-grande-instruct','j2-jumbo','j2-grande', 'j2-large'

    def set_api_key(self, api_key, env_var="USER_MANAGED_AI21_API_KEY"):

        # set api_key
        os.environ[env_var] = api_key
        logging.info("update: added and stored AI21 api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_AI21_API_KEY"):
        self.api_key = os.environ.get(env_var)
        return self.api_key

    def token_counter(self, text_sample):

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids

        return len(toks)

    def prompt_engineer (self, query, context, inference_dict=None):

        if not self.add_prompt_engineering:
            if context:
                selected_prompt = "default_with_context"
            else:
                selected_prompt = "default_no_context"
        else:
            selected_prompt = self.add_prompt_engineering

        prompt_dict = PromptCatalog().build_core_prompt(prompt_name=selected_prompt,
                                                        separator=self.separator,
                                                        query=query,
                                                        context=context,
                                                        inference_dict=inference_dict)

        if prompt_dict:
            prompt_engineered = prompt_dict["core_prompt"]
        else:

            # default case
            prompt_engineered = "Please read the following text: " + context + " -- "
            prompt_engineered += " ## "
            prompt_engineered += "Please answer the following question based on the text: " + query
            prompt_engineered += " ## "

        return prompt_engineered

    def inference(self, prompt, add_context=None, add_prompt_engineering=None, inference_dict=None,
                  api_key=None):

        if add_context:
            self.add_context = add_context

        if add_prompt_engineering:
            self.add_prompt_engineering = add_prompt_engineering

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

        if api_key:
            self.api_key = api_key

        if not self.api_key:
            self.api_key = self._get_api_key()

        if not self.api_key:
            logging.error("error: invoking AI21 Jurassic model with no api_key")

        prompt_enriched = prompt

        prompt_enriched = self.prompt_engineer(prompt_enriched,self.add_context, inference_dict=inference_dict)

        time_start = time.time()

        try:
            ai21.api_key = self.api_key

            response = ai21.Completion.execute(
                model=self.model_name,
                prompt=prompt_enriched,
                numResults=1,
                maxTokens=self.target_requested_output_tokens,
                temperature=0.7,
                topKReturn=0,
                topP=1,
                stopSequences=["##"]
                )

            # api parameters: {"prompt", "numResults", "maxTokens", "minTokens", "temperature", "topP",
            #   "stopSequences" = list of sequences that when generated will cause the model to stop
            #   "topKReturn" = number of top scoring tokens to consider in each generation step
            #   "frequencyPenalty" = penalty applied to frequently generated tokens
            #   "presencePenalty" =  penalty applied to tokens already present in the prompt.
            #   "countPenalty" = penalty applied to tokens based on frequency in the generated responses.

            text_out = response["completions"][0]["data"]["text"]

            usage = {"input": len(prompt_enriched), "output": len(text_out),
                     "total": len(prompt_enriched) + len(text_out), "metric": "chars",
                     "processing_time": time.time() - time_start}

        except Exception as e:

            # this is special error code that will be picked and handled in inference handler

            text_out = "/***ERROR***/"

            usage = {"input": 0, "output": 0, "total": 0, "metric": "chars",
                     "processing_time": time.time() - time_start}

            # raise LLMInferenceResponseException(e)
            logging.error("error: Jurassic model inference produced error - %s ", e)

        # will look to capture usage metadata

        output_response = {"llm_response": text_out, "usage": usage}

        return output_response


class CohereGenModel:

    """ CohereGenModel class implements the API for Cohere's generative models. """

    def __init__(self, model_name=None, api_key=None, context_window=2048):

        self.api_key = api_key
        self.model_name = model_name

        self.error_message = "\nUnable to connect to Cohere. Please try again later."

        self.separator = " -- "

        #   set max_total_len -> adjust input and output based on use case
        #   confirmed - Cohere generation models - 2048 max context window
        self.max_total_len = context_window
        self.max_input_len = int(context_window * 0.5)

        self.llm_max_output_len = int(context_window * 0.5)

        # inference settings
        self.temperature = 0.7
        self.target_requested_output_tokens = 100
        self.add_prompt_engineering = False
        self.add_context = ""

        # cohere generative models - 'command-medium-nightly',
        # 'command-xlarge-nightly','xlarge','medium', "summarize-xlarge", "summarize-medium"

    def set_api_key(self, api_key, env_var="USER_MANAGED_COHERE_API_KEY"):

        # set api_key
        os.environ[env_var] = api_key
        logging.info("update: added and stored COHERE api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_COHERE_API_KEY"):

        self.api_key = os.environ.get(env_var)

        return self.api_key

    def token_counter(self, text_sample):

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids

        return len(toks)

    def prompt_engineer (self, query, context, inference_dict=None):

        # Cohere prompt prototype - very simple - uses " -- " as separators - does not like " " at the end

        if not self.add_prompt_engineering:
            if context:
                selected_prompt = "default_with_context"
            else:
                selected_prompt = "default_no_context"
        else:
            selected_prompt = self.add_prompt_engineering

        prompt_dict = PromptCatalog().build_core_prompt(prompt_name=selected_prompt,
                                                        separator=self.separator,
                                                        query=query,
                                                        context=context,
                                                        inference_dict=inference_dict)

        if prompt_dict:
            prompt_engineered = prompt_dict["core_prompt"]
        else:
            # default case
            prompt_engineered = "Please read the following materials: " + context + self.separator
            prompt_engineered += "Please answer the following question: " + query + self.separator
            prompt_engineered += "Please answer the question only with facts provided in the materials.  " \
                                 "If the question can not be answered in the materials, then please " \
                                 "respond 'Not Found.'"

        return prompt_engineered

    def inference(self, prompt, add_context=None, add_prompt_engineering=None, inference_dict=None,
                  api_key=None):

        if add_context:
            self.add_context = add_context

        if add_prompt_engineering:
            self.add_prompt_engineering = add_prompt_engineering

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

        #tokens_in_prompt = self.token_counter(prompt)
        #tokens_in_context = self.token_counter(self.add_context)

        prompt_enriched = prompt

        logging.info("update: in cohere model inference: %s - %s", prompt_enriched, self.add_prompt_engineering)

        prompt_enriched = self.prompt_engineer(prompt_enriched,self.add_context, inference_dict=inference_dict)

        if api_key:
            self.api_key = api_key

        if not self.api_key:
            self.api_key = self._get_api_key()

        if not self.api_key:
            logging.error("error: invoking Cohere Generative model with no api_key")

        co = cohere.Client(self.api_key)

        time_start = time.time()

        try:

            if self.model_name in ["summarize-xlarge", "summarize-medium"]:
                # alternate - summarize api
                response = co.summarize(text=self.add_context, model=self.model_name, length='short', temperature=0.7,
                                        format="bullets", extractiveness='medium', additional_command=prompt)

                text_out = response.summary

                usage = {"input": len(prompt_enriched), "output": len(text_out),
                         "total": len(prompt_enriched) + len(text_out), "metric": "chars",
                         "processing_time": time.time() - time_start}

            else:
                # generate api
                response = co.generate(model=self.model_name, prompt=prompt_enriched,
                                       max_tokens=self.target_requested_output_tokens, temperature=0.6,
                                       stop_sequences=["--"])

                text_out = response.generations[0].text

                usage = {"input": len(prompt_enriched), "output": len(text_out),
                         "total": len(prompt_enriched) + len(text_out), "metric": "chars",
                         "processing_time": time.time() - time_start}

        except Exception as e:

            # print(traceback.format_exc())

            text_out = "/***ERROR***/"

            usage = {"input": 0, "output": 0, "total": 0, "metric": "chars",
                     "processing_time": time.time() - time_start}

            # raise LLMInferenceResponseException(e)
            logging.error("error: Cohere model inference produced error - %s - ", e)

        # will look to capture usage metadata

        output_response = {"llm_response": text_out, "usage": usage}

        logging.info("update:  output response - cohere : %s ", output_response)

        return output_response


class AIBReadGPTModel:

    """ AIBReadGPT implements the AIB Bloks API for the READ GPT model. """

    def __init__(self, model_name=None, api_key=None, context_window=2048):

        self.api_key = api_key

        self.model_name = model_name
        self.model = None
        self.tokenizer = None

        self.error_message = "\nUnable to connect to AIB READ GPT API. Please try again later."

        #   set max_total_len -> adjust input and output based on use case
        self.max_total_len = context_window
        self.max_input_len = int(0.4 * context_window)
        self.llm_max_output_len = int(0.4 * context_window)

        self.separator = "\n"

        # inference settings
        self.temperature = 0.2
        self.target_requested_output_tokens = 200
        self.add_prompt_engineering = True
        self.add_context = ""

    def set_api_key(self, api_key, env_var="USER_MANAGED_READ_GPT_API_KEY"):

        # set api_key
        os.environ[env_var] = api_key
        logging.info("update: added and stored READ_GPT api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_READ_GPT_API_KEY"):

        self.api_key = os.environ.get(env_var)

        return self.api_key

    def token_counter(self, text_sample):

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids
        return len(toks)

    # very simple prompt construction used for now -> will likely evolve over time
    def prompt_engineer(self, query, context, inference_dict=None):

        if not query:
            query = "What is a list that summarizes the key points?"

        # default_case
        prompt_engineered = context + "\n" + query

        if self.add_prompt_engineering == "top_level_summary_select":
            prompt_engineered += query + "\n"
            prompt_engineered += "Which of the following selections best answers the question?"
            prompt_engineered += context

        if self.add_prompt_engineering == "summarize_with_bullets_no_query":
            issue = "What is a list of the most important points?"
            prompt_engineered = context + "\n" + issue

        return prompt_engineered

    def load_model_for_inference(self, model_name=None, model_card=None, fp=None):
        # look up model_name in configs
        if model_name:
            self.model_name = model_name
        return self

    def load_pretrained_model(self, model_name=None):
        if model_name:
            self.model_name = model_name
        # convenience method for pretrained models as a single step
        return self

    def inference(self, prompt, add_context=None, add_prompt_engineering=None, inference_dict=None,
                  api_key=None):

        if add_context:
            self.add_context = add_context

        if add_prompt_engineering:
            self.add_prompt_engineering = add_prompt_engineering

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

        prompt_enriched = self.prompt_engineer(prompt, self.add_context, inference_dict=inference_dict)

        # safety check on length - set cap with small 'buffer'
        input_tokens = self.token_counter(prompt_enriched)
        buffer = 10
        available_tokens_in_output_context_window = self.max_total_len - input_tokens - buffer
        # if target requested output is less, then keep - otherwise, cap with 'safe' maximum len
        target_len = min(self.target_requested_output_tokens, available_tokens_in_output_context_window)

        output_dict_new = {}
        output_response = {}
        usage = {"input": input_tokens}

        if api_key:
            self.api_key = api_key

        if not self.api_key:
            self.api_key = self._get_api_key()

        params = {"prompt": prompt_enriched, "max_output_tokens": target_len, "api_key": self.api_key}

        time_start = time.time()

        try:
            # linked to TEST SERVER
            output = requests.post(os.environ.get("AIB_READ_GPT_URI"), data=params)
            output_dict_new = ast.literal_eval(output.text)
            success_path = 1

        except:

            text_output = "/***ERROR***/"
            usage = {"input": 0, "output": 0, "total": 0, "metric": "tokens",
                     "processing_time": time.time() - time_start}

            logging.error("error: no response from aib remote server for aib-read-gpt model - "
                          "check api key and connection")

            success_path = -1
            output_response = {"llm_response": "", "usage": usage}

        # quick postprocessing

        if success_path == 1:

            for keys, values in output_dict_new.items():
                if keys.startswith("response_"):
                    response = output_dict_new[keys]

                    output_len = self.token_counter(response)
                    usage.update({"output": output_len})
                    usage.update({"total": usage["input"] + output_len})
                    usage.update({"metric": "tokens"})
                    usage.update({"processing_time": time.time() - time_start})

                    output_response = {"llm_response": response, "usage": usage}

                    logging.info("update: output_response - aib-read-gpt - %s", output_response)

                if keys == "message":
                    logging.error("error - output not received from model")

        return output_response


class LLMWareModel:

    """LLMWareModel class implements the API for LLMWare generative models. """

    def __init__(self, model_name=None, api_key=None, context_window=2048):

        self.api_key = api_key

        self.model_name = model_name
        self.model = None
        self.tokenizer = None

        self.error_message = "\nUnable to connect to LLMWare GPT API. Please try again later."

        #   set max_total_len -> adjust input and output based on use case
        self.max_total_len = context_window
        self.max_input_len = int(0.4 * context_window)
        self.llm_max_output_len = int(0.4 * context_window)

        self.separator = "\n"

        # inference settings
        self.temperature = 0.2
        self.target_requested_output_tokens = 200
        self.add_prompt_engineering = True
        self.add_context = ""

    def set_api_key(self, api_key, env_var="USER_MANAGED_LLMWARE_GPT_API_KEY"):

        # set api_key
        os.environ[env_var] = api_key
        logging.info("update: added and stored READ_GPT api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_LLMWARE_GPT_API_KEY"):

        self.api_key = os.environ.get(env_var)

        return self.api_key

    def token_counter(self, text_sample):

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids
        return len(toks)

    # very simple prompt construction used for now -> will likely evolve over time
    def prompt_engineer(self, query, context, inference_dict=None):

        if not query:
            query = "What is a list that summarizes the key points?"

        # default_case
        prompt_engineered = context + "\n" + query

        if self.add_prompt_engineering == "top_level_summary_select":
            prompt_engineered += query + "\n"
            prompt_engineered += "Which of the following selections best answers the question?"
            prompt_engineered += context

        if self.add_prompt_engineering == "summarize_with_bullets_no_query":
            issue = "What is a list of the most important points?"
            prompt_engineered = context + "\n" + issue

        return prompt_engineered

    def load_model_for_inference(self, model_name=None, model_card=None,fp=None):
        # look up model_name in configs
        if model_name:
            self.model_name = model_name
        return self

    def load_pretrained_model(self, model_name=None):
        if model_name:
            self.model_name = model_name
        # convenience method for pretrained models as a single step
        return self

    def inference(self, prompt, add_context=None, add_prompt_engineering=None, inference_dict=None,
                  api_key=None):

        if add_context:
            self.add_context = add_context

        if add_prompt_engineering:
            self.add_prompt_engineering = add_prompt_engineering

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

        prompt_enriched = self.prompt_engineer(prompt, self.add_context, inference_dict=inference_dict)

        # safety check on length - set cap with small 'buffer'
        input_tokens = self.token_counter(prompt_enriched)
        buffer = 10
        available_tokens_in_output_context_window = self.max_total_len - input_tokens - buffer
        # if target requested output is less, then keep - otherwise, cap with 'safe' maximum len
        target_len = min(self.target_requested_output_tokens, available_tokens_in_output_context_window)

        output_dict_new = {}
        output_response = {}
        usage = {"input": input_tokens}

        if api_key:
            self.api_key = api_key

        if not self.api_key:
            self.api_key = self._get_api_key()

        params = {"context": self.add_context,
                  "question": prompt,
                  "max_output_tokens": target_len,
                  "api_key": self.api_key}

        # params = {"context": prompt["context"],"question": prompt["query"], "max_output_tokens": 50, "api_key": good_key}

        time_start = time.time()

        try:

            output = requests.post(os.environ.get("LLMWARE_GPT_URI"), data=params)
            output_dict_new = ast.literal_eval(output.text)
            success_path = 1
            output_response = output_dict_new

        except:

            text_output = "/***ERROR***/"
            usage = {"input": 0, "output": 0, "total": 0, "metric": "tokens",
                     "processing_time": time.time() - time_start}

            logging.error("error: no response from aib remote server for llmware-gpt model - "
                          "check api key and connection")

            success_path = -1
            output_response = {"llm_response": "", "usage": usage}

        return output_response


class OpenAIEmbeddingModel:

    """ OpenaIEmbeddingModel class implements the OpenAI API for embedding models, specifically text-ada. """

    def __init__(self, model_name=None, api_key=None, embedding_dims=None):

        # must have elements for embedding model
        self.model_name = model_name
        self.api_key = api_key

        if not embedding_dims:
            self.embedding_dims = 1536
        else:
            self.embedding_dims = embedding_dims

        self.max_total_len = 2048

        self.error_message = "\nUnable to connect to OpenAI. Please try again later."

    def set_api_key(self, api_key,env_var="USER_MANAGED_OPENAI_API_KEY"):

        # set api_key
        os.environ[env_var] = api_key
        logging.info("update: added and stored OpenAI api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_OPENAI_API_KEY"):

        self.api_key = os.environ.get(env_var)
        return self.api_key

    def token_counter(self, text_sample):
        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids
        return len(toks)

    def embedding(self, text_sample, api_key=None):

        model = "text-embedding-ada-002"

        if api_key:
            self.api_key = api_key

        if not self.api_key:
            self.api_key = self._get_api_key()

        if not self.api_key:
            logging.error("error: invoking OpenAI Embedding model with no api_key")

        # need to prepare for batches
        if isinstance(text_sample, list):
            text_prompt = text_sample
            input_len = len(text_sample)
        else:
            text_prompt = [text_sample]
            input_len = 1

        # set as default openai base
        openai_api_base_entering_state = openai.api_base
        openai.api_base = "https://api.openai.com/v1"

        openai.api_key = self.api_key
        response = openai.Embedding.create(model=model, input=text_prompt)

        logging.info("update: response: %s ", response)

        if input_len == 1:
            embedding = response['data'][0]['embedding']
        else:
            embedding = []
            for i, entries in enumerate(response['data']):
                embedding.append(response['data'][i]['embedding'])

        # logging.info("update: embedding only: %s ", embedding)
        logging.info("update: embedding dims: %s ", len(embedding))

        # embedding = np.array(embedding)
        # embedding_2d = np.expand_dims(embedding, 0)

        # reset global environment variable to state before the inference
        #   --in most cases, this will be the same, but allows for overloaded use of this var with OpenChat
        openai.api_base = openai_api_base_entering_state

        return embedding


class CohereEmbeddingModel:

    """ CohereEmbeddingModel implements the Cohere API for embedding models. """

    def __init__(self, model_name = None, api_key=None, embedding_dims=None):

        self.api_key = api_key
        self.model_name = model_name

        if not embedding_dims:
            self.embedding_dims = 4096
        else:
            self.embedding_dims = embedding_dims

        self.max_total_len = 2048
        self.error_message = "\nUnable to connect to Cohere. Please try again later."

    def set_api_key(self, api_key, env_var="USER_MANAGED_COHERE_API_KEY"):

        # set api_key
        os.environ[env_var] = api_key
        logging.info("update: added and stored COHERE api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_COHERE_API_KEY"):

        self.api_key = os.environ.get(env_var)

        return self.api_key

    def token_counter(self, text_sample):
        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids
        return len(toks)

    def embedding(self,text_sample):

        if not self.api_key:
            self.api_key = self._get_api_key()

        if not self.api_key:
            logging.error("error: invoking Cohere embedding model with no api_key")

        co = cohere.Client(self.api_key)

        # need safety check on length of text_sample

        # need to prepare for batches
        if isinstance(text_sample, list):
            text_prompt = text_sample
            input_len = len(text_sample)
        else:
            text_prompt = [text_sample]
            input_len = 1

        # adding model name as parameter passed to the Cohere embedding API
        response = co.embed(text_prompt,model=self.model_name)

        output = []
        for i, emb in enumerate(response.embeddings):

            logging.info("update: embedding - %s - %s ", i, emb)

            # normalization of the Cohere embedding vector improves performance
            emb_vec = np.array(emb) / np.linalg.norm(emb)

            output.append(emb_vec)

        return output


class GoogleEmbeddingModel:

    """ GoogleEmbeddingModel implements the Google API for text embedding models.  Note: to use Google models
    requires a separate install of the Google SDKs, e.g., vertexai and google.cloud.platform """

    def __init__(self, model_name=None, api_key=None, embedding_dims=None):

        try:
            from vertexai.preview.language_models import TextGenerationModel, TextEmbeddingModel
            from vertexai import init
            import google.cloud.aiplatform as aiplatform
        except:
            raise DependencyNotInstalledException("google-cloud-aiplatform")

        self.api_key = api_key
        self.model_name = model_name

        self.max_total_len = 3072

        # supports context window up to 3072 tokens for embedding

        if not embedding_dims:
            self.embedding_dims = 768   # Google text-embedding-gecko-001 has 768 dims
        else:
            self.embedding_dims = embedding_dims

        self.error_message = "\nUnable to connect to Google/Text Embedding Model. Please try again later."

    def set_api_key(self, api_key, env_var="USER_MANAGED_GOOGLE_API_KEY"):

        # set api_key
        os.environ[env_var] = api_key
        logging.info("update: added and stored GOOGLE api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_GOOGLE_API_KEY"):

        self.api_key = os.environ.get(env_var)
        return self.api_key

    def token_counter(self, text_sample):
        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids
        return len(toks)

    def embedding(self,text_sample, api_key= None):

        if api_key:
            self.api_key = api_key

        if not self.api_key:
            self.api_key = self._get_api_key()

        if not self.api_key:
            logging.error("error: invoking Google Embedding model with no api_key")

        # Important: Before calling the model, we need to ensure the contents of the api_key
        # (the json dict string) have been persisted to a file
        # and the environment variable GOOGLE_APPLICATION_CREDENTIALS points to that file path

        google_json_credentials = self.api_key_to_json()
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_json_credentials

        embeddings_output = []

        try:

            model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")

            if isinstance(text_sample,list):
                text_list = text_sample
            else:
                text_list = [text_sample]

            # need to batch the text list
            # Google appears to set a cap of 5 text samples per embedding inference call

            google_max_samples_per_inference = 5

            batch_count = len(text_list) // google_max_samples_per_inference
            if batch_count * google_max_samples_per_inference < len(text_list):
                batch_count += 1

            for x in range(0, batch_count):
                new_batch = text_list[x*google_max_samples_per_inference:
                                      min((x+1)*google_max_samples_per_inference, len(text_list))]

                logging.info("update: new batch - %s - %s ", x, len(new_batch))

                embeddings_from_google = model.get_embeddings(new_batch)

                for i, embedding in enumerate(embeddings_from_google):
                    embeddings_output.append(np.array(embedding.values))

        except Exception as e:
            # raise LLMInferenceResponseException(e)
            logging.error("error: Google model inference produced error - %s ", e)

        finally:
            os.remove(google_json_credentials)

        return embeddings_output

    def api_key_to_json(self):

        # Google authentication key is an entire json dictionary which we have the user pass in as an env var
        # We write out the json and we need to escape newlines which seem to be always present in
        # google auth json files

        temp_json_path = tempfile.NamedTemporaryFile(prefix="googlecreds", delete=False).name
        with open(temp_json_path, "w", encoding='utf-8') as f:
            f.write(self.api_key.replace("\n", "\\n"))
        return temp_json_path


class HFEmbeddingModel:

    """HFEmbeddingModel class implements the API for HuggingFace embedding models. """

    def __init__(self, model=None, tokenizer=None, model_name=None, api_key=None, model_card=None,
                 embedding_dims=None):

        # pull in expected hf input
        self.model_name = model_name
        self.model = model
        self.tokenizer= tokenizer
        self.embedding_dims = embedding_dims
        self.model_type = None
        self.max_total_len = 2048
        self.model_architecture = None

        logging.info("update - loading HF Model - %s", model.config.to_dict())

        if self.model:

            self.config = model.config.to_dict()

            if "hidden_size" in self.config:
                self.embedding_dims = self.config["hidden_size"]
                logging.info("warning: embedding_dims - from config - %s ", self.embedding_dims)

            if "model_type" in self.config:
                self.model_type = self.config["model_type"]

            if "max_position_embeddings" in self.config:
                self.max_total_len = self.config["max_position_embeddings"]

            if "_name_or_path" in self.config:
                self.model_name = self.config["_name_or_path"]
                logging.info("update: model_name - from config - %s ", self.model_name)

            if "architectures" in self.config:
                if isinstance(self.config["architectures"],list):
                    self.model_architectures = self.config["architectures"][0]
                else:
                    self.model_architectures = self.config["architectures"]

        else:
            raise ModelNotFoundException(model_name)

        # no api key expected or required
        self.api_key = api_key

    def token_counter(self, text_sample):
        #   need to support HF tokenizer
        toks = self.tokenizer.encode(text_sample).ids
        return len(toks)

    # this is here for temporary reference - will be removed
    def stransformer_embedding(self, sentence):
        embedding = self.model.encode(sentence, convert_to_tensor=True)
        embedding_2d = embedding.unsqueeze(0)
        return embedding_2d

    def embedding (self, text_sample, api_key=None):

        # return embeddings only
        if isinstance(text_sample,list):
            sequence = text_sample

        else:
            sequence = [text_sample]

        logging.info("update: HFEmbedding.embedding() - %s ", len(text_sample))

        # shorter than 512
        model_inputs = self.tokenizer(sequence, truncation=True, max_length=500, return_tensors="pt",padding=True)

        model_outputs = self.model(model_inputs.input_ids,
                                   attention_mask=model_inputs.attention_mask, output_hidden_states=True)

        # the [cls] aggregated embedding is in the last hidden state
        # dims of [1, 768]

        embedding = model_outputs.hidden_states[-1][:,0]

        # embedding = embedding.detach().numpy()
        logging.info("update: hf embeddings output shape - %s ", embedding.shape)

        # normalize hf embeddings
        embeddings_normalized = torch.nn.functional.normalize(embedding, p=2, dim=1)
        embeddings_normalized = embeddings_normalized.detach().numpy()

        return embeddings_normalized


class HFGenerativeModel:

    """ HFGenerativeModel class implements the HuggingFace generative model API, and is used generally for
     models in HuggingFace repositories, e.g., Dragon, Bling, etc. """

    #   support instantiating HF model in two different ways:
    #       1.  directly passing a previously loaded HF model object and tokenizer object
    #       2.  passing a model_name only, which will then create the model and tokenizer

    def __init__(self, model=None, tokenizer=None, model_name=None, api_key=None, model_card=None,
                 prompt_wrapper=None, instruction_following=False, context_window=2048,
                 use_gpu_if_available=True, trust_remote_code=False):

        # pull in expected hf input
        self.model_name = model_name
        self.model = model
        self.tokenizer= tokenizer
        
        # note - these two parameters will control how prompts are handled - model-specific
        self.prompt_wrapper = prompt_wrapper
        self.instruction_following = instruction_following
        
        # instantiate if model_name passed without actual model and tokenizer
        if model_name and not model and not tokenizer:

            try:
                # will wrap in Exception if import fails and move to model catalog class
                from transformers import AutoModelForCausalLM, AutoTokenizer
            except:
                raise DependencyNotInstalledException("transformers")

            if api_key:
                if torch.cuda.is_available():
                    self.model = AutoModelForCausalLM.from_pretrained(model_name,token=api_key, trust_remote_code=trust_remote_code, torch_dtype="auto")
                else:
                    self.model = AutoModelForCausalLM.from_pretrained(model_name,token=api_key, trust_remote_code=trust_remote_code)
             
                self.tokenizer = AutoTokenizer.from_pretrained(model_name,token=api_key, trust_remote_code=trust_remote_code)
            else:
                if torch.cuda.is_available():
                    self.model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=trust_remote_code, torch_dtype="auto")
                else:
                    self.model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=trust_remote_code)
                self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=trust_remote_code)
            
            # set to defaults for HF models in Model Catalog
            # this can be over-ridden post initiation if needed for custom models
            self.prompt_wrapper = "human_bot"
            self.instruction_following = False
            
        self.trailing_space = ""
        
        self.model_type = None
        self.config = None
        self.max_total_len = context_window
        self.max_input_len = int(0.5 * context_window)
        self.llm_max_output_len = int(0.5 * context_window)
        self.model_architecture = None
        self.separator = "\n"

        # use 0 as eos token id by default in generation -> but try to pull from model config
        self.eos_token_id = 0

        #   will load model and inference onto gpu,
        #   if (a) CUDA available and (b) use_gpu_if_available set to True (default)
        self.use_gpu = torch.cuda.is_available() and use_gpu_if_available

        if self.model:

            if isinstance(self.model.config, dict):
                self.config = self.model.config
            else:
                self.config = self.model.config.to_dict()
            
            if "trailing_space" in self.config:
                self.trailing_space = self.config["trailing_space"]
                
            if "eos_token_id" in self.config:
                # only use to set if value is not None
                if self.config["eos_token_id"]:
                    self.eos_token_id = self.config["eos_token_id"]

            if "model_type" in self.config:
                self.model_type = self.config["model_type"]

            if "hidden_size" in self.config:
                self.embedding_dims = self.config["hidden_size"]

            if "max_position_embeddings" in self.config:
                self.max_total_len = self.config["max_position_embeddings"]

            if "architectures" in self.config:
                if isinstance(self.config["architectures"],list):
                    self.model_architectures = self.config["architectures"][0]
                else:
                    self.model_architectures = self.config["architectures"]

            # prepare model for inference
            self.model.eval()

            if self.use_gpu:
                self.model.to('cuda')
                logging.info("update: HFGenerative loading - moving model to cuda")

        else:
            logging.error("error: HFGenerativeModel - could not identify model  - ", model_name)

        # no api key expected or required
        self.api_key = api_key

        self.error_message = "\nUnable to identify and load HuggingFace model."

        # inference settings
        self.temperature = 0.5
        self.target_requested_output_tokens = 100
        self.add_prompt_engineering = False
        self.add_context = ""

    def set_api_key (self, api_key, env_var="USER_MANAGED_HF_API_KEY"):

        # set api_key
        os.environ[env_var] = api_key
        logging.info("update: added and stored HF api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key (self, env_var="USER_MANAGED_HF_API_KEY"):

        self.api_key = os.environ.get(env_var)

        if not self.api_key:
            logging.error("error: _get_api_key could not successfully retrieve value from: %s ", env_var)

        return self.api_key

    def token_counter(self, text_sample):
        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids
        return len(toks)

    def prompt_engineer (self, query, context, inference_dict):

        # if loaded model was not pretrained on instruction_following, then skip any instructions
        if not self.instruction_following:

            if context:
                output = context + "\n" + query
            else:
                output = query

            # unlikely that there would be an 'instruct wrapping' on text, but allow for possibility
            if self.prompt_wrapper:
                output = PromptCatalog().apply_prompt_wrapper(output, self.prompt_wrapper,
                                                              instruction=None)

            return output

        # move ahead to add instructions and prompt engineering

        if not self.add_prompt_engineering:
            if context:
                selected_prompt = "default_with_context"
            else:
                selected_prompt = "default_no_context"
        else:
            selected_prompt = self.add_prompt_engineering

        prompt_dict = PromptCatalog().build_core_prompt(prompt_name=selected_prompt,
                                                        separator=self.separator,
                                                        query=query,
                                                        context=context,
                                                        inference_dict=inference_dict)

        if prompt_dict:
            prompt_engineered = prompt_dict["core_prompt"]
        else:
            # default case
            prompt_engineered = "Please read the following text: " + context + self.separator
            prompt_engineered += "Based on this text, please answer the question: " + query + self.separator
            prompt_engineered += "Please answer the question only with facts provided in the materials.  " \
                                 "If the question can not be answered in the materials, then please " \
                                 "respond 'Not Found.'"

        #   final wrapping, based on model-specific instruct training format
        #   --provides a final 'wrapper' around the core prompt text, based on model expectations

        if self.prompt_wrapper:
            prompt_engineered = PromptCatalog().apply_prompt_wrapper(prompt_engineered, self.prompt_wrapper,
                                                                     instruction=None)

        return prompt_engineered

    @torch.no_grad()
    def inference(self, prompt, add_context=None, add_prompt_engineering=None, api_key=None,
                  inference_dict=None):

        # first prepare the prompt

        if add_context:
            self.add_context = add_context

        if add_prompt_engineering:
            self.add_prompt_engineering = add_prompt_engineering

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

        text_prompt = prompt

        if self.add_prompt_engineering:
            prompt_enriched = self.prompt_engineer(prompt, self.add_context, inference_dict=inference_dict)
            prompt_final = prompt_enriched
            
            # text_prompt = prompt_final + "\n"
            
            # most models perform better with no trailing space or line-break at the end of prompt
            #   -- in most cases, the trailing space will be ""
            #   -- yi model prefers a trailing "\n"
            #   -- keep as parameterized option to maximize generation performance
            #   -- can be passed either thru model_card or model config from HF
            
            text_prompt = prompt_final + self.trailing_space
            
        # second - tokenize to get the input_ids

        tokenizer_output = self.tokenizer.encode(text_prompt)
        input_token_len = len(tokenizer_output)
        input_ids = torch.tensor(tokenizer_output).unsqueeze(0)

        #   explicit check and setting to facilitate debugging
        if self.use_gpu:
            input_ids = input_ids.to('cuda')
        else:
            input_ids = input_ids.to('cpu')

        # time start
        time_start = time.time()

        #   Note: this is a simplified 'sampling' generation loop, derived from the far more
        #   sophisticated Generation capabilities provided by the Transformers library
        #   It is included here to enable transformers users to easily extend llmware to include
        #   their favorite generative models in the transformers library.

        #   The code below contains code copied from, derived from or inspired from the Huggingface
        #   transformers generation code.
        #   (https: // github.com / huggingface / transformers / src / transformers / generation)

        #   Copyright 2018 The Google AI Language Team Authors and The HuggingFace Inc.team.
        #   Copyright(c) 2018, NVIDIA CORPORATION.All rights reserved.
        #   Licensed under the Apache License, Version 2.0(the "License"); you may not use this
        #   file except in compliance with the License. You may obtain a copy of the License at
        #   http: // www.apache.org / licenses / LICENSE - 2.0 Unless required by applicable law or agreed
        #   to in writing, software distributed under the License is distributed on an "AS IS" BASIS,
        #   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License
        #   for the specific language governing permissions and limitations under the License.

        # default settings
        pad_token_id = 0
        
        # for most models, eos_token_id = 0, but llama and mistral = 2
        eos_token_id = [self.eos_token_id]
        # eos_token_id = [0]

        eos_token_id_tensor = torch.tensor(eos_token_id).to(input_ids.device)

        # keep track of which sequences are already finished
        unfinished_sequences = torch.ones(input_ids.shape[0], dtype=torch.long, device=input_ids.device)

        this_peer_finished = False  # used by synced_gpus only
        # auto-regressive generation
        new_tokens_generated = 0

        attn_mask = torch.ones(input_ids.shape[1]).unsqueeze(0)

        #   explicit check and setting to facilitate debugging, if needed
        if self.use_gpu:
            attn_mask = attn_mask.to('cuda')
        else:
            attn_mask = attn_mask.to('cpu')

        batch_size = input_ids.shape[0]
        seq_len = input_ids.shape[1]

        pkv = None

        while True:

            inp_one_time: torch.LongTensor = input_ids

            if new_tokens_generated > 0:
                inp_one_time = input_ids[:, -1:]

            #   explicit check and setting to facilitate debugging, if needed
            if self.use_gpu:
                inp0 = inp_one_time.to('cuda')
                inp1 = attn_mask.to('cuda')
            else:
                inp0 = inp_one_time.to('cpu')
                inp1 = attn_mask.to('cpu')

            # inp3 = torch.LongTensor([new_tokens_generated])

            # need to invoke forward pass on model
            # outputs = self.model(inp0,inp1,pkv)

            outputs = self.model(input_ids=inp0,attention_mask=inp1, past_key_values=pkv,
                                 return_dict=True)

            new_tokens_generated += 1

            next_token_logits = outputs.logits[:,-1,:]

            if self.temperature:
                next_token_scores = next_token_logits / self.temperature
            else:
                next_token_scores = next_token_logits

            # sample
            probs = nn.functional.softmax(next_token_scores, dim=-1)
            next_tokens = torch.multinomial(probs, num_samples=1).squeeze(1)

            # finished sentences should have their next token be a padding token
            if eos_token_id is not None:
                next_tokens = next_tokens * unfinished_sequences + pad_token_id * (1 - unfinished_sequences)

            # update generated ids, model inputs, and length for next step
            input_ids = torch.cat([input_ids, next_tokens[:, None]], dim=-1)

            #   testing output in progress starts here
            """
            print("update: input_ids -", input_ids)
            # outputs_detached = outputs.to('cpu')
            outputs_np = np.array(input_ids[0])
            output_str = self.tokenizer.decode(outputs_np)
            print("update: output string - ", output_str)
            """
            #   end - testing output in progress

            pkv = outputs.past_key_values

            # update attention mask
            attn_mask = torch.cat([attn_mask, attn_mask.new_ones((attn_mask.shape[0], 1))], dim=-1)

            # if eos_token was found in one sentence, set sentence to finished
            if eos_token_id_tensor is not None:
                unfinished_sequences = unfinished_sequences.mul(
                    next_tokens.tile(eos_token_id_tensor.shape[0], 1).ne(eos_token_id_tensor.unsqueeze(1)).prod(dim=0)
                )

                # stop when each sentence is finished
                if unfinished_sequences.max() == 0:
                    this_peer_finished = True

            # stop if we exceed the maximum length
            if new_tokens_generated > self.target_requested_output_tokens:
                this_peer_finished = True

            if this_peer_finished:
                break

        #   Generation completed - prepare the output

        if self.use_gpu:
            outputs_np = np.array(input_ids[0].to('cpu'))
        else:
            outputs_np = np.array(input_ids[0])

        output_only = outputs_np[input_token_len:]

        # print("update: output only - ", output_only)

        output_str = self.tokenizer.decode(output_only)
        
        # post-processing clean-up - stop at endoftext
        eot = output_str.find("<|endoftext|>")
        if eot > -1:
            output_str = output_str[:eot]
        
        # new post-processing clean-up - stop at </s>
        eots = output_str.find("</s>")
        if eots > -1:
            output_str = output_str[:eots]

        # post-processing clean-up - start after bot wrapper
        bot = output_str.find("<bot>:")
        if bot > -1:
            output_str = output_str[bot+len("<bot>:"):]
        
        # new post-processing cleanup - skip repeating starting <s>
        boss = output_str.find("<s>")
        if boss > -1:
            output_str = output_str[boss+len("<s>"):]
        
        # end - post-processing
        
        total_len = len(outputs_np)

        usage = {"input": input_token_len,
                 "output": total_len - input_token_len,
                 "total": total_len,
                 "metric": "tokens",
                 "processing_time": time.time() - time_start}

        output_response = {"llm_response": output_str, "usage": usage}

        return output_response


class ConfigStruct(Structure):

    """Utility method for managing ctypes/cpp interaction in GGUFGenerativeModel"""

    _fields_ = [
        ("context_length", c_int),
        ("gpu_layers", c_int),
        ("mmap", c_bool),
        ("mlock", c_bool),
    ]


class GGUFGenerativeModel:

    """ GGUFGenerativeModel implements interface into llama.cpp """

    #   This implementation of GGUFGenerativeModel includes code derived, inspired, and modified from ctransformers
    #   For more information on ctransformers: please see https://github.com/marella/ctransformers
    #
    #   ctransformers is a a Python and CPP wrapper on llama.cpp
    #   note:  we have attempted to conform with the ctransformers interface specification, for easy portability to
    #   integrate with llmware - over time, this interface specification may evolve
    #
    #   For more information on llama.cpp: please see https://github.com/ggerganov/llama.cpp - this is a pure C/C++
    #   implementation of core LLM models for performance and portability, and easy integration of K-quantization
    #
    #   For more information on GGUF models available on HF: please see TheBloke @ https://huggingface.co/TheBloke

    def __init__(self, model_name=None, model_card=None, api_key=None, prompt_wrapper=None, instruction_following=False,
                 context_window=2048, use_gpu_if_available=True, config=None):

        # defaults - "human_bot" & False
        self.model_name = model_name
        self.prompt_wrapper = prompt_wrapper
        self.instruction_following = instruction_following
        self.trailing_space = ""
        self.separator = "\n"
        self.eos_token_id = 0
        self.max_total_len = 2048
        self.max_input_len = int(0.5 * context_window)
        self.llm_max_output_len = int(0.5 * context_window)
        self.target_requested_output_tokens = 100
        self.add_prompt_engineering = False
        self.add_context = ""
        self.temperature = 0.3
        self.model_type = "gguf"

        if model_card:

            if "trailing_space" in model_card:
                self.trailing_space = model_card["trailing_space"]

            if "eos_token_id" in model_card:
                self.eos_token_id = model_card["eos_token_id"]

            if "context_window" in model_card:
                self.max_total_len = model_card["context_window"]

            if "temperature" in model_card:
                self.temperature = model_card["temperature"]

            if "prompt_wrapper" in model_card:
                self.prompt_wrapper = model_card["prompt_wrapper"]

        #   gguf specific attributes
        self.gguf_file = None
        self.gguf_repo = None
        self.config = config
        self._model_path = None
        self._config = config
        self._llm = None
        self._lib = None
        self._context = []

        #   if (a) CUDA available and (b) use_gpu_if_available set to True (default)
        #   note: this parameter is not currently used for GGUFGenerativeModels
        self.use_gpu = torch.cuda.is_available() and use_gpu_if_available

        # no api key expected or required
        self.api_key = api_key

        self.error_message = "\nUnable to identify and load GGUF Generative model."

        #   note: default sampling parameters set to conform with ctransformers implementation

        # sample
        self.top_k = 40
        self.top_p = 0.95
        self.temperature = 0.3
        self.repetition_penalty= 1.1
        self.last_n_tokens= 64
        self.seed = -1

        # eval
        self.batch_size= 8
        self.threads= -1

        # generate
        self.max_new_tokens = 256
        self.stop = None
        self.stream = False
        self.reset = True

        # model
        self.context_length = 2048
        self.gpu_layers = 50
        self.mmap = True
        self.mlock = False

        self.model_path = None

        self._llm = None
        self._lib = None
        self._context = []

    def load_model_for_inference(self, file_loading_path, model_card=None):

        if model_card:
            self.model_name = model_card["model_name"].split("/")[-1]
            self.gguf_file = model_card["gguf_file"]     # e.g., "ggml-model-q4_k_m.gguf",
            self.gguf_repo = model_card["gguf_repo"]     # e.g., "llmware/dragon-mistral-7b-v0-gguf"

        model_file = os.path.join(file_loading_path, self.gguf_file)

        if not Path(model_file).is_file():
            raise ValueError(f"Model path '{model_file}' doesn't exist.")

        self.model_type = "gguf"

        # self.gpu_layers = 50
        config_struct = ConfigStruct(context_length=self.context_length, gpu_layers=self.gpu_layers,
                                     mmap=self.mmap, mlock=self.mlock)

        self._lib = self.load_library()
        self._llm = self._lib.ctransformers_llm_create(model_file.encode(), self.model_type.encode(), config_struct)

        if self._llm is None:
            raise RuntimeError(
                f"Failed to create LLM '{self.model_type}' from '{model_file}'.")

        #   wip - over time, will support wider set of model architectures and types
        # architecture = self.ctransformers_llm_architecture().decode()
        # print("update: architecture - ", architecture)
        # if architecture: self.model_type = architecture

        return self

    def __getattr__(self, name):

        #   note: this implementation of the CTYPES / CPP interface is intended to be conforming with:
        #   -- https://github.com/marella/ctransformers/blob/main/models/llm.cc

        if name.startswith("ctransformers_llm_") and hasattr(self._lib, name):
            return partial(getattr(self._lib, name), self._llm)
        raise AttributeError(f"'LLM' object has no attribute '{name}'")

    def tokenize(self, text, add_bos_token = None):

        #   note: this implementation of the CTYPES / CPP interface is intended to be conforming with:
        #   -- https://github.com/marella/ctransformers/blob/main/models/llm.cc

        if add_bos_token is None:
            add_bos_token = self.model_type == "llama"
        tokens = (c_int * (len(text) + 1))()
        n_tokens = self.ctransformers_llm_tokenize(text.encode(), add_bos_token, tokens)

        return tokens[:n_tokens]

    def detokenize(self, tokens, decode):

        #   note: this implementation of the CTYPES / CPP interface is intended to be conforming with:
        #   -- https://github.com/marella/ctransformers/blob/main/models/llm.cc

        if isinstance(tokens, int):
            tokens = [tokens]
        texts = []
        for token in tokens:
            text = self.ctransformers_llm_detokenize(token)
            texts.append(text)
        texts = b"".join(texts)
        if decode:
            texts = texts.decode(errors="ignore")

            if tokens[:1] == [self.bos_token_id] and texts[:1] == " ":
                texts = texts[1:]

        return texts

    def eval(self, tokens):

        """Evaluates a list of tokens.  Args:  tokens: The list of tokens to evaluate.  {params} """

        #   note: this implementation of the CTYPES / CPP interface is intended to be conforming with:
        #   -- https://github.com/marella/ctransformers/blob/main/models/llm.cc

        # config = self.config
        batch_size = self.batch_size
        threads = self.threads

        n_past = len(self._context)
        n_tokens = len(tokens)

        # if n_past + n_tokens > self.context_length:  no_action_taken_replacing_logger = 0

        tokens = (c_int * n_tokens)(*tokens)
        status = self.ctransformers_llm_batch_eval(tokens, n_tokens, n_past, batch_size, threads)

        if not status:
            raise RuntimeError("Failed to evaluate tokens.")
        self._context.extend(tokens)

    def sample(self):

        """Samples a token from the model. Args: {params} Returns: The sampled token. """

        #   note: this implementation of the CTYPES / CPP interface is intended to be conforming with:
        #   -- https://github.com/marella/ctransformers/blob/main/models/llm.cc

        # config = self.config
        top_k = self.top_k
        top_p = self.top_p
        temperature = self.temperature
        repetition_penalty = self.repetition_penalty
        last_n_tokens = self.last_n_tokens
        seed = self.seed

        if last_n_tokens < 0:
            last_n_tokens = self.context_length
        last_tokens = self._context[-last_n_tokens:]
        n_last = len(last_tokens)
        last_tokens = (c_int * n_last)(*last_tokens)

        return self.ctransformers_llm_sample(last_tokens, n_last, top_k, top_p, temperature,
                                             repetition_penalty, seed)

    def prepare_inputs_for_generation(self, tokens):

        if not self.reset:
            return tokens

        # Keep at least one input token to evaluate the logits.
        n = min(len(tokens) - 1, len(self._context))
        l = 0
        while l < n and tokens[l] == self._context[l]:
            l += 1
        # Remove input tokens that are evaluated in the past and update context.
        tokens = tokens[l:]
        self._context = self._context[:l]

        return tokens

    def generate(self, tokens):

        #   note: this implementation of the CTYPES / CPP interface is intended to be conforming with:
        #   -- https://github.com/marella/ctransformers/blob/main/models/llm.cc

        tokens = self.prepare_inputs_for_generation(tokens)
        self.eval(tokens)

        while True:

            token = self.sample()

            self.eval([token])

            if self.ctransformers_llm_is_eos_token(token):
                break

            yield token

    def _stream(self, prompt):

        #   note: this implementation of the CTYPES / CPP interface is intended to be conforming with:
        #   -- https://github.com/marella/ctransformers/blob/main/models/llm.cc

        # config = self.config
        max_new_tokens = self.max_new_tokens
        stop = []
        if isinstance(stop, str):
            stop = [stop]

        tokens = self.tokenize(prompt)

        stop_regex = re.compile("|".join(map(re.escape, stop)))
        count = 0
        text = ""
        incomplete = b""
        for token in self.generate(tokens):

            # Handle incomplete UTF-8 multi-byte characters.
            incomplete += self.detokenize([token], decode=False)

            # complete, incomplete = utf8_split_incomplete(incomplete)

            """Splits a sequence of UTF-8 encoded bytes into complete and incomplete bytes."""
            i = len(incomplete)

            while i > 0 and (incomplete[i - 1] & 0b10000000) != 0:
                # while i > 0 and utf8_is_continuation_byte(seq[i - 1]):
                i -= 1
            complete = incomplete[:i]
            incomplete = incomplete[i:]

            text += complete.decode(errors="ignore")

            # https://github.com/abetlen/llama-cpp-python/blob/
            # 1a13d76c487df1c8560132d10bda62d6e2f4fa93/llama_cpp/llama.py#L686-L706
            # Check if one of the stop sequences is part of the text.
            # Note that the stop sequence may not always be at the end of text.
            if stop:
                match = stop_regex.search(text)
                if match:
                    text = text[: match.start()]
                    break

            # Avoid sending the longest suffix of text which is also a prefix
            # of a stop sequence, as it can form a stop sequence with the text
            # generated later.
            longest = 0
            for s in stop:
                for i in range(len(s), 0, -1):
                    if text.endswith(s[:i]):
                        longest = max(i, longest)
                        break

            end = len(text) - longest
            if end > 0:
                yield text[:end]
                text = text[end:]

            count += 1
            if count >= max_new_tokens:
                break

        if text:
            yield text

    def find_library(self):

        #   current implementation support in core library - will expand/evaluate over time

        lib_path = os.path.join(LLMWareConfig.get_config("shared_lib_path"), "gguf")
        system = platform.system()
        lib_file = None

        if platform.system() == "Windows":
            lib_file = "lib_ctransformers.dll"
        else:
            machine = os.uname().machine.lower()

            if system.lower() == "darwin":
                if machine not in ['arm64', 'x86_64']:
                    # default to arm64
                    lib_file = "lib_ctransformers_mac_os_aarch64.dylib"
                else:
                    if machine == 'arm64':
                        lib_file = "lib_ctransformers_mac_os_aarch64.dylib"
                    else:
                        lib_file = "lib_ctransformers_mac_os_x86_avx2.dylib"

            if system.lower() == "linux":
                if machine not in ['arm64', 'x86_64']:
                    # default to x86
                    lib_file = "lib_ctransformers_linux_x86_avx2.so"
                else:
                    if machine == 'x86_64':
                        lib_file = "lib_ctransformers_linux_x86_avx2.so"
                    else:

                        # lib_file = "lib_ctransformer_linux_arm64.so"
                        raise RuntimeError(f"No prebuilt llama.cpp lib for Linux Arm64 yet. "
                                           f"Options: \n1. run on current prebuilt "
                                           f"platforms - Mac Arch64, Mac x86, Linux x86, Windows; \n2. build lib "
                                           f"from source - see instructions in repository.")

        if not lib_file:
            raise RuntimeError(f"Failed to find matching library for - '{system}'.")

        path = os.path.join(lib_path, lib_file)

        return path

    def load_library(self):

        c_int_p = POINTER(c_int)
        c_float_p = POINTER(c_float)
        llm_p = c_void_p

        if os.environ.get("GGUF_CUSTOM_LIB_PATH"):
            #   allows user to build from source and pass as lib to use
            #   note: there are several prebuilt shared libraries available for llama.cpp

            path = os.environ.get("GGUF_CUSTOM_LIB_PATH")

            logging.info("update: custom gguf lib path - %s ", path)

        else:
            # default case
            path = self.find_library()
            # if "cuda" in path: self.load_cuda()

        #   note: this implementation of the CTYPES / CPP interface is intended to be conforming with:
        #   -- https://github.com/marella/ctransformers/blob/main/models/llm.cc

        try:
            lib = CDLL(path)
        except:
            raise ModuleNotFoundException("GGUF-Implementation")

        lib.ctransformers_llm_create.argtypes = [c_char_p, c_char_p, ConfigStruct]
        lib.ctransformers_llm_create.restype = llm_p

        lib.ctransformers_llm_delete.argtypes = [llm_p]
        lib.ctransformers_llm_delete.restype = None

        lib.ctransformers_llm_tokenize.argtypes = [llm_p, c_char_p, c_bool, c_int_p]
        lib.ctransformers_llm_tokenize.restype = c_int

        lib.ctransformers_llm_detokenize.argtypes = [llm_p, c_int]
        lib.ctransformers_llm_detokenize.restype = c_char_p

        lib.ctransformers_llm_is_eos_token.argtypes = [llm_p, c_int]
        lib.ctransformers_llm_is_eos_token.restype = c_bool

        lib.ctransformers_llm_eos_token_id.argtypes = [llm_p]
        lib.ctransformers_llm_eos_token_id.restype = c_int

        lib.ctransformers_llm_bos_token_id.argtypes = [llm_p]
        lib.ctransformers_llm_bos_token_id.restype = c_int

        lib.ctransformers_llm_vocab_size.argtypes = [llm_p]
        lib.ctransformers_llm_vocab_size.restype = c_int

        lib.ctransformers_llm_context_length.argtypes = [llm_p]
        lib.ctransformers_llm_context_length.restype = c_int

        lib.ctransformers_llm_architecture.argtypes = [llm_p]
        lib.ctransformers_llm_architecture.restype = c_char_p

        lib.ctransformers_llm_batch_eval.argtypes = [llm_p, c_int_p, c_int, c_int, c_int, c_int]
        lib.ctransformers_llm_batch_eval.restype = c_bool

        lib.ctransformers_llm_logits_data.argtypes = [llm_p]
        lib.ctransformers_llm_logits_data.restype = c_float_p
        lib.ctransformers_llm_logits_size.argtypes = [llm_p]
        lib.ctransformers_llm_logits_size.restype = c_int

        lib.ctransformers_llm_embeddings_data.argtypes = [llm_p]
        lib.ctransformers_llm_embeddings_data.restype = c_float_p
        lib.ctransformers_llm_embeddings_size.argtypes = [llm_p]
        lib.ctransformers_llm_embeddings_size.restype = c_int

        lib.ctransformers_llm_sample.argtypes = [llm_p, c_int_p, c_int, c_int, c_float, c_float, c_float, c_int]
        lib.ctransformers_llm_sample.restype = c_int

        lib.ctransformers_llm_reset.argtypes = [llm_p]
        lib.ctransformers_llm_reset.restype = None

        return lib

    def set_api_key(self, api_key, env_var="USER_MANAGED_HF_API_KEY"):

        # set api_key
        os.environ[env_var] = api_key
        logging.info("update: added and stored HF api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_HF_API_KEY"):

        self.api_key = os.environ.get(env_var)

        if not self.api_key:
            logging.error("error: _get_api_key could not successfully retrieve value from: %s ", env_var)

        return self.api_key

    def token_counter(self, text_sample):
        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids
        return len(toks)

    def prompt_engineer(self, query, context, inference_dict):

        # if loaded model was not pretrained on instruction_following, then skip any instructions
        if not self.instruction_following:

            if context:
                output = context + "\n" + query
            else:
                output = query

            # unlikely that there would be an 'instruct wrapping' on text, but allow for possibility
            if self.prompt_wrapper:
                output = PromptCatalog().apply_prompt_wrapper(output, self.prompt_wrapper,
                                                              instruction=None)

            return output

        # move ahead to add instructions and prompt engineering

        if not self.add_prompt_engineering:
            if context:
                selected_prompt = "default_with_context"
            else:
                selected_prompt = "default_no_context"
        else:
            selected_prompt = self.add_prompt_engineering

        prompt_dict = PromptCatalog().build_core_prompt(prompt_name=selected_prompt,
                                                        separator=self.separator,
                                                        query=query,
                                                        context=context,
                                                        inference_dict=inference_dict)

        if prompt_dict:
            prompt_engineered = prompt_dict["core_prompt"]
        else:
            # default case
            prompt_engineered = "Please read the following text: " + context + self.separator
            prompt_engineered += "Based on this text, please answer the question: " + query + self.separator
            prompt_engineered += "Please answer the question only with facts provided in the materials.  " \
                                 "If the question can not be answered in the materials, then please " \
                                 "respond 'Not Found.'"

        #   final wrapping, based on model-specific instruct training format
        #   --provides a final 'wrapper' around the core prompt text, based on model expectations

        if self.prompt_wrapper:
            prompt_engineered = PromptCatalog().apply_prompt_wrapper(prompt_engineered, self.prompt_wrapper,
                                                                     instruction=None)

        return prompt_engineered

    def inference(self, prompt, add_context=None, add_prompt_engineering=None,api_key=None,inference_dict=None):

        # first prepare the prompt

        if add_context:
            self.add_context = add_context

        if add_prompt_engineering:
            self.add_prompt_engineering = add_prompt_engineering

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

        text_prompt = prompt

        if self.add_prompt_engineering:
            prompt_enriched = self.prompt_engineer(prompt, self.add_context, inference_dict=inference_dict)
            prompt_final = prompt_enriched

            # text_prompt = prompt_final + "\n"

            # most models perform better with no trailing space or line-break at the end of prompt
            #   -- in most cases, the trailing space will be ""
            #   -- yi model prefers a trailing "\n"
            #   -- keep as parameterized option to maximize generation performance
            #   -- can be passed either thru model_card or model config from HF

            text_prompt = prompt_final + self.trailing_space

        time_start = time.time()

        text = self._stream(text_prompt)
        output_str = "".join(text)

        # post-processing clean-up - stop at endoftext
        eot = output_str.find("<|endoftext|>")
        if eot > -1:
            output_str = output_str[:eot]

        # new post-processing clean-up - stop at </s>
        eots = output_str.find("</s>")
        if eots > -1:
            output_str = output_str[:eots]

        # post-processing clean-up - start after bot wrapper
        bot = output_str.find("<bot>:")
        if bot > -1:
            output_str = output_str[bot + len("<bot>:"):]

        # new post-processing cleanup - skip repeating starting <s>
        boss = output_str.find("<s>")
        if boss > -1:
            output_str = output_str[boss + len("<s>"):]

        # end - post-processing

        input_toks = self.token_counter(text_prompt)
        output_toks = self.token_counter(output_str)

        usage = {"input": input_toks,
                 "output": output_toks,
                 "total": input_toks + output_toks,
                 "metric": "tokens",
                 "processing_time": time.time() - time_start}

        output_response = {"llm_response": output_str, "usage": usage}

        return output_response


class LLMWareSemanticModel:

    """ LLMWareSemanticModel class implements the LLMWareSemanticModel API, which is based on the SentenceTransformer
    architecture. """

    def __init__(self, model_name=None, model=None, embedding_dims=None, max_seq_length=150,
                 model_card=None, api_key=None):

        self.model_name = model_name
        self.error_message = "\nUnable to process LLMWare Semantic Model. Please try again later"

        self.max_input_len = 512
        self.max_output_len = 512
        self.max_seq_length = max_seq_length

        # to be applied to 'passed-in' Sentence Transformers model
        self.normalize_embeddings = True
        self.received_loaded_model = False

        # need to parameterize the embedding dims based on model config
        if not embedding_dims:
            self.embedding_dims = 768
            if model_name == 'mini-lm-sbert':
                self.embedding_dims = 384

        else:
            self.embedding_dims = embedding_dims

        self.model_repo_location = LLMWareConfig.get_model_repo_path()
        self.model_size="standard"
        if model_name == 'mini-lm-sbert':
            self.model_size = "mini"
        self.transformer_base_model = None

        if model:
            logging.info("update: SemanticEmbedding model received model - will attempt to load as "
                         "Sentence Transformer model")

            self.model = model
            self.received_loaded_model = True

            if len(model) >= 2:

                try:
                    #   general case is that embedding dimension is the "word_embedding_dimension" of the
                    #   'Pooling' layer, which is generally the second and last layer of the sbert model
                    self.embedding_dims = model[1].word_embedding_dimension

                    #   there are at least 2 edge cases, in which a "Dense" layer is attached after the
                    #   Pooling layer, and further consolidates the embeddings

                    if len(model) > 2:
                        logging.info("update: Sentence Transformer model with more than two layers - unusual - "
                                     " depending upon the architecture, there may be issues loading the model- %s",
                                     len(model))

                        #   note: the most common case is with a Dense 3rd layer that maps the Pooling output to
                        #   a different dimension - in this case - this should give the dimensions:
                        #
                        #           last_layer_config = model[-1].get_config_dict()
                        #           if "out_features" in last_layer_config:
                        #               self.embedding_dims = last_layer_config["out_features"]

                except:
                    logging.error("error: could not identify model to run embedding - ", model_name)
                    raise ModelNotFoundException(model_name)

        if model_card and not model:

            if "model_location" in model_card:
                if model_card["model_location"] == "st_repo":
                    # try to pull the model and instantiate directly from Sentence Transformers
                    try:
                        from sentence_transformers import SentenceTransformer
                    except:
                        raise DependencyNotInstalledException("sentence_transformer")

                    try:
                        self.model = SentenceTransformer(model_card["model_name"])
                    except:
                        raise ModelNotFoundException(model_card["model_name"])

                    if "embedding_dims" in model_card:
                        self.embedding_dims = model_card["embedding_dims"]
                    else:
                        self.embedding_dims = self.model[1].word_embedding_dimension

    def load_model_for_inference(self,fp=None, model_card=None):

        if fp:
            self.model_repo_location = fp

        self.model = STransformer(self.model_repo_location, model_size=self.model_size,
                                  max_seq_length=self.max_seq_length)

        return self

    def embedding(self, sentence):

        # embedding = self.model.encode(sentence, convert_to_tensor=True)
        embedding = self.model.encode(sentence)

        # add normalization for imported sentence transformer models
        """
        if self.received_loaded_model and self.normalize_embeddings:
            # normalize embeddings
            embedding = torch.tensor(embedding).squeeze(0)
            embedding = torch.nn.functional.normalize(embedding, p=2, dim=1)
            embedding = embedding.detach().numpy()
        """

        # embedding_2d = embedding.unsqueeze(0)
        return embedding

    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def euclidean_distance(self,a,b):
        # aligning with FAISS - which returns square of Euclidean distance
        return np.linalg.norm(a - b) * np.linalg.norm(a-b)


# The code that follows contains code copied from, derived from or inspired by Nils Reimers and the
# UKP Lab Sentence Transformers Model. (https://github.com/UKPLab/sentence-transformers)
# Copyright 2019 Nils Reimers
# Modifications Copyright 2023 llmware

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class STransformer (nn.Sequential):

    """STransformer class is simplified implementation of Sentence Transformers. """

    def __init__(self, model_path, max_seq_length=150, model_size="standard",
                 torch_dtype=torch.float32):

        super().__init__()

        self.do_lower_case=False
        self.max_seq_length = max_seq_length
        self.torch_dtype = torch_dtype
        self.device = 'cuda' if torch.cuda.is_available() else "cpu"

        logging.info("update - creating Transformer - model dims - %s ", model_size)

        self.word_embedding_model = Transformer(model_path, model_size=model_size)

        # pooling mode = "mean" by default
        self.pooling_model = Pooling(self.word_embedding_model.get_word_embedding_dimension())

        modules=[self.word_embedding_model, self.pooling_model]
        self.model = OrderedDict([(str(idx), module) for idx, module in enumerate(modules)])

    def tokenize(self, texts):
        return self.word_embedding_model.tokenize_wrapper(texts)

    def encode(self, sentences, batch_size=32, normalize_embeddings=True):

        self.eval()

        output_value = "sentence_embedding"
        convert_to_numpy = True
        convert_to_tensor = False
        normalize_embeddings = True
        device = None

        # output expected to be in numpy array

        input_was_string = False
        if isinstance(sentences, str) or not hasattr(sentences, '__len__'):
            sentences = [sentences]
            input_was_string = True

        self.to(self.device)

        all_embeddings = []
        length_sorted_idx = np.argsort([-self._text_length(sen) for sen in sentences])
        sentences_sorted = [sentences[idx] for idx in length_sorted_idx]

        show_progress_bar = None

        for start_index in trange(0, len(sentences), batch_size, desc="Batches", disable=not show_progress_bar):
            sentences_batch = sentences_sorted[start_index:start_index+batch_size]
            features = self.tokenize(sentences_batch)

            for key in features:
                if isinstance(features[key], Tensor):
                    features[key] = features[key].to(self.device)

            with torch.no_grad():

                out_features = self.forward(features)

                # assume sentence_embeddings only
                embeddings = out_features[output_value]
                embeddings = embeddings.detach()

                if normalize_embeddings:
                    embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

                if convert_to_numpy:
                    embeddings = embeddings.cpu()

                all_embeddings.extend(embeddings)

        all_embeddings = [all_embeddings[idx] for idx in np.argsort(length_sorted_idx)]

        if convert_to_tensor:
            all_embeddings = torch.stack(all_embeddings)

        elif convert_to_numpy:
            all_embeddings = np.asarray([emb.numpy() for emb in all_embeddings])

        if input_was_string:
            all_embeddings = all_embeddings[0]

        return all_embeddings

    def _text_length(self, text):

        if isinstance(text, dict):
            #   {key: value} case
            return len(next(iter(text.values())))

        elif not hasattr(text, '__len__'):
            #   Object has no len() method
            return 1

        elif len(text) == 0 or isinstance(text[0], int):
            #   Empty string or list of ints
            return len(text)

        else:
            #   Sum of length of individual strings
            return sum([len(t) for t in text])


class Transformer (nn.Module):

    """ Transformer is simplified implementation of wrapper utility class used to assemble Sentence Transformers. """

    def __init__(self, model_path, max_seq_length=150, do_lower_case= False, model_size="standard"):
        super().__init__()

        # need to look up model config first
        try:
            self.config = json.load(open(os.path.join(model_path,"config.json"), "r", encoding='utf-8'))

        except:
            if model_size == "mini":
                self.config = bert_mini_config
            else:
                self.config = bert_base_config

        self.config_keys = ['max_seq_length', 'do_lower_case']

        self.do_lower_case = do_lower_case
        self.max_seq_length = max_seq_length

        bert_config = BertConfig(config_dict=self.config)
        # print("loading weights from path - ", model_path)

        #   by default, assume BERT based model - TODO:  extend to Roberta base options
        self.auto_model = BertModel(bert_config).load_weights_from_file(model_path)

        tokenizer_file = "tokenizer.json"
        self.tokenizer = Utilities().load_tokenizer_from_file(os.path.join(model_path, tokenizer_file))

        # tokenizer is where the max_length is applied
        self.tokenizer.enable_truncation(max_length=self.max_seq_length,strategy="longest_first")
        self.tokenizer.enable_padding(pad_id=0)

    def forward(self, features):

        # note: features in forward from Transformer passed to Pooling layer for final output
        trans_features = {'input_ids': features['input_ids'], 'attention_mask': features['attention_mask']}
        output_states = self.auto_model(**trans_features)
        output_tokens = output_states[0]
        features.update({'token_embeddings': output_tokens, 'attention_mask': features['attention_mask']})

        return features

    def get_word_embedding_dimension(self):
        return self.auto_model.config.hidden_size

    def tokenize_wrapper(self, text, padding=True, truncation="longest_first"):

        self.tokenizer.enable_truncation(max_length=self.max_seq_length, strategy=truncation)
        if padding:
            self.tokenizer.enable_padding(pad_id=0)

        batch_input = self.tokenizer.encode_batch(text)

        input_id_list = []
        token_id_list = []
        am_list = []

        for i, encoding_obj in enumerate(batch_input):
            input_id_list.append(encoding_obj.ids)
            token_id_list.append(encoding_obj.type_ids)
            am_list.append(encoding_obj.attention_mask)

        inputs_agg = {"input_ids": torch.tensor(input_id_list, dtype=torch.long),
                      "token_type_ids": torch.tensor(token_id_list, dtype=torch.long),
                      "attention_mask": torch.tensor(am_list, dtype=torch.long)}

        return inputs_agg


class Pooling(nn.Module):

    """Pooling is a component of the Sentence Transformer architecture. """

    def __init__(self, word_embedding_dimension):

        super(Pooling, self).__init__()

        self.pooling_mode = "mean"
        self.word_embedding_dimension = word_embedding_dimension
        self.pooling_mode_mean_tokens = True

    def forward(self, features):

        token_embeddings = features['token_embeddings']
        attention_mask = features['attention_mask']

        #   Pooling strategy - "pooling_mode_mean_tokens"
        output_vectors = []

        self.pooling_mode_mean_tokens = True

        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)

        sum_mask = input_mask_expanded.sum(1)
        sum_mask = torch.clamp(sum_mask, min=1e-9)

        output_vectors.append(sum_embeddings / sum_mask)

        output_vector = torch.cat(output_vectors, 1)
        features.update({'sentence_embedding': output_vector})

        return features


"""PyTorch BERT model."""

# The code below contains code copied from, derived from or inspired from the PyTorch BERT model.
# (https://github.com/huggingface/transformers)
# Copyright 2018 The Google AI Language Team Authors and The HuggingFace Inc. team.
# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.

# Note: this is a very streamlined implementation of the BERT model, optimized for use in LLMWARE
# There are many features and options that have been purposefully omitted
# For a more robust implementation of BERT, please see the Google BERT repository, or HuggingFace

# coding=utf-8
# Copyright 2018 The Google AI Language Team Authors and The HuggingFace Inc. team.
# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


bert_base_config = {
    "_name_or_path": "bert-base-uncased",
    "architectures": [
        "BertModel"
    ],
    "attention_probs_dropout_prob": 0.1,
    "classifier_dropout": None,
    "gradient_checkpointing": False,
    "hidden_act": "gelu",
    "hidden_dropout_prob": 0.1,
    "hidden_size": 768,
    "initializer_range": 0.02,
    "intermediate_size": 3072,
    "layer_norm_eps": 1e-12,
    "max_position_embeddings": 512,
    "model_type": "bert",
    "num_attention_heads": 12,
    "num_hidden_layers": 12,
    "pad_token_id": 0,
    "position_embedding_type": "absolute",
    "torch_dtype": "float32",
    "type_vocab_size": 2,
    "use_cache": True,
    "vocab_size": 30522,
    "model_size": "standard"
}


bert_mini_config = {
    "_name_or_path": "nreimers/MiniLM-L6-H384-uncased",
    "architectures": [
        "BertModel"
    ],
    "attention_probs_dropout_prob": 0.1,
    "gradient_checkpointing": False,
    "hidden_act": "gelu",
    "hidden_dropout_prob": 0.1,
    "hidden_size": 384,   # vs 768
    "initializer_range": 0.02,
    "intermediate_size": 1536,  # vs. 3072
    "layer_norm_eps": 1e-12,
    "max_position_embeddings": 512,
    "model_type": "bert",
    "num_attention_heads": 12,
    "num_hidden_layers": 6, # vs. 12
    "pad_token_id": 0,
    "position_embedding_type": "absolute",
    "type_vocab_size": 2,
    "use_cache": True,
    "vocab_size": 30522,
    "model_size": "mini"
}


class BertConfig:

    # note: if no config passed, then defaults to standard 'bert-base-uncased' model
    def __init__(self, config_dict=None, **kwargs):

        # set default parameters -> will be over-ridden by any passed configs
        self.vocab_size =30522,
        self.hidden_size =768,
        self.num_hidden_layers =12,
        self.num_attention_heads =12,
        self.intermediate_size =3072,
        self.hidden_act ="gelu",
        self.hidden_dropout_prob =0.1,
        self.attention_probs_dropout_prob =0.1,
        self.max_position_embeddings =512,
        self.type_vocab_size =2,
        self.initializer_range =0.02,
        self.layer_norm_eps =1e-12,
        self.pad_token_id =0,
        self.position_embedding_type ="absolute",
        self.use_cache =True,
        self.classifier_dropout =None,
        self.model_size ="standard"

        for key in config_dict:
            setattr(self, key, config_dict[key])

        self.output_hidden_states = False
        self.output_attentions = False
        self.torch_dtype = kwargs.pop("torch_dtype", None)
        self.pruned_heads = kwargs.pop("pruned_heads", {})

        # self.tie_word_embeddings = kwargs.pop("tie_word_embeddings", True)


class BertEmbeddings(nn.Module):

    def __init__(self, config):
        super().__init__()

        self.word_embeddings = nn.Embedding(config.vocab_size, config.hidden_size,
                                            padding_idx=config.pad_token_id)
        self.position_embeddings = nn.Embedding(config.max_position_embeddings, config.hidden_size)
        self.token_type_embeddings = nn.Embedding(config.type_vocab_size, config.hidden_size)

        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)

        self.position_embedding_type = "absolute"

        self.register_buffer("position_ids", torch.arange(config.max_position_embeddings).expand((1, -1)))
        self.register_buffer(
            "token_type_ids", torch.zeros(self.position_ids.size(), dtype=torch.long), persistent=False
        )

    def forward(self, input_ids):

        past_key_values_length = 0

        input_shape = input_ids.size()
        seq_length = input_shape[1]

        position_ids = self.position_ids[:, past_key_values_length : seq_length + past_key_values_length]

        if hasattr(self, "token_type_ids"):
            buffered_token_type_ids = self.token_type_ids[:, :seq_length]
            buffered_token_type_ids_expanded = buffered_token_type_ids.expand(input_shape[0], seq_length)
            token_type_ids = buffered_token_type_ids_expanded
        else:
            token_type_ids = torch.zeros(input_shape, dtype=torch.long, device=self.position_ids.device)

        inputs_embeds = self.word_embeddings(input_ids)
        token_type_embeddings = self.token_type_embeddings(token_type_ids)

        embeddings = inputs_embeds + token_type_embeddings

        if self.position_embedding_type == "absolute":
            position_embeddings = self.position_embeddings(position_ids)
            embeddings += position_embeddings

        embeddings = self.LayerNorm(embeddings)
        embeddings = self.dropout(embeddings)
        return embeddings


class BertSelfAttention(nn.Module):

    def __init__(self, config):
        super().__init__()

        self.num_attention_heads = config.num_attention_heads
        self.attention_head_size = int(config.hidden_size / config.num_attention_heads)
        self.all_head_size = self.num_attention_heads * self.attention_head_size

        self.query = nn.Linear(config.hidden_size, self.all_head_size)
        self.key = nn.Linear(config.hidden_size, self.all_head_size)
        self.value = nn.Linear(config.hidden_size, self.all_head_size)

        self.dropout = nn.Dropout(config.attention_probs_dropout_prob)

        self.position_embedding_type = "absolute"

    def transpose_for_scores(self, x):
        new_x_shape = x.size()[:-1] + (self.num_attention_heads, self.attention_head_size)
        x = x.view(new_x_shape)
        return x.permute(0, 2, 1, 3)

    def forward(self, hidden_states, attention_mask= None):

        output_attentions = False

        mixed_query_layer = self.query(hidden_states)

        key_layer = self.transpose_for_scores(self.key(hidden_states))
        value_layer = self.transpose_for_scores(self.value(hidden_states))

        query_layer = self.transpose_for_scores(mixed_query_layer)

        # Take the dot product between "query" and "key" to get the raw attention scores.
        attention_scores = torch.matmul(query_layer, key_layer.transpose(-1, -2))

        attention_scores = attention_scores / math.sqrt(self.attention_head_size)
        if attention_mask is not None:
            # Apply the attention mask is (precomputed for all layers in BertModel forward() function)
            attention_scores = attention_scores + attention_mask

        # Normalize the attention scores to probabilities.
        attention_probs = nn.functional.softmax(attention_scores, dim=-1)

        # This is actually dropping out entire tokens to attend to (taken from original Transformer paper)
        attention_probs = self.dropout(attention_probs)

        context_layer = torch.matmul(attention_probs, value_layer)

        context_layer = context_layer.permute(0, 2, 1, 3).contiguous()
        new_context_layer_shape = context_layer.size()[:-2] + (self.all_head_size,)
        context_layer = context_layer.view(new_context_layer_shape)

        outputs = (context_layer, attention_probs) if output_attentions else (context_layer,)

        return outputs


class BertSelfOutput(nn.Module):

    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)

    def forward(self, hidden_states, input_tensor):
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states = self.LayerNorm(hidden_states + input_tensor)
        return hidden_states


class BertAttention(nn.Module):

    def __init__(self, config):
        super().__init__()
        self.self = BertSelfAttention(config)
        self.output = BertSelfOutput(config)
        self.pruned_heads = set()

    def prune_heads(self, heads):

        if len(heads) == 0:
            return
        heads, index = find_pruneable_heads_and_indices(
            heads, self.self.num_attention_heads, self.self.attention_head_size, self.pruned_heads
        )

        # Prune linear layers
        self.self.query = prune_linear_layer(self.self.query, index)
        self.self.key = prune_linear_layer(self.self.key, index)
        self.self.value = prune_linear_layer(self.self.value, index)
        self.output.dense = prune_linear_layer(self.output.dense, index, dim=1)

        # Update hyper params and store pruned heads
        self.self.num_attention_heads = self.self.num_attention_heads - len(heads)
        self.self.all_head_size = self.self.attention_head_size * self.self.num_attention_heads
        self.pruned_heads = self.pruned_heads.union(heads)

    def forward(self, hidden_states, attention_mask= None):

        self_outputs = self.self(hidden_states, attention_mask)
        attention_output = self.output(self_outputs[0], hidden_states)
        outputs = (attention_output,) + self_outputs[1:]  # add attentions if we output them
        return outputs


class BertIntermediate(nn.Module):

    def __init__(self, config):
        super().__init__()

        self.dense = nn.Linear(config.hidden_size, config.intermediate_size)
        self.intermediate_act_fn = nn.functional.gelu

    def forward(self, hidden_states):
        hidden_states = self.dense(hidden_states)
        hidden_states = self.intermediate_act_fn(hidden_states)
        return hidden_states


class BertOutput(nn.Module):

    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.intermediate_size, config.hidden_size)
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)

    def forward(self, hidden_states, input_tensor):
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states = self.LayerNorm(hidden_states + input_tensor)
        return hidden_states


class BertLayer(nn.Module):

    def __init__(self, config):
        super().__init__()

        self.seq_len_dim = 1
        self.attention = BertAttention(config)
        self.intermediate = BertIntermediate(config)
        self.output = BertOutput(config)

    def forward(self, hidden_states, attention_mask= None):

        self_attention_outputs = self.attention(hidden_states, attention_mask)
        attention_output = self_attention_outputs[0]
        outputs = self_attention_outputs[1:]

        layer_output = self.feed_forward_chunk(attention_output)

        outputs = (layer_output,) + outputs

        return outputs

    def feed_forward_chunk(self, attention_output):
        intermediate_output = self.intermediate(attention_output)
        layer_output = self.output(intermediate_output, attention_output)
        return layer_output


class BertEncoder(nn.Module):

    def __init__(self, config):
        super().__init__()

        self.config = config
        self.layer = nn.ModuleList([BertLayer(config) for _ in range(config.num_hidden_layers)])

    def forward(self, hidden_states, attention_mask= None):

        for i, layer_module in enumerate(self.layer):
            layer_outputs = layer_module(hidden_states, attention_mask)
            hidden_states = layer_outputs[0]

        return (hidden_states,)


class BertPooler(nn.Module):

    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.activation = nn.Tanh()

    def forward(self, hidden_states):
        # We "pool" the model by simply taking the hidden state corresponding to the first token.
        first_token_tensor = hidden_states[:, 0]
        pooled_output = self.dense(first_token_tensor)
        pooled_output = self.activation(pooled_output)
        return pooled_output


class BertModel (nn.Module):

    def __init__(self, config, add_pooling_layer=True, torch_dtype=torch.float16):
        super().__init__()

        self.config = config
        self.embeddings = BertEmbeddings(config)
        self.encoder = BertEncoder(config)
        self.pooler = BertPooler(config) if add_pooling_layer else None
        self.torch_dtype = torch_dtype
        self.dtype = torch_dtype

    def load_weights_from_file(self, fp=None):
        model_file = "pytorch_model.bin"
        self.load_state_dict(torch.load(os.path.join(fp,model_file), map_location=torch.device('cpu')), strict=False)
        logging.info("update: re-loaded model weights from file")
        self.eval()
        return self

    def _prune_heads(self, heads_to_prune):
        for layer, heads in heads_to_prune.items():
            self.encoder.layer[layer].attention.prune_heads(heads)

    def forward(self, input_ids, attention_mask= None):

        token_type_ids = None
        input_shape = input_ids.size()
        batch_size, seq_length = input_shape
        device = input_ids.device

        if attention_mask is None:
            attention_mask = torch.ones(((batch_size, seq_length)), device=device)

        if token_type_ids is None:
            if hasattr(self.embeddings, "token_type_ids"):
                buffered_token_type_ids = self.embeddings.token_type_ids[:, :seq_length]
                buffered_token_type_ids_expanded = buffered_token_type_ids.expand(batch_size, seq_length)
                token_type_ids = buffered_token_type_ids_expanded
            else:
                token_type_ids = torch.zeros(input_shape, dtype=torch.long, device=device)

        extended_attention_mask = self.get_extended_attention_mask(attention_mask, input_shape)

        embedding_output = self.embeddings(input_ids=input_ids)

        encoder_outputs = self.encoder(embedding_output, attention_mask=extended_attention_mask)

        sequence_output = encoder_outputs[0]
        pooled_output = self.pooler(sequence_output) if self.pooler is not None else None

        return (sequence_output, pooled_output) + encoder_outputs[1:]

    def get_extended_attention_mask(self, attention_mask, input_shape):

        if attention_mask.dim() == 3:
            extended_attention_mask = attention_mask[:, None, :, :]

        elif attention_mask.dim() == 2:
            # Provided a padding mask of dimensions [batch_size, seq_length]
            # - if the model is an encoder, make the mask:  [batch_size, num_heads, seq_length, seq_length]
            extended_attention_mask = attention_mask[:, None,None, :]

        else:
            raise ValueError(
                f"Wrong shape for input_ids (shape {input_shape}) or attention_mask (shape {attention_mask.shape})"
            )

        extended_attention_mask = extended_attention_mask.to(dtype=self.dtype)  # fp16 compatibility
        extended_attention_mask = (1.0 - extended_attention_mask) * torch.finfo(self.dtype).min
        return extended_attention_mask


def find_pruneable_heads_and_indices(heads, n_heads, head_size, already_pruned_heads):

    mask = torch.ones(n_heads, head_size)
    heads = set(heads) - already_pruned_heads  # Convert to set and remove already pruned heads
    for head in heads:
        # Compute how many pruned heads are before the head and move the index accordingly
        head = head - sum(1 if h < head else 0 for h in already_pruned_heads)
        mask[head] = 0
    mask = mask.view(-1).contiguous().eq(1)
    index: torch.LongTensor = torch.arange(len(mask))[mask].long()
    return heads, index


def prune_linear_layer(layer, index, dim= 0):

    index = index.to(layer.weight.device)
    W = layer.weight.index_select(dim, index).clone().detach()
    if layer.bias is not None:
        if dim == 1:
            b = layer.bias.clone().detach()
        else:
            b = layer.bias[index].clone().detach()
    new_size = list(layer.weight.size())
    new_size[dim] = len(index)
    new_layer = nn.Linear(new_size[1], new_size[0], bias=layer.bias is not None).to(layer.weight.device)
    new_layer.weight.requires_grad = False
    new_layer.weight.copy_(W.contiguous())
    new_layer.weight.requires_grad = True
    if layer.bias is not None:
        new_layer.bias.requires_grad = False
        new_layer.bias.copy_(b.contiguous())
        new_layer.bias.requires_grad = True
    return new_layer


class LLMWareInferenceServer:

    """ LLMWare Inference Server class implements the server-side lightweight inference server. """

    def __init__(self, model_name, model_catalog=None, hf_api_key=None, secret_api_key=None, home_path=None,
                 port=8080):

        self.HOME_PATH = home_path
        self.hf_api_key = hf_api_key
        self.current_api_key = secret_api_key
        self.port = port

        if not model_catalog:
            self.model_catalog = ModelCatalog()
        else:
            self.model_catalog = model_catalog

        self.model = self.model_catalog.load_model(model_name, api_key=self.hf_api_key)

    def start(self):

        # if inference server started, then try to get flask dependency
        try:
            global flask
            from flask import Flask, request, jsonify
        except:
            raise DependencyNotInstalledException("flask")

        app = Flask(__name__, template_folder=self.HOME_PATH, static_folder=self.HOME_PATH)
        app.add_url_rule("/", methods=['GET', 'POST'], view_func=self.index_route)
        app.config.update(
            TESTING=True,
            # note: this is not a real secret key - it is just random letters
            SECRET_KEY='asdasdsaddfdsggsdfdsfsdggdsd',
            SEND_FILE_MAX_AGE_DEFAULT=0,
            MAX_CONTENT_LENGTH=1000 * 1024 * 1024
        )

        # launch server
        my_host = '0.0.0.0'
        my_port = self.port
        app.run(host=my_host, port=my_port)

    def llmware_inference(self, prompt, context):

        t1 = time.time()

        output = self.model.inference(prompt, add_context=context, add_prompt_engineering=True)

        print("update: model inference output - ", output["llm_response"], output["usage"])

        t2 = time.time()

        print("update: total processing time: ", t2 - t1)

        return output

    def index_route(self):

        # defaults
        api_key = ""
        question = ""
        context = ""

        # if inference server started, then try to get flask dependency
        try:
            from flask import Flask, request, jsonify
        except:
            raise DependencyNotInstalledException("flask")

        for keys in request.form:

            print("update: keys / values input received: ", keys, request.form.get(keys))

            if keys == "context":
                context = request.form.get(keys)

            if keys == "question":
                question = request.form.get(keys)

            if keys == "max_output_tokens":
                max_output_len = request.form.get(keys)
                try:
                    max_output_len = int(max_output_len)
                except:
                    max_output_len = 200

            if keys == "api_key":
                api_key = request.form.get(keys)

        t1 = time.time()

        if not question and not context:
            output_str = "Got your message - No content found to process"
            return jsonify({"message": output_str})

        if api_key != self.current_api_key:
            output_str = "Got your message - Thanks for testing - API key not confirmed!"
            return jsonify({"message": output_str})

        # start processing here

        output = self.llmware_inference(question, context)

        torch.cuda.empty_cache()

        return jsonify(output)

