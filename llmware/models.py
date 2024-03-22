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

"""The models module implements the model registry, the catalog for models and prompts, and all the currently
supported models, which includes the SLIM model series, the DRAGON model series, the BLING model series,
and the BERT model series.

Besides the logic mentioned above, this module also implements the configuration for BERT and the
inference server of llmware.
"""

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

# new imports
from collections import deque


from llmware.util import Utilities
from llmware.configs import LLMWareConfig
from llmware.resources import CloudBucketManager
from llmware.exceptions import (ModelNotFoundException, DependencyNotInstalledException, ModuleNotFoundException,
                                ModelCardNotRegisteredException, GGUFLibNotLoadedException)

from llmware.model_configs import (global_model_repo_catalog_list, global_model_finetuning_prompt_wrappers_lookup,
                                   global_default_prompt_catalog)

from llmware.gguf_configs import *
from llmware.gguf_configs import _LlamaModel, _LlamaContext, _LlamaBatch, _LlamaTokenDataArray

import transformers
transformers.logging.set_verbosity_error()


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

    #   list of function calling classifier tools

    llm_fx_tools = ["ner", "sentiment", "topics", "ratings", "emotions", "nli",
                    "intent", "sql", "answer", "category", "tags", "summary", "xsum", "extract",
                    "boolean", "sa-ner","tags-3b"]

    llm_fx_tools_map = {"ner": "slim-ner-tool",
                        "sentiment": "slim-sentiment-tool",
                        "topics": "slim-topics-tool",
                        "ratings": "slim-ratings-tool",
                        "emotions": "slim-emotions-tool",
                        "nli": "slim-nli-tool",
                        "sql": "slim-sql-tool",
                        "tags": "slim-tags-tool",
                        "answer": "bling-answer-tool",
                        "category": "slim-category-tool",
                        "intent": "slim-intent-tool",
                        # new tools added
                        "summary": "slim-summary-tool",
                        "xsum": "slim-xsum-tool",
                        "extract": "slim-extract-tool",
                        "boolean": "slim-boolean-tool",
                        "sa-ner": "slim-sa-ner-tool",
                        "tags-3b": "slim-tags-3b-tool"
                        }
    @classmethod
    def get_model_list(cls):
        """ List current view of registered models """
        return cls.registered_models

    @classmethod
    def get_wrapper_list(cls):
        """ List current registered wrapper formats """
        return cls.registered_wrappers

    @classmethod
    def get_llm_fx_tools_list (cls):
        """ List of function calling model tools available """
        return cls.llm_fx_tools

    @classmethod
    def get_llm_fx_mapping (cls):
        """ List of function calling model tools to repo name """
        return cls.llm_fx_tools_map

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
            # added option to match with display name
            if models["model_name"] == model_name_lookup or models["display_name"] == model_name_lookup:
                del cls.registered_models[i]
                cls.registered_models.append(new_model_card_dict)
                updated = True
                break

        return updated

    def delete_model(cls, model_name):

        """ Removes model from Model Registry list """

        model_found=False

        for i, models in enumerate(cls.registered_models):
            # added option to match with display name
            if models["model_name"] == model_name or models["display_name"] == model_name:
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

        # attributes that are used when a model is selected through .load_model method
        self.loaded_model_name = None
        self.loaded_model_class = None
        self.temperature = 0.3
        self.use_gpu = True
        self.sample = True
        self.max_output = 100
        self.get_logits = False
        self.force_reload = False

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
                            context_window=2048, instruction_following=True):

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
            # add option to match with display_name as alternative alias for model
            if models["model_name"] == selected_model_name or models["display_name"] == selected_model_name:
                model_card = models
                model_card.update({"standard":True})
                break

        #   if model not found, then return None, and downstream calling function responsible for handling

        # print("update: lookup_model_card - ", model_card)

        return model_card

    def locate_and_retrieve_model_bits (self, model_card, api_key=None):

        """ For models requiring instantiation locally, this utility method retrieves the model bits using the
        instructions provided in the model card entry. """

        # check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):
            # if not explicitly set up by user, then create folder directory structure
            LLMWareConfig.setup_llmware_workspace()

        model_folder_name = model_card["model_name"]

        # new insert - check if custom_model_repo
        if "custom_model_repo" in model_card:
            if model_card["custom_model_repo"]:
                if os.path.exists(model_card["custom_model_repo"]):
                    if "custom_model_files" in model_card:
                        if model_card["custom_model_files"]:
                            if len(model_card["custom_model_files"]) > 0:
                                if os.path.exists(os.path.join(model_card["custom_model_repo"],
                                                               model_card["custom_model_files"][0])):
                                    # confirmed that custom path and at least model artifact exist
                                    print("update: returning custom model path: ", model_card["custom_model_repo"],
                                          model_card["custom_model_files"])

                                    return model_card["custom_model_repo"]
                else:
                    raise ModelNotFoundException(f"Custom model repo path - {model_card['custom_model_repo']}")

        if model_card["model_family"] == "GGUFGenerativeModel":
            model_folder_name = model_folder_name.split("/")[-1]

        if not os.path.exists(LLMWareConfig.get_model_repo_path()):
            os.mkdir(LLMWareConfig.get_model_repo_path())

        model_location = os.path.join(LLMWareConfig.get_model_repo_path(), model_folder_name)

        if os.path.exists(model_location) and not self.force_reload:
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

            if "snapshot" in model_card:
                # pull snapshot from gguf repo in model card
                model_repo = model_card["gguf_repo"]
                # replacing:  model_repo = model_card["model_name"]
                self.pull_snapshot_from_hf(model_repo, model_location, api_key=api_key)
            else:
                # general case
                self.pull_model_from_hf(model_card, model_location, api_key=api_key)

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
                                                                                      api_key=api_key,
                                                                                      model_card=model_card)

            if model_class == "CohereEmbeddingModel": my_model = CohereEmbeddingModel(model_name=model_name,
                                                                                      embedding_dims=embedding_dims,
                                                                                      api_key=api_key,
                                                                                      model_card=model_card)

            if model_class == "GoogleEmbeddingModel": my_model = GoogleEmbeddingModel(model_name=model_name,
                                                                                      embedding_dims=embedding_dims,
                                                                                      api_key=api_key,
                                                                                      model_card=model_card)

            if model_class == "LLMWareSemanticModel": my_model = LLMWareSemanticModel(model_name=model_name,
                                                                                      embedding_dims=embedding_dims,
                                                                                      api_key=api_key,
                                                                                      model_card=model_card)

            # HF models
            if model_class == "HFGenerativeModel":
                my_model = HFGenerativeModel(model_name=model_name,api_key=api_key, trust_remote_code=True,
                                             model_card=model_card,
                                             # new options added
                                             use_gpu_if_available=self.use_gpu,
                                             get_logits=self.get_logits,
                                             temperature=self.temperature,
                                             max_output=self.max_output,
                                             sample=self.sample)

            if model_class == "GGUFGenerativeModel":

                my_model = GGUFGenerativeModel(model_name=model_name, api_key=api_key, model_card=model_card,
                                               # new configuration options
                                               use_gpu_if_available=True,
                                               get_logits=self.get_logits,
                                               temperature=self.temperature,
                                               max_output=self.max_output,
                                               sample=self.sample
                                                )

            if model_class == "HFEmbeddingModel": my_model = HFEmbeddingModel(model_name=model_name,
                                                                              api_key=api_key,
                                                                              embedding_dims=embedding_dims,
                                                                              model_card=model_card,
                                                                              trust_remote_code=True)

        return my_model

    def load_model (self, selected_model, api_key=None, use_gpu=True, sample=True,get_logits=False,
                    max_output=100, temperature=-99, force_reload=False):

        """ Main method for loading and fully instantiating a model based solely on the model's name """

        # apply optional attributes - will be available to the loaded model
        self.use_gpu=use_gpu
        self.sample=sample
        self.max_output=max_output
        self.get_logits=get_logits
        self.force_reload = force_reload

        # note: temperature set by default at -99, which is a dummy value that is over-ridden by the temperature
        # in the model card.   This temperature will only be used if explicitly set by the user at value != -99

        self.temperature=temperature

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
            loading_directions = self.locate_and_retrieve_model_bits(model_card, api_key=api_key)
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

    def load_hf_embedding_model(self, model, tokenizer,trust_remote_code=False):

        """ Loads and integrates a Huggingface embedding model """

        model = HFEmbeddingModel(model, tokenizer, trust_remote_code=trust_remote_code)
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
                loaded_model = ModelCatalog().load_hf_embedding_model(model,tokenizer, trust_remote_code=True)
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
            # add check for match with display_name as alias
            if models["model_name"] == model_name or models["display_name"] == model_name:
                my_model = models
                break

        return my_model

    def get_model_by_name(self, model_name, api_key=None):

        """ Gets and instantiates model by name. """

        my_model = None

        for models in self.global_model_list:

            #   add check for display name match
            if models["model_name"] == model_name or models["display_name"] == model_name:
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

    def pull_snapshot_from_hf(self, repo_name, local_model_repo_path, api_key=None):

        """ Pulls snapshot of HF model repository and saves into local folder path. """

        from huggingface_hub import snapshot_download

        snapshot = snapshot_download(repo_name, local_dir=local_model_repo_path, token=api_key,
                                     local_dir_use_symlinks=False)

        return local_model_repo_path

    def get_llm_toolkit(self, tool_list=None, api_key=None):

        """ Caches all SLIM tools by default, or if list provided, then selected tools only. """

        model_repo_path = LLMWareConfig.get_model_repo_path()

        if not os.path.exists(model_repo_path):
            os.makedirs(model_repo_path)

        if not tool_list:
            tool_list = _ModelRegistry().get_llm_fx_tools_list()

        logging.info("update: ModelCatalog - get_toolset - %s ", tool_list)

        for tool in tool_list:

            tool_name = _ModelRegistry().get_llm_fx_mapping()[tool]

            logging.info("update: ModelCatalog - get_toolset - %s - %s", tool, tool_name)

            found_model = False
            local_model_repo_path = os.path.join(model_repo_path, tool_name)

            if os.path.exists(local_model_repo_path):
                model_parts_in_folder = os.listdir(local_model_repo_path)
                if len(model_parts_in_folder) > 0:
                    found_model = True

            if not found_model:

                model_card = self.lookup_model_card(tool_name)
                if "gguf_repo" in model_card:
                    repo_name = model_card["gguf_repo"]
                else:
                    repo_name = tool_name

                self.pull_snapshot_from_hf(repo_name, local_model_repo_path, api_key=api_key)

        return 0

    def list_llm_tools(self):
        """Provides a list of the currently available SLIM tools available in the catalog. """
        return _ModelRegistry().get_llm_fx_tools_list()

    def get_llm_fx_mapping(self):
        """Provides a current mapping of Tools to LLM Function Call - this mapping is used by LLMfx class to
        orchestrate among multiple models deployed locally as tools. """
        return _ModelRegistry().get_llm_fx_mapping()

    def get_test_script(self, model_name):

        """ Checks if a test script is available with the model repo - and if so,
        retrieves the test set as a json dictionary """

        test_set = None

        model_repo_path = LLMWareConfig().get_model_repo_path()
        local_model_path = os.path.join(model_repo_path, model_name)
        if os.path.exists(local_model_path):
            model_files = os.listdir(local_model_path)
            if "config.json" in model_files:
                config_json = json.load(open(os.path.join(local_model_path, "config.json"), "r",
                                             encoding="utf-8"))
                if "test_set" in config_json:
                    test_set = config_json["test_set"]

        return test_set

    def tool_test_run(self, model_name, api_key=None, verbose=False,
                      # add more optional configurations to flow thru to the model inference
                      use_gpu=True, sample=True, get_logits=True,
                      max_output=100, temperature=-99):

        """ Loads a tool, if required, and executes a series of test runs.
        Note: only available for 'tool' implementation models. """

        model_card = self.lookup_model_card(model_name)

        if not model_card:
            raise ModelNotFoundException(model_name)

        if "snapshot" in model_card:

            model = self.load_model(model_name, api_key=api_key, use_gpu=use_gpu, sample=sample,
                                    get_logits=get_logits,max_output=max_output, temperature=temperature)

            test_set = self.get_test_script(model_name)

            if test_set:

                if "function_call" not in model_card:

                    # run traditional inference on test set
                    print("\nTest: ", model_name)

                    for i, entries in enumerate(test_set):

                        print("\nupdate: query - ", i, entries["query"])

                        response = model.inference(entries["query"],add_context=entries["context"],
                                                   add_prompt_engineering="default_with_context")
                        print("update: llm_response - ", i, response["llm_response"])
                        if "answer" in entries:
                            print("update: gold answer -  ", i, entries["answer"])

                else:

                    print("\nTest: ", model_name)

                    for i, entries in enumerate(test_set):

                        text = entries["context"]

                        # special case for nli
                        if "conclusion" in entries:
                            text = "Evidence: " + text + "\nConclusion: " + entries["conclusion"]

                        # special case for boolean (question = params)
                        if "question" in entries:
                            params = entries["question"] + " (explain)"
                            response = model.function_call(text, params=[params])
                        else:
                            # general case - use default params and function from model card
                            response = model.function_call(text)

                        # if verbose:
                        print(f"\nupdate: context - test - {i} - {text}")

                        print("update: 'llm_response' - test - ", i, response["llm_response"])

                        # print("update: 'output_tokens' - test - ", i, response["output_tokens"])

                        logit_analysis = self.logit_analysis(response, model_card, model.hf_tokenizer_name,
                                                             api_key=api_key)

                        if "ryg_string" in logit_analysis:
                            print("update: red-yellow-green confidence - ", logit_analysis["ryg_string"])

                        if "confidence_score" in logit_analysis:
                            print("update: confidence score - ", logit_analysis["confidence_score"])

                        if "marker_tokens" in logit_analysis:
                            if logit_analysis["marker_tokens"]:
                                print("update: marker tokens - ", logit_analysis["marker_tokens"])

                        if "choices" in logit_analysis:
                            choices = logit_analysis["choices"]
                            if len(choices) > 0:
                                choices = choices[0]

                            print("update: choices - ", choices)

        return 0

    def list_function_call_models(self):

        """ Returns a list of model card dictionaries for models that implement function_calls."""

        fc_model_list = []
        for models in self.global_model_list:
            if "function_call" in models:
                # confirm that value is positive
                if models["function_call"]:
                    fc_model_list.append(models)

        return fc_model_list

    def logit_analysis(self, response, model_card, hf_tokenizer_name,api_key=None):

        """ Analyzes logits from llm response - currently exposed only as option for function
        call inferences in HFGenerative and GGUFGenerative models. """

        logit_analysis = []
        ryg_string = ""
        vz_choices = []
        marker_token_probs = []
        low_confidence_choices = []
        confidence_score = -1

        # only go ahead if logits found in response
        if "logits" not in response:
            logging.warning("update: logit_analysis requires a response dictionary with 'logits' key- skipping")
            return logit_analysis

        try:
            from colorama import Fore
            red = Fore.RED
            green = Fore.GREEN
            yellow = Fore.YELLOW
            color_reset = Fore.RESET
        except:
            logging.warning("update: logit analysis - could not import colorama - please import to see color coded"
                            "visualization of the output string confidence level.")

            # setting color inserts to empty
            red = ""
            green = ""
            yellow = ""
            color_reset = ""

        try:
            #   tokenizer used as part of building confidence level string
            from transformers import AutoTokenizer
        except:
            raise DependencyNotInstalledException("transformers")

        """ Analyzes logits from llm response """

        # marker tokens for sentiment analysis
        marker_tokens = []
        marker_token_lookup = {}

        if "marker_tokens" in model_card:
            marker_tokens = model_card["marker_tokens"]
        if "marker_token_lookup" in model_card:
            marker_token_lookup = model_card["marker_token_lookup"]

        if "logits" in response:

            logits = response["logits"]

            # hf tokenizer name
            tokenizer = AutoTokenizer.from_pretrained(hf_tokenizer_name, token=api_key)

            try:
                # pull bos attributes from tokenizer
                bos_token_id = tokenizer.bos_token_id
                bos_str = tokenizer.bos_token
            except:
                # unexpected - but if fail, then take llama defaults
                bos_token_id = 1
                bos_str = "<s>"

            ryg_string = ""

            token_probs = []
            marker_token_probs = []
            vz_choices = []
            vz_capture_on = False

            for i, toks in enumerate(response["output_tokens"]):

                # change - look directly for '[' in tokenized output
                if "]" in tokenizer.decode(toks):
                    vz_capture_on = False

                if toks in marker_tokens:

                    for x in range(0, len(logits[i])):
                        if logits[i][x][0] in marker_tokens:
                            new_entry = (marker_token_lookup[logits[i][x][0]],
                                         logits[i][x][0],
                                         logits[i][x][1])
                            marker_token_probs.append(new_entry)

                if vz_capture_on:

                    new_entry = {}
                    for x in range(0,3):
                        key = "choice_" + str(x+1)
                        new_entry.update({key: [tokenizer.decode(logits[i][x][0]),
                                                logits[i][x][1],logits[i][x][0]]})

                        # set confidence score as normalized logit value of first token in value zone
                        #TODO:  need to assess whether averaging across multiple tokens more effective

                        if len(vz_choices) == 0:
                            if logits[i][x][0] == toks:
                                confidence_score = logits[i][x][1]

                    vz_choices.append(new_entry)

                # change - look for "[" directly in token decoded output
                if "[" in tokenizer.decode(toks):
                    vz_capture_on = True

                if toks == 2:
                    break

                for x in range(0, len(logits[i])):

                    if toks == logits[i][x][0]:

                        token_probs.append(logits[i][x][1])

                        if logits[i][x][1] > 0.70:
                            ryg_string += green + tokenizer.decode([bos_token_id, logits[i][x][0]])

                        if 0.3 <= logits[i][x][1] <= 0.70:
                            ryg_string += yellow + tokenizer.decode([bos_token_id, logits[i][x][0]])

                            new_entry = {}
                            for y in range(0, 3):
                                key = "choice_" + str(y + 1)
                                new_entry.update({key: [tokenizer.decode(logits[i][y][0]),
                                                        logits[i][y][1], logits[i][y][0]]})

                            low_confidence_choices.append(new_entry)

                        if logits[i][x][1] < 0.3:
                            ryg_string += red + tokenizer.decode([bos_token_id, logits[i][x][0]])

                            new_entry = {}
                            for y in range(0, 3):
                                key = "choice_" + str(y + 1)
                                new_entry.update({key: [tokenizer.decode(logits[i][y][0]),
                                                        logits[i][y][1], logits[i][y][0]]})

                            low_confidence_choices.append(new_entry)

            # removing hard-coded "<s>"
            ryg_string = ryg_string.replace(bos_str, "")

        logit_analysis = {"ryg_string": ryg_string + color_reset, "choices": vz_choices,
                          "marker_tokens": marker_token_probs,
                          "low_confidence_choices": low_confidence_choices,
                          "confidence_score": confidence_score}

        return logit_analysis

    def fc_output_values(self, model_name):

        """ Takes as input a model_name, and if the model is function-calling, then will output a list
        of the expected function calling output values for the model.  If no value provided, or no specific
        expected 'constraints' on output values, then returns an empty list. """

        output_values = []

        model_card = self.lookup_model_card(model_name)

        if model_card:
            if "fc_output_values" in model_card:
                output_values = model_card["fc_output_values"]

        else:
            logging.error("error: ModelCatalog - could not identify model card for selected model - %s ", model_name)

            raise ModelNotFoundException(model_name)

        return output_values

    def fc_primary_keys(self, model_name):

        """ Takes as input a model_name, and if the model is function-calling, then will output a list of the
        primary keys, if any, to be passed as parameters to the model.  If no primary keys, then returns an
        empty list.  """

        output_keys = []

        model_card = self.lookup_model_card(model_name)

        if model_card:
            if "primary_keys" in model_card:
                output_keys = model_card["primary_keys"]
        else:
            logging.error("error: ModelCatalog - could not identify model card for selected model - %s ", model_name)

            raise ModelNotFoundException(model_name)

        return output_keys

    def remediate_function_call_string(self,input_string, dedupe_values=True):

        """ This method attempts to remediate a function call output string that can not be automatically
        converted into a programmatic object.  The method supports both DICT and LIST outputs.   It is designed
        to address the most common source of automatic failing, which is a premature termination at the end of the
        string, usually due to a max_len cap, e.g., {'key': ['value1', value2', ..., 'val """

        starter = 3
        keys = []
        values = []

        #   if very short output, then can not remediate - assume that a bigger problem happened with the inference
        if len(input_string) < starter:
            # print("update: llm response very short - could not remediate and convert to dict or list")
            return "string", input_string

        start = -1
        list_start = -1

        #   will scan the start of the string for either a dictionary start '{' or list start '['
        #   if neither found, will return the original string

        for x in range(0, starter):

            if input_string[x] == "{":
                # found dict starter
                start = x

            if input_string[x] == "[":
                # found list starter
                list_start = x

        if start < 0 and list_start < 0:
            # print("update: remediation not successful - could not find a start marker for dictionary or list")
            return "string", input_string

        #  based on the start marker, determine the target output type
        if start < 0 and list_start >= 0:
            # try to build the string as a list output
            list_type = True
            key_or_value = "value"
            response_type = "list"
            start = list_start-1
        else:
            # try to build the string as a dictionary output
            list_type = False
            key_or_value = "key"
            response_type = "dict"

        string_on = False
        key_tmp = ""
        counter = 0
        output_dict = {}
        output_list = []
        current_key = ""

        # print("***test*** - remediation - input string - ", input_string)

        for y in range(start + 1, len(input_string)):

            #   note: ASCII ORD conversion - 58 - ':' | 91 - '[' | 93 - ']' | 44 - ','

            if string_on and ord(input_string[counter]) not in [34, 39]:
                if ord(input_string[counter]) not in [91, 93, 58, 44]:
                    if ord(input_string[counter]) == 32 and not key_tmp.strip():
                        pass
                    else:
                        key_tmp += input_string[counter]

                # edge case where there is quote around outer bracket
                if ord(input_string[counter]) == 91 and string_on:
                    string_on = False
                    key_tmp = ""

            # string markers of ' and "
            if ord(input_string[counter]) in [34, 39]:

                # insert new check if ' followed by 's'
                exception_skip = False
                if len(input_string) > counter+1:
                    if ord(input_string[counter+1]) in [115]:
                        exception_skip = True
                        # counter += 1
                # end - new check

                if not exception_skip:

                    if not string_on:
                        string_on = True
                        key_tmp = ""

                    else:
                        # end of string token
                        string_on = False

                        if len(key_tmp) > 0:

                            if not list_type:
                                if key_or_value == "key":
                                    keys.append(key_tmp)
                                    current_key = key_tmp
                                    output_dict.update({current_key: []})

                                else:
                                    values.append(key_tmp)
                                    if current_key in output_dict:
                                        output_dict[current_key].append(key_tmp)
                                    else:
                                        logging.warning("update: remediation - could not find key-value to correct - output "
                                                        "may be missing certain content in structured output.")

                                key_tmp = ""
                            else:
                                output_list.append(key_tmp)
                                values.append(key_tmp)
                                key_tmp = ""

            if ord(input_string[counter]) == 58:

                if len(input_string) > counter + 5:
                    for z in range(1, 5):
                        if ord(input_string[counter + z]) == 91:
                            key_or_value = "value"
                            counter += z - 1
                            break

            if ord(input_string[counter]) == 93:
                key_or_value = "key"

            counter += 1
            if counter >= len(input_string):
                break

        if not list_type:
            # remediation successful in converting to dict output
            if dedupe_values:
                for keys, values in output_dict.items():
                    output_dict[keys] = list(set(values))

            return response_type, output_dict
        else:
            # remediation successful in converting to list output
            if dedupe_values:
                dd_output = []
                for elements in output_list:
                    if elements not in dd_output:
                        dd_output.append(elements)

                # not using set because it can change the order of the list from output
                # output_list = list(set(output_list))

                output_list = dd_output

            return response_type, output_list

    def analyze_sampling(self,response):

        """ Analyzes a llm response output dictionary and produces a 'sampling_stats' dictionary to provide
        details on the effects, if any, of sampling in the output generation. """

        sampling_stats = {}

        if "logits" not in response or "output_tokens" not in response:
            logging.warning("warning: function get_fx_scores requires a response dictionary with 'logits' key - "
                            "not found in the current response provided.  Set the model parameters to 'get_logits=True'"
                            "for function call to provide logits")
            return sampling_stats

        logits = response["logits"]
        output_tokens = response["output_tokens"]

        not_top_selected = 0
        top_token_not_used = []

        if len(output_tokens) == 0:
            return sampling_stats

        for x in range(0, len(output_tokens)):

            top_selected = True

            if output_tokens[x] != logits[x][0][0] and x > 0:
                top_selected = False
                top_token_not_used.append((x, output_tokens[x], logits[x]))

            if not top_selected and x > 0:
                not_top_selected += 1

        tokens_considered = len(output_tokens) - 1
        if tokens_considered > 0:
            percent_top_token = (tokens_considered - not_top_selected) / tokens_considered
        else:
            percent_top_token = 0.0

        # sampling_stats added to the output dictionary
        sampling_stats.update({"total_output_tokens": len(output_tokens),
                               "percent_top_token": round(percent_top_token, 3),
                               "not_top_tokens": top_token_not_used})

        return sampling_stats

    def get_fx_scores(self,response, hf_tokenizer_name, top_choices=3, logit_count=1, api_key=None):

        """ Provides useful metrics and scores derived from analyzing the logits and output tokens from function call
        llm response - currently only supported for HFGenerative and GGUFGenerative models.

        Inputs:
            -- llm response dictionary, including logits and output tokens
            -- hf_tokenizer_name for the model, which will be used to decode output tokens, logits and identify key
                'value zone' markers for the output response, e.g., identify list boundaries '[' and ']'
            -- top_choices - number of candidates to consider in each logit, e.g., top 3 choices considered
            -- logit_count - number of tokens to consider in the value zone, whether the first only, or more
            -- api_key - optional, if tokenizer in private repository requiring an api key

        Output (dictionary):
            -- for each key in the output response, there is a list of the candidate logits in the value zone associated
                with that key - the list will be the length of the logit count requested
            -- a sampling_stats key will also be produced that will provide summary data on the number of 'value zone'
                tokens, the percentage taken from the top output logit candidate and a list of the 'sampled', e.g.,
                'not top' logits taken
        """

        # output is a dict of dict
        output = {}

        if "logits" not in response or "output_tokens" not in response:
            logging.warning("warning: function get_fx_scores requires a response dictionary with 'logits' key - "
                            "not found in the current response provided.  Set the model parameters to 'get_logits=True'"
                            "for function call to provide logits")
            return output

        logits = response["logits"]

        keys_list = []
        llm_response = response["llm_response"]

        if isinstance(llm_response, dict):
            for key, value in llm_response.items():
                keys_list.append(key)
        elif isinstance(llm_response, list):
            keys_list.append("llm_response")
        else:
            keys_list.append("llm_response")

        # hf tokenizer name
        try:
            from transformers import AutoTokenizer
        except ImportError:
            raise DependencyNotInstalledException("transformers")

        tokenizer = AutoTokenizer.from_pretrained(hf_tokenizer_name, token=api_key)

        vz_choices = []
        vz_capture_on = False
        key_counter = 0

        min_threshold = 0.005
        vz_logits = 0
        vz_top_logits = 0
        top_token_not_used = []

        for i, toks in enumerate(response["output_tokens"]):

            decoded = tokenizer.decode(toks)

            if "]" in decoded:
                vz_capture_on = False
                if vz_choices:
                    output.update({keys_list[key_counter]: vz_choices})
                    key_counter += 1
                    vz_choices = []

            if vz_capture_on:

                new_entry = {}
                if toks == logits[i][0][0]:
                    vz_top_logits += 1
                else:
                    # the output token does not correspond to the logit with the highest score, so there was a
                    # 'sampling' effect to this generation - adding this token and corresponding logit to be saved
                    # and provided as output in 'sampling_stats'
                    # print("no match: ", i, tokenizer.decode(toks), tokenizer.decode(logits[i][0][0]),toks, logits[i])
                    top_token_not_used.append((i, toks, logits[i]))

                vz_logits += 1

                for x in range(0, top_choices):

                    if logits[i][x][1] >= min_threshold:
                        new_entry.update({tokenizer.decode(logits[i][x][0]): round(logits[i][x][1], 3)})

                if len(vz_choices) < logit_count:
                    vz_choices.append(new_entry)

            if "[" in decoded:
                vz_capture_on = True
                vz_choices = []

        if vz_top_logits > 0:
            top_token_in_value_zone = round(vz_logits / vz_top_logits, 2)
        else:
            top_token_in_value_zone = 0.0

        # sampling_stats added to the output dictionary
        output.update({"sampling_stats": {"total_vz_tokens": vz_logits,
                                          "percent_top_token": top_token_in_value_zone,
                                          "not_top_tokens": top_token_not_used}
                       })

        return output


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
        #   -- in openai >= 1.0:  .api_base replaced with 'base_url' attribute

        try:
            from openai import OpenAI
        except ImportError:
            raise DependencyNotInstalledException("openai >= 1.0")

        if not self.api_key:
            client = OpenAI(api_key="not-used",base_url=self.api_base)
        else:
            client = OpenAI(api_key=self.api_key,base_url=self.api_base)

        # default case - pass the prompt received without change
        prompt_enriched = prompt

        usage = {}
        time_start = time.time()

        try:

            if self.model_type == "chat":

                messages = self.prompt_engineer_chat(prompt_enriched, self.add_context, inference_dict)

                #   using openai >1.0 api -> create client object, and output is pydantic, not dicts

                response = client.chat.completions.create(model=self.model_name,messages=messages,
                                                          max_tokens=self.target_requested_output_tokens)

                """ assume 'minimal' api output conformance with OpenAI """

                text_out = response.choices[0].message.content

                """ note: some openchat api do not support providing usage output consistent with OpenAI API """

                pt = 0
                ct = 0
                tt = 0

                """ best effort to gather usage data if conforms with OpenAI """

                if hasattr(response, "usage"):

                    if hasattr(response.usage, "prompt_tokens"):
                        pt = response.usage.prompt_tokens

                    if hasattr(response.usage, "completion_tokens"):
                        ct = response.usage.completion_tokens

                    if hasattr(response.usage, "total_tokens"):
                        tt = response.usage.total_tokens

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

                response = client.completions.create(model=self.model_name, prompt=text_prompt,
                                                     temperature=self.temperature,
                                                     max_tokens=self.target_requested_output_tokens)

                """ assume 'minimal' api output conformance with OpenAI """

                text_out = response.choices[0].text

                """ note: some openchat api do not support providing usage output consistent with OpenAI API """

                pt = 0
                ct = 0
                tt = 0

                """ best effort to gather usage data if conforms with OpenAI API """

                if hasattr(response, "usage"):

                    if hasattr(response.usage, "prompt_tokens"):
                        pt = response.usage.prompt_tokens

                    if hasattr(response.usage, "completion_tokens"):
                        ct = response.usage.completion_tokens

                    if hasattr(response.usage, "total_tokens"):
                        tt = response.usage.total_tokens

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

    def __init__(self, model_name=None, api_key=None, context_window=4000, max_output=100,temperature=0.7):

        self.api_key = api_key
        self.model_name = model_name

        self.error_message = "\nUnable to connect to OpenAI. Please try again later."

        self.separator = "\n"

        # assume input (50%) + output (50%)
        self.max_total_len = context_window
        self.max_input_len = int(context_window * 0.5)
        self.llm_max_output_len = int(context_window * 0.5)

        # inference settings
        self.temperature = temperature
        self.target_requested_output_tokens = max_output
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

        # new - change with openai v1 api
        try:
            from openai import OpenAI
        except ImportError:
            raise DependencyNotInstalledException("openai >= 1.0")

        usage = {}
        time_start = time.time()

        try:

            if self.model_name in ["gpt-3.5-turbo","gpt-4","gpt-4-1106-preview","gpt-3.5-turbo-1106", 
                                   "gpt-4-0125-preview", "gpt-3.5-turbo-0125"]:

                messages = self.prompt_engineer_chatgpt3(prompt_enriched, self.add_context, inference_dict)

                # updated OpenAI client to >v1.0 API - create client, and returns pydantic objects

                client = OpenAI(api_key=self.api_key)
                response = client.chat.completions.create(model=self.model_name,messages=messages,
                                                          max_tokens=self.target_requested_output_tokens)

                text_out = response.choices[0].message.content

                usage = {"input": response.usage.prompt_tokens,
                         "output": response.usage.completion_tokens,
                         "total": response.usage.total_tokens,
                         "metric": "tokens",
                         "processing_time": time.time() - time_start}

            else:
                # openai traditional 'instruct gpt' completion models

                prompt_enriched = self.prompt_engineer(prompt_enriched, self.add_context, inference_dict=inference_dict)

                prompt_final = prompt_enriched

                text_prompt = prompt_final + self.separator

                client = OpenAI(api_key=self.api_key)
                response = client.completions.create(model=self.model_name, prompt=text_prompt,
                                                     temperature=self.temperature,
                                                     max_tokens=self.target_requested_output_tokens)

                text_out = response.choices[0].text

                usage = {"input": response.usage.prompt_tokens,
                         "output": response.usage.completion_tokens,
                         "total": response.usage.total_tokens,
                         "metric": "tokens",
                         "processing_time": time.time() - time_start}

        except Exception as e:
            # this is special error code that will be picked and handled in AIModels().inference handler
            text_out = "/***ERROR***/"
            usage = {"input":0, "output":0, "total":0, "metric": "tokens",
                     "processing_time": time.time() - time_start}

            # raise LLMInferenceResponseException(e)
            logging.error("error: OpenAI model inference produced error - %s ", e)

        output_response = {"llm_response": text_out, "usage": usage}

        return output_response


class ClaudeModel:

    """ ClaudeModel class implements the Anthropic Claude API for calling Anthropic models. """

    def __init__(self, model_name=None, api_key=None, context_window=8000, max_output=100, temperature=0.7):

        self.api_key = api_key
        self.model_name = model_name

        self.error_message = "\nUnable to connect to Anthropic/Claude. Please try again later."

        self.separator = "\n"

        #   Claude/Anthropic model - 8000 max token context window
        self.max_total_len = context_window
        self.max_input_len = int(context_window * 0.5)
        self.llm_max_output_len = int(context_window * 0.5)

        # inference settings
        self.temperature = temperature
        self.target_requested_output_tokens = max_output
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

        try:
            import anthropic
        except ImportError:
            raise DependencyNotInstalledException("anthropic")

        client = anthropic.Client(api_key=self.api_key)

        # prototype prompt sample:   prompt_enriched = "\n\nHuman:" + " please read the following- " +
        # self.add_context + " Based on these materials, " + prompt["prompt"] + "\n\nAssistant:"

        prompt_enriched = self.prompt_engineer(prompt,self.add_context, inference_dict=inference_dict)

        # preferred model = "claude-instant-v1"

        time_start = time.time()

        try:

            # new Claude 3 models use the 'messages' API
            # please check that you have pip installed the latest anthropic python sdk

            if self.model_name in ["claude-3-opus-20240229", "claude-3-sonnet-20240229"]:

                # use messages API
                message = client.messages.create(model=self.model_name, max_tokens=self.target_requested_output_tokens,
                                                 messages=[{"role": "user", "content": prompt_enriched}] )

                text_out = message.content[0].text
                input_count = message.usage.input_tokens
                output_count = message.usage.output_tokens

            else:

                # use completion api for 'original' Claude models

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

    def __init__(self, model_name=None, api_key=None, context_window=8192, max_output=100, temperature=0.7):

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
        self.temperature = temperature
        self.target_requested_output_tokens = max_output
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

        try:
            from vertexai.preview.language_models import TextGenerationModel, TextEmbeddingModel
            from vertexai import init
            import google.cloud.aiplatform as aiplatform
        except ImportError:
            raise DependencyNotInstalledException("google-cloud-aiplatform")

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

    def __init__(self, model_name=None, api_key=None, context_window=2048, max_output=100,temperature=0.7):

        self.api_key = api_key
        self.model_name = model_name

        self.error_message = "\nUnable to connect to Jurassic. Please try again later."

        self.separator = " -- "

        #   set max_total_len -> adjust input and output based on use case
        self.max_total_len = context_window
        self.max_input_len = int(context_window * 0.5)

        self.llm_max_output_len = int(context_window * 0.5)

        # inference settings
        self.temperature = temperature
        self.target_requested_output_tokens = max_output
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

        try:
            import ai21
        except ImportError:
            raise DependencyNotInstalledException("ai21")

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

    def __init__(self, model_name=None, api_key=None, context_window=2048, max_output=100,temperature=0.7):

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
        self.temperature = temperature
        self.target_requested_output_tokens = max_output
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

        try:
            import cohere
        except ImportError:
            raise DependencyNotInstalledException("cohere")

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

    """ OpenaIEmbeddingModel class implements the OpenAI API for embedding models. """

    def __init__(self, model_name=None, api_key=None, embedding_dims=None, model_card=None, max_len=None):

        # must have elements for embedding model
        self.model_name = model_name
        self.api_key = api_key
        self.model_card = model_card
        self.tokenizer = None

        if not embedding_dims:
            self.embedding_dims = 1536
        else:
            self.embedding_dims = embedding_dims

        #   openai standard for embeddings is 8191 as of feb 2024
        self.max_total_len = 8191
        self.max_len = self.max_total_len

        if model_card:
            if "embedding_dims" in model_card:
                self.embedding_dims = model_card["embedding_dims"]

            if "context_window" in model_card:
                self.max_total_len = model_card["context_window"]

        self.error_message = "\nUnable to connect to OpenAI. Please try again later."

        if max_len:
            if max_len < self.max_total_len:
                self.max_len = max_len

    def set_api_key(self, api_key,env_var="USER_MANAGED_OPENAI_API_KEY"):

        # set api_key
        os.environ[env_var] = api_key
        logging.info("update: added and stored OpenAI api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_OPENAI_API_KEY"):

        self.api_key = os.environ.get(env_var)
        return self.api_key

    def get_tokenizer(self):
        self.tokenizer = Utilities().get_default_tokenizer()
        return self.tokenizer

    def token_counter(self, text_sample):
        return len(self.tokenizer.encode(text_sample).ids)

    def embedding(self, text_sample, api_key=None):

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

        try:
            from openai import OpenAI
        except ImportError:
            raise DependencyNotInstalledException("openai >= 1.0")

        # insert safety check here
        safe_samples = []
        safety_buffer = 200
        if self.max_total_len < 8191:
            self.max_total_len = 8191

        tokenizer = self.get_tokenizer()

        for sample in text_prompt:

            tok_len = self.token_counter(sample)

            if tok_len < (self.max_total_len - safety_buffer):
                safe_samples.append(sample)

            else:

                if len(sample) > 300:
                    display_sample = sample[0:300] + " ... "
                else:
                    display_sample = sample

                logging.warning(f"warning: OpenAI Embedding - input sample len - {tok_len} > context_window size "
                                f"\ninput_sample - {display_sample} "
                                f"\n\nSample is being truncated.")

                tok = tokenizer.encode(sample).ids
                tok = tok[0:(self.max_total_len - safety_buffer)]
                sample = tokenizer.decode(tok)
                safe_samples.append(sample)

        text_prompt = safe_samples
        # end - safety check

        # update to open >v1.0 api - create client and output is pydantic objects
        client = OpenAI(api_key=self.api_key)
        response = client.embeddings.create(model=self.model_name, input=text_prompt)

        # logging.info("update: response: %s ", response)

        if input_len == 1:
            embedding = response.data[0].embedding
        else:
            embedding = []
            for i, entries in enumerate(response.data):
                embedding.append(response.data[i].embedding)

        return embedding


class CohereEmbeddingModel:

    """ CohereEmbeddingModel implements the Cohere API for embedding models. """

    def __init__(self, model_name = None, api_key=None, embedding_dims=None, model_card=None,max_len=None):

        self.api_key = api_key
        self.model_name = model_name
        self.model_card = model_card

        if not embedding_dims:
            self.embedding_dims = 4096
        else:
            self.embedding_dims = embedding_dims

        self.max_total_len = 2048
        self.error_message = "\nUnable to connect to Cohere. Please try again later."

        self.max_len = self.max_total_len
        if max_len:
            if max_len < self.max_total_len:
                self.max_len = max_len

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

        try:
            import cohere
        except ImportError:
            raise DependencyNotInstalledException("cohere")

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

    def __init__(self, model_name=None, api_key=None, embedding_dims=None, model_card=None, max_len=None):

        self.api_key = api_key
        self.model_name = model_name
        self.model_card = model_card

        self.max_total_len = 3072

        # supports context window up to 3072 tokens for embedding

        if not embedding_dims:
            self.embedding_dims = 768   # Google text-embedding-gecko-001 has 768 dims
        else:
            self.embedding_dims = embedding_dims

        self.error_message = "\nUnable to connect to Google/Text Embedding Model. Please try again later."

        self.max_len = self.max_total_len
        if max_len:
            if max_len < self.max_total_len:
                self.max_len = max_len

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
            from vertexai.preview.language_models import TextGenerationModel, TextEmbeddingModel
            from vertexai import init
            import google.cloud.aiplatform as aiplatform
        except ImportError:
            raise DependencyNotInstalledException("google-cloud-aiplatform")

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
                 embedding_dims=None, trust_remote_code=False, use_gpu_if_available=True, max_len=None):

        # pull in expected hf input
        self.model_name = model_name
        self.model = model
        self.tokenizer= tokenizer
        self.embedding_dims = embedding_dims
        self.model_type = None
        self.max_total_len = 2048
        self.model_architecture = None
        self.model_card = model_card
        self.safe_buffer = 12

        # default for HF embedding model -> will be over-ridden by model card / configs, if available
        self.context_window = 512

        if self.model_card:
            if "embedding_dims" in self.model_card:
                self.embedding_dims = self.model_card["embedding_dims"]

            if "context_window" in self.model_card:
                self.context_window = self.model_card["context_window"]

        if self.model_name and not model:
            # pull from HF
            try:
                # will wrap in Exception if import fails and move to model catalog class
                from transformers import AutoModel, AutoTokenizer
            except ImportError:
                raise DependencyNotInstalledException("transformers")

            hf_repo_name = self.model_name

            if not self.model_card:
                self.model_card = ModelCatalog().lookup_model_card(model_name)

            if self.model_card:
                if "hf_repo" in self.model_card:
                    hf_repo_name = self.model_card["hf_repo"]

            if api_key:
                if torch.cuda.is_available():
                    self.model = AutoModel.from_pretrained(hf_repo_name, token=api_key,
                                                           trust_remote_code=trust_remote_code,
                                                           torch_dtype="auto")
                else:
                    self.model = AutoModel.from_pretrained(hf_repo_name, token=api_key,
                                                           trust_remote_code=trust_remote_code)

                self.tokenizer = AutoTokenizer.from_pretrained(hf_repo_name, token=api_key,
                                                               trust_remote_code=trust_remote_code)
            else:
                if torch.cuda.is_available():
                    self.model = AutoModel.from_pretrained(hf_repo_name, trust_remote_code=trust_remote_code,
                                                           torch_dtype="auto")
                else:
                    self.model = AutoModel.from_pretrained(hf_repo_name, trust_remote_code=trust_remote_code)

                self.tokenizer = AutoTokenizer.from_pretrained(hf_repo_name, trust_remote_code=trust_remote_code)

        self.use_gpu = torch.cuda.is_available() and use_gpu_if_available

        if self.model:

            self.config = self.model.config.to_dict()

            if "hidden_size" in self.config:
                self.embedding_dims = self.config["hidden_size"]

            if "model_type" in self.config:
                self.model_type = self.config["model_type"]

            if "max_position_embeddings" in self.config:

                try:
                    self.context_window = int(self.config["max_position_embeddings"])
                except:
                    pass

            if "_name_or_path" in self.config:
                self.model_name = self.config["_name_or_path"]

            if "architectures" in self.config:
                if isinstance(self.config["architectures"],list):
                    self.model_architectures = self.config["architectures"][0]
                else:
                    self.model_architectures = self.config["architectures"]

            self.model.eval()

            if self.use_gpu:
                self.model.to('cuda')

        else:
            raise ModelNotFoundException(model_name)

        # no api key expected or required
        self.api_key = api_key

        # set max len for tokenizer truncation with 'safe_buffer' below context_window size
        if self.context_window > self.safe_buffer:
            self.max_len = self.context_window - self.safe_buffer
        else:
            self.max_len = self.context_window

        # option to set smaller size than model context window
        if max_len:
            if max_len < self.context_window:
                self.max_len = max_len

    def set_api_key(self, api_key, env_var="USER_MANAGED_HF_API_KEY"):

        """ Sets the API key - generally not needed for public HF repositories. """

        os.environ[env_var] = api_key
        logging.info("update: added and stored HF api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_HF_API_KEY"):

        """ Gets API key from os.environ variable. """

        self.api_key = os.environ.get(env_var)

        if not self.api_key:
            logging.error("error: _get_api_key could not successfully retrieve value from: %s ", env_var)

        return self.api_key

    def token_counter(self, text_sample):
        #   need to support HF tokenizer
        toks = self.tokenizer.encode(text_sample).ids
        return len(toks)

    @torch.no_grad()
    def embedding (self, text_sample, api_key=None):

        # return embeddings only
        if isinstance(text_sample,list):
            sequence = text_sample

        else:
            sequence = [text_sample]

        model_inputs = self.tokenizer(sequence, truncation=True, max_length=self.max_len, return_tensors="pt",padding=True)

        if self.use_gpu:
            input_ids = model_inputs.input_ids.to('cuda')
            attn_mask = model_inputs.attention_mask.to('cuda')
        else:
            input_ids = model_inputs.input_ids.to('cpu')
            attn_mask = model_inputs.attention_mask.to('cpu')

        model_outputs = self.model(input_ids, attention_mask=attn_mask)

        embedding = model_outputs.last_hidden_state[:,0]

        # normalize hf embeddings
        embeddings_normalized = torch.nn.functional.normalize(embedding, p=2, dim=1)

        if self.use_gpu:
            embeddings_normalized = np.array(embeddings_normalized.detach().to('cpu'))
        else:
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
                 use_gpu_if_available=True, trust_remote_code=False, sample=True,max_output=100, temperature=0.3,
                 get_logits=False):

        #   pull in expected hf input
        self.model_name = model_name
        self.hf_tokenizer_name = model_name
        self.model = model
        self.tokenizer = tokenizer

        #   new parameters
        self.sample=sample
        self.get_logits=get_logits
        self.auto_remediate_function_call_output = True

        # Function Call parameters
        self.model_card = model_card
        self.logits_record = []
        self.output_tokens = []
        self.top_logit_count = 10
        self.primary_keys = None
        self.function = None
        self.fc_supported = False

        if model_card:

            if "primary_keys" in model_card:
                self.primary_keys = model_card["primary_keys"]

            if "function" in model_card:
                self.function = model_card["function"]

            if "function_call" in model_card:
                self.fc_supported = model_card["function_call"]

        # instantiate if model_name passed without actual model and tokenizer
        if model_name and not model and not tokenizer:

            try:
                # will wrap in Exception if import fails and move to model catalog class
                from transformers import AutoModelForCausalLM, AutoTokenizer
            except:
                raise DependencyNotInstalledException("transformers")

            hf_repo_name = self.model_name

            if not self.model_card:
                self.model_card = ModelCatalog().lookup_model_card(self.model_name)

            if self.model_card:
                if "hf_repo" in self.model_card:
                    hf_repo_name = self.model_card["hf_repo"]
                    self.hf_tokenizer_name = hf_repo_name

            if api_key:
                if torch.cuda.is_available():
                    self.model = AutoModelForCausalLM.from_pretrained(hf_repo_name, token=api_key,
                                                                      trust_remote_code=trust_remote_code,
                                                                      torch_dtype="auto")
                else:
                    self.model = AutoModelForCausalLM.from_pretrained(hf_repo_name, token=api_key,
                                                                      trust_remote_code=trust_remote_code)

                self.tokenizer = AutoTokenizer.from_pretrained(hf_repo_name, token=api_key,
                                                               trust_remote_code=trust_remote_code)
            else:
                if torch.cuda.is_available():
                    self.model = AutoModelForCausalLM.from_pretrained(hf_repo_name, trust_remote_code=trust_remote_code,
                                                                      torch_dtype="auto")
                else:
                    self.model = AutoModelForCausalLM.from_pretrained(hf_repo_name, trust_remote_code=trust_remote_code)
                self.tokenizer = AutoTokenizer.from_pretrained(hf_repo_name, trust_remote_code=trust_remote_code)

            # set to defaults for HF models in Model Catalog
            # this can be over-ridden post initiation if needed for custom models
            self.prompt_wrapper = "human_bot"
            self.instruction_following = False

        # set specific parameters associated with custom models
        # note - these two parameters will control how prompts are handled - model-specific
        self.prompt_wrapper = prompt_wrapper
        self.instruction_following = instruction_following

        if "instruction_following" in model_card:
            self.instruction_following = model_card["instruction_following"]
        else:
            self.instruction_following = False

        if "prompt_wrapper" in model_card:
            self.prompt_wrapper = model_card["prompt_wrapper"]
        else:
            self.prompt_wrapper = "human_bot"

        #   sets trailing space default when constructing the prompt
        #   in most cases, this is * no trailing space * but for some models, a trailing space or "\n" improves
        #   performance

        self.trailing_space = ""

        if "trailing_space" in model_card:
            self.trailing_space = model_card["trailing_space"]

        self.model_type = None
        self.config = None

        # parameters on context len + output generation
        self.max_total_len = context_window
        self.max_input_len = int(0.5 * context_window)
        self.llm_max_output_len = int(0.5 * context_window)

        # key output parameters
        self.max_output=max_output
        self.target_requested_output_tokens = self.max_output

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
                if isinstance(self.config["architectures"], list):
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

        # temperature settings

        # if temperature set at time of loading the model, then use that setting
        if temperature != -99:
            self.temperature = temperature
        elif "temperature" in model_card:
            # if not set, then pull the default temperature from the model card
            self.temperature = model_card["temperature"]
        else:
            # if no guidance from model loading or model card, then set at default of 0.3
            self.temperature = 0.3

        self.add_prompt_engineering = False
        self.add_context = ""

    def set_api_key(self, api_key, env_var="USER_MANAGED_HF_API_KEY"):

        """ Sets the API key - generally not needed for public HF repositories. """

        os.environ[env_var] = api_key
        logging.info("update: added and stored HF api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_HF_API_KEY"):

        """ Gets API key from os.environ variable. """

        self.api_key = os.environ.get(env_var)

        if not self.api_key:
            logging.error("error: _get_api_key could not successfully retrieve value from: %s ", env_var)

        return self.api_key

    def token_counter(self, text_sample):

        """ Quick approximate token counter - uses default tokenizer so may have minor differences from the
        model's actual tokenization. """

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids

        return len(toks)

    def prompt_engineer(self, query, context, inference_dict):

        """ Applies prompt and templating preparation. """

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

        """ Executes generation inference on model. """

        # first prepare the prompt

        if add_context:
            self.add_context = add_context

        if add_prompt_engineering:
            self.add_prompt_engineering = add_prompt_engineering

        #   add defaults if add_prompt_engineering not set
        if not self.add_prompt_engineering:

            if self.add_context:
                self.add_prompt_engineering = "default_with_context"
            else:
                self.add_prompt_engineering = "default_no_context"

        #   end - defaults update

        #   show warning if function calling model
        if self.fc_supported:
            logging.warning("warning: this is a function calling model - using .inference may lead to unexpected "
                            "results.   Recommended to use the .function_call method to ensure correct prompt "
                            "template packaging.")

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

            outputs = self.model(input_ids=inp0, attention_mask=inp1, past_key_values=pkv,
                                 return_dict=True)

            new_tokens_generated += 1

            next_token_logits = outputs.logits[:, -1, :]

            # capture top logits - not currently activated for inference
            # self.register_top_logits(next_token_logits)
            # shape of next_token_logits = torch.Size([1, 32000])
            # print("next token logits shape - ", next_token_logits.shape)

            if self.temperature and self.sample:
                next_token_scores = next_token_logits / self.temperature
            else:
                next_token_scores = next_token_logits

            # get token from logits
            probs = nn.functional.softmax(next_token_scores, dim=-1)

            if not self.sample:
                # will pull the 'top logit' only
                next_tokens = torch.argmax(probs).unsqueeze(0)
            else:
                # will apply probabilistic sampling
                next_tokens = torch.multinomial(probs, num_samples=1).squeeze(1)

            # new - option to capture logits and output tokens for analysis
            if self.get_logits:
                self.register_top_logits(next_token_logits)

                # capture the output tokens
                if self.use_gpu:
                    next_tokens_np = np.array(next_tokens.to('cpu'))
                else:

                    # print("next tokens: ", next_tokens)

                    next_tokens_np = np.array(next_tokens)

                self.output_tokens.append(next_tokens_np[0])

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
            if new_tokens_generated >= self.target_requested_output_tokens:
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
            output_str = output_str[bot + len("<bot>:"):]

        # new post-processing cleanup - skip repeating starting <s>
        boss = output_str.find("<s>")
        if boss > -1:
            output_str = output_str[boss + len("<s>"):]

        # end - post-processing

        total_len = len(outputs_np)

        usage = {"input": input_token_len,
                 "output": total_len - input_token_len,
                 "total": total_len,
                 "metric": "tokens",
                 "processing_time": time.time() - time_start}

        output_response = {"llm_response": output_str, "usage": usage}

        if self.get_logits:
            output_response.update({"logits": self.logits_record})
            output_response.update({"output_tokens": self.output_tokens})

        return output_response

    def fc_prompt_engineer(self, context, params=None, function=None):

        """ Prompt engineering for Function Call prompts. """

        if not params:
            params = self.primary_keys

        if not function:
            function = self.function[0]

        # prepare SLIM prompt
        class_str = ""
        for key in params:
            class_str += str(key) + ", "
        if class_str.endswith(", "):
            class_str = class_str[:-2]

        f = str(function)

        # key templating format for SLIM function calls
        full_prompt = "<human>: " + context + "\n" + "<{}> {} </{}>".format(f, class_str, f) + "\n<bot>:"

        full_prompt = full_prompt + self.trailing_space

        return full_prompt

    def register_top_logits(self, next_token_logit):

        """ Retrieves the logits for current sample, and packages into indexed top list and
        registers in self.logit_record. """

        #   assumes input of next_token_logit from generation script
        #   will be a tensor of shape [1,vocab_size]

        logit_size = next_token_logit.shape[-1]
        logit = torch.squeeze(next_token_logit)

        if self.use_gpu:
            logit_array = np.array(logit.to('cpu'))
        else:
            logit_array = np.array(logit)

        sm = np.exp(logit_array) / sum(np.exp(logit_array))

        sm_sorted = np.sort(sm)
        sm_args_sorted = np.argsort(sm)

        top_logits = []
        # by default, self.top_logit_count = 10, will get the top 10 highest values in logit output
        for x in range(0, self.top_logit_count):
            # experiment - rounding the long float number
            pair = (sm_args_sorted[logit_size - x - 1], round(sm_sorted[logit_size - x - 1],3))
            top_logits.append(pair)

        self.logits_record.append(top_logits)

        return top_logits

    @torch.no_grad()
    def function_call(self, context, function=None, params=None, get_logits=True,
                      temperature=-99, max_output=None):

        """ This is the key inference method for SLIM models - takes a context passage and a key list
        which is packaged in the prompt as the keys for the dictionary output"""

        if not self.fc_supported:
            logging.warning("warning: HFGenerativeModel - loaded model does not support function calls.  "
                            "Please either use the standard .inference method with this model, or use a  "
                            "model that has 'function_calls' key set to True in its model card.")
            return []

        # reset and start from scratch with new function call
        self.output_tokens = []
        self.logits_record = []

        if temperature != -99:
            self.temperature = temperature

        if max_output:
            self.target_requested_output_tokens = max_output

        if get_logits:
            self.get_logits = get_logits

        if params:
            self.primary_keys = params

        if not self.primary_keys:
            logging.warning("warning: function call - no keys provided - function call may yield unpredictable results")

        prompt = self.fc_prompt_engineer(context, params=self.primary_keys, function=function)

        # second - tokenize to get the input_ids

        tokenizer_output = self.tokenizer.encode(prompt)
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

            outputs = self.model(input_ids=inp0, attention_mask=inp1, past_key_values=pkv,
                                 return_dict=True)

            new_tokens_generated += 1

            next_token_logits = outputs.logits[:, -1, :]

            # option to capture logits for analysis
            # if self.get_logits: self.register_top_logits(next_token_logits)

            if self.temperature and self.sample:
                next_token_scores = next_token_logits / self.temperature
            else:
                next_token_scores = next_token_logits

            # get token from logits
            probs = nn.functional.softmax(next_token_scores, dim=-1)

            if not self.sample:
                # will pull the 'top logit' only
                next_tokens = torch.argmax(probs).unsqueeze(0)
            else:
                # will apply probabilistic sampling
                next_tokens = torch.multinomial(probs, num_samples=1).squeeze(1)

            # option to capture logits and output tokens for analysis
            if self.get_logits:
                self.register_top_logits(next_token_logits)

                # capture the output tokens
                if self.use_gpu:
                    next_tokens_np = np.array(next_tokens.to('cpu'))
                else:
                    next_tokens_np = np.array(next_tokens)

                self.output_tokens.append(next_tokens_np[0])

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
                    next_tokens.tile(eos_token_id_tensor.shape[0], 1).ne(eos_token_id_tensor.unsqueeze(1)).prod(
                        dim=0)
                )

                # stop when each sentence is finished
                if unfinished_sequences.max() == 0:
                    this_peer_finished = True

            # stop if we exceed the maximum length
            if new_tokens_generated >= self.target_requested_output_tokens:
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
            output_str = output_str[bot + len("<bot>:"):]

        # new post-processing cleanup - skip repeating starting <s>
        boss = output_str.find("<s>")
        if boss > -1:
            output_str = output_str[boss + len("<s>"):]

        # end - post-processing

        total_len = len(outputs_np)

        usage = {"input": input_token_len,
                 "output": total_len - input_token_len,
                 "total": total_len,
                 "metric": "tokens",
                 "processing_time": time.time() - time_start}

        try:
            output_value = ast.literal_eval(output_str)

            output_type = "dict"

            # allow for multiple valid object types - will expand over time
            if isinstance(output_value,dict): output_type = "dict"
            if isinstance(output_value,list): output_type = "list"

            usage.update({"type": output_type})

        except:
            # could not convert automatically to python object
            output_type = "string"
            usage.update({"type": output_type})
            output_value = output_str

            # INSERT NEW HERE

            if self.auto_remediate_function_call_output:

                # attempt to remediate
                output_type, output_rem = ModelCatalog().remediate_function_call_string(output_str)

                usage.update({"type": output_type, "remediation": True})
                output_value = output_rem

            if output_type == "string":
                logging.warning("update: automatic conversion of function call output failed, and attempt to "
                                "remediate was not successful - %s ", output_str)
            else:
                logging.info("update: function call output could not be automatically converted, but remediation "
                                "was successful to type - %s ", output_type)

        # INSERT ENDS HERE

        output_response = {"llm_response": output_value, "usage": usage}

        if get_logits:
            output_response.update({"logits": self.logits_record})
            output_response.update({"output_tokens": self.output_tokens})

        return output_response


class GGUFGenerativeModel:

    """ Implementation of GGUF Model class - instantiate and run inferences and function calls using
    GGUF llama.cpp models """

    #   This implementation of GGUFGenerativeModel provides a fairly complete python API interface into
    #   llama.cpp.  llama.cpp is a pure C/C++ implementation of tensor-level model operations, including
    #   quantization and various sampling techniques to enable LLMs to run locally on a CPU (and without Pytorch).
    #   For more information on llama.cpp:  please see https://github.com/ggerganov/llama.cpp

    #   As of llmware 0.2.4 (~end Feb 2024), we have updated the interface to align with
    #   llama_cpp_python (please see https://github.com/abetlen/llama-cpp-python)
    #   to expose more llama.cpp interfaces and to build shared libraries directly
    #   from llama_cpp, using a build script that is intended to be compatible with llama_cpp_python
    #   with the primary objective of aligning to emerging standards and norms, and to enable advanced users
    #   to "bring their own" pre-built llama_cpp libs in conjunction with llmware

    def __init__(self, model_name=None, model_card=None, api_key=None, prompt_wrapper=None, instruction_following=False,
                 context_window=2048, use_gpu_if_available=True, get_logits=False,
                 sample=True,max_output=100, temperature=0.3):

        #   set verbose level in environ level - will be picked up by callback in llama_cpp
        os.environ["llama_cpp_verbose"] = GGUFConfigs().get_config("llama_cpp_verbose")

        #   adding new parameters - use_sampling, temperature, max_output
        self.use_sampling=sample
        self.get_logits=get_logits
        self.logits_record = []
        self.output_tokens = []
        self.top_logit_count = 10
        self.auto_remediate_function_call_output = True

        # TODO:  max_output by GGUFConfigs defaults

        #   default safety check in GGUF Configs that can be adjusted
        gguf_configs_max = GGUFConfigs().get_config("max_output_tokens")

        if max_output > gguf_configs_max:
            # truncate max output to GGUFConfigs max
            logging.warning(f"update: requested output len - {max_output} > {gguf_configs_max}, which is the "
                            f"current GGUF default max.\n--Truncating to {gguf_configs_max} output tokens.\n--Note: "
                            f"to change GGUF default max to new integer amount, say 500:\n "
                            f"  GGUFConfigs().set_config(\"max_output_tokens\", 500)"
                            )

            max_output = gguf_configs_max

        self.max_output=max_output

        #   key configs
        # self.n_seq_max = GGUFConfigs().get_config("max_output_tokens")
        #   *** NEW - KEY CHANGE ***
        self.n_seq_max = max_output
        #   *** end key change ***

        self.target_requested_output_tokens = self.n_seq_max

        # TODO: cleanup repetitive output size attributes
        self.max_total_len = 2048
        self.max_input_len = int(0.5 * context_window)
        self.llm_max_output_len = int(0.5 * context_window)
        self.max_output_len = self.n_seq_max

        self.model_name = model_name
        self.prompt_wrapper = prompt_wrapper
        self.instruction_following = instruction_following
        self.trailing_space = ""
        self.separator = "\n"
        self.eos_token_id = 0

        self.add_prompt_engineering = False
        self.add_context = ""
        self.model_type = "gguf"
        self.model_card = model_card

        self.gguf_file = None
        self.gguf_repo = None
        self.primary_keys = None
        self.function = None
        self.hf_tokenizer_name = None
        self.fc_supported = False

        if model_card:

            if "primary_keys" in model_card:
                self.primary_keys = model_card["primary_keys"]

            if "function" in model_card:
                self.function = model_card["function"]

            if "tokenizer" in model_card:
                self.hf_tokenizer_name = model_card["tokenizer"]

            if "function_call" in model_card:
                self.fc_supported = model_card["function_call"]

            if "trailing_space" in model_card:
                self.trailing_space = model_card["trailing_space"]
            else:
                self.trailing_space = ""

            if "eos_token_id" in model_card:
                self.eos_token_id = model_card["eos_token_id"]

            if "context_window" in model_card:
                self.max_total_len = model_card["context_window"]

            if "prompt_wrapper" in model_card:
                self.prompt_wrapper = model_card["prompt_wrapper"]
            else:
                self.prompt_wrapper = "human_bot"

            if "gguf_file" in model_card:
                self.gguf_file = model_card["gguf_file"]  # e.g., "ggml-model-q4_k_m.gguf"

            if "gguf_repo" in model_card:
                self.gguf_repo = model_card["gguf_repo"]  # e.g., "llmware/dragon-mistral-7b-v0-gguf"

            if "instruction_following" in model_card:
                self.instruction_following = model_card["instruction_following"]

        #   temperature configuration

        # if temperature set at time of loading the model, then use that setting
        if temperature != -99:
            self.temperature = temperature
        elif "temperature" in model_card:
            # if not set, then pull the default temperature from the model card
            self.temperature = model_card["temperature"]
        else:
            # if no guidance from model loading or model card, then set at GGUFConfigs default
            self.temperature = GGUFConfigs().get_config("temperature_default")

        #   gguf specific attributes

        self._lib = None
        self._model = None
        self._ctx = None
        self._batch = None
        self.model_path = None
        self.model_params = None
        self.context_params = None

        #   use_gpu set to TRUE only if:
        #   (1) cuda_platform (e.g., linux or win32), e.g., not set on Mac OS
        #   (2) use_gpu set to True in GGUFConfigs
        #   (3) use_gpu_if_available flag set to True (by default)
        #   (4) cuda found via:  torch.cuda.is_available() -> note: torch not used in GGUF processing, but is used
        #       here as a safety check to confirm that CUDA is found and linked correctly to Python - over time,
        #       we may identify a better way to make this check outside of Torch

        self.use_gpu = (GGUFConfigs().get_config("use_gpu")
                        and sys.platform.lower() in GGUFConfigs().get_config("cuda_platforms")
                        and torch.cuda.is_available()
                        and use_gpu_if_available)

        if self.use_gpu:

            #   need to check that the CUDA driver version is supported

            cuda_version = torch.version.cuda
            if not cuda_version:
                self.use_gpu = False

                logging.warning(f"warning: no CUDA detected - will load model on CPU.\n"
                                f"-- potential causes:  (1) CUDA drivers not correctly installed, (2) CUDA_PATH not set, "
                                f"or (3) Pytorch not compiled with CUDA - other causes possible, but these are the most common."
                                f"-- note:  Pytorch is not used to run the model, but is used as a safety check to test "
                                f"if Python is recognizing the CUDA driver."
                                f"-- checks:  run `nvcc --version` and `nvidia-smi` to get CUDA local information.")

            else:

                # confirm that CUDA driver version is greater than current min (e.g., 12.1)

                try:
                    cuda_version_value = float(cuda_version)
                except:
                    cuda_version_value = 99

                cuda_min_required = GGUFConfigs().get_config("cuda_driver_min_level")
                if cuda_version_value < cuda_min_required:

                    self.use_gpu = False
                    logging.warning(f"warning: CUDA detected, but drivers are at level: {cuda_version} and use of GGUF"
                                    f"model requires at least CUDA drivers at {cuda_min_required}.  Shifting to CPU mode. "
                                    f"To use CUDA, either upgrade NVIDIA CUDA drivers, or use a custom gguf lib built "
                                    f"to earlier driver version.")
                else:
                    # leaving as print for now to maximize clarity, will shift to logging warning/info over time
                    print(f"update: confirmed CUDA drivers recognized- will load model on CUDA - {cuda_version}")

        # set default minimum
        self.n_batch = 2048

        self.last_n_tokens_size = 64

        self._n_vocab = None
        self._n_ctx = None
        self._token_nl = None
        self._token_eos = None
        self._candidates = None
        self.input_ids = None
        self.scores = None
        self.n_tokens = 0
        self.prev = []
        self.grammar = None

        for key, value in GGUFConfigs().get_sampling_params().items():
            setattr(self, key, value)

        # no api key expected or required
        self.api_key = api_key

        self.error_message = "\nUnable to identify and load GGUF Generative model."

    def load_model_for_inference(self, model_repo_path, model_card = None):

        """ Loads and instantiates model along with other required objects. """

        # load shared library
        self._lib = self._load_llama_cpp_shared_library()
        self._lib = add_ctypes_declarations(self._lib)

        if not GGUFConfigs().get_config("backend_initialized"):
            # is this backend init required?
            self._lib.llama_backend_init()
            GGUFConfigs().set_config("backend_initialized", True)

        self._lib.llama_log_set(llama_log_callback, ctypes.c_void_p(0))

        self.model_params = self._lib.llama_model_default_params()

        # update model params parameters
        self.model_params.n_gpu_layers = 0
        self.model_params.split_mode = 1
        self.model_params.main_gpu = 0
        self.model_params.vocab_only = False
        self.model_params.use_mmap = True
        self.model_params.use_mlock = False

        if self.use_gpu:
            # on darwin, keep at 0 - on win32 and linux - set to 50 by default (e.g., shift all model layers to GPU)
            if sys.platform.lower() == "win32" or sys.platform.lower().startswith("linux"):

                self.model_params.n_gpu_layers = GGUFConfigs().get_config("n_gpu_layers")

        # update context parameters
        self.context_params = self._lib.llama_context_default_params()
        self.context_params.n_ctx = 2048
        self.context_params.n_batch = self.n_batch

        if model_card:
            self.model_name = model_card["model_name"].split("/")[-1]
            self.gguf_file = model_card["gguf_file"]  # e.g., "ggml-model-q4_k_m.gguf",
            self.gguf_repo = model_card["gguf_repo"]  # e.g., "llmware/dragon-mistral-7b-v0-gguf"

        self.model_path = os.path.join(model_repo_path, self.gguf_file)

        #   loads and instantiates the key objects
        self._model = _LlamaModel(self._lib, path_model=self.model_path, params=self.model_params)
        self._ctx = _LlamaContext(self._lib,model=self._model, params=self.context_params)
        self._batch = _LlamaBatch(self._lib,n_tokens=self.n_batch, embd=0, n_seq_max=self.context_params.n_ctx)

        self._n_vocab = self.n_vocab()
        self._n_ctx = self.n_ctx()

        self._token_nl = self.token_nl()
        self._token_eos = self.token_eos()

        self._candidates = _LlamaTokenDataArray(n_vocab=self._n_vocab)

        self.input_ids = np.ndarray((self._n_ctx,), dtype=np.intc)
        self.scores = np.ndarray((self._n_ctx, self._n_vocab), dtype=np.single)

        return self

    def _load_llama_cpp_shared_library(self):

        """ Loads llama_cpp shared library - checks if a custom lib path has been configured - otherwise,
        it loads the llmware provided dynamic libraries based on the platform/system. """

        # check first if custom_lib_path - expected to be full path to custom so/dylib file
        custom_path = GGUFConfigs().get_config("custom_lib_path")
        cdll_args = dict()

        # add option to fall_back if CUDA driver can not be loaded correctly to CPU driver for that OS
        fall_back_option = ""

        if custom_path:

            if os.path.exists(custom_path):
                _lib_paths = [custom_path]
            else:
                raise "ModuleNotFound error: could not find location of custom lib"

        else:

            # general case - will look for llama.cpp dynamic library included with llmware

            _base_path = os.path.join(LLMWareConfig.get_config("shared_lib_path"), "gguf")

            _lib_paths = []

            system_platform = sys.platform.lower()

            # Determine the file extension based on the platform
            if system_platform.startswith("linux"):

                if self.use_gpu:
                    _lib_paths.append(os.path.join(_base_path, GGUFConfigs().get_config("linux_cuda")))

                    # new - will try to use x86 as fallback
                    fall_back_option = os.path.join(_base_path, GGUFConfigs().get_config("linux_x86"))

                else:
                    _lib_paths.append(os.path.join(_base_path, GGUFConfigs().get_config("linux_x86")))

            elif system_platform == "darwin":

                machine = os.uname().machine.lower()

                if machine == 'x86_64':
                    _lib_paths.append(os.path.join(_base_path, GGUFConfigs().get_config("mac_x86")))
                else:
                    _lib_paths.append(os.path.join(_base_path, GGUFConfigs().get_config("mac_metal")))

            elif sys.platform == "win32":

                if self.use_gpu:
                    _lib_paths.append(os.path.join(_base_path, GGUFConfigs().get_config("windows_cuda")))

                    # new - will try to use x86 as fallback
                    fall_back_option = os.path.join(_base_path, GGUFConfigs().get_config("windows"))

                else:
                    _lib_paths.append(os.path.join(_base_path, GGUFConfigs().get_config("windows")))

            else:
                raise ModuleNotFoundException(f"No Matching Llama.CPP binary for platform - {system_platform}")

            # Add the library directory to the DLL search path on Windows (if needed)
            if sys.platform == "win32" and sys.version_info >= (3, 8):
                os.add_dll_directory(str(_base_path))

                # need to review
                if "CUDA_PATH" in os.environ:
                    os.add_dll_directory(os.path.join(os.environ["CUDA_PATH"], "bin"))
                    os.add_dll_directory(os.path.join(os.environ["CUDA_PATH"], "lib"))

                # not supported currently
                """
                if "HIP_PATH" in os.environ:
                    os.add_dll_directory(os.path.join(os.environ["HIP_PATH"], "bin"))
                    os.add_dll_directory(os.path.join(os.environ["HIP_PATH"], "lib"))
                """
                # end - review options

                cdll_args["winmode"] = ctypes.RTLD_GLOBAL

        # Try to load the shared library, handling potential errors
        for _lib_path in _lib_paths:

            if not os.path.exists(_lib_path):
                if fall_back_option:
                    _lib_path = fall_back_option

            if os.path.exists(_lib_path):

                try:
                    return ctypes.CDLL(str(_lib_path), **cdll_args)

                except Exception as e:

                    # NEW INSERT - if fail, and CUDA selected, then try to fall back to matching CPU version
                    if fall_back_option:
                        try:

                            logging.warning("update: Not successful loading CUDA lib, so reverting to CPU driver.")

                            return ctypes.CDLL(str(fall_back_option), **cdll_args)
                        except:

                            # if fall-back fails
                            raise GGUFLibNotLoadedException("llama_cpp_backend",
                                                            sys.platform.lower(),
                                                            self.use_gpu,
                                                            _lib_path,
                                                            custom_path)
                    else:
                        raise GGUFLibNotLoadedException("llama_cpp_backend",sys.platform.lower(),
                                                        self.use_gpu, _lib_path, custom_path)

        # if not loaded
        raise ModuleNotFoundException("llama_cpp_backend")

    def _inference (self, prompt):

        """ Tokenizes the prompt and executes generation loop. """

        t0 = time.time()

        completion_tokens = [] if len(prompt) > 0 else [self.token_bos()]

        prompt_tokens = (
            (
                self.tokenize(prompt.encode("utf-8"), special=True)
                if prompt != ""
                else [self.token_bos()]
            )
            if isinstance(prompt, str)
            else prompt
        )

        # confirm that input is smaller than context_window
        input_len = len(prompt_tokens)
        context_window = self.n_ctx()

        if input_len > context_window:
            logging.warning("update: GGUFGenerativeModel - input is too long for model context window - truncating")
            min_output_len = 10
            prompt_tokens = prompt_tokens[0:context_window-min_output_len]
            input_len = len(prompt_tokens)

        text = b""

        for token in self.generate(prompt_tokens):

            if self.get_logits:
                self.register_top_logits()
                self.output_tokens.append(token)

            if token == self._token_eos:
                text = self.detokenize(completion_tokens)
                break

            completion_tokens.append(token)

            #   stop at max output len
            if len(completion_tokens) >= self.max_output_len:
                text = self.detokenize(completion_tokens)
                break

            #   stop if combined input + output at context window size
            if (input_len + len(completion_tokens)) >= context_window:
                text = self.detokenize(completion_tokens)
                break

        text_str = text.decode("utf-8", errors="ignore")

        # post-processing clean-up - stop at endoftext
        eot = text_str.find("<|endoftext|>")
        if eot > -1:
            text_str = text_str[:eot]

        # new post-processing clean-up - stop at </s>
        eots = text_str.find("</s>")
        if eots > -1:
            text_str = text_str[:eots]

        # post-processing clean-up - start after bot wrapper
        bot = text_str.find("<bot>:")
        if bot > -1:
            text_str = text_str[bot + len("<bot>:"):]

        # new post-processing cleanup - skip repeating starting <s>
        boss = text_str.find("<s>")
        if boss > -1:
            text_str = text_str[boss + len("<s>"):]

        # end - post-processing

        output = {"llm_response": text_str,
                  "usage": {"input": len(prompt_tokens),"output": len(completion_tokens),
                            "total": len(prompt_tokens) + len(completion_tokens), "metric": "tokens",
                            "processing_time": time.time() - t0}}

        if self.get_logits:
            output.update({"logits": self.logits_record, "output_tokens": self.output_tokens})

        return output

    def generate(self, tokens, reset=True):

        """ Generator that samples the model and yields tokens until stopped. """

        # Reset the model state
        if reset:
            self.reset()

        sample_idx = self.n_tokens + len(tokens) -1
        tokens = list(tokens)

        tokens_created = 0
        input_start_len = len(tokens)

        # Eval and sample
        while True:

            self._lib.llama_kv_cache_seq_rm(self._ctx.ctx, -1, self.n_tokens, -1)

            for i in range(0, len(tokens), self.n_batch):
                batch = tokens[i: min(len(tokens), i + self.n_batch)]
                n_past = self.n_tokens
                n_tokens = len(batch)

                self._batch.set_batch(batch=batch, n_past=n_past, logits_all=self.context_params.logits_all)

                return_code = self._lib.llama_decode(self._ctx.ctx, self._batch.batch)

                #TODO: add better error handling if return_code 1 - usually overflow of ctx
                if return_code != 0:
                    raise RuntimeError(f"error: llama_decode call returned {return_code} - in most cases, this "
                                       f"is due to exceeding the maximum context window.")

                self.input_ids[n_past: n_past + n_tokens] = batch
                rows = n_tokens
                cols = self._n_vocab
                offset = (0 if self.context_params.logits_all else n_tokens - 1)

                self.scores[n_past + offset: n_past + n_tokens, :].reshape(-1)[:] = self._lib.llama_get_logits(self._ctx.ctx)[
                                                                                    offset * cols: rows * cols]

                self.n_tokens += n_tokens

            while sample_idx < self.n_tokens:

                logits = self._scores[-1, :]

                self.prev = list(self.eval_tokens)
                token = self.sample(logits_array=logits)

                # print("token: ", token)

                self.accept(id=id,apply_grammar=None)

                tokens_created += 1

                sample_idx += 1

                tokens_or_none = yield token
                tokens.clear()
                tokens.append(token)
                if tokens_or_none is not None:
                    tokens.extend(tokens_or_none)

                if sample_idx < self.n_tokens and token != self._input_ids[sample_idx]:
                    self.n_tokens = sample_idx

                    self._lib.llama_kv_cache_seq_rm(self._ctx.ctx, -1, self.n_tokens, -1)

                    break

                if tokens_created > self.max_output_len:
                    logging.info("update: GGUFGenerativeModel - stopping generation loop - reached limit of max output len")
                    break

    def tokenize(self, text, add_bos=True, special=False):

        """ Tokenizes text. """

        n_ctx = self.n_ctx_train()
        tokens = (ctypes.c_int32 * n_ctx)()
        n_tokens = self._lib.llama_tokenize(self._model.model, text, len(text), tokens, n_ctx, add_bos, special)

        if n_tokens < 0:
            n_tokens = abs(n_tokens)
            tokens = (ctypes.c_int32 * n_tokens)()
            n_tokens = self._lib.llama_tokenize(self._model.model, text, len(text), tokens, n_tokens, add_bos, special)

            if n_tokens < 0:
                raise RuntimeError(f'error: GGUFGenerativeModel - tokenization error - "{text}" - n_tokens={n_tokens}')

        return list(tokens[:n_tokens])

    def detokenize(self, tokens, prev_tokens=None):

        """ Detokenizes tokens, e.g., converts tokens back into a text string. """

        output = b""
        size = 32
        buffer = (ctypes.c_char * size)()
        for token in tokens:
            n = self._lib.llama_token_to_piece(self._model.model, llama_token(token), buffer, size)

            assert n <= size
            output += bytes(buffer[:n])

        # removes a leading space if the first token is a beginning of sentence token
        return output[1:] if len(tokens) > 0 and tokens[0] == self.token_bos() else output

    def sample(self, idx=0, logits_array=None):

        """ Sample applies the correct sampling method/strategy to obtain a token id. """

        n_vocab = self.n_vocab()
        id = 0

        if logits_array is None:

            logits = self._lib.llama_get_logits_ith(self._ctx.ctx, idx)

            logits_array = np.array(
                ctypes.cast(logits, ctypes.POINTER(ctypes.c_float * n_vocab)).contents,
                dtype=np.single,
            )

        # apply logit_bias
        for token, logit_bias in self.logit_bias.items():
            logits_array[token] += logit_bias

        token_data_array = _LlamaTokenDataArray(n_vocab=n_vocab)
        token_data_array.copy_logits(logits_array)

        # apply penalties
        if len(self.prev) > 0:

            nl_token = self.token_nl()

            nl_logit = logits_array[nl_token]

            # note: important to skip this if use_sampling is False
            if self.penalty_last_n > 0 and self.use_sampling:

                self._lib.llama_sample_repetition_penalties(self._ctx.ctx,
                                                            ctypes.byref(token_data_array.candidates),
                                                            (llama_token * len(self.prev))(*self.prev),
                                                            self.penalty_last_n,
                                                            self.penalty_repeat,
                                                            self.penalty_freq,
                                                            self.penalty_present,)

            if not self.penalize_nl:
                token_data_array.candidates_data["logit"][nl_token] = nl_logit

        #   note: grammar implementation options  will be expanded over time
        if self.grammar is not None:
            self._lib.llama_sample_grammar(self._ctx.ctx, ctypes.byref(token_data_array.candidates), self.grammar.grammar, )

        if self.temperature < 0:
            assert self._ctx.ctx is not None

            self._lib.llama_sample_softmax(self._ctx.ctx, ctypes.byref(token_data_array.candidates), )

            #TODO - need to check/confirm this
            id = token_data_array.candidates_data["id"][0][0]

        elif self.temperature == 0 or not self.use_sampling:
            assert self._ctx.ctx is not None

            id = self._lib.llama_sample_token_greedy(self._ctx.ctx, ctypes.byref(token_data_array.candidates), )

        else:

            # note: mirostat sampling options are left here for completeness, but not fully exposed or tested
            #   --implementation of mirostat will be expanded over time

            if self.mirostat == 1:
                mirostat_m = 100

                assert self._ctx.ctx is not None

                self._lib.llama_sample_temp(self._ctx.ctx, ctypes.byref(token_data_array.candidates), self.temperature)

                self._lib.llama_sample_token_mirostat(self._ctx.ctx, ctypes.byref(token_data_array.candidates),
                                                      self.mirostat_tau,
                                                      self.mirostat_eta,
                                                      mirostat_m,
                                                      ctypes.pointer(self.mirostat_mu, ))

            elif self.mirostat == 2:

                self._lib.llama_sample_temp(self._ctx.ctx, ctypes.byref(token_data_array.candidates), self.temperature)

                id = self._lib.llama_sample_token_mirostat_v2(self._ctx.ctx, ctypes.byref(token_data_array.candidates),
                                                         self.mirostat_tau,
                                                         self.mirostat_eta,
                                                         ctypes.pointer(self.mirostat_mu), )

            else:
                min_keep = max(1, self.n_probs)

                self._lib.llama_sample_top_k(self._ctx.ctx, ctypes.byref(token_data_array.candidates), self.top_k,
                                        min_keep)

                self._lib.llama_sample_tail_free(self._ctx.ctx, ctypes.byref(token_data_array.candidates), self.tfs_z,
                                            min_keep)

                self._lib.llama_sample_typical(self._ctx.ctx, ctypes.byref(token_data_array.candidates), self.typical_p,
                                          min_keep)

                self._lib.llama_sample_top_p(self._ctx.ctx, ctypes.byref(token_data_array.candidates), self.top_p,
                                        min_keep)

                self._lib.llama_sample_min_p(self._ctx.ctx, ctypes.byref(token_data_array.candidates), self.min_p,
                                        min_keep)

                self._lib.llama_sample_temp(self._ctx.ctx, ctypes.byref(token_data_array.candidates), self.temperature)

                id = self._lib.llama_sample_token(self._ctx.ctx, ctypes.byref(token_data_array.candidates))

        return id

    def accept(self, id, apply_grammar):

        """ Formal step post sampling that 'accepts' and adds the token id to the running generation. """

        if apply_grammar and self.grammar is not None:
            self._lib.llama_grammar_accept_token(self._ctx.ctx, self.grammar.grammar, id)

        self.prev.append(id)

    def register_top_logits(self):

        """ Gets the top logits and keeps a running log for output analysis. """

        #TODO:  there is issue with first logit computation - not corresponding to first token
        logit_pointer = self._lib.llama_get_logits(self._ctx.ctx)

        logit_size = self.n_vocab()
        logit_array = np.zeros(logit_size)
        for x in range(0, logit_size):
            logit_array[x] = logit_pointer[x]

        sm = np.exp(logit_array) / sum(np.exp(logit_array))

        sm_sorted = np.sort(sm)
        sm_args_sorted = np.argsort(sm)

        top_logits = []

        for x in range(0,self.top_logit_count):
            # experiment - try rounding the float number
            pair = (sm_args_sorted[logit_size-x-1],round(sm_sorted[logit_size-x-1],3))
            top_logits.append(pair)

        self.logits_record.append(top_logits)

        return top_logits

    def set_api_key(self, api_key, env_var="USER_MANAGED_GGUF_API_KEY"):

        """ Sets API key - generally not used in GGUF models. """

        # set api_key
        os.environ[env_var] = api_key
        logging.info("update: added and stored GGUF api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_GGUF_API_KEY"):

        """ Gets API key - generally not used in GGUF models. """

        self.api_key = os.environ.get(env_var)

        if not self.api_key:
            logging.error("error: _get_api_key could not successfully retrieve value from: %s ", env_var)

        return self.api_key

    def token_counter(self, text_sample):

        """ Fast approximate token counter. """

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids
        return len(toks)

    @property
    def ctx(self):
        return self._ctx.ctx

    @property
    def model(self):
        return self._model.model

    @property
    def _input_ids(self):
        return self.input_ids[: self.n_tokens]

    @property
    def _scores(self):
        return self.scores[: self.n_tokens, :]

    @property
    def eval_tokens(self):
        return deque(self.input_ids[: self.n_tokens].tolist(), maxlen=self._n_ctx)

    @property
    def eval_logits(self):
        return deque(
            self.scores[: self.n_tokens, :].tolist(),
            maxlen=self._n_ctx if self.context_params.logits_all else 1,
        )

    def reset(self):
        self.n_tokens = 0

    def n_ctx(self):
        return self._lib.llama_n_ctx(self._ctx.ctx)

    def n_ctx_train(self):
        return self._lib.llama_n_ctx_train(self._model.model)

    def n_vocab(self):
        return self._lib.llama_n_vocab(self._model.model)

    def token_eos(self):
        return self._lib.llama_token_eos(self._model.model)

    def token_bos(self):
        return self._lib.llama_token_bos(self._model.model)

    def token_nl(self):
        return self._lib.llama_token_nl(self._model.model)

    def unload_model(self):

        """ Unloads a model to release memory """

        # note: removing pointer seems to safely remove from Python reference tracking
        #   --will evaluate under multiple scenarios if free explicitly needs to be called in llama.cpp engine

        self._batch = None
        self._ctx = None
        self._model = None

        return 0

    def prompt_engineer(self, query, context, inference_dict):

        """ Prompt engineering, packaging and templating. """

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

    def inference(self, prompt, add_context=None, add_prompt_engineering=None, api_key=None, inference_dict=None,
                  get_logits=False):

        """ Main method for inference generation. """

        # first prepare the prompt

        if add_context:
            self.add_context = add_context

        if add_prompt_engineering:
            self.add_prompt_engineering = add_prompt_engineering

        #   update default handling for no add_prompt_engineering

        if not self.add_prompt_engineering:
            if self.add_context:
                self.add_prompt_engineering = "default_with_context"
            else:
                self.add_prompt_engineering = "default_no_context"

        #   end - update

        #   show warning if function calling model
        if self.fc_supported:
            logging.warning("warning: this is a function calling model - using .inference may lead to unexpected "
                            "results.   Recommended to use the .function_call method to ensure correct prompt "
                            "template packaging.")

        # start with clean logits_record and output_tokens for each function call
        self.logits_record = []
        self.output_tokens = []

        if get_logits:
            self.get_logits = get_logits

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

        output_response = self._inference(text_prompt)

        return output_response

    def function_call(self, context, function=None, params=None, get_logits=True,
                      temperature=-99, max_output=None):

        """ This is the key inference method for SLIM models - takes a context passage and a key list
        which is packaged in the prompt as the keys for python dictionary output"""

        if not self.fc_supported:
            logging.warning("warning: GGUFGenerativeModel - loaded model does not support function calls.  "
                            "Please either use the standard .inference method with this model, or use a GGUF "
                            "model that has 'function_calls' key set to True in its model card.")
            return []

        # start with clean logits_record and output_tokens for each function call
        self.logits_record = []
        self.output_tokens = []

        if get_logits:
            self.get_logits = get_logits

        if params:
            self.primary_keys = params

        if not self.primary_keys:
            logging.warning("warning: GGUF - function call - no keys provided - "
                            "function call may yield unpredictable results")

        if not params:
            params = self.primary_keys

        if not function:
            function = self.function[0]

        # prepare SLIM prompt
        class_str = ""
        for key in params:
            class_str += str(key) + ", "
        if class_str.endswith(", "):
            class_str = class_str[:-2]

        f = str(function)

        full_prompt = "<human>: " + context + "\n" + "<{}> {} </{}>".format(f, class_str, f) + "\n<bot>:"
        full_prompt = full_prompt + self.trailing_space

        text_prompt = full_prompt

        if temperature != -99:
            self.temperature = temperature

        if max_output:
            self.max_output_len = max_output

        # call inference here
        output_response = self._inference(text_prompt)

        output_str = output_response["llm_response"]

        try:
            output_dict = ast.literal_eval(output_str)

            output_type = "dict"
            if isinstance(output_dict,dict): output_type = "dict"
            if isinstance(output_dict,list): output_type = "list"

            output_response["usage"].update({"type": output_type})
            output_response.update({"llm_response": output_dict})

        except:

            output_type = "string"
            output_response["usage"].update({"type": output_type})

            if self.auto_remediate_function_call_output:

                # attempt to automatically remediate
                output_type, output_rem = ModelCatalog().remediate_function_call_string(output_str)

                if output_type != "string":
                    output_response["usage"].update({"type": output_type, "remediation":True})
                    output_response.update({"llm_response": output_rem})

            if output_type == "string":
                logging.warning("update: automatic conversion of function call output failed, and attempt to "
                                "remediate was not successful - %s ", output_str)
            else:
                logging.info("update: function call output could not be automatically converted, but remediation "
                                "was successful to type - %s ", output_type)

        return output_response


class LLMWareSemanticModel:

    """ LLMWareSemanticModel class implements the LLMWareSemanticModel API, which is based on the SentenceTransformer
    architecture. """

    def __init__(self, model_name=None, model=None, embedding_dims=None, max_len=150,
                 model_card=None, api_key=None):

        self.model_name = model_name
        self.error_message = "\nUnable to process LLMWare Semantic Model. Please try again later"

        self.max_input_len = 512
        self.max_output_len = 512
        self.max_len = max_len

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
                                  max_seq_length=self.max_len)

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

