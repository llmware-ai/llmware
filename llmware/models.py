# Copyright 2023-2024 llmware

# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.  You
# may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.

"""The models module implements the model registry, the catalog for models and prompts, and classes that
implement the interface for each of the supported models. """

import logging
import json
import requests
import tempfile
import ast
import time
from collections import deque
import shutil
import importlib
from importlib import util

from llmware.util import Utilities, AgentWriter, LocalTokenizer
from llmware.configs import LLMWareConfig
from llmware.exceptions import (DependencyNotInstalledException, ModuleNotFoundException,
                                ModelCardNotRegisteredException, GGUFLibNotLoadedException, LLMWareException)

from llmware.model_configs import (global_model_repo_catalog_list, global_model_finetuning_prompt_wrappers_lookup,
                                   global_default_prompt_catalog, model_benchmark_data)

from llmware.gguf_configs import *
from llmware.gguf_configs import _LlamaModel, _LlamaContext, _LlamaBatch, _LlamaTokenDataArray

#   torch - import only if needed
#   --torch is a required dependency for HFGenerativeModels and HFEmbeddingModels
#   --if either of those classes is called, Torch will be imported at that time
torch = None
GLOBAL_TORCH_IMPORT = False

#   openvino - import only if needed
#   --openvino and openvino_genai are dependencies of OVGenerativeModel
GLOBAL_OVG_IMPORT = False
GLOBAL_OPENVINO_IMPORT = False
ovg = None
openvino = None

#   onnxruntime_genai - import only if needed
#   -- onnxruntime_genai is dependency of ONNXGenerativeModel
GLOBAL_ONNX_GENAI_RUNTIME = False
og = None

logger = logging.getLogger(__name__)
logger.setLevel(level=LLMWareConfig().get_logging_level_by_module(__name__))


class _ModelRegistry:

    """ ModelRegistry class is wrapper class around the global_model_repo_catalog_list for easy dynamic updating,
     and holds most of the key Model, ModelClass and Function/Tool mappings and configurations. """

    #   notes:
    #   --held out as internal global cls to keep options to adapt implementation over time
    #   --generally does not to be directly accessed -> make changes through ModelCatalog

    #   pulls default model list from model_configs.py
    registered_models = global_model_repo_catalog_list

    #   global list of supported model classes with module lookup - and placeholder for other attributes over time
    model_classes = {"ONNXGenerativeModel": {"module": "llmware.models", "open_source": True},
                     "OVGenerativeModel": {"module": "llmware.models", "open_source": True},
                     "GGUFGenerativeModel": {"module": "llmware.models", "open_source":True},
                     "WhisperCPPModel": {"module": "llmware.models", "open_source": True},
                     "HFGenerativeModel": {"module": "llmware.models", "open_source":True},
                     "HFReRankerModel": {"module": "llmware.models", "open_source": True},
                     "LLMWareModel": {"module": "llmware.models", "open_source": True},
                     "LLMWareSemanticModel": {"module": "llmware.models", "open_source": True},
                     "HFEmbeddingModel": {"module": "llmware.models", "open_source": True},
                     "OpenChatModel": {"module": "llmware.models", "open_source": True},
                     "OllamaModel":{"module": "llmware.models", "open_source": True},
                     "OpenAIGenModel":{"module": "llmware.models", "open_source": False},
                     "ClaudeModel":{"module": "llmware.models", "open_source": False},
                     "GoogleGenModel":{"module": "llmware.models", "open_source": False},
                     "CohereGenModel":{"module": "llmware.models", "open_source": False},
                     "JurassicModel":{"module": "llmware.models", "open_source": False},
                     "OpenAIEmbeddingModel":{"module": "llmware.models", "open_source": False},
                     "CohereEmbeddingModel":{"module": "llmware.models", "open_source": False},
                     "GoogleEmbeddingModel":{"module": "llmware.models", "open_source": False}
                     }

    model_catalog_state_attributes = ["selected_model", "loaded_model_name", "loaded_model_class", "temperature",
                                      "api_endpoint", "get_logits", "max_output", "sample",
                                      "force_reload", "account_name", "library_name", "api_key"]

    #   model card validation for registering new model - required attributes
    min_required_fields = ["model_name", "model_family", "model_category"]

    #   most fine-tuned models require a specific prompt wrapping that was used in the fine-tuning process
    #   we are treating these "prompt_wrappers" as core attributes of the model
    prompt_wrappers = ["alpaca", "human_bot", "chatgpt", "<INST>", "open_chat", "hf_chat", "chat_ml", "phi_3",
                       "llama_3_chat","tiny_llama_chat","stablelm_zephyr_chat", "google_gemma_chat",
                       "vicuna_chat"]

    registered_wrappers = global_model_finetuning_prompt_wrappers_lookup

    #   list of specialized function calling tools

    llm_fx_tools = ["ner", "sentiment", "topics", "ratings", "emotions", "nli",
                    "intent", "sql", "answer", "category", "tags", "summary", "xsum", "extract",
                    "boolean", "sa-ner","tags-3b", "q_gen", "qa_gen"]

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
                        "summary": "slim-summary-tool",
                        "xsum": "slim-xsum-tool",
                        "extract": "slim-extract-tool",
                        "boolean": "slim-boolean-tool",
                        "sa-ner": "slim-sa-ner-tool",
                        "tags-3b": "slim-tags-3b-tool",
                        "q_gen": "slim-q-gen-tiny-tool",
                        "qa_gen": "slim-qa-gen-tiny-tool"
                        }

    @classmethod
    def get_model_list(cls):
        """ List current view of registered models """
        return cls.registered_models

    @classmethod
    def get_model_classes(cls):
        """ List of model classes supported in LLMWare. """
        return cls.model_classes

    @classmethod
    def add_model_class(cls, new_class, module="llmware.models", open_source=False,over_write=False):

        """ Adds a new model with flexibility to instantiate in new module. By default, it
        assumes that the module is the current one, e.g., 'llmware.models'. """

        if over_write or new_class not in cls.model_classes:
            cls.model_classes.update({new_class:{"module": module, "open_source": open_source}})
        elif new_class in cls.model_classes:
            logger.warning(f"_ModelRegistry: this model class - {new_class} already exists - to reset the module,"
                           f"then please pass option over_write=True")

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

        #   removing this condition from validation - provides more extensibility in creating new model classes
        """
        if model_card_dict["model_family"] not in cls.model_classes:
            return False
        """

        if "prompt_wrapper" in model_card_dict:

            pwrap = model_card_dict["prompt_wrapper"]

            if pwrap:

                # ok if prompt_wrapper = ""

                if pwrap not in cls.get_wrapper_list():

                    # permits registering of new model card but issues warning

                    logger.warning(f"this prompt wrapper - {pwrap} - is not registered which may lead "
                                   f"to unpredictable results in inference - you should register this prompt "
                                   f"format for better results.")

        return True

    @classmethod
    def add_model(cls, model_card_dict, over_write=True):

        """ Adds a model to the registry """

        if cls.validate(model_card_dict):

            #   confirm that no overlap in names with model already in the catalog

            for i, model in enumerate(cls.registered_models):
                if (model["model_name"] in [model_card_dict["model_name"], model_card_dict["display_name"]] or
                        model["display_name"] in [model_card_dict["model_name"], model_card_dict["display_name"]]):

                    if not over_write:

                        raise LLMWareException(message=f"Exception: model name overlaps with another model already "
                                                       f"in the ModelCatalog - {model}")

                    else:
                        # logger.warning(f"_ModelRegistry - over-write = True - {model['model_name']} - mew model added.")

                        del cls.registered_models[i]

            #   go ahead and add model to the catalog

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

    @classmethod
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

    @classmethod
    def new_model_registry(cls, model_registry):

        #   remove current models
        cls.registered_models = []

        #   add new model registry
        for i, model in enumerate(model_registry):

            if cls.validate(model):
                cls.registered_models.append(model)

        return True

    @classmethod
    def get_model_catalog_vars(cls):
        return cls.model_catalog_state_attributes

    @classmethod
    def add_model_catalog_vars(cls, new_attr):
        cls.model_catalog_state_attributes.append(new_attr)
        return True


def pull_model_from_hf(model_card, local_model_repo_path, api_key=None, **kwargs):

    """ Fetches a specific model file from Huggingface repository into local model repo path, generally used for
    GGUF models in a repository that contains multiple files - and this method will pull a single designated file.

    Inputs: model_card, path to the local model repo, and an api_key (optional). """

    from huggingface_hub import hf_hub_download

    gguf_file = model_card["gguf_file"]     # e.g., "ggml-model-q4_k_m.gguf",
    gguf_repo = model_card["gguf_repo"]     # e.g., "llmware/dragon-mistral-7b-v0-gguf"

    if not os.path.exists(local_model_repo_path):
        os.mkdir(local_model_repo_path)

    logger.warning(f"Models - pulling model from repo - {gguf_repo} - "
                   f"and will cache into local folder - {local_model_repo_path}")

    try:
        downloader = hf_hub_download(gguf_repo, gguf_file, local_dir=local_model_repo_path,
                                     local_dir_use_symlinks=False, token=api_key)
    except:
        raise LLMWareException(message=f"Models - load_model - pull_model_from_hf - Something has "
                                       f"gone wrong in the download process.   Please try again.")

    #   remove ongoing links, if any, created by attributes not in the file repo
    files_created = os.listdir(local_model_repo_path)

    if "validation_files" in model_card:
        validation_files = model_card["validation_files"]
        for files in validation_files:
            if files not in files_created:
                logger.warning(f"Models - load_model - pull_snapshot_from_hf - missing validation file "
                               f"expected to run the model correctly - {files}")

    if ".huggingface" in files_created:
        try:
            shutil.rmtree(os.path.join(local_model_repo_path,".huggingface"))
            logger.debug("Models - load_model - pull_snapshot_from_hf - removed: .huggingface")
        except:
            logger.info(f"Models - load_model - pull_snapshot_from_hf - "
                         f".huggingface folder created in repo and not auto-removed.")
            pass

    if ".cache" in files_created:
        try:
            shutil.rmtree(os.path.join(local_model_repo_path,".cache"))
            logger.debug("Models - load_model - pull_snapshot_from_hf - removed: .cache")
        except:
            logger.info(f"Models - load_model - pull_snapshot_from_hf - "
                         f".cache folder created in repo and not auto-removed.")
            pass

    if ".gitattributes" in files_created:
        try:
            os.remove(os.path.join(local_model_repo_path, ".gitattributes"))
            logger.debug("Models - load_model - pull_snapshot_from_hf - removed: .gitattributes")
        except:
            logger.info(f"Models - load_model - pull_snapshot_from_hf - "
                        f".gitattributes created in repo and not auto-removed.")
            pass

    return local_model_repo_path


def pull_snapshot_from_hf(model_card, local_model_repo_path, api_key=None, **kwargs):

    """ Fetches snapshot of HF model repository and saves into local folder path - two required
    inputs:
        -- repo_name - the full name of the Huggingface repo, e.g., microsoft/phi-2
        -- local_model_repo_path - the local path to save the model files.
    """

    from huggingface_hub import snapshot_download

    if "gguf_repo" in model_card:
        repo_name = model_card["gguf_repo"]
    elif "hf_repo" in model_card:
        repo_name = model_card["hf_repo"]
    elif "ov_repo" in model_card:
        repo_name = model_card["ov_repo"]
    else:
        raise LLMWareException("Model Fetch process error: no repo identified as source to fetch the model.")

    # repo_name = model_card["gguf_repo"]

    try:
        snapshot = snapshot_download(repo_name, local_dir=local_model_repo_path, token=api_key,
                                     local_dir_use_symlinks=False)
    except:
        raise LLMWareException(message=f"Models - load_model - pull_snapshot_from_hf - {repo_name} - Something has "
                                       f"gone wrong in the download process.   Please try again.")

    files_created = os.listdir(local_model_repo_path)

    logger.debug(f"Models - load_model - pull_snapshot_from_hf - downloaded snapshot - "
                 f"files cached locally - {files_created}")

    if "validation_files" in model_card:
        validation_files = model_card["validation_files"]
        for files in validation_files:
            if files not in files_created:
                logger.warning(f"Models - load_model - pull_snapshot_from_hf - missing validation file "
                                f"expected to run the model correctly - {files}")

    #   clean up any residual download artifacts in model folder
    if ".huggingface" in files_created:
        try:
            shutil.rmtree(os.path.join(local_model_repo_path,".huggingface"))
            logger.debug("Models - load_model - pull_snapshot_from_hf - removed: .huggingface")
        except:
            logger.info(f"Models - load_model - pull_snapshot_from_hf - .huggingface folder created in "
                        f"repo and not auto-removed.")
            pass

    if ".cache" in files_created:
        try:
            shutil.rmtree(os.path.join(local_model_repo_path,".cache"))
            logger.debug("Models - load_model - pull_snapshot_from_hf - removed: .cache")
        except:
            logger.info(f"Models - load_model - pull_snapshot_from_hf - "
                         f".cache folder created in repo and not auto-removed.")
            pass

    if ".gitattributes" in files_created:
        try:
            os.remove(os.path.join(local_model_repo_path, ".gitattributes"))
            logger.debug("Models - load_model - pull_snapshot_from_hf - removed: .gitattributes")
        except:
            logger.info(f"Models - load_model - pull_snapshot_from_hf - .gitattributes created "
                         f"in repo and not auto-removed.")
            pass

    return local_model_repo_path


class ModelCatalog:

    """ ModelCatalog is the main class responsible for model lookup of (1) Model Card and (2) Finding Model Class.
    In most cases, ModelCatalog is the interface for all facets of interacting with the model classes.
    """

    def __init__(self):

        #   ModelCatalog is simple, flexible mechanism to track registered models
        #   Easy to create "model repo" with mix of model types and instantiation approaches
        #   Builds on standard model classes with standard inference

        self.model_classes = _ModelRegistry().get_model_classes()
        self.global_model_list = _ModelRegistry().get_model_list()

        self.base_attributes = _ModelRegistry().get_model_catalog_vars()

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
        self.api_endpoint = None

        self.selected_model = None
        self.api_key= None
        self.custom_loader = None

        # new - add - 102024
        self.model_kwargs = {}

    def to_state_dict(self):

        """ Writes selected model state parameters to dictionary. """

        state_dict = {}
        for keys in self.base_attributes:
            if hasattr(self, keys):
                state_dict.update({keys: getattr(self, keys)})

        return state_dict

    def pull_latest_manifest(self):
        """ Not implemented currently """
        # will add to check manifest in global repo and make available for pull down
        return 0

    def save_model_registry(self, fp=None, fn="llmware_model_catalog.json"):

        """ Utility method to export global model list to json file """

        if not fp:
            fp = LLMWareConfig().get_model_repo_path()

        json_dict = json.dumps(self.global_model_list, indent=1)
        with open(os.path.join(fp, fn), "w", encoding='utf-8') as outfile:
            outfile.write(json_dict)

        return 0

    def load_model_registry(self, fp=None, fn="llmware_model_catalog.json"):

        """ Utility method to load global model list from json file.  Will remove the current
        global model list and replace with the model cards from file. """

        if not fp:
            fp = LLMWareConfig().get_model_repo_path()

        model_list = json.load(open(os.path.join(fp,fn), "r"))

        _ModelRegistry().new_model_registry(model_list)

        self.global_model_list = _ModelRegistry().get_model_list()

        return 0

    def add_model_cards_from_file(self, fp=None, fn="custom_models_manifest.json"):

        """ Utility method that loads model cards from a single json file and incrementally adds
        to the model global model list.  """

        if not fp:
            fp = LLMWareConfig().get_model_repo_path()

        model_add_list = json.load(open(os.path.join(fp, fn), "r"))

        for i, model in enumerate(model_add_list):
            _ModelRegistry().add_model(model)

        self.global_model_list = _ModelRegistry().get_model_list()

        return 0

    def register_new_model_card(self, model_card_dict):

        """ Registers a new model card directly in the model catalog """

        _ModelRegistry().add_model(model_card_dict)

        #   update the global list in ModelCatalog instance
        self.global_model_list = _ModelRegistry().get_model_list()

        return 0

    def delete_model_card(self, model_name):

        """ Removes a model card from the registry """

        _ModelRegistry().delete_model(model_name)

        #   update current ModelCatalog instance
        self.global_model_list = _ModelRegistry().get_model_list()

        return 0

    def register_new_finetune_wrapper(self, name, main_start="", main_stop="", llm_start="",
                                      system_start="", system_stop=""):

        """ Registers a new fine-tuning wrapper using a basic template that assembles a prompt and will add
        special tokens as indicated in the wrapper:

            -- main_start - token, if any, to be provided at the start of the prompt template
            -- main_stop  - token, if any, to be provided at the end of the main 'user' input
            -- llm_start  - token, if any, at the end of the prompt that is the signal to start the 'assistant' role
            -- system_start - optional token to start an initial segment indicating a 'system' instruction
            -- system_stop  - optional token to stop an initial segment indicating a 'system' instruction.

            For example, the LLama-2-Chat wrapper is implemented as follows:

                main_start = "<INST>"
                main_stop  = "</INST>
                llm_start  = ""

        """

        new_dict = {"main_start": main_start, "main_stop": main_stop, "start_llm_response": llm_start,
                    "system_start": system_start, "system_stop": system_stop}

        _ModelRegistry().add_wrapper(name, new_dict)

        return 0

    def get_list_registered_finetune_wrappers(self):

        """ Returns an updated list of registered fine-tuning wrappers. """

        return _ModelRegistry().get_wrapper_list()

    def register_new_hf_generative_model(self, hf_model_name, llmware_lookup_name=None, display_name=None,
                                         context_window=2048, prompt_wrapper="<INST>",
                                         temperature=0.3, trailing_space="", link=""):

        """ Registers any Huggingface Generative Model in the ModelCatalog for easy future lookup and
        integration into LLMWare RAG workflows.

        The most important input parameter is hf_model_name, which should correspond to the Huggingface Repo/Model
        format, e.g., microsoft/phi-2

        Any names can be assigned as 'aliases' for the LLMWare Model catalog with both a main lookup name and an
        optional secondary lookup to be used as a short-name for screen display.

        For example, the 'llmware_lookup_name' for 'microsoft/phi-2' could be 'phi-2'
        or 'my-favorite-model-with-2-in-the-name'.

        If no llmware_lookup_name is provided, then it will automatically save as the hf_model_name. """

        if not llmware_lookup_name:
            llmware_lookup_name = hf_model_name

        if not display_name:
            display_name = hf_model_name

        model_card = {"model_name": llmware_lookup_name,
                      "context_window": context_window,
                      "prompt_wrapper": prompt_wrapper,

                      # hf_model_name should correspond to the hf repo/model standard
                      "hf_repo": hf_model_name,
                      "display_name": display_name, "temperature": temperature, "trailing_space": trailing_space,
                      "model_family": "HFGenerativeModel", "model_category": "generative_local",
                      "model_location": "hf_repo", "instruction_following": False,
                      "link": link,
                      "custom_model_files": [], "custom_model_repo": ""}

        _ModelRegistry().add_model(model_card)

        self.global_model_list = _ModelRegistry().get_model_list()

        return model_card

    def register_sentence_transformer_model(self, model_name, embedding_dims, context_window,
                                            display_name=None, link=""):

        """ Registers a model from the SentenceTransformers library into an LLMWare Model Catalog.

        NOTE: for SentenceTransformers, the model_name should match the SentenceTransformer library lookup
        name.  """

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

        self.global_model_list = _ModelRegistry().get_model_list()

        return new_model_card_dict

    def register_gguf_model(self, model_name, gguf_model_repo, gguf_model_file_name, prompt_wrapper=None,
                            eos_token_id=0, display_name=None,trailing_space="", temperature=0.3,
                            context_window=2048, instruction_following=True):

        """ Registers a new GGUF model in model catalog - by default, assumes that the GGUF file is in a Huggingface
        repository, and will be pulled directly from that repository into a local model_repo cache.

        Any arbitrary name can be selected as the model_name and/or display_name for the llmware catalog, as the
        core lookup is in the "gguf_repo" and "gguf_file" parameters.

        If the GGUF file is in another local file path, then you can access it directly by setting:

            "custom_model_repo": "/path/to/local/gguf_model/"
            "custom_model_files": "my_model.gguf"

        """

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
                               "link": "", "custom_model_files": [], "custom_model_repo":"",
                               "fetch": {"module":"llmware.models","method":"pull_model_from_hf"},
                               "validation_files":[gguf_model_file_name]
                               }

        _ModelRegistry().add_model(new_model_card_dict)

        self.global_model_list = _ModelRegistry().get_model_list()

        return new_model_card_dict

    def register_open_chat_model(self, model_name, api_base=None, model_type="chat", display_name=None,
                                 context_window=4096, instruction_following=True, prompt_wrapper="",
                                 temperature=0.5):

        """ Add any open chat model into the LLMWare Model Catalog for easy access, e.g.,

         ModelCatalog().register_open_chat_model("my_open_chat_model1", api_base="http://localhost:1234/v1",
                                                 prompt_wrapper="<INST>", model_type="chat")

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

        self.global_model_list = _ModelRegistry().get_model_list()

        return 0

    def register_ollama_model(self, model_name, host="localhost", port=11434, model_type="chat",
                              raw=False, stream=False, display_name=None, context_window=4096,
                              instruction_following=True, prompt_wrapper="", temperature=0.5):

        """ Add any Ollama model into Model Catalog - key parameters:

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

        self.global_model_list = _ModelRegistry().get_model_list()

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

        return model_card

    def _instantiate_model_class_from_string(self, model_class, model_name, model_card, api_key=None,
                                             api_endpoint=None, **kwargs):

        """ Internal utility method to instantiate model classes from strings. """

        # by default - if model not found - return None
        my_model = None
        context_window= 2048    # used in generative models - use 2048 as default safe backup
        embedding_dims = None   # used in embedding models

        if "context_window" in model_card:
            context_window = model_card["context_window"]

        if "embedding_dims" in model_card:
            embedding_dims = model_card["embedding_dims"]

        if model_class in self.model_classes:

            module = self.model_classes[model_class]["module"]
            model_module = importlib.import_module(module)
            if hasattr(model_module, model_class):
                model_class = getattr(model_module, model_class)

                my_model = model_class(model_name=model_name, context_window=context_window,
                                       api_key=api_key,
                                       trust_remote_code=True,
                                       model_card=model_card,
                                       use_gpu_if_available=self.use_gpu,
                                       get_logits=self.get_logits,
                                       temperature=self.temperature,
                                       max_output=self.max_output,
                                       sample=self.sample,
                                       embedding_dims=embedding_dims,
                                       api_endpoint=api_endpoint,
                                       **kwargs)
        else:
            raise LLMWareException(message=f"Exception: {model_class} not found.")

        return my_model

    def model_load_optimizer(self):

        """ Enables the ability to intercept the standard model loading process for inserting 'auto optimization'
        steps, such as the availability of an API instance of the model or a better performing package, e.g., GGUF
        given the intended deployment environment, or even a preferred implementation/version of the model -
        without having to change any code.

        Currently, not implemented by default, but can be configured to enable custom steps to enable
        advanced model routing optimization. """

        router_method = ""
        router_class = ""
        exec_method = None

        model_router = LLMWareConfig().get_config("model_router")
        router_module = model_router["module"]
        if "class" in model_router:
            router_class = model_router["class"]
        if "method" in model_router:
            router_method = model_router["method"]

        module = importlib.import_module(router_module)

        if router_class:
            if hasattr(module, router_class):
                exec_class = getattr(module, router_class)()
                if hasattr(exec_class, router_method):
                    exec_method = getattr(exec_class, router_method)
        else:
            if hasattr(module, router_method):
                exec_method = getattr(module, router_method)

        if exec_method:
            success_dict = exec_method(self.to_state_dict())
            if success_dict:
                #   write attributes, if any, to the ModelCatalog state, which will be picked up
                #   to "re-direct" the model loading parameters
                if isinstance(success_dict, dict):
                    for k, v in success_dict.items():
                        setattr(self,k,v)

        return True

    def load_model (self, selected_model, api_key=None, use_gpu=True, sample=True,get_logits=False,
                    max_output=100, temperature=-99, force_reload=False, api_endpoint=None,
                    custom_loader=None, **kwargs):

        """ Main method for loading and fully instantiating a model with lookup based on the model_name in
         the ModelCatalog. """

        # apply optional attributes - will be available to the loaded model
        self.use_gpu=use_gpu
        self.sample=sample
        self.max_output=max_output
        self.get_logits=get_logits
        self.force_reload = force_reload
        self.api_endpoint = api_endpoint

        self.selected_model = selected_model
        self.api_key=api_key
        self.use_gpu = use_gpu
        self.custom_loader = custom_loader

        # note: temperature set by default at -99, which is a dummy value that is over-ridden by the temperature
        # in the model card.   This temperature will only be used if explicitly set by the user at value != -99

        self.temperature=temperature

        # assumed to be set to FALSE in default configs - should not be changed until model route optimizer implemented
        if LLMWareConfig().get_config("apply_model_load_router"):
            self.model_load_optimizer()

        # completes all preparatory steps, and returns 'ready-for-inference' model
        selected_model = self.selected_model

        logger.debug(f"ModelCatalog - load_model - loading model - {selected_model}")

        # step 1- lookup model card from the catalog
        model_card = self.lookup_model_card(self.selected_model)
        if not model_card:
            logger.error(f"error: ModelCatalog - unexpected - could not identify model card for "
                         f"selected model - {self.selected_model}")

            raise ModelNotFoundException(self.selected_model)

        # new - 1020 add
        if self.model_kwargs:
            if not kwargs:
                kwargs = {}
            for k,v in self.model_kwargs.items():
                kwargs.update({k:v})
        # end - new add

        # step 2- instantiate the right model class
        my_model = self.get_model_by_name(model_card["model_name"], api_key=self.api_key,
                                          api_endpoint=self.api_endpoint, **kwargs)

        if not my_model:
            logger.error(f"error: ModelCatalog - unexpected - could not identify the model - "
                         f"{self.selected_model}")

            raise ModelNotFoundException(self.selected_model)

        # step 3- if physical model, then need to locate, validate, potentially fetch and then load

        if model_card["model_location"] == "llmware_repo" and not self.api_endpoint:

            loading_directions = self.prepare_local_model(model_card,
                                                          custom_loader=self.custom_loader,
                                                          api_key=self.api_key,
                                                          **kwargs)

            my_model = my_model.load_model_for_inference(loading_directions, model_card=model_card, **kwargs)

        else:
            # if api_key passed, save as environ variable
            # TODO - look at this
            if api_key:
                my_model.set_api_key(api_key)
                os.environ[selected_model] = api_key

            # pass model name to the model directly
            my_model.model_name = selected_model

        return my_model

    def prepare_local_model(self, model_card, custom_loader=None, api_key=None, **kwargs):

        """ Resolves obtaining a valid local path to the required model components.

         1.  Identify if model is available in local path.
            -- if custom path provided, then validate from that path.
            -- if custom loader provided, then use custom loader to complete this step
            -- once local path resolved:
                -- Validate that local path contains the required elements
                -- Return the loading path to load_the_model_for_inference

        2.  If not available locally, then need to fetch.
            --  Use the fetch method provided in the Model Card
            --  if not provided, then use a default for model class
            --  need to provide error-handling if download fails

         """

        #   Step 1 - resolve local path

        if custom_loader:
            return custom_loader(model_card, api_key=api_key)

        if "custom_model_repo" in model_card:
            custom_repo = model_card["custom_model_repo"]
        else:
            custom_repo = None

        if custom_repo and os.path.exists(custom_repo):

            # if path exists ...  (if null result, then will continue down main resolve path)

            custom_local_path = self.check_custom_local_repo(model_card, api_key=api_key)
            if custom_local_path:
                return custom_local_path

        #   Main resolve path

        #   check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):
            # if not explicitly set up by user, then create folder directory structure
            LLMWareConfig.setup_llmware_workspace()

        if not os.path.exists(LLMWareConfig.get_model_repo_path()):
            os.mkdir(LLMWareConfig.get_model_repo_path())

        #   strip '/' from model name
        model_folder_name = model_card["model_name"].split("/")[-1]

        model_location = os.path.join(LLMWareConfig.get_model_repo_path(), model_folder_name)

        go_ahead = False

        if os.path.exists(model_location):

            go_ahead = True

            model_files = os.listdir(model_location)

            if "validation_files" in model_card:
                for file in model_card["validation_files"]:
                    if file not in model_files:
                        go_ahead = False
                        break

            if len(model_files) == 0:
                go_ahead = False

            if go_ahead:
                return model_location

        if not go_ahead:

            #   need to fetch the model files

            fetch, fetch_method_name = self.fetch_resolve(model_card)

            if fetch and fetch_method_name:

                logger.warning(f"ModelCatalog - load_model - fetching model - {model_card['model_name']} - "
                               f"from remote repository using {fetch_method_name} - "
                               f"this may take a couple of minutes the first time.")

                #   fetch method input:  model_card, save_to_path, api_key (optional)
                #   fetch method must be able to resolve the repo using info in the model card
                success = fetch(model_card, model_location, api_key=api_key, **kwargs)

                if isinstance(success, dict):
                    #   write attributes, if any, to the Model instance state
                    for k, v in success.items():
                        setattr(self, k, v)

                return model_location

            else:
                raise(LLMWareException(message=f"Models - load_model - selected model not found in local path - and "
                                               f"could not identify a supporting fetch method to "
                                               f"retrieve selected model from model repository."))

    def fetch_resolve(self, model_card):

        """ Returns the fetch method from model card - if not found, then loads default. """

        #   need to fetch the model -> will use fetch method provided in model card
        fetch_module = None
        fetch_method = None
        fetch_class = None
        fetch_exec = None

        default_fetch = LLMWareConfig().get_config("model_fetch")

        if LLMWareConfig().get_config("apply_default_fetch_override"):

            #   if set to True, will over-ride the model card and use the default fetch mechanism

            fetch_module = default_fetch["module"]
            if "class" in default_fetch:
                fetch_class = default_fetch["class"]
            if "method" in default_fetch:
                fetch_method = default_fetch["method"]

        else:

            #   primary (default) case - each model card provides configs for how to fetch the model

            if "fetch" in model_card:
                if "module" in model_card["fetch"]:
                    fetch_module = model_card["fetch"]["module"]
                if "method" in model_card["fetch"]:
                    fetch_method = model_card["fetch"]["method"]
                if "class" in model_card["fetch"]:
                    fetch_class = model_card["fetch"]["class"]

        if not fetch_module:

            #   fallback case - if not provided in model card, then fallback to the default fetch mechanism

            fetch_module = default_fetch["module"]

            if "class" in default_fetch:
                fetch_class = default_fetch["class"]
            if "method" in default_fetch:
                fetch_method = default_fetch["method"]

        module = importlib.import_module(fetch_module)

        if fetch_class:
            if hasattr(module, fetch_class):
                class_exec = getattr(module, fetch_class)()
                if hasattr(class_exec, fetch_method):
                    fetch_exec = getattr(class_exec,fetch_method)
        else:
            if hasattr(module, fetch_method):
                fetch_exec = getattr(module, fetch_method)

        return fetch_exec, fetch_method

    def check_custom_local_repo(self, model_card, api_key=None):

        """ Model card provides the option for a custom local path as the execution location for the model.
        If 'custom_model_repo' parameter found, then this method will resolve the local path and return
        that local path for loading the model. """

        # if custom model repo path provided in model card, then pull model from this path
        if "custom_model_repo" in model_card:
            if model_card["custom_model_repo"]:
                if os.path.exists(model_card["custom_model_repo"]):
                    if "custom_model_files" in model_card:
                        if model_card["custom_model_files"]:
                            if len(model_card["custom_model_files"]) > 0:
                                if os.path.exists(os.path.join(model_card["custom_model_repo"],
                                                               model_card["custom_model_files"][0])):

                                    # confirmed that custom path and at least model artifact exist
                                    logger.info(f"update: returning custom model path: "
                                                f"{model_card['custom_model_repo']} - "
                                                f"{model_card['custom_model_files']}")

                                    return model_card["custom_model_repo"]
                else:
                    raise ModelNotFoundException(f"Custom model repo path - {model_card['custom_model_repo']}")

        #   fallback - if can not validate the path, then will return None and handle in caller

        return None

    def add_api_key (self, selected_model_name, api_key):

        """ Convenience method to apply an api_key to a pass to a model """

        # step 1- lookup model card from the catalog
        model_card = self.lookup_model_card(selected_model_name)

        if not model_card:

            logger.error(f"error: ModelCatalog - could not identify model card for "
                         f"selected model - {selected_model_name}")

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
                logger.error("ModelCatalog - load_embedding_model - could not identify the "
                             "passed model - if model is from HuggingFace, then mark optional "
                             "'from_hf' flag to True.  If model is from Sentence Transformers, "
                             "then mark optional 'from_sentence_transformers' flag "
                             "to True.  Note: setting search mode to text search, in absence of embedding "
                             "model.")
        else:
            # main case - load embedding model from Catalog
            loaded_model = ModelCatalog().load_model(selected_model=model_name)

        return loaded_model

    def list_open_source_models(self):

        """ Lists the open source models in the ModelCatalog. """

        open_source_models = []

        open_source_class = []
        model_classes = _ModelRegistry().get_model_classes()
        for key, value in model_classes.items():
            if "open_source" in value:
                if value["open_source"]:
                    open_source_class.append(key)

        for x in self.global_model_list:

            if x["model_family"] in open_source_class:
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

        """ Looks up model by model_name. Will check both the primary 'model_name' and the secondary/optional
        display_name to look for a match in the ModelCatalog. """

        my_model = None

        for models in self.global_model_list:
            # add check for match with display_name as alias
            if models["model_name"] == model_name or models["display_name"] == model_name:
                my_model = models
                break

        return my_model

    def get_model_by_name(self, model_name, api_key=None, api_endpoint=None, **kwargs):

        """ Gets and instantiates model by name. """

        my_model = None

        for models in self.global_model_list:

            #   add check for display name match
            if models["model_name"] == model_name or models["display_name"] == model_name:
                selected_model = models
                my_model = self._instantiate_model_class_from_string(selected_model["model_family"],
                                                                     model_name, models,api_key=api_key,
                                                                     api_endpoint=api_endpoint, **kwargs)
                break

        return my_model

    def save_benchmark_report(self, fp=None,fn=None):

        """ Saves model benchmark score data to jsonl file.  Optional inputs to assign folder path (fp) and
        filename (fn).  If not provided, then will be saved in llmware_data path with default name.
        """

        if not fp:
            fp = LLMWareConfig().get_llmware_path()

        if not fn:
            fn = "llmware_model_benchmark_scores"

        test_fn = fn + ".jsonl"

        f_out = open(os.path.join(fp, test_fn), "w")

        for entry in model_benchmark_data:
            jsonl_row = json.dumps(entry)
            f_out.write(jsonl_row)
            f_out.write("\n")

        f_out.close()

        return fp
    def get_benchmark_score(self, model_name):

        """ Looks up benchmark score for a model, if available. Returns None if no benchmark available. """

        for i, entry in enumerate(model_benchmark_data):
            if entry["model_name"] == model_name:
                return entry

        logger.debug(f"ModelCatalog - get_benchmark_score - {model_name} does not have a benchmark available.")

        return None

    def get_benchmark_by_filter (self, conditions=None):

        """ Will apply a list of {key:value} conditions to provide a subset of models that fit the conditions.

        Conditions are a list of dictionaries, with each dictionary entry consisting of the following:
            -- {key, "eval str"},
            -- e.g., {"parameters", "parameters < 3"}

        To create multiple conditions - create a list of several dictionaries:
            -- e.g., [ {"parameters", "parameters < 6"}, {"accuracy_score", "accuracy_score > 95"} ]
        """

        if not conditions:

            logger.debug("ModelCatalog - get_benchmark_by_filter - no conditions provided, so returning all of the "
                         "benchmark data list.")

            return model_benchmark_data

        if isinstance(conditions,dict):
            conditions = [conditions]
        else:
            if not isinstance(conditions,list):
                logger.warning(f"ModelCatalog - conditions should be structured as a list of dictionary entries, "
                               f"with each dictionary entry consisting of a pair of a key:eval_str")
                return model_benchmark_data

        results = []
        for i, entry in enumerate(model_benchmark_data):

            num_conditions = 0
            true_conditions = 0

            for cond in conditions:
                if isinstance(cond, dict):
                    num_conditions += 1
                    for key,value in cond.items():
                        if key in entry:
                            truth_value = eval(value, {key:entry[key]})
                            if truth_value:
                                true_conditions += 1

            if num_conditions > 0 and num_conditions == true_conditions:
                results.append(entry)

        return results

    def get_llm_toolkit(self, tool_list=None, api_key=None):

        """ Caches all SLIM tools by default, or if list provided, then selected tools only. """

        model_repo_path = LLMWareConfig.get_model_repo_path()

        if not os.path.exists(model_repo_path):
            os.makedirs(model_repo_path)

        if not tool_list:
            tool_list = _ModelRegistry().get_llm_fx_tools_list()

        for tool in tool_list:

            tool_name = _ModelRegistry().get_llm_fx_mapping()[tool]

            logger.info(f"ModelCatalog - get_toolset - {tool} - {tool_name}")

            found_model = False
            local_model_repo_path = os.path.join(model_repo_path, tool_name)

            if os.path.exists(local_model_repo_path):
                model_parts_in_folder = os.listdir(local_model_repo_path)
                if len(model_parts_in_folder) > 0:
                    found_model = True

            if not found_model:

                model_card = self.lookup_model_card(tool_name)
                pull_snapshot_from_hf(model_card, local_model_repo_path, api_key=api_key)

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
                      max_output=100, temperature=-99, custom_test_script=None,
                      api_endpoint=None):

        """ Loads a tool, if required, and executes a series of test runs.  Most of the input
        parameters are optional configuration parameters that will be passed when the model is loaded
        and instantiated.

        Note: only available for GGUF quantized 'tool' implementation models. """

        model_card = self.lookup_model_card(model_name)

        agent_writer = AgentWriter()

        if not model_card:
            raise ModelNotFoundException(model_name)

        model = self.load_model(model_name, api_key=api_key, use_gpu=use_gpu, sample=sample,
                                get_logits=get_logits,max_output=max_output, temperature=temperature,
                                api_endpoint=api_endpoint)

        if custom_test_script:
            #   custom_test_script can be any json file with list of json dictionary entries with
            #   keys corresponding to test set, e.g., "context", "query", "answer"
            test_set = custom_test_script
        else:
            test_set = self.get_test_script(model_name)

        if test_set:

            if "function_call" not in model_card:

                # run traditional inference on test set
                agent_writer.write(f"\nTest: {model_name}")

                for i, entries in enumerate(test_set):

                    agent_writer.write(f"\nupdate: query - {i} - {entries['query']}")

                    response = model.inference(entries["query"],add_context=entries["context"],
                                               add_prompt_engineering="default_with_context")

                    agent_writer.write(f"\nupdate: llm_response - {i} - {response['llm_response']}")

                    if "answer" in entries:
                        agent_writer.write(f"update: gold answer - {i} - {entries['answer']}")

            else:

                agent_writer.write(f"\nTest: {model_name}")

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
                    agent_writer.write(f"\nupdate: context - test - {i} - {text}")

                    agent_writer.write(f"update: 'llm_response' - test - {i} - {response['llm_response']}")

                    logit_analysis = self.logit_analysis(response, model_card, model.hf_tokenizer_name,
                                                         api_key=api_key)

                    if "ryg_string" in logit_analysis:
                        agent_writer.write(f"update: red-yellow-green confidence - {logit_analysis['ryg_string']}")

                    if "confidence_score" in logit_analysis:
                        agent_writer.write(f"update: confidence score - {logit_analysis['confidence_score']}")

                    if "marker_tokens" in logit_analysis:
                        if logit_analysis["marker_tokens"]:
                            agent_writer.write(f"update: marker tokens - {logit_analysis['marker_tokens']}")

                    if "choices" in logit_analysis:
                        choices = logit_analysis["choices"]
                        if len(choices) > 0:
                            choices = choices[0]

                        agent_writer.write(f"update: choices - {choices}")

        agent_writer.close()

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
            logger.warning("ModelCatalog - logit_analysis requires a response dictionary with 'logits' key- skipping")
            return logit_analysis

        try:
            from colorama import Fore
            red = Fore.RED
            green = Fore.GREEN
            yellow = Fore.YELLOW
            color_reset = Fore.RESET
        except:
            logger.warning("ModelCatalog - logit analysis - could not import colorama - please import to see color coded"
                            "visualization of the output string confidence level.")

            # setting color inserts to empty
            red = ""
            green = ""
            yellow = ""
            color_reset = ""

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

            # tokenizer load
            if "tokenizer_local" in model_card:
                tokenizer = LocalTokenizer(tokenizer_fn=model_card["tokenizer_local"])
            elif util.find_spec("transformers"):
                # hf tokenizer name
                pt_loader = PyTorchLoader(api_key=api_key, trust_remote_code=True, custom_loader=None)
                tokenizer = pt_loader.get_tokenizer(hf_tokenizer_name)
            else:
                raise LLMWareException(message="Exception: could not identify tokenizer to use")

            try:
                # pull bos attributes from tokenizer
                # -- note: will be a list of .bos_id and .eos_id, e.g., [2], not 2
                bos_token_id = tokenizer.bos_id
                bos_str = tokenizer.bos_token

                eos_token_id = tokenizer.eos_id
                eos_str = tokenizer.eos_token

                if not isinstance(eos_token_id, list):
                    eos_token_id = [eos_token_id]

                if isinstance(bos_token_id, list):
                    if len(bos_token_id) > 0:
                        bos_token_id = bos_token_id[0]
                    else:
                        #   set to llama as fallback
                        bos_token_id = 1
            except:
                # unexpected - but if fail, then take llama defaults
                bos_token_id = 1
                bos_str = "<s>"

                eos_token_id = [2]
                eos_str = "</s>"

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

                            # new add 1020 - if from file, then dict number converted to str
                            if logits[i][x][0] in marker_token_lookup:
                                entry0 = marker_token_lookup[logits[i][x][0]]

                            elif str(logits[i][x][0]) in marker_token_lookup:
                                entry0 = marker_token_lookup[str(logits[i][x][0])]

                            else:
                                entry0 = "NA"
                            # end here

                            new_entry = (entry0,
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

                # e.g., if toks in [2]:
                if toks in eos_token_id:
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
            logger.error(f"ModelCatalog - could not identify model card "
                         f"for selected model - {model_name} ")

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
            logger.error(f"ModelCatalog - could not identify model card for "
                         f"selected model - {model_name}")

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
            #   llm response very short - could not remediate and convert to dict or list
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
            # remediation not successful - could not find a start marker for dictionary or list
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

        logger.debug(f"***test*** - remediation - input string - {input_string}")

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
                                        logger.warning("remediation - could not find key-value to correct - output "
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
            logger.warning("ModelCatalog - function get_fx_scores requires a response dictionary with 'logits' key - "
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

    def get_fx_scores(self,response, model_name, top_choices=3, logit_count=1, api_key=None):

        """ Provides useful metrics and scores derived from analyzing the logits and output tokens from function call
        llm response - currently only supported for HFGenerative and GGUFGenerative models.

        Inputs:
            -- llm response dictionary, including logits and output token
            -- model_name which will be used to lookup the model card and get applicable tokenizer(s)
            -- tokenizer will be used to decode output tokens, logits and identify key
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

        # model name - look up model card
        model_card = self.lookup_model_card(model_name)

        hf_tokenizer_name = None
        tokenizer_local = None

        if "tokenizer" in model_card:
            hf_tokenizer_name = model_card["tokenizer"]

        if "tokenizer_local" in model_card:
            tokenizer_local = model_card["tokenizer_local"]

        # output is a dict of dict
        output = {}

        if "logits" not in response or "output_tokens" not in response:
            logger.warning("ModelCatalog - function get_fx_scores requires a response dictionary with 'logits' key - "
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

        # tokenizer load
        if tokenizer_local:
            tokenizer = LocalTokenizer(tokenizer_fn=model_card["tokenizer_local"])
        elif hf_tokenizer_name and util.find_spec("transformers"):
            # hf tokenizer name
            pt_loader = PyTorchLoader(api_key=api_key, trust_remote_code=True, custom_loader=None)
            tokenizer = pt_loader.get_tokenizer(hf_tokenizer_name)
        else:
            raise LLMWareException(message="Exception: could not identify tokenizer to use")

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

    def gpu_available(self, suppress_warnings=True, driver_min_levels=None):

        """ Checks if CUDA GPU drivers found on machine, and whether the drivers are at
        the required minimum level.

        -- driver_min_level is a tuple of integers consisting of the major/minor driver level, e.g., (525, 15)
        -- if no driver_min_level is passed, then the test will be skipped and come back False by default.
        """

        major_driver = 0
        minor_driver = 0

        result = {"gpu_found": False, "drivers_current": False,
                  "gpu_name": "", "driver": "", "multiple_gpu": False}


        try:
            from subprocess import Popen, PIPE
        except:
            if not suppress_warnings:
                logger.warning("ModelCatalog - check gpu availability - unable to check if gpu available")
            return result

        if sys.platform.lower() == "win32":
            nvidia_smi = shutil.which('nvidia-smi')
        elif sys.platform.lower().startswith("linux"):
            nvidia_smi = "nvidia-smi"
        else:
            if not suppress_warnings:
                logger.warning("ModelCatalog - check gpu availability - only check for CUDA drivers on Windows or Linux")
            return result

        try:
            gpu_pipe = Popen([nvidia_smi, "--query-gpu=index,driver_version,name","--format=csv,noheader,nounits"],
                             stdout=PIPE)
            gpu, errors = gpu_pipe.communicate()
        except Exception as e:
            gpu = []
            errors = e

        if gpu:

            result["gpu_found"] = True

            # only looking at 'first' gpu
            results = str(gpu).split(",")
            if len(results) > 1:

                #TODO: handle multiple GPUs on device!
                driver_index = results[0].strip().encode('utf')

                driver_level = results[1].strip()
                result["driver"] = driver_level

                if len(results) > 2:
                    result["gpu_name"] = results[2].strip()

                if driver_min_levels:

                    driver_split = driver_level.split(".")

                    if len(driver_split) > 0:
                        try:
                            major_driver = int(driver_split[0].strip())
                            if len(driver_split) > 1:
                                minor_driver = int(driver_split[1].strip())
                        except:
                            pass

                    if major_driver > driver_min_levels[0] or (major_driver == driver_min_levels[0]
                                                           and minor_driver >= driver_min_levels[1]):
                        result["drivers_current"] = True

                    else:
                        result["drivers_current"] = False
                        logger.warning(f"ModelCatalog - check gpu availability - CUDA device found - but drivers "
                                       f"look out of date, relative to required min levels: \n"
                                       f"--drivers found: {driver_level}\n"
                                       f"--min required:  {driver_min_levels}\n")

        return result


class PromptCatalog:

    """ PromptCatalog manages prompt styles and prompt wrappers and builds prompt templates for inference
    generation. """

    def __init__(self):

        self.prompt_catalog = global_default_prompt_catalog
        self.prompt_wrappers = _ModelRegistry().prompt_wrappers
        self.prompt_wrapper_lookup = _ModelRegistry().get_wrapper_list()

        self.prompt_list = self.list_all_prompts()

    def lookup_prompt(self, prompt_name):

        """ Looks up a predefined prompt template by prompt_name. """

        for prompts in self.prompt_catalog:
            if prompts["prompt_name"] == prompt_name:
                return prompts

        return None

    def get_all_prompts(self):

        """ Returns all predefined prompts. """

        return self.prompt_catalog

    def list_all_prompts(self):

        """ Returns a list of all predefined prompts. """

        prompt_list = []
        for prompt in self.prompt_catalog:
            if "prompt_name" in prompt:
                prompt_list.append(prompt["prompt_name"])
        return prompt_list

    def parse_instruction_for_user_vars(self, prompt_card, inference_dict=None):

        """ Utility method that looks for user_vars in prompt card to dynamically insert into Prompt. """

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

        logger.debug(f"prompt catalog - constructed dynamic instruction - {updated_instruction}")

        return updated_instruction.strip()

    def build_core_prompt(self, prompt_card=None, prompt_name=None, separator="\n", query=None, context=None,
                          inference_dict=None):

        """ Builds the core prompt from the prompt_card template. """

        if not context:  context = ""
        if not query: query = ""

        if not prompt_card and not prompt_name:
            # error - returning query
            logger.warning("prompt catalog - no prompt selected in PromptCatalog().build_core_prompt")
            prompt_dict = {"core_prompt": context + "\n" + query, "prompt_card": {}}
            return prompt_dict

        if not prompt_card:
            prompt_card = PromptCatalog().lookup_prompt(prompt_name)

        logger.debug(f"prompt catalog - prompt_card - {prompt_card}")

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
            core_prompt += prompt_card["instruction"]
        """

        prompt_dict = {"core_prompt": core_prompt, "prompt_card": prompt_card}

        logger.debug(f"prompt catalog - prompt created - {prompt_dict}")

        return prompt_dict

    def add_custom_prompt_card(self, prompt_name, run_order_list, prompt_dict, prompt_description=None):

        """ Registers a new custom prompt_card with 'run_order_list' that shows how to assemble the components
        of a Prompt.  """

        new_prompt_card = {"prompt_name": prompt_name,
                           "prompt_description": prompt_description,
                           "run_order": run_order_list}

        for keys, values in prompt_dict.items():
            new_prompt_card.update({keys: values})

        self.prompt_catalog.append(new_prompt_card)

        return new_prompt_card

    def apply_prompt_wrapper(self, text, prompt_wrapper, separator="\n", instruction=None):

        """ Applies the selected prompt_wrapper to the prompt. """

        output_text = text

        if prompt_wrapper not in self.prompt_wrappers:
            logger.info(f"apply_prompt_wrapper - selected wrapper - {prompt_wrapper} - could not be identified - "
                        f"returning text prompt without any special format wrapping")

            return output_text

        if prompt_wrapper == "chatgpt":
            return self.wrap_chatgpt_sample(text, instruction)

        else:
            wrapped_prompt = self.wrap_custom(text, prompt_wrapper, instruction=instruction)
            return wrapped_prompt

    def wrap_chat_ml_sample(self, text, separator, instruction):

        """ Deprecated - custom handler for wrap_chat_ml_sample. Replaced by general method. """

        if not instruction:
            instruction = "You are a helpful assistant."

        output_text = "<|im_start|>system\n" + instruction + "<|im_end|>\n" + \
                      "<|im_start|>user" + text + "<|im_end|>\n" + \
                      "<|im_start|>assistant"

        return output_text

    def wrap_custom(self, text, wrapper_type, instruction=None):

        """ Builds wrapper on Prompt based on the selected wrapper_type. """

        prompt_out = ""

        if wrapper_type in self.prompt_wrapper_lookup:

            prompt_template = self.prompt_wrapper_lookup[wrapper_type]

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

        """ Applies chatgpt format wrapper to a prompt. """

        if not instruction:
            instruction = "You are a helpful assistant."

        new_sample = [{"role": "system", "content": instruction},
                      {"role": "user", "content": text}]

        return new_sample

    def wrap_human_bot_sample(self, text, user_separator="<human>: ", response_separator="<bot>:"):

        """ Applies 'human-bot' wrapper to a prompt.  Deprecated and replaced by general method.  """

        content = user_separator + text + "\n" + response_separator

        return content

    def wrap_llama2_chat_sample(self, text, separator):

        """ Applies 'llama2 - INST' wrapper to a prompt.  Deprecated and replaced by general method.  """

        content = "<INST> " + text + "</INST>"

        return content

    def wrap_alpaca_sample(self, text, separator="\n"):

        """ Applies 'Alpaca style' wrapper to a prompt.  Deprecated and replaced by general method.  """

        content = "### Instruction: " + text + separator + "### Response: "

        return content

    def wrap_openchat_sample(self, text, separator="\n"):

        """ Applies 'openchat style' wrapper to a prompt.  Deprecated and replaced by general method.  """

        content = "GPT4 User: " + text + "<|endofturn|>" + "GPT4 Assistant:"

        return content

    def wrap_hf_chat_zephyr_sample(self, text, separator="\n"):

        """ Applies 'HF Chat - Zephyr style' wrapper to a prompt.  Deprecated and replaced by general method.  """

        content = "<|system|>You are a helpful assistant.\n</s>" + \
                  "<|user|>" + text + "\n</s>" + \
                  "<|assistant|>"

        return content


class InferenceHistory:

    """ Global State History of All Inferences Completed in Session """

    base_model_keys = ["llm_response", "usage", "logits", "output_tokens", "prompt", "add_context","final_prompt",
                       "model_name", "model_card", "temperature", "add_prompt_engineering",
                       "model_class", "model_category", "prompt_wrapper", "time_stamp"
                       ]

    inference_history = []

    global_inference_counter = 0

    save = True

    @classmethod
    def get_base_model_keys(cls):
        return cls.base_model_keys

    @classmethod
    def add_base_model_key(cls, new_key):
        if new_key not in cls.base_model_keys:
            cls.base_model_keys.append(new_key)
        return True

    @classmethod
    def del_base_model_key(cls, key_to_delete):
        if key_to_delete in cls.base_model_keys:
            del cls.base_model_keys[key_to_delete]
        return True

    @classmethod
    def get_transactions(cls):
        """ List current view of implemented supported vector db for embeddings. """
        return cls.inference_history

    @classmethod
    def add_transaction(cls, model_state_dict):
        """ Adds a vector db including the module and class. """
        cls.inference_history.append(model_state_dict)
        return True

    @classmethod
    def get_global_inference_count(cls):
        return cls.global_inference_counter

    @classmethod
    def increment_global_inference_count(cls):
        cls.global_inference_counter += 1
        return cls.global_inference_counter

    @classmethod
    def reset_global_inference_count(cls):
        cls.global_inference_counter = 0
        return cls.global_inference_counter

    @classmethod
    def get_save_status(cls):
        return cls.save

    @classmethod
    def set_save_status(cls, status):
        if isinstance(status, bool):
            cls.save = status
        else:
            raise LLMWareException(message="Exception: save status must be boolean - True/False")


def register(kv_dict):

    """ Default register function called after each Model inference activity.  This method can be over-ridden and
     customized by re-routing the LLMWareConfig as follows:

        `LLMWareConfig().set_config('model_register', {'module': 'my_module', 'class': 'my_register_fx'})

        `module` currently points to this module:   'llmware.models'
        `class` currently points to this method:    'register'
    """

    #   if save status set to False, then skip
    if not InferenceHistory().get_save_status():
        logger.debug(f"InferenceHistory - skipping registration since save status is False")
        return True

    for k, v in kv_dict.items():
        logger.debug(f"InferenceHistory - register: {k} - {v}")

    InferenceHistory().increment_global_inference_count()

    logger.debug(f"InferenceHistory - global inference counter - {InferenceHistory().get_global_inference_count()}")

    #   by default, will register all generative inferences, but takes no action to track embedding inferences
    if "model_category" in kv_dict:
        if kv_dict["model_category"] == "generative":
            InferenceHistory().add_transaction(kv_dict)

    return True


def post_init(kv_dict):

    """ Not implemented by default. """
    logger.debug(f"Model Load - in post_init - not implemented - returning True - no action taken")

    return True


def validate(kv_dict):

    """ Not implemented by default. """
    logger.debug(f"Model Load - validate - not implemented - returning True - no action taken")

    return True


def preview(kv_dict):

    """ Not implemented by default. """
    logger.debug(f"Model Load - preview - not implemented - returning True - no action taken")

    return True


def route_optimizer(kv_dict):

    """ Not implemented by default. """
    logger.debug(f"Model Route Optimizer - not implemented - returning True - no action taken")

    return True


class BaseModel:

    """ BaseModel class subclassed by all models. Should not be instantiated directly.   Provides several
    common utility methods across each of the Model class implementations.  """

    def __init__(self, **kwargs):

        # InferenceHistory provides a set of state parameters to be captured from each Model instantiation
        self.base_model_keys = InferenceHistory().get_base_model_keys()

        self.time_stamp = None
        self.model_class = None
        self.model_category = None

        # output inference parameters
        for keys in self.base_model_keys:
            if keys in kwargs:
                setattr(self,keys,kwargs[keys])
            else:
                setattr(self, keys, None)

    def to_state_dict(self):

        """ Writes selected model state parameters to dictionary. """

        state_dict = {}
        for keys in self.base_model_keys:
            if hasattr(self,keys):
                state_dict.update({keys: getattr(self,keys)})

        return state_dict

    def method_resolver(self, config_name):

        """ Resolves method to invoke selected function. """

        process_class = ""
        process_method = ""

        method_exec = None

        state_dict = self.to_state_dict()
        process = LLMWareConfig().get_config(config_name)
        process_module = process["module"]

        if "class" in process:
            process_class = process["class"]

        if "method" in process:
            process_method = process["method"]

        module_exec = importlib.import_module(process_module)

        if process_class:
            if hasattr(module_exec, process_class):
                class_exec = getattr(module_exec, process_class)()

                if process_method:
                    if hasattr(class_exec, process_method):
                        method_exec = getattr(class_exec, process_method)
        else:
            if hasattr(module_exec, process_method):
                method_exec = getattr(module_exec, process_method)

        if method_exec:

            success = method_exec(state_dict)

            if isinstance(success, dict):
                #   write attributes, if any, to the Model instance state
                for k, v in success.items():
                    setattr(self,k,v)

        return True

    def post_init(self):
        return self.method_resolver("model_post_init")

    def register(self):
        return self.method_resolver("model_register")

    def validate(self):
        return self.method_resolver("model_validate")

    def preview(self):
        return self.method_resolver("model_preview")


class ONNXGenerativeModel(BaseModel):

    """ONNXGenerativeModel class implements the ONNX Runtime generative model interface, and is used generally for
     models converted from Pytorch into ONNX for faster inference performance and packaging on Windows platforms
     and x86 architectures. """

    def __init__(self, model_name=None, api_key=None, model_card=None, instruction_following=False, context_window=2048,
                 sample=True, max_output=100, temperature=0.3, get_logits=False, api_endpoint=None, **kwargs):

        super().__init__()

        self.model_class = "ONNXGenerativeModel"
        self.model_category = "generative"
        self.llm_response = None
        self.usage = None
        self.logits = None
        self.output_tokens = None
        self.final_prompt = None

        self.model_name = model_name
        self.hf_tokenizer_name = model_name
        self.model = None
        self.tokenizer = None
        self.generator = None
        self.context_window = context_window
        self.sample = sample
        self.get_logits = get_logits
        self.auto_remediate_function_call_output = True

        # Function Call parameters
        self.model_card = model_card
        self.logits_record = []
        self.output_tokens = []
        self.top_logit_count = 10
        self.primary_keys = None
        self.function = None
        self.fc_supported = False
        self.tool_type = None

        if model_card:

            if "primary_keys" in model_card:
                self.primary_keys = model_card["primary_keys"]

            if "function" in model_card:
                self.function = model_card["function"]

            if "function_call" in model_card:
                self.fc_supported = model_card["function_call"]

            if "context_window" in model_card:
                self.context_window = model_card["context_window"]

        # insert dynamic onnx load here
        if not api_endpoint:

            global GLOBAL_ONNX_GENAI_RUNTIME

            if not GLOBAL_ONNX_GENAI_RUNTIME:

                if util.find_spec("onnxruntime_genai"):

                    try:
                        global og
                        og = importlib.import_module("onnxruntime_genai")
                        GLOBAL_ONNX_GENAI_RUNTIME = True
                    except:
                        raise LLMWareException(message="ONNXGenerativeModel: could not load onnxruntime_genai module. "
                                                       "If you have pip installed the library, then please check "
                                                       "that your platform is supported by onnxruntime.")

                else:
                    import platform
                    if platform.system() == "Darwin":
                        raise LLMWareException(message=f"ONNXGenerativeModel: identified current platform as 'Mac OS' "
                                                       f"which is not supported for onnxruntime_genai currently. "
                                                       f"\nWe would recommend using GGUF for generative inference on a "
                                                       f"Mac, or if you wish to use ONNXGenerativeModel, then please "
                                                       f"shift to a supported Windows or Linux platform.")

                    raise LLMWareException(message="ONNXGenerativeModel: need to import "
                                                   "onnxruntime_genai to use this class, e.g., 'pip3 install "
                                                   "onnxruntime_genai`")

        # end dynamic import here

        if model_name and not api_endpoint:

            if not self.model_card:
                self.model_card = ModelCatalog().lookup_model_card(self.model_name)

            if self.model_card:
                if "hf_repo" in self.model_card:
                    hf_repo_name = self.model_card["hf_repo"]
                    self.hf_tokenizer_name = hf_repo_name

            self.model = None
            self.tokenizer = None
            self.tokenizer_stream = None

            # this can be over-ridden post initiation if needed for custom models
            self.prompt_wrapper = "human_bot"
            self.instruction_following = False

        self.params = None

        # set specific parameters associated with custom models
        # note - these two parameters will control how prompts are handled - model-specific
        self.prompt_wrapper = "human_bot"
        self.instruction_following = instruction_following

        if not model_card:
            # safety - empty iterable rather than 'None'
            model_card = {}

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
        self.max_total_len = self.context_window
        self.max_input_len = int(0.5 * self.context_window)
        self.llm_max_output_len = int(0.5 * self.context_window)

        # key output parameters
        self.max_output = max_output
        self.target_requested_output_tokens = self.max_output

        self.model_architecture = None
        self.separator = "\n"

        # use 0 as eos token id by default in generation -> but try to pull from model config
        self.eos_token_id = 0

        #   will load model and inference onto gpu,
        #   if (a) CUDA available and (b) use_gpu_if_available set to True (default)
        #  TODO: CUDA option handling for ONNX models
        if not api_endpoint:
            self.use_gpu = False
        else:
            self.use_gpu = False

        # no api key expected or required
        self.api_key = api_key

        self.error_message = "\nUnable to identify and load ONNX model."

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
        self.context = ""
        self.prompt = ""

        self.api_endpoint = api_endpoint

        self.model_repo_path = None

        self.post_init()

    def load_model_for_inference(self, loading_directions, model_card=None):

        """ Loads ONNX Model from local path using loading directions. """

        global og

        self.model_repo_path = loading_directions

        if model_card:
            self.model_card = model_card

        self.validate()

        onnx_model_path = os.path.join(LLMWareConfig().get_model_repo_path(),
                                       self.model_name)

        try:
            self.model = og.Model(onnx_model_path)
            self.tokenizer = og.Tokenizer(self.model)
            self.tokenizer_stream = self.tokenizer.create_stream()
        except:
            raise LLMWareException(message=f"ONNXGenerativeModel - unable to load and instantiate the model at: "
                                           f"\n{onnx_model_path}\nThis could be for a number of reasons, but "
                                           f"most likely is one of the following:"
                                           f"\n1. onnxruntime not installed correctly."
                                           f"\n2. platform (e.g, Mac) is not supported by current ONNX Build."
                                           f"\n3. model could not be found at this path, or is not a valid ONNX model."
                                   )

        # set to defaults for HF models in Model Catalog
        # this can be over-ridden post initiation if needed for custom models
        self.prompt_wrapper = "human_bot"
        self.instruction_following = False

        search_options = {}

        # max length set at minimum of 2048
        # adjusted to the actual model context window (if available)
        # currently cap at 'safety' max of 8192
        # --seems to have performance impact at larger lengths

        max_length = max(2048, self.max_total_len)
        if max_length > 8192:
            max_length = 8192

        search_options['max_length'] = max_length

        self.params = og.GeneratorParams(self.model)
        self.params.set_search_options(**search_options)

        return self

    def unload_model(self):

        """ Remove model pointer from memory space.  In most use cases, simply deleting the model pointer will suffice
        to trigger Python memory cleanup with an explicit call to gc.collect(). This is WIP and will continue
        to test different scenarios to explore the best 'safe' unload steps. """

        self.model = None
        self.tokenizer = None
        import gc
        gc.collect()

        return True

    def set_api_key(self, api_key, env_var="USER_MANAGED_ONNX_API_KEY"):

        """ Sets the API key - generally not needed for ONNX self-hosted models. """

        os.environ[env_var] = api_key
        logger.info("ONNXGenerativeModel - added and stored ONNX api_key in "
                    "environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_ONNX_API_KEY"):

        """ Gets API key from os.environ variable. """

        self.api_key = os.environ.get(env_var)

        if not self.api_key:
            logger.error("ONNXGenerativeModel - _get_api_key could not successfully "
                         "retrieve value from: %s ", env_var)

        return self.api_key

    def token_counter(self, text_sample):

        """ Not Used for ONNXGenerativeModel class - Quick approximate token counter -
        uses default tokenizer so may have minor differences from the model's actual tokenization. """

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids

        return len(toks)

    def prompt_engineer(self, query, context, inference_dict):

        """ Applies prompt and templating preparation. """

        # if loaded model was not pretrained to require instruction_following, then skip any instructions
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

    def inference(self, prompt, add_context=None, add_prompt_engineering=None, api_key=None,
                  inference_dict=None):

        """ Executes generation inference on model. """

        global og

        # first prepare the prompt
        t0 = time.time()

        self.prompt = prompt

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
            logger.warning("ONNXGenerativeModel - this is a function calling model - using .inference may lead to "
                           "unexpected results.  Recommended to use the .function_call method to ensure correct prompt "
                           "template packaging.")

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

        self.preview()

        #   START - route to api endpoint
        if self.api_endpoint:
            return self.inference_over_api_endpoint(self.prompt, context=self.add_context,
                                                    inference_dict=inference_dict)
        #   END - route to api endpoint

        text_prompt = self.prompt

        if self.add_prompt_engineering:
            prompt_enriched = self.prompt_engineer(self.prompt, self.add_context, inference_dict=inference_dict)
            prompt_final = prompt_enriched

            # text_prompt = prompt_final + "\n"

            # most models perform better with no trailing space or line-break at the end of prompt
            #   -- in most cases, the trailing space will be ""
            #   -- yi model prefers a trailing "\n"
            #   -- keep as parameterized option to maximize generation performance
            #   -- can be passed either thru model_card or model config from HF

            text_prompt = prompt_final + self.trailing_space

        input_tokens = self.tokenizer.encode(text_prompt)
        self.params.input_ids = input_tokens
        token_count = 0
        output = ""

        try:
            generator = og.Generator(self.model, self.params)
        except:
            raise LLMWareException(message=f"ONNXGenerativeModel - attempt to instantiate ONNX generator with "
                                           f"model and prompt failed.  This is most likely due to an error in the "
                                           f"installation of the onnxruntime, or a problem with loading either the "
                                           f"model or the input tokens.")

        # borrow 'get_first_token_speed' config from GGUFConfigs
        get_first_token_speed = GGUFConfigs().get_config("get_first_token_speed")
        t_gen_start = time.time()
        first_token_processing_time = -1.0

        while not generator.is_done():

            token_count += 1
            generator.compute_logits()
            generator.generate_next_token()

            # get logits - in most cases, get_logits is set to False for basic inference

            if self.get_logits:
                logit = generator.get_output("logits")
                self.register_top_logits(logit)

            new_token = generator.get_next_tokens()[0]

            # first token capture
            if get_first_token_speed:
                if token_count == 1:
                    first_token_processing_time = time.time() - t_gen_start
            # first token capture ends here

            if self.get_logits:
                self.output_tokens.append(new_token)

            output += self.tokenizer_stream.decode(new_token)

            #   add stream on/off options
            # print(self.tokenizer_stream.decode(new_token), end="", flush=True)

            if token_count > self.max_output:
                break

        # direct deletion of generator recommended in onnxruntime_genai examples
        del generator

        llm_response = {"llm_response": output, "usage": {}}

        usage = {"input": len(input_tokens),
                 "output": token_count,
                 "total": len(input_tokens) + token_count,
                 "metric": "tokens",
                 "processing_time": time.time() - t0}

        if get_first_token_speed:
            usage.update({"first_token_processing_time": first_token_processing_time})

        output_response = {"llm_response": output, "usage": usage}

        if self.get_logits:
            output_response.update({"logits": self.logits_record})
            output_response.update({"output_tokens": self.output_tokens})
            self.logits = self.logits_record

        # output inference parameters
        self.llm_response = output
        self.usage = usage
        self.final_prompt = text_prompt

        self.register()

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

    def register_top_logits(self, logit):

        """ Gets the top logits and keeps a running log for output analysis. """

        # logit will be in form of (1,1,vocab_len), for all but the first logit
        # if first logit (will have shape of context len - add [-1])

        if logit.shape[1] > 1:
            # used for first logit with shape, e.g., (1,input_token_len,vocab_size)
            logit_array = logit.squeeze()[-1]
        else:
            # all other logits after the first token
            logit_array = logit.squeeze()

        logit_size = logit.shape[-1]

        # useful check on shape of logit_array
        logit_array_size = logit_array.shape

        sm = np.exp(logit_array) / sum(np.exp(logit_array))

        sm_sorted = np.sort(sm)
        sm_args_sorted = np.argsort(sm)

        top_logits = []

        for x in range(0, self.top_logit_count):
            # round the float number to 3 digits
            pair = (sm_args_sorted[logit_size - x - 1], round(sm_sorted[logit_size - x - 1], 3))
            top_logits.append(pair)

        self.logits_record.append(top_logits)

        return top_logits

    def function_call(self, context, function=None, params=None, get_logits=True,
                      temperature=-99, max_output=None):

        """ This is the key inference method for SLIM models - takes a context passage and a key list
        which is packaged in the prompt as the keys for the dictionary output"""

        t0 = time.time()

        self.context = context

        if not self.fc_supported:
            logger.warning(f"ONNXGenerativeModel - loaded model does not support function calls.  "
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

        if function:
            self.function = function

        if not self.primary_keys:
            logger.warning(f"ONNXGenerativeModel - function call - no keys provided - "
                           f"function call may yield unpredictable results")

        self.preview()

        #   START - route to api endpoint

        if self.api_endpoint:
            return self.function_call_over_api_endpoint(model_name=self.model_name,
                                                        context=self.context, params=self.primary_keys,
                                                        function=self.function,
                                                        api_key=self.api_key, get_logits=self.get_logits)

        #   END - route to api endpoint

        prompt = self.fc_prompt_engineer(self.context, params=self.primary_keys, function=self.function)

        input_tokens = self.tokenizer.encode(prompt)
        self.params.input_ids = input_tokens
        token_count = 0
        output = ""

        try:
            generator = og.Generator(self.model, self.params)
        except:
            raise LLMWareException(message=f"ONNXGenerativeModel - attempt to instantiate ONNX generator with "
                                           f"model and prompt failed.  This is most likely due to an error in the "
                                           f"installation of the onnxruntime, or a problem with loading either the "
                                           f"model or the input tokens.")

        while not generator.is_done():

            token_count += 1
            generator.compute_logits()

            # to get logit value
            if self.get_logits:
                logit = generator.get_output("logits")
                self.register_top_logits(logit)

            generator.generate_next_token()

            new_token = generator.get_next_tokens()[0]

            if self.get_logits:
                self.output_tokens.append(new_token)

            output += self.tokenizer_stream.decode(new_token)

            # add as streaming option to turn on/off
            # print(self.tokenizer_stream.decode(new_token), end="", flush=True)

            if token_count >= self.max_output:
                break

        # done with generator
        del generator

        llm_response = {"llm_response": output, "usage": {}}

        usage = {"input": len(input_tokens),
                 "output": token_count,
                 "total": len(input_tokens) + token_count,
                 "metric": "tokens",
                 "processing_time": time.time() - t0}

        output_response = {"llm_response": output, "usage": usage}

        # end - post-processing

        try:
            import ast
            output_value = ast.literal_eval(output)

            output_type = "dict"

            # allow for multiple valid object types - will expand over time
            if isinstance(output_value, dict): output_type = "dict"
            if isinstance(output_value, list): output_type = "list"

            usage.update({"type": output_type})

        except:
            # could not convert automatically to python object
            output_type = "string"
            usage.update({"type": output_type})
            output_value = output

            # INSERT NEW HERE

            if self.auto_remediate_function_call_output:
                # attempt to remediate
                output_type, output_rem = ModelCatalog().remediate_function_call_string(output)

                usage.update({"type": output_type, "remediation": True})
                output_value = output_rem

            if output_type == "string":
                logger.warning(f"ONNXGenerativeModel - function call - automatic conversion of function call output "
                               f"failed, and attempt to remediate was not successful - {output}")
            else:
                logger.info(f"ONNXGenerativeModel - function call output could not be automatically converted, but "
                            f"remediation was successful to type -{output_type}")

        # INSERT ENDS HERE

        output_response = {"llm_response": output_value, "usage": usage}

        if get_logits:
            output_response.update({"logits": self.logits_record})
            output_response.update({"output_tokens": self.output_tokens})
            self.logits = self.logits_record

        # output inference parameters
        self.llm_response = output_value
        self.usage = usage
        self.final_prompt = prompt

        self.register()

        return output_response

    def stream(self, prompt, add_context=None, add_prompt_engineering=None, api_key=None,
               inference_dict=None):

        """ Executes stream generation inference on model. """

        # first prepare the prompt
        t0 = time.time()

        self.prompt = prompt

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
            logger.warning("ONNXGenerativeModel - this is a function calling model - "
                           "using .inference may lead to unexpected "
                           "results.  Recommended to use the .function_call method to "
                           "ensure correct prompt template packaging.")

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

        self.preview()

        #   START - route to api endpoint
        if self.api_endpoint:
            return self.inference_over_api_endpoint(self.prompt, context=self.add_context,
                                                    inference_dict=inference_dict)
        #   END - route to api endpoint

        text_prompt = self.prompt

        if self.add_prompt_engineering:
            prompt_enriched = self.prompt_engineer(self.prompt, self.add_context, inference_dict=inference_dict)
            prompt_final = prompt_enriched

            # text_prompt = prompt_final + "\n"

            # most models perform better with no trailing space or line-break at the end of prompt
            #   -- in most cases, the trailing space will be ""
            #   -- yi model prefers a trailing "\n"
            #   -- keep as parameterized option to maximize generation performance
            #   -- can be passed either thru model_card or model config from HF

            text_prompt = prompt_final + self.trailing_space

        input_tokens = self.tokenizer.encode(text_prompt)
        self.params.input_ids = input_tokens
        token_count = 0
        output = ""

        # adding as a state var so it can be shut down by chat app if user terminates
        try:
            self.generator = og.Generator(self.model, self.params)
        except:
            raise LLMWareException(message=f"ONNXGenerativeModel - attempt to instantiate ONNX generator with "
                                           f"model and prompt failed.  This is most likely due to an error in the "
                                           f"installation of the onnxruntime, or a problem with loading either the "
                                           f"model or the input tokens.")

        while not self.generator.is_done():

            token_count += 1
            self.generator.compute_logits()
            self.generator.generate_next_token()

            self.get_logits = False
            # to get logit value
            if self.get_logits:
                logit = self.generator.get_output("logits")
                self.register_top_logits(logit)

            new_token = self.generator.get_next_tokens()[0]

            if self.get_logits:
                self.output_tokens.append(new_token)

            output += self.tokenizer_stream.decode(new_token)

            if token_count > self.max_output:
                break

            yield self.tokenizer_stream.decode(new_token)

        print()
        # del self.generator
        self.generator = None

        llm_response = {"llm_response": output, "usage": {}}

        usage = {"input": len(input_tokens),
                 "output": token_count,
                 "total": len(input_tokens) + token_count,
                 "metric": "tokens",
                 "processing_time": time.time() - t0}

        output_response = {"llm_response": output, "usage": usage}

        if self.get_logits:
            output_response.update({"logits": self.logits_record})
            output_response.update({"output_tokens": self.output_tokens})
            self.logits = self.logits_record

        # output inference parameters
        self.llm_response = output
        self.usage = usage
        self.final_prompt = text_prompt

        self.register()

        return output_response

    def cleanup_stream_gen_on_early_stop(self):

        """ Utility method to call if streaming interrupted early to clean up the generator. """

        self.generator = None
        return True

    def inference_over_api_endpoint(self, prompt, context=None, inference_dict=None, get_logits=False):

        """ Called by .inference method when there is an api_endpoint passed in the model constructor. Rather
        than execute the inference locally, it will be sent over API to inference server. """

        import ast
        import requests

        self.prompt = prompt
        self.context = context

        self.preview()

        url = self.api_endpoint + "{}".format("/")
        output_raw = requests.post(url, data={"model_name": self.model_name,
                                              "question": self.prompt,
                                              "context": self.context,
                                              "api_key": self.api_key,
                                              "max_output": self.max_output,
                                              "temperature": self.temperature})

        try:

            output = json.loads(output_raw.text)

            #   will attempt to unpack logits - but catch any exceptions and skip
            if "logits" in output:
                try:
                    logits = ast.literal_eval(output["logits"])
                    output["logits"] = logits
                except:
                    output["logits"] = []

            #   will attempt to unpack output tokens - but catch any exceptions and skip
            if "output_tokens" in output:
                try:
                    # alt: ot_int = [int(x) for x in output["output_tokens"]]
                    # alt: output["output_tokens"] = ot_int
                    output_tokens = ast.literal_eval(output["output_tokens"])
                    output["output_tokens"] = output_tokens
                except:
                    output["output_tokens"] = []

        except:
            logger.warning("warning: api inference was not successful")
            output = {"llm_response": "api-inference-error", "usage": {}}

        # output inference parameters
        self.llm_response = output["llm_response"]
        self.usage = output["usage"]
        self.final_prompt = prompt

        if "logits" in output:
            self.logits = output["logits"]
        if "output_tokens" in output:
            self.output_tokens = output["output_tokens"]

        self.register()

        return output

    def function_call_over_api_endpoint(self, context="", tool_type="", model_name="", params="", prompt="",
                                        function=None, endpoint_base=None, api_key=None, get_logits=False):

        """ Called by .function_call method when there is an api_endpoint passed in the model constructor. Rather
        than execute the inference locally, it will be sent over API to inference server. """

        #   send to api agent server

        import ast
        import requests

        self.context = context
        self.tool_type = tool_type
        if model_name:
            self.model_name = model_name

        self.preview()

        if endpoint_base:
            self.api_endpoint = endpoint_base

        if api_key:
            # e.g., "demo-test"
            self.api_key = api_key

        if not params:
            model_name = _ModelRegistry().get_llm_fx_mapping()[tool_type]
            mc = ModelCatalog().lookup_model_card(model_name)
            if "primary_keys" in mc:
                params = mc["primary_keys"]
                self.primary_keys = params

        if function:
            self.function = function

        self.context = context
        self.prompt = prompt

        url = self.api_endpoint + "{}".format("/agent")
        output_raw = requests.post(url, data={"model_name": self.model_name, "api_key": self.api_key,
                                              "tool_type": self.tool_type,
                                              "function": self.function,
                                              "params": self.primary_keys, "max_output": 50,
                                              "temperature": 0.0, "sample": False, "prompt": self.prompt,
                                              "context": self.context, "get_logits": True})

        try:
            output = json.loads(output_raw.text)
            if "logits" in output:
                logits = ast.literal_eval(output["logits"])
                output["logits"] = logits

            if "output_tokens" in output:
                ot_int = [int(x) for x in output["output_tokens"]]
                output["output_tokens"] = ot_int

            # need to clean up logits

        except:
            logger.warning(f"ONNXGenerativeModel - function call - api inference was not successful")
            output = {}

        logger.info(f"ONNXGenerativeModel - executed Agent call over API endpoint - "
                    f"{self.model_name} - {self.function} - {output}")

        # output inference parameters
        self.llm_response = output["llm_response"]
        self.usage = output["usage"]
        self.final_prompt = prompt

        if "logits" in output:
            self.logits = output["logits"]
        if "output_tokens" in output:
            self.output_tokens = output["output_tokens"]

        self.register()

        return output


class OVGenerativeModel(BaseModel):

    """ OVGenerativeModel class implements the OpenVino generative model interface for fast inference
    performance on x86 Intel architectures, including both Intel CPU and GPU.  """

    def __init__(self, model=None, tokenizer=None, model_name=None, api_key=None, model_card=None,
                 prompt_wrapper=None, instruction_following=False, context_window=2048,
                 sample=False,max_output=100, temperature=0.0,
                 get_logits=False, api_endpoint=None, device="GPU", **kwargs):

        super().__init__()

        self.model_class = "OVGenerativeModel"
        self.model_category = "generative"
        self.llm_response = None
        self.usage = None
        self.logits = None
        self.output_tokens = None
        self.final_prompt = None
        self.model_name = model_name
        self.hf_tokenizer_name = model_name
        self.model = model
        self.tokenizer = tokenizer
        self.sample=sample
        self.get_logits=get_logits

        if get_logits:
            logger.warning(f"OVGenerativeModel - current implementation does not support "
                           f"get_logits option.")
            self.get_logits = False

        self.auto_remediate_function_call_output = True

        # Function Call parameters
        self.model_card = model_card
        self.logits_record = []
        self.output_tokens = []
        self.top_logit_count = 10
        self.primary_keys = None
        self.function = None
        self.fc_supported = False

        self.cache_dir = None

        if model_card:

            if "primary_keys" in model_card:
                self.primary_keys = model_card["primary_keys"]

            if "function" in model_card:
                self.function = model_card["function"]

            if "function_call" in model_card:
                self.fc_supported = model_card["function_call"]

            #   will look for special cache_dir set in the model card
            #   can be over-ridden if passed as kwarg in loading model

            if "cache_dir" in model_card:
                self.cache_dir = model_card["cache_dir"]

        # insert dynamic openvino load here
        if not api_endpoint:

            global openvino
            global ovg
            global GLOBAL_OVG_IMPORT
            global GLOBAL_OPENVINO_IMPORT
            if not GLOBAL_OPENVINO_IMPORT or not GLOBAL_OVG_IMPORT:

                if not util.find_spec("openvino") or not util.find_spec("openvino_genai"):
                    raise LLMWareException(message="OVGenerativeModel: to use OVGenerativeModel requires "
                                                   "install of 'openvino' and 'openvino_genai' libraries.  "
                                                   "Please try: `pip3 install openvino` and "
                                                   "`pip3 install openvino_genai` and confirm that your "
                                                   "hardware platform is supported.")

                if util.find_spec("openvino"):
                    try:
                        openvino = importlib.import_module("openvino")
                        GLOBAL_OPENVINO_IMPORT = True
                    except:
                        raise LLMWareException(message="OVGenerativeModel: could not load openvino module.")

                if openvino:
                    if util.find_spec("openvino_genai"):
                        try:
                            ovg = importlib.import_module("openvino_genai")
                            GLOBAL_OVG_IMPORT = True
                        except:
                            raise LLMWareException(message="OVGenerativeModel: could not load openvino_genai module.")

                if not openvino or not ovg:
                    raise LLMWareException(message="OVGenerativeModel: could not load required openvino dependencies.")

        # end dynamic import here

        # set specific parameters associated with custom models
        # note - these two parameters will control how prompts are handled - model-specific
        self.prompt_wrapper = prompt_wrapper
        self.instruction_following = instruction_following

        if not model_card:
            # safety - empty iterable rather than 'None'
            model_card = {}

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

        # eos_token_id set as list to allow for more than one id
        self.eos_token_id = []

        #   use_gpu parameter not used - deprecated
        self.use_gpu = False

        self.device = device

        if "device" in kwargs:
            self.device = kwargs["device"]

        if "cache_dir" in kwargs:
            self.cache_dir = kwargs["cache_dir"]

        # no api key expected or required
        self.api_key = api_key

        self.error_message = "\nUnable to identify and load model."

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
        self.context = ""
        self.prompt = ""
        self.tool_type = ""

        self.api_endpoint = api_endpoint
        self.pipe = None

        self.input_token_count = 0
        self.output_token_count = 0
        self.params = None
        self.model_repo_path = None

        self.tokenizer_fn = ""

        from llmware.configs import OVConfig

        #   OVConfig object provided in llmware.configs - in most cases, will not be touched, but
        #   exposes more options for configuration of the underlying OpenVino implementation

        #   if config set to CPU - then ensure CPU execution
        if OVConfig().get_config("device") == "CPU":
            self.device = "CPU"
            self.optimize_for_gpu_if_available = False
        else:
            self.optimize_for_gpu_if_available = OVConfig().optimize_for_gpu()

        self.generation_version = OVConfig().generation_version()
        self.cache = OVConfig().get_config("cache")
        self.cache_with_model = OVConfig().get_config("cache_with_model")
        self.cache_custom = OVConfig().get_config("cache_custom_path")
        self.apply_performance_hints = OVConfig().get_config("apply_performance_hints")
        self.use_ov_tokenizer = OVConfig().get_config("use_ov_tokenizer")
        self.verbose_mode = OVConfig().get_config("verbose_mode")

        self.get_token_counts = OVConfig().get_config("get_token_counts")

        # please note that the external tokenizer is used solely for producing
        # input and output token counts - and can be switched off in OVConfig
        if self.get_token_counts:
            self.load_ov_external_tokenizer()

        self.performance_hints = OVConfig().get_gpu_hints()

        self.post_init()

    def load_model_for_inference(self, loading_directions, model_card=None, **kwargs):

        """ Loads OV Model from local path using loading directions. """

        global ovg

        self.model_repo_path = loading_directions
        if model_card:
            self.model_card = model_card

        self.validate()

        if self.device == "GPU" or self.optimize_for_gpu_if_available:
            device = self.device_resolver()
            if device != self.device:
                # resets self.device to the resolved device
                # if changed, then warning provided by resolver method
                self.device = device

        if self.device == "GPU" and self.apply_performance_hints:

            for k,v in self.performance_hints.items():

                try:
                    # sets GPU performance hints thru openvino core
                    #TODO: will evaluate if better way to construct/destruct the core object

                    core = openvino.Core()
                    core.set_property("GPU", {k:v})

                    if self.verbose_mode:
                        logger.info(f"OVGenerativeModel - setting performance hint - {k} - {v}")
                except:
                    logger.warning(f"OVGenerativeModel - unsuccessful setting performance hint - {k} - {v}")

        #   default is to cache to optimize performance on subsequent loads

        if self.cache:
            if self.cache_with_model:
                # will put the cache files co-located with the model assets
                path_to_cache_dir = loading_directions
            else:
                path_to_cache_dir = self.cache_custom

            if self.verbose_mode:
                logger.info(f"OVGenerativeModel - creating pipeline - "
                            f"{self.device} - {self.cache} - {path_to_cache_dir}")

            try:
                #TODO: need to test safety of path_to_cache_dir input in LLMPipeline constructor

                self.pipe = ovg.LLMPipeline(loading_directions, self.device,
                                            {"CACHE_DIR": path_to_cache_dir})

            except:
                raise LLMWareException(message=f"OVGenerativeModel - attempt to instantiate LLMPipeline failed - "
                                               f"this could be for a number of reasons, including: "
                                               f"\n1. openvino and openvino_genai installs are not supported "
                                               f"on this os / hardware platform."
                                               f"\n2. the model could not found at path: {loading_directions}, or "
                                               f"\n3. the model may not a valid OpenVino format model.")
        else:

            #TODO: confirm that empty plugin instructions with no caching will work on all platforms
            try:
                self.pipe = ovg.LLMPipeline(loading_directions, self.device, {})
            except:
                raise LLMWareException(message=f"OVGenerativeModel - attempt to instantiate LLMPipeline failed - "
                                               f"this could be for a number of reasons, including: "
                                               f"\n1. openvino and openvino_genai installs are not supported "
                                               f"on this os / hardware platform."
                                               f"\n2. the model could not found at path: {loading_directions}, or "
                                               f"\n3. the model may not a valid OpenVino format model.")

        if self.verbose_mode:
            logger.info("OVGenerativeModel - completed new pipe creation")

        return self

    def device_resolver(self):

        """ By default, will look for 'GPU' and if device found, then will select - if no GPU,
        then falls back to 'CPU'. """

        global ovg

        try:

            # check if GPU device can be found successfully - if not, auto fallback to CPU device

            core = openvino.Core()
            gpu_device_name = core.get_property("GPU", "FULL_DEVICE_NAME")
            logger.warning(f"OVGenerativeModel - loading - confirmed GPU device name: "
                           f"{gpu_device_name}")
            device = "GPU"

        except:

            logger.warning("OVGenerativeModel - loading - could not find GPU - setting device for CPU")
            device = "CPU"

        return device

    def set_api_key(self, api_key, env_var="USER_MANAGED_OV_API_KEY"):

        """ Sets the API key - generally not needed for self-hosted OV models. """
        os.environ[env_var] = api_key
        logger.info("OVGenerativeModel - added and stored OV api_key in environmental "
                    "variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_OV_API_KEY"):

        """ Gets API key from os.environ variable. """
        self.api_key = os.environ.get(env_var)

        if not self.api_key:
            logger.error("OVGenerativeModel - _get_api_key could not successfully "
                         "retrieve value from: %s ", env_var)

        return self.api_key

    def load_ov_external_tokenizer(self):

        """ Called in class constructor if OVConfig flag set to 'get_output_counts',
        and will create a local instance of the tokenizer used to get the counts. """

        if "tokenizer_local" in self.model_card:
            tok_local_name = self.model_card["tokenizer_local"]
            self.tokenizer = LocalTokenizer(tokenizer_fn=tok_local_name)
        else:
            # if no tokenizer found, then falls back to default tokenizer for 'approximate' count
            self.tokenizer = Utilities().get_default_tokenizer()

    def ov_token_counter(self, text):

        """ Called twice in inference generation loop to get the input_token_count and
        output_token_count.   This step can be skipped by setting the OVConfig as follows:

        `from llmware.configs import OVConfig
        OVConfig().set_config("get_token_counts", False)`

        In our testing, the performance impact is negligible, but may be different in your
        environment and use case.

        If this is set to False, then no token counts will be provided in the usage totals.
        """

        if self.tokenizer:
            toks = len(self.tokenizer.encode(text))
        else:
            toks = 0

        return toks

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

    def _generate_ov_genai(self, prompt):

        """ Core generation script provided by generation loop exposed in the OpenVino_GenAI library. """

        global ovg

        if self.verbose_mode:
            logger.info("OVGenerativeModel - calling openvino_genai backend in _generate_ov_genai method.")

        config = ovg.GenerationConfig()
        config.max_new_tokens = self.max_output

        #   prevent error in generation if sampling True and temperature is set to 0.0
        if self.sample and self.temperature == 0.0:
            self.temperature = 0.2
            logger.warning(f"OVGenerativeModel - since sample is set to True, adjusting "
                           f"temperature from 0.0 to small value - 0.2 - to avoid error "
                           f"in the generation loop.")

        config.temperature = self.temperature
        config.do_sample = self.sample

        #   core generation step - runs generation loop on pipe with prompt and config
        output = self.pipe.generate(prompt, config)

        return output

    def inference(self, prompt, add_context=None, add_prompt_engineering=None, api_key=None,
                  inference_dict=None):

        """ Executes generation inference on model. """

        # first prepare the prompt
        self.prompt = prompt

        if add_context:
            self.add_context = add_context

        self.context = self.add_context

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
            logger.warning("OVGenerativeModel - this is a function calling model - using .inference may lead "
                           "to unexpected results.  Recommended to use the .function_call method to ensure "
                           "correct prompt template packaging.")

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

        self.preview()

        #   START - route to api endpoint
        if self.api_endpoint:
            return self.inference_over_api_endpoint(self.prompt, context=self.add_context,
                                                    inference_dict=inference_dict)
        #   END - route to api endpoint

        text_prompt = self.prompt

        if self.add_prompt_engineering:
            prompt_enriched = self.prompt_engineer(self.prompt, self.add_context, inference_dict=inference_dict)
            prompt_final = prompt_enriched

            # text_prompt = prompt_final + "\n"

            # most models perform better with no trailing space or line-break at the end of prompt
            #   -- in most cases, the trailing space will be ""
            #   -- yi model prefers a trailing "\n"
            #   -- keep as parameterized option to maximize generation performance
            #   -- can be passed either thru model_card or model config from HF

            text_prompt = prompt_final + self.trailing_space

        #   counts the input tokens
        if self.get_token_counts:
            self.input_token_count = self.ov_token_counter(text_prompt)
        else:
            self.input_token_count = 0

        time_start = time.time()

        #   main call to inner generate function
        output = self._generate_ov_genai(text_prompt)

        output_str = output

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

        # counts the output tokens
        if self.get_token_counts:
            self.output_token_count = self.ov_token_counter(output_str)
        else:
            self.output_token_count = 0

        usage = {"input": self.input_token_count,
                 "output": self.output_token_count,
                 "total": self.input_token_count + self.output_token_count,
                 "metric": "tokens",
                 "processing_time": time.time() - time_start}

        output_response = {"llm_response": output_str, "usage": usage}

        self.get_logits = False

        # output inference parameters
        self.llm_response = output_str
        self.usage = usage
        self.final_prompt = text_prompt

        self.register()

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

    def function_call(self, context, function=None, params=None, get_logits=False,
                      temperature=-99, max_output=None):

        """ This is the key inference method for SLIM models - takes a context passage and a key list
        which is packaged in the prompt as the keys for the dictionary output"""

        self.context = context

        if not self.fc_supported:
            logger.warning("OVGenerativeModel - loaded model does not support function calls.  "
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
            logger.warning("OVGenerativeModel - current implementation does not support get_logits option.")
            self.get_logits = False

        if params:
            self.primary_keys = params

        if function:
            self.function = function

        if not self.primary_keys:
            logger.warning("OVGenerativeModel - function call - no keys provided - function call may "
                           "yield unpredictable results")

        self.preview()

        #   START - route to api endpoint

        if self.api_endpoint:
            return self.function_call_over_api_endpoint(model_name=self.model_name,
                                                        context=self.context,params=self.primary_keys,
                                                        function=self.function,
                                                        api_key=self.api_key,get_logits=self.get_logits)

        #   END - route to api endpoint

        prompt = self.fc_prompt_engineer(self.context, params=self.primary_keys, function=function)

        time_start = time.time()

        #   counts the input tokens
        if self.get_token_counts:
            self.input_token_count = self.ov_token_counter(prompt)
        else:
            self.input_token_count = 0

        # main call to inner generate function
        output_str = self._generate_ov_genai(prompt)

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

        # counts the output tokens
        if self.get_token_counts:
            self.output_token_count = self.ov_token_counter(output_str)
        else:
            self.output_token_count = 0

        usage = {"input": self.input_token_count,
                 "output": self.output_token_count,
                 "total": self.input_token_count + self.output_token_count,
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

            # auto remediate set to False - turning off this capability currently
            self.auto_remediate_function_call_output = False

            if self.auto_remediate_function_call_output:

                # attempt to remediate
                output_type, output_rem = ModelCatalog().remediate_function_call_string(output_str)

                usage.update({"type": output_type, "remediation": True})
                output_value = output_rem

            if output_type == "string":
                logger.warning("OVGenerativeModel - automatic conversion of function call output failed, "
                               "and attempt to remediate was not successful - %s ", output_str)
            else:
                logger.info("OVGenerativeModel - function call output could not be automatically "
                            "converted, but remediation was successful to type - %s ", output_type)

        output_response = {"llm_response": output_value, "usage": usage}

        # get_logits - not currently implemented
        if get_logits:
            output_response.update({"logits": self.logits_record})
            output_response.update({"output_tokens": self.output_tokens})
            self.logits = self.logits_record

        # output inference parameters
        self.llm_response = output_value
        self.usage = usage
        self.final_prompt = prompt

        self.register()

        return output_response

    def unload_model(self):

        """ Resetting the pipe removes pointer to pipeline in Python, and generally triggers a (safe) release of
        the memory.   WIP - will continue to evaluate effectiveness across use patterns and platforms. """

        self.pipe = None

        return True

    def inference_over_api_endpoint(self, prompt, context=None, inference_dict=None, get_logits=False):

        """ Called by .inference method when there is an api_endpoint passed in the model constructor. Rather
        than execute the inference locally, it will be sent over API to inference server. """

        import ast
        import requests

        self.prompt = prompt
        self.context = context

        url = self.api_endpoint + "{}".format("/")
        output_raw = requests.post(url, data={"model_name": self.model_name,
                                              "question": self.prompt,
                                              "context": self.context,
                                              "api_key": self.api_key,
                                              "max_output": self.max_output,
                                              "temperature": self.temperature})

        try:

            output = json.loads(output_raw.text)

            #   will attempt to unpack logits - but catch any exceptions and skip
            if "logits" in output:
                try:
                    logits = ast.literal_eval(output["logits"])
                    output["logits"] = logits
                except:
                    output["logits"] = []

            #   will attempt to unpack output tokens - but catch any exceptions and skip
            if "output_tokens" in output:
                try:
                    # ot_int = [int(x) for x in output["output_tokens"]]
                    # output["output_tokens"] = ot_int
                    output_tokens = ast.literal_eval(output["output_tokens"])
                    output["output_tokens"] = output_tokens
                except:
                    output["output_tokens"] = []

        except:
            logger.warning("OVGenerativeModel - api inference was not successful")
            output = {"llm_response": "api-inference-error", "usage": {}}

        # output inference parameters
        self.llm_response = output["llm_response"]
        self.usage = output["usage"]
        self.final_prompt = prompt

        if "logits" in output:
            self.logits = output["logits"]
        if "output_tokens" in output:
            self.output_tokens = output["output_tokens"]

        self.register()

        return output

    def stream(self, prompt, add_context=None, add_prompt_engineering=None, api_key=None,
               inference_dict=None):

        """ Not currently implemented. """

        logger.warning(f"OVGenerativeModel - streaming option not provided by current implementation. "
                       f"Use .inference or .function_call methods for generation.")

        return ""

    def function_call_over_api_endpoint(self, context="", tool_type="", model_name="", params="", prompt="",
                                        function=None, endpoint_base=None, api_key=None, get_logits=False):

        """ Called by .function_call method when there is an api_endpoint passed in the model constructor. Rather
        than execute the inference locally, it will be sent over API to inference server. """

        #   send to api agent server

        self.context = context
        self.tool_type = tool_type
        self.prompt = prompt

        import ast
        import requests

        if endpoint_base:
            self.api_endpoint = endpoint_base

        if api_key:
            # e.g., "demo-test"
            self.api_key = api_key

        if not params:

            self.model_name = _ModelRegistry().get_llm_fx_mapping()[tool_type]
            mc = ModelCatalog().lookup_model_card(self.model_name)
            if "primary_keys" in mc:
                params = mc["primary_keys"]
                self.primary_keys = params

        if function:
            self.function = function

        self.context = context

        self.preview()

        url = self.api_endpoint + "{}".format("/agent")
        output_raw = requests.post(url, data={"model_name": self.model_name, "api_key": self.api_key,
                                              "tool_type": self.tool_type,
                                              "function": self.function, "params": self.primary_keys, "max_output": 50,
                                              "temperature": 0.0, "sample": False, "prompt": self.prompt,
                                              "context": self.context, "get_logits": True})

        try:
            # output = ast.literal_eval(output_raw.text)
            output = json.loads(output_raw.text)
            if "logits" in output:
                logits = ast.literal_eval(output["logits"])
                output["logits"] = logits

            if "output_tokens" in output:
                ot_int = [int(x) for x in output["output_tokens"]]
                output["output_tokens"] = ot_int

        except:
            logger.warning("OVGenerativeModel - api inference was not successful")
            output = {}

        logger.info(f"OVGenerativeModel - executed Agent call over API endpoint - "
                    f"{model_name} - {function} - {output}")

        # output inference parameters
        self.llm_response = output["llm_response"]
        self.usage = output["usage"]
        self.final_prompt = prompt

        if "logits" in output:
            self.logits = output["logits"]
        if "output_tokens" in output:
            self.output_tokens = output["output_tokens"]

        self.register()

        return output


class OpenChatModel(BaseModel):

    """ OpenChatModel class implements the OpenAI prompt API and is intended for use with OpenChat compatible
    inference servers """

    def __init__(self, model_name=None,  model_card=None, context_window=4000,prompt_wrapper=None, api_key="not_used",
                 **kwargs):

        super().__init__(**kwargs)

        #   expected to take config parameters from model card
        self.api_key = api_key
        self.model_name = model_name
        self.model_card = model_card

        self.model_class = "OpenChatModel"
        self.model_category = "generative"
        self.llm_response = None
        self.usage = None
        self.logits = None
        self.output_tokens = None
        self.final_prompt = None

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
        self.prompt = ""

        # new post_init check
        self.post_init()

    def set_api_key (self, api_key, env_var="USER_MANAGED_OPEN_CHAT_API_KEY"):

        """ Utility method to set API key if needed. """

        # set api_key
        os.environ[env_var] = api_key
        logger.info("update: added and stored OpenChat api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key (self, env_var="USER_MANAGED_OPEN_CHAT_API_KEY"):

        """ Utility method to get API key if needed. """

        #   not expected to use api_key - so may be empty - handled in inference separately
        self.api_key = os.environ.get(env_var)

        return self.api_key

    def token_counter(self, text_sample):

        """ Gets GPT2 tokenizer for fast approximate token counting. """

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids

        return len(toks)

    def prompt_engineer_chat(self, query, context, inference_dict=None):

        """ Creates Prompt Template for Chat Interaction. """

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

        """ Creates Prompt for 'Completion' style interface. """

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

        """ Executes inference on the Model. Required input is a text prompt.  Optional parameters include
        an 'add_context' to be used as a source in the prompt, and assembled according to the prompt
        engineering style (e.g., add_prompt_engineering).  An optional inference_dict can include other optional
        parameters such as temperature and max_tokens. If an API key is required, it can be passed here, or
        will be picked up through the appropriate os.environ variable """

        self.prompt = prompt

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

        #   call to preview (not implemented by default)
        self.preview()

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
        prompt_enriched = self.prompt

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

            logger.error(f"Open Chat model inference produced error - {e}")

        output_response = {"llm_response": text_out, "usage": usage}

        # output inference parameters
        self.llm_response = text_out
        self.usage = usage
        self.logits = None
        self.output_tokens = None
        self.final_prompt = prompt_enriched

        self.register()

        return output_response


class OllamaModel(BaseModel):

    """ OllamaModel class implements the Ollama model prompt API and is intended for use in building
     RAG pipelines while using a Ollama endpoint primarily for rapid local prototyping. """

    def __init__(self, model_name=None,  model_card=None, context_window=4000,prompt_wrapper=None, api_key="not_used",
                 **kwargs):

        super().__init__(**kwargs)

        self.model_class = "OllamaModel"
        self.model_category = "generative"
        self.llm_response = None
        self.usage = None
        self.logits = None
        self.output_tokens = None
        self.final_prompt = None

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
        self.prompt = ""

        # self.uri = "http://localhost:11434/api/"
        self.uri = f"http://{self.host}:{self.port}/api/"

        self.post_init()

    def set_api_key (self, api_key, env_var="USER_MANAGED_OLLAMA_API_KEY"):

        """ Utility method to store api_key in os.environ variable. """

        # set api_key
        os.environ[env_var] = api_key
        logger.info("update: added and stored Ollama api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key (self, env_var="USER_MANAGED_OLLAMA_API_KEY"):

        """ Utility method to get api_key from os.environ variable. """

        self.api_key = os.environ.get(env_var)

        return self.api_key

    def token_counter(self, text_sample):

        """ Uses default GPT2 tokenizer for fast, approximate token count, if needed. """

        #   note: this is an approximation for counting the input tokens using a default tokenizer
        #   --to get 100% accurate, need to use the tokenizer being applied on the 'ollama' decoding

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids

        return len(toks)

    def prompt_engineer (self, query, context, inference_dict=None):

        """ Builds prompt by assembling query, context and applying the selected prompt style. """

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

        logger.info("update: OllamaModel - discover_models - %s ", response.text)

        output = json.loads(response.text)

        return output

    def inference(self, prompt, add_context=None, add_prompt_engineering=None, inference_dict=None,
                  api_key=None):

        """ In typical case with raw_mode = False, then no prompt engineering, just apply a basic
        assembly of the prompt and context. """

        self.prompt = prompt

        if add_context:
            self.add_context = add_context

        if add_prompt_engineering:
            self.add_prompt_engineering = add_prompt_engineering

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

        #   call to preview hook (not implemented by default)
        self.preview()

        # default case - pass the prompt received without change
        prompt_enriched = self.prompt

        usage = {}

        time_start = time.time()

        try:

            #   assumes 'chat' api by default

            if self.model_type == "chat":

                full_prompt = self.prompt_engineer(prompt_enriched, self.add_context, inference_dict)

                messages = [{"role": "user", "content": full_prompt}]
                uri = self.uri + "chat"

                response = requests.post(uri,
                                         json={"model": self.model_name,
                                               "messages": messages, "stream": self.stream_mode})

                logger.info("update: OllamaModel response - chat - %s ", response.text)

                output = json.loads(response.text)

                text_out = output["message"]["content"]

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

            logger.error(f"error: Ollama model inference produced error - {e}")

        output_response = {"llm_response": text_out, "usage": usage}

        # output inference parameters
        self.llm_response = text_out
        self.usage = usage
        self.logits = None
        self.output_tokens = None
        self.final_prompt = prompt_enriched

        self.register()

        return output_response


class OpenAIGenModel(BaseModel):

    """ OpenAIGenModel class implements the OpenAI API for its generative decoder models. """

    def __init__(self, model_name=None, api_key=None, context_window=4000, max_output=100,temperature=0.7, **kwargs):

        super().__init__(**kwargs)

        self.model_class = "OpenAIGenModel"
        self.model_category = "generative"
        self.llm_response = None
        self.usage = None
        self.logits = None
        self.output_tokens = None
        self.final_prompt = None

        self.api_key = api_key
        self.model_name = model_name

        self.error_message = "\nUnable to connect to OpenAI. Please try again later."

        self.separator = "\n"

        # assume input (50%) + output (50%)
        self.max_total_len = context_window
        self.max_input_len = int(context_window * 0.5)
        self.llm_max_output_len = int(context_window * 0.5)

        # inference settings
        if temperature >= 0.0:
            self.temperature = temperature
        else:
            self.temperature = 0.7

        self.target_requested_output_tokens = max_output
        self.add_prompt_engineering = False
        self.add_context = ""
        self.prompt = ""

        # provides option to pass custom openai_client to model class at inference time
        self.openai_client = None

        if "model_card" in kwargs:
            self.model_card = kwargs["model_card"]
        else:
            self.model_card = {}

        self.post_init()

    def set_api_key (self, api_key, env_var="USER_MANAGED_OPENAI_API_KEY"):

        """ Utility method to set the API key in os.environ variable. """

        # set api_key
        os.environ[env_var] = api_key
        logger.info("update: added and stored OpenAI api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key (self, env_var="USER_MANAGED_OPENAI_API_KEY"):

        """ Utility method to get the API key from os.environ variable. """

        self.api_key = os.environ.get(env_var)

        if not self.api_key:
            logger.error("error: _get_api_key could not successfully retrieve value from: %s ", env_var)

        return self.api_key

    def token_counter(self, text_sample):

        """ Fast, approximate token counting using GPT2 tokenizer. """

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids

        return len(toks)

    def prompt_engineer_chatgpt3(self, query, context, inference_dict=None):

        """ Builds prompt in ChatGPT format.  """

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

        """ Builds Prompt in traditional 'completion' style. """

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

        """ Executes inference on OpenAI Model.  Only required input is text-based prompt, with optional
        parameters to "add_context" passage that will be assembled using the prompt style in the
        "add_prompt_engineering" parameter.  Optional inference_dict for temperature and max_tokens configuration,
        and optional passing of api_key at time of inference. """

        self.prompt = prompt

        if add_context:
            self.add_context = add_context

        if add_prompt_engineering:
            self.add_prompt_engineering = add_prompt_engineering

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

            if "openai_client" in inference_dict:
                self.openai_client = inference_dict["openai_client"]

        from llmware.configs import OpenAIConfig

        if not self.openai_client:
            azure_client = OpenAIConfig().get_azure_client()
        else:
            azure_client = self.openai_client

        # api_key
        if api_key:
            self.api_key = api_key

        if not self.api_key:
            if not azure_client:
                self.api_key = self._get_api_key()

        if not self.api_key and not azure_client:
            logger.error("OpenAIGenModel: invoking OpenAI Generative model with no api_key.")

        #   call to preview hook (not implemented by default)
        self.preview()

        # default case - pass the prompt received without change
        prompt_enriched = self.prompt

        # new - change with openai v1 api
        try:
            from openai import OpenAI
        except ImportError:
            raise DependencyNotInstalledException("openai >= 1.0")

        usage = {}
        time_start = time.time()

        try:

            if self.model_name in ["gpt-3.5-turbo","gpt-4","gpt-4-1106-preview","gpt-3.5-turbo-1106", 
                                   "gpt-4-0125-preview", "gpt-3.5-turbo-0125", "gpt-4o", "gpt-4o-2024-05-13",
                                   "gpt-4o-mini-2024-07-18","gpt-4o-mini","gpt-4o-2024-08-06"]:

                messages = self.prompt_engineer_chatgpt3(prompt_enriched, self.add_context, inference_dict)

                # updated OpenAI client to >v1.0 API - create client, and returns pydantic objects

                if not azure_client:
                    client = OpenAI(api_key=self.api_key)
                    model_name = self.model_name

                else:

                    logger.debug("OpenAIGenModel - applying custom OpenAI client from OpenAIConfig")

                    client = azure_client

                    # adapt model name for azure, e.g., replace(".", "")
                    model_name = OpenAIConfig().get_azure_model_name(self.model_name)

                response = client.chat.completions.create(model=model_name,messages=messages,
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

                azure_client = OpenAIConfig().get_azure_client()

                if not azure_client:
                    client = OpenAI(api_key=self.api_key)
                    model_name = self.model_name
                else:

                    logger.debug("OpenAIGenModel - applying custom OpenAI client from OpenAIConfig")

                    client = azure_client
                    # adapt model name for azure, e.g., replace(".", "")
                    model_name = OpenAIConfig().get_azure_model_name(self.model_name)

                response = client.completions.create(model=model_name, prompt=text_prompt,
                                                     temperature=self.temperature,
                                                     max_tokens=self.target_requested_output_tokens)

                text_out = response.choices[0].text

                usage = {"input": response.usage.prompt_tokens,
                         "output": response.usage.completion_tokens,
                         "total": response.usage.total_tokens,
                         "metric": "tokens",
                         "processing_time": time.time() - time_start}

        except Exception as e:
            # catch error
            text_out = "/***ERROR***/"
            usage = {"input":0, "output":0, "total":0, "metric": "tokens",
                     "processing_time": time.time() - time_start}

            logger.error("OpenAIGenModel - inference produced error - %s ", e)

        output_response = {"llm_response": text_out, "usage": usage}

        # output inference parameters
        self.llm_response = text_out
        self.usage = usage
        self.logits = None
        self.output_tokens = None
        self.final_prompt = prompt_enriched

        self.register()

        return output_response

    def stream(self, prompt, add_context=None, add_prompt_engineering=None, inference_dict=None,
                  api_key=None):

        """ Executes stream inference on OpenAI Model.

        Only required input is text-based prompt, with optional
        parameters to "add_context" passage that will be assembled using the prompt style in the
        "add_prompt_engineering" parameter.  Optional inference_dict for temperature and max_tokens configuration,
        and optional passing of api_key at time of inference.
        """

        self.prompt = prompt

        if add_context:
            self.add_context = add_context

        if add_prompt_engineering:
            self.add_prompt_engineering = add_prompt_engineering

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

            if "openai_client" in inference_dict:
                self.openai_client = inference_dict["openai_client"]

        from llmware.configs import OpenAIConfig

        if not self.openai_client:
            azure_client = OpenAIConfig().get_azure_client()
        else:
            azure_client = self.openai_client

        # api_key
        if api_key:
            self.api_key = api_key

        if not self.api_key:
            if not azure_client:
                self.api_key = self._get_api_key()

        if not self.api_key and not azure_client:
            logger.error("OpenAIGenModel - invoking OpenAI Generative model with no api_key.")

        #   call to preview hook (not implemented by default)
        self.preview()

        # default case - pass the prompt received without change
        prompt_enriched = self.prompt

        # new - change with openai v1 api
        try:
            from openai import OpenAI
        except ImportError:
            raise DependencyNotInstalledException("openai >= 1.0")

        usage = {}
        time_start = time.time()

        try:

            if self.model_name in ["gpt-3.5-turbo","gpt-4","gpt-4-1106-preview","gpt-3.5-turbo-1106",
                                   "gpt-4-0125-preview", "gpt-3.5-turbo-0125", "gpt-4o", "gpt-4o-2024-05-13",
                                   "gpt-4o-mini-2024-07-18","gpt-4o-mini","gpt-4o-2024-08-06"]:

                messages = self.prompt_engineer_chatgpt3(prompt_enriched, self.add_context, inference_dict)

                # updated OpenAI client to >v1.0 API - create client, and returns pydantic objects

                if not azure_client:
                    client = OpenAI(api_key=self.api_key)
                    model_name = self.model_name

                else:

                    logger.debug("OpenAIGenModel - applying custom OpenAI client from OpenAIConfig.")

                    client = azure_client

                    # adapt model name for azure, e.g., replace(".", "")
                    model_name = OpenAIConfig().get_azure_model_name(self.model_name)

                text_out = ""
                prompt_tokens = 0
                completion_tokens = 0
                total_tokens = 0

                stream_response = client.chat.completions.create(model=model_name,messages=messages,
                                                                 max_tokens=self.target_requested_output_tokens,
                                                                 stream=True)

                # implement streaming generator to yield chunk of tokens
                for chunk in stream_response:
                    if len(chunk.choices) > 0:
                        token = chunk.choices[0].delta.content or ""
                        text_out += token
                        yield token

                usage = {"input": prompt_tokens,
                         "output": completion_tokens,
                         "total": prompt_tokens + completion_tokens,
                         "metric": "tokens",
                         "processing_time": time.time() - time_start}

            else:
                # openai traditional 'instruct gpt' completion models

                prompt_enriched = self.prompt_engineer(prompt_enriched, self.add_context, inference_dict=inference_dict)

                prompt_final = prompt_enriched

                text_prompt = prompt_final + self.separator

                azure_client = OpenAIConfig().get_azure_client()

                if not azure_client:
                    client = OpenAI(api_key=self.api_key)
                    model_name = self.model_name

                else:

                    logger.debug("OpenAIGenModel - applying custom OpenAI client from OpenAIConfig.")

                    client = azure_client
                    model_name = OpenAIConfig().get_azure_model_name(self.model_name)

                text_out = ""
                prompt_tokens = 0
                completion_tokens = 0
                total_tokens = 0

                stream_response = client.completions.create(model=model_name, prompt=text_prompt,
                                                            temperature=self.temperature,
                                                            max_tokens=self.target_requested_output_tokens,
                                                            stream=True)

                # implement streaming generator to yield chunk of tokens
                for chunk in stream_response:
                    if len(chunk.choices) > 0:
                        token = chunk.choices[0].delta.content or ""
                        text_out += token
                        yield token

                usage = {"input": prompt_tokens,
                         "output": completion_tokens,
                         "total": prompt_tokens + completion_tokens,
                         "metric": "tokens",
                         "processing_time": time.time() - time_start}

        except Exception as e:
            # catch error
            text_out = "/***ERROR***/"
            usage = {"input":0, "output":0, "total":0, "metric": "tokens",
                     "processing_time": time.time() - time_start}

            logger.error("OpenAIGenModel - OpenAI model inference produced error - %s ", e)

        output_response = {"llm_response": text_out, "usage": usage}

        # output inference parameters
        self.llm_response = text_out
        self.usage = usage
        self.logits = None
        self.output_tokens = None
        self.final_prompt = prompt_enriched

        self.register()

        return output_response


class ClaudeModel(BaseModel):

    """ ClaudeModel class implements the Anthropic Claude API for calling Anthropic models. """

    def __init__(self, model_name=None, api_key=None, context_window=8000, max_output=100, temperature=0.7, **kwargs):

        super().__init__(**kwargs)

        self.model_class = "ClaudeModel"
        self.model_category = "generative"
        self.llm_response = None
        self.usage = None
        self.logits = None
        self.output_tokens = None
        self.final_prompt = None

        self.api_key = api_key
        self.model_name = model_name

        self.error_message = "\nUnable to connect to Anthropic/Claude. Please try again later."

        self.separator = "\n"

        #   Claude/Anthropic model - 8000 max token context window
        self.max_total_len = context_window
        self.max_input_len = int(context_window * 0.5)
        self.llm_max_output_len = int(context_window * 0.5)

        # inference settings
        if temperature >= 0.0:
            self.temperature = temperature
        else:
            self.temperature = 0.7

        self.target_requested_output_tokens = max_output
        self.add_prompt_engineering = False
        self.add_context = ""
        self.prompt = ""

        self.post_init()

    def set_api_key(self, api_key, env_var="USER_MANAGED_ANTHROPIC_API_KEY"):

        """ Utility method to set the API key in os.environ variable. """

        os.environ[env_var] = api_key
        logger.info("update: added and stored ANTHROPIC api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_ANTHROPIC_API_KEY"):

        """ Utility method to get api_key from os.environ variable. """

        self.api_key = os.environ.get(env_var)

        if not self.api_key:
            logger.error("error: _get_api_key could not successfully retrieve value from: %s ", env_var)

        return self.api_key

    def token_counter(self, text_sample):

        """ Gets GPT2 tokenizer for fast approximate token counting. """

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids
        return len(toks)

    def prompt_engineer (self, query, context, inference_dict=None):

        """ Builds prompt by assembling query, context and applying prompt style. """

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

        """ Executes inference on Anthropic Model.  Only required input is text-based prompt, with optional
        parameters to "add_context" passage that will be assembled using the prompt style in the
        "add_prompt_engineering" parameter.  Optional inference_dict for temperature and max_tokens configuration,
        and optional passing of api_key at time of inference. """

        self.prompt = prompt

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
            logger.error("error: invoking Anthropic Claude Generative model with no api_key")

        #   call to preview hook (not implemented by default)
        self.preview()

        try:
            import anthropic
        except ImportError:
            raise DependencyNotInstalledException("anthropic")

        client = anthropic.Client(api_key=self.api_key)

        # prototype prompt sample:   prompt_enriched = "\n\nHuman:" + " please read the following- " +
        # self.add_context + " Based on these materials, " + prompt["prompt"] + "\n\nAssistant:"

        prompt_enriched = self.prompt_engineer(self.prompt,self.add_context, inference_dict=inference_dict)

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
            logger.error("error: Anthropic model inference produced error - %s ", e)

        output_response = {"llm_response": text_out, "usage": usage}

        logger.debug(f"update: output_response - anthropic: {output_response}")

        # output inference parameters
        self.llm_response = text_out
        self.usage = usage
        self.logits = None
        self.output_tokens = None
        self.final_prompt = prompt_enriched

        self.register()

        return output_response


class GoogleGenModel(BaseModel):

    """ GoogleGenModel class implements the Google Vertex API for Google's generative models.
    Note: to use GoogleModels does require a separate import of Google SDKs - vertexai and google.cloud.platform """

    def __init__(self, model_name=None, api_key=None, context_window=8192, max_output=100, temperature=0.7, **kwargs):

        super().__init__(**kwargs)

        self.model_class = "GoogleGenModel"
        self.model_category = "generative"
        self.llm_response = None
        self.usage = None
        self.logits = None
        self.output_tokens = None
        self.final_prompt = None

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
        if temperature >= 0.0:
            self.temperature = temperature
        else:
            self.temperature = 0.7

        self.target_requested_output_tokens = max_output
        self.add_prompt_engineering = False
        self.add_context = ""
        self.prompt = ""

        self.post_init()

    def set_api_key(self, api_key, env_var="USER_MANAGED_GOOGLE_API_KEY"):

        """ Utility method to set the API key in os.environ variable. """

        os.environ[env_var] = api_key
        logger.info("update: added and stored GOOGLE api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_GOOGLE_API_KEY"):

        """ Utility method to get api_key from os.environ variable. """

        self.api_key = os.environ.get(env_var)
        return self.api_key

    def token_counter(self, text_sample):

        """ Gets GPT2 tokenizer for fast approximate token counting. """

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids

        return len(toks)

    def prompt_engineer (self, query, context, inference_dict=None):

        """ Builds Prompt by assembling query, context and applying the selected prompt engineering style. """

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

        """ Executes inference on Google Model.  Only required input is text-based prompt, with optional
        parameters to "add_context" passage that will be assembled using the prompt style in the
        "add_prompt_engineering" parameter.  Optional inference_dict for temperature and max_tokens configuration,
        and optional passing of api_key at time of inference. """

        self.prompt = prompt

        if add_context:
            self.add_context = add_context

        if add_prompt_engineering:
            self.add_prompt_engineering = add_prompt_engineering

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

        #   call to preview hook (not implemented by default)
        self.preview()

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
            logger.error("error: invoking Google Generative model with no api_key")

        prompt_enriched = self.prompt_engineer(self.prompt,self.add_context, inference_dict=inference_dict)

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

            logger.debug(f"google model response: {response.text}")
         
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
            logger.error("error: Google model inference produced error:  %s", e)

        finally:
            # Close the credentials json which automatically deletes it (since it is a NamedTemporaryFile)
            os.remove(google_json_credentials)
        
        output_response = {"llm_response": text_out, "usage": usage}

        logger.debug("update: output_response - google: %s ", output_response)

        # output inference parameters
        self.llm_response = text_out
        self.usage = usage
        self.logits = None
        self.output_tokens = None
        self.final_prompt = prompt_enriched

        self.register()

        return output_response
    
    def api_key_to_json(self):

        # Google authentication key is an entire json dictionary which we have the user pass in as an env var
        # We write out the json and we need to escape newlines which seem to be always present in
        # google auth json files

        temp_json_path = tempfile.NamedTemporaryFile(prefix="googlecreds", delete=False).name

        with open(temp_json_path, "w", encoding='utf-8') as f:
            f.write(self.api_key.replace("\n", "\\n"))

        return temp_json_path


class JurassicModel(BaseModel):

    """ JurassicModel class implements the AI21 Jurassic API. """

    def __init__(self, model_name=None, api_key=None, context_window=2048, max_output=100,temperature=0.7, **kwargs):

        super().__init__(**kwargs)

        self.model_class = "JurassicModel"
        self.model_category = "generative"
        self.llm_response = None
        self.usage = None
        self.logits = None
        self.output_tokens = None
        self.final_prompt = None

        self.api_key = api_key
        self.model_name = model_name

        self.error_message = "\nUnable to connect to Jurassic. Please try again later."

        self.separator = " -- "

        #   set max_total_len -> adjust input and output based on use case
        self.max_total_len = context_window
        self.max_input_len = int(context_window * 0.5)

        self.llm_max_output_len = int(context_window * 0.5)

        # inference settings
        if temperature >= 0.0:
            self.temperature = temperature
        else:
            self.temperature = 0.7

        self.target_requested_output_tokens = max_output
        self.add_prompt_engineering = False
        self.add_context = ""
        self.prompt = ""

        # 'j2-jumbo-instruct', 'j2-grande-instruct','j2-jumbo','j2-grande', 'j2-large'

        self.post_init()

    def set_api_key(self, api_key, env_var="USER_MANAGED_AI21_API_KEY"):

        """ Utility method to set the API key in os.environ variable. """

        os.environ[env_var] = api_key
        logger.info("update: added and stored AI21 api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_AI21_API_KEY"):

        """ Utility method to get api_key from os.environ variable. """

        self.api_key = os.environ.get(env_var)

        return self.api_key

    def token_counter(self, text_sample):

        """ Gets GPT2 tokenizer for fast approximate token counting. """

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids

        return len(toks)

    def prompt_engineer (self, query, context, inference_dict=None):

        """ Builds prompt by assembling query, context and applying the selected prompt style. """

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

        """ Executes inference on Jurassic Model.  Only required input is text-based prompt, with optional
        parameters to "add_context" passage that will be assembled using the prompt style in the
        "add_prompt_engineering" parameter.  Optional inference_dict for temperature and max_tokens configuration,
        and optional passing of api_key at time of inference. """

        self.prompt = prompt

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
            logger.error("error: invoking AI21 Jurassic model with no api_key")

        #   call to preview hook (not implemented by default)
        self.preview()

        try:
            import ai21
        except ImportError:
            raise DependencyNotInstalledException("ai21")

        prompt_enriched = self.prompt

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
            logger.error("error: Jurassic model inference produced error - %s ", e)

        # will look to capture usage metadata

        output_response = {"llm_response": text_out, "usage": usage}

        # output inference parameters
        self.llm_response = text_out
        self.usage = usage
        self.logits = None
        self.output_tokens = None
        self.final_prompt = prompt_enriched

        self.register()

        return output_response


class CohereGenModel(BaseModel):

    """ CohereGenModel class implements the API for Cohere's generative models. """

    def __init__(self, model_name=None, api_key=None, context_window=2048, max_output=100,temperature=0.7, **kwargs):

        super().__init__(**kwargs)

        self.model_class = "CohereGenModel"
        self.model_category = "generative"
        self.llm_response = None
        self.usage = None
        self.logits = None
        self.output_tokens = None
        self.final_prompt = None

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
        if temperature >= 0.0:
            self.temperature = temperature
        else:
            self.temperature = 0.7

        self.target_requested_output_tokens = max_output
        self.add_prompt_engineering = False
        self.add_context = ""
        self.prompt = ""

        # cohere generative models - 'command-medium-nightly',
        # 'command-xlarge-nightly','xlarge','medium', "summarize-xlarge", "summarize-medium"

        self.post_init()

    def set_api_key(self, api_key, env_var="USER_MANAGED_COHERE_API_KEY"):

        """ Utility method to set the API key in os.environ variable. """

        os.environ[env_var] = api_key
        logger.info("update: added and stored COHERE api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_COHERE_API_KEY"):

        """ Utility method to get api_key from os.environ variable. """

        self.api_key = os.environ.get(env_var)

        return self.api_key

    def token_counter(self, text_sample):

        """ Gets GPT2 tokenizer for fast approximate token counting. """

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids

        return len(toks)

    def prompt_engineer (self, query, context, inference_dict=None):

        """ Builds prompt by assembling query, context and applying the selected prompt style. """

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

        """ Executes inference on Cohere Model.  Only required input is text-based prompt, with optional
        parameters to "add_context" passage that will be assembled using the prompt style in the
        "add_prompt_engineering" parameter.  Optional inference_dict for temperature and max_tokens configuration,
        and optional passing of api_key at time of inference. """

        self.prompt = prompt

        if add_context:
            self.add_context = add_context

        if add_prompt_engineering:
            self.add_prompt_engineering = add_prompt_engineering

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

        #   call to preview hook (not implemented by default)
        self.preview()

        #tokens_in_prompt = self.token_counter(prompt)
        #tokens_in_context = self.token_counter(self.add_context)

        prompt_enriched = self.prompt

        logger.debug(f"Cohere Model - inference - {prompt_enriched} - {self.add_prompt_engineering}")

        prompt_enriched = self.prompt_engineer(prompt_enriched,self.add_context, inference_dict=inference_dict)

        if api_key:
            self.api_key = api_key

        if not self.api_key:
            self.api_key = self._get_api_key()

        if not self.api_key:
            logger.error(f"Cohere Model - invoking Cohere Generative model with no api_key")

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
                                        format="bullets", extractiveness='medium', additional_command=self.prompt)

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

            text_out = "/***ERROR***/"

            usage = {"input": 0, "output": 0, "total": 0, "metric": "chars",
                     "processing_time": time.time() - time_start}

            logger.error("error: Cohere model inference produced error - %s - ", e)

        # will look to capture usage metadata

        output_response = {"llm_response": text_out, "usage": usage}

        logger.debug("update:  output response - cohere : %s ", output_response)

        # output inference parameters
        self.llm_response = text_out
        self.usage = usage
        self.logits = None
        self.output_tokens = None
        self.final_prompt = prompt_enriched

        self.register()

        return output_response


class LLMWareModel(BaseModel):

    """LLMWareModel class implements the API for LLMWare generative models. """

    def __init__(self, model_name=None, api_key=None, context_window=2048, **kwargs):

        super().__init__(**kwargs)

        self.model_class = "LLMWareModel"
        self.model_category = "generative"
        self.llm_response = None
        self.usage = None
        self.logits = None
        self.output_tokens = None
        self.final_prompt = None

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
        self.prompt = ""

        self.post_init()

    def set_api_key(self, api_key, env_var="USER_MANAGED_LLMWARE_GPT_API_KEY"):

        """ Utility method to set the API key in os.environ variable. """

        os.environ[env_var] = api_key
        logger.info("update: added and stored READ_GPT api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_LLMWARE_GPT_API_KEY"):

        """ Utility method to get api_key from os.environ variable. """

        self.api_key = os.environ.get(env_var)

        return self.api_key

    def token_counter(self, text_sample):

        """ Gets GPT2 tokenizer for fast approximate token counting. """

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids
        return len(toks)

    def prompt_engineer(self, query, context, inference_dict=None):

        """ Builds prompt by assembling query, context and applying the selected prompt style. """

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

    def load_model_for_inference(self, model_name=None, model_card=None,fp=None, **kwargs):

        #   validate before loading - turned off
        # self.validate()

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

        """ Executes inference on LLMWare Model.  Only required input is text-based prompt, with optional
        parameters to "add_context" passage that will be assembled using the prompt style in the
        "add_prompt_engineering" parameter.  Optional inference_dict for temperature and max_tokens configuration,
        and optional passing of api_key at time of inference. """

        self.prompt = prompt

        if add_context:
            self.add_context = add_context

        if add_prompt_engineering:
            self.add_prompt_engineering = add_prompt_engineering

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

        #   call to preview hook (not implemented by default)
        self.preview()

        prompt_enriched = self.prompt_engineer(self.prompt, self.add_context, inference_dict=inference_dict)

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
                  "question": self.prompt,
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

            logger.error("error: no response from aib remote server for llmware-gpt model - "
                          "check api key and connection")

            success_path = -1
            output_response = {"llm_response": "", "usage": usage}

        # output inference parameters
        self.llm_response = ""
        self.usage = usage
        self.logits = None
        self.output_tokens = None
        self.final_prompt = prompt_enriched

        self.register()

        return output_response


class OpenAIEmbeddingModel(BaseModel):

    """ OpenAIEmbeddingModel class implements the OpenAI API for embedding models. """

    def __init__(self, model_name=None, api_key=None, embedding_dims=None, model_card=None, max_len=None, **kwargs):

        super().__init__(**kwargs)

        self.model_class = "OpenAIEmbeddingModel"
        self.model_category = "embedding"

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

        self.text_sample = None

        self.post_init()

    def set_api_key(self, api_key,env_var="USER_MANAGED_OPENAI_API_KEY"):

        """ Utility method to set the API key in os.environ variable. """

        os.environ[env_var] = api_key
        logger.info("update: added and stored OpenAI api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_OPENAI_API_KEY"):

        """ Utility method to get api_key from os.environ variable. """

        self.api_key = os.environ.get(env_var)
        return self.api_key

    def get_tokenizer(self):
        self.tokenizer = Utilities().get_default_tokenizer()
        return self.tokenizer

    def token_counter(self, text_sample):

        """ Counts tokens in text sample. """

        return len(self.tokenizer.encode(text_sample).ids)

    def embedding(self, text_sample, api_key=None):

        self.text_sample = text_sample

        #   call to preview (not implemented by default)
        self.preview()

        if api_key:
            self.api_key = api_key

        if not self.api_key:
            self.api_key = self._get_api_key()

        if not self.api_key:
            logger.error("error: invoking OpenAI Embedding model with no api_key")

        # need to prepare for batches
        if isinstance(self.text_sample, list):
            text_prompt = self.text_sample
            input_len = len(text_sample)
        else:
            text_prompt = [self.text_sample]
            input_len = 1

        try:
            from openai import OpenAI
        except ImportError:
            raise DependencyNotInstalledException("openai >= 1.0")

        from llmware.configs import OpenAIConfig

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

                logger.warning(f"warning: OpenAI Embedding - input sample len - {tok_len} > context_window size "
                                f"\ninput_sample - {display_sample} "
                                f"\n\nSample is being truncated.")

                tok = tokenizer.encode(sample).ids
                tok = tok[0:(self.max_total_len - safety_buffer)]
                sample = tokenizer.decode(tok)
                safe_samples.append(sample)

        text_prompt = safe_samples
        # end - safety check

        # update to open >v1.0 api - create client and output is pydantic objects

        azure_client = OpenAIConfig().get_azure_client()

        if not azure_client:
            client = OpenAI(api_key=self.api_key)

        else:

            logger.info("update: applying custom OpenAI client from OpenAIConfig")

            client = azure_client

        response = client.embeddings.create(model=self.model_name, input=text_prompt)

        if input_len == 1:
            embedding = response.data[0].embedding
        else:
            embedding = []
            for i, entries in enumerate(response.data):
                embedding.append(response.data[i].embedding)

        self.register()

        return embedding


class CohereEmbeddingModel(BaseModel):

    """ CohereEmbeddingModel implements the Cohere API for embedding models. """

    def __init__(self, model_name = None, api_key=None, embedding_dims=None, model_card=None,max_len=None, **kwargs):

        super().__init__(**kwargs)

        self.model_class = "CohereEmbeddingModel"
        self.model_category = "embedding"

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

        self.text_sample = None

        self.post_init()

    def set_api_key(self, api_key, env_var="USER_MANAGED_COHERE_API_KEY"):

        """ Utility method to set the API key in os.environ variable. """

        os.environ[env_var] = api_key
        logger.info("update: added and stored COHERE api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_COHERE_API_KEY"):

        """ Utility method to get api_key from os.environ variable. """

        self.api_key = os.environ.get(env_var)

        return self.api_key

    def token_counter(self, text_sample):

        """ Gets GPT2 tokenizer for fast approximate token counting. """

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids
        return len(toks)

    def embedding(self,text_sample):

        self.text_sample = text_sample

        #   call to preview (not implemented by default)
        self.preview()

        if not self.api_key:
            self.api_key = self._get_api_key()

        if not self.api_key:
            logger.error("error: invoking Cohere embedding model with no api_key")

        try:
            import cohere
        except ImportError:
            raise DependencyNotInstalledException("cohere")

        co = cohere.Client(self.api_key)

        # need safety check on length of text_sample

        # need to prepare for batches
        if isinstance(self.text_sample, list):
            text_prompt = self.text_sample
            input_len = len(self.text_sample)
        else:
            text_prompt = [self.text_sample]
            input_len = 1

        # adding model name as parameter passed to the Cohere embedding API
        response = co.embed(text_prompt,model=self.model_name)

        output = []
        for i, emb in enumerate(response.embeddings):

            logger.debug(f"Cohere embedding - {i} - {emb}")

            # normalization of the Cohere embedding vector improves performance
            emb_vec = np.array(emb) / np.linalg.norm(emb)

            output.append(emb_vec)

        self.register()

        return output


class GoogleEmbeddingModel(BaseModel):

    """ GoogleEmbeddingModel implements the Google API for text embedding models.  Note: to use Google models
    requires a separate install of the Google SDKs, e.g., vertexai and google.cloud.platform """

    def __init__(self, model_name=None, api_key=None, embedding_dims=None, model_card=None, max_len=None, **kwargs):

        super().__init__(**kwargs)

        self.model_class = "GoogleEmbeddingModel"
        self.model_category = "embedding"

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

        self.text_sample = None

        self.post_init()

    def set_api_key(self, api_key, env_var="USER_MANAGED_GOOGLE_API_KEY"):

        """ Utility method to set the API key in os.environ variable. """

        os.environ[env_var] = api_key
        logger.info("update: added and stored GOOGLE api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_GOOGLE_API_KEY"):

        """ Utility method to get api_key from os.environ variable. """

        self.api_key = os.environ.get(env_var)
        return self.api_key

    def token_counter(self, text_sample):

        """ Gets GPT2 tokenizer for fast approximate token counting. """

        tokenizer = Utilities().get_default_tokenizer()
        toks = tokenizer.encode(text_sample).ids
        return len(toks)

    def embedding(self,text_sample, api_key= None):

        """ Executes Embedding inference on Model. """

        self.text_sample = text_sample

        #   call to preview (not implemented by default)
        self.preview()

        if api_key:
            self.api_key = api_key

        if not self.api_key:
            self.api_key = self._get_api_key()

        if not self.api_key:
            logger.error("error: invoking Google Embedding model with no api_key")

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

            if isinstance(self.text_sample,list):
                text_list = self.text_sample
            else:
                text_list = [self.text_sample]

            # need to batch the text list
            # Google appears to set a cap of 5 text samples per embedding inference call

            google_max_samples_per_inference = 5

            batch_count = len(text_list) // google_max_samples_per_inference
            if batch_count * google_max_samples_per_inference < len(text_list):
                batch_count += 1

            for x in range(0, batch_count):
                new_batch = text_list[x*google_max_samples_per_inference:
                                      min((x+1)*google_max_samples_per_inference, len(text_list))]

                logger.debug("update: new batch - %s - %s ", x, len(new_batch))

                embeddings_from_google = model.get_embeddings(new_batch)

                for i, embedding in enumerate(embeddings_from_google):
                    embeddings_output.append(np.array(embedding.values))

        except Exception as e:
            # raise LLMInferenceResponseException(e)
            logger.error("error: Google model inference produced error - %s ", e)

        finally:
            os.remove(google_json_credentials)

        self.register()

        return embeddings_output

    def api_key_to_json(self):

        # Google authentication key is an entire json dictionary which we have the user pass in as an env var
        # We write out the json and we need to escape newlines which seem to be always present in
        # google auth json files

        temp_json_path = tempfile.NamedTemporaryFile(prefix="googlecreds", delete=False).name
        with open(temp_json_path, "w", encoding='utf-8') as f:
            f.write(self.api_key.replace("\n", "\\n"))
        return temp_json_path


class HFReRankerModel(BaseModel):

    """HFReRankerModel class implements the interface for HuggingFace ReRanker models. """

    def __init__(self, model=None, tokenizer=None, model_name=None, api_key=None, model_card=None,
                 embedding_dims=None, trust_remote_code=False, use_gpu_if_available=True, max_len=None, **kwargs):

        super().__init__(**kwargs)

        self.model_class = "HFReRankerModel"
        self.model_category = "reranker"

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

        # insert dynamic pytorch load here
        global GLOBAL_TORCH_IMPORT
        if not GLOBAL_TORCH_IMPORT:

            logger.debug("update: ModelCatalog - HFReRankerModel - local dynamic load of torch here")
            if util.find_spec("torch"):

                try:
                    global torch
                    torch = importlib.import_module("torch")
                    GLOBAL_TORCH_IMPORT = True
                except:
                    raise LLMWareException(message="Exception: could not load torch module.")

            else:
                raise LLMWareException(message="Exception: need to import torch to use this class.")

        # end dynamic import here

        if self.model_name and not model:

            # pull from HF
            hf_repo_name = self.model_name

            if not self.model_card:
                self.model_card = ModelCatalog().lookup_model_card(model_name)

            if self.model_card:
                if "hf_repo" in self.model_card:
                    hf_repo_name = self.model_card["hf_repo"]

            pt_loader = PyTorchLoader(api_key=api_key,trust_remote_code=trust_remote_code,custom_loader=None)

            self.model=pt_loader.get_reranker_model(hf_repo_name)
            self.tokenizer=None

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

        self.query = ""
        self.text_results = None

        self.post_init()

    def set_api_key(self, api_key, env_var="USER_MANAGED_HF_API_KEY"):

        """ Sets the API key - generally not needed for public HF repositories. """

        os.environ[env_var] = api_key
        logger.info("update: added and stored HF api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_HF_API_KEY"):

        """ Gets API key from os.environ variable. """

        self.api_key = os.environ.get(env_var)

        if not self.api_key:
            logger.error("error: _get_api_key could not successfully retrieve value from: %s ", env_var)

        return self.api_key

    def token_counter(self, text_sample):

        """ Counts tokens in text sample. Not currently implemented. """

        return -1

    def inference (self, query, text_results, api_key=None, top_n=20, relevance_threshold=None, min_return=3):

        """ Executes reranking inference. """

        self.query = query
        self.text_results = text_results

        #   call to preview (not implemented by default)
        self.preview()

        documents = []
        for i, chunks in enumerate(text_results):
            documents.append(chunks['text'])

        sentence_pairs = [[self.query, doc] for doc in documents]

        scores = self.model.compute_score(sentence_pairs)

        output = []
        for i, score in enumerate(scores):
            text_results[i].update({"rerank_score": score})
            output.append(text_results[i])

        ranked_output = sorted(output, key=lambda x: x["rerank_score"], reverse=True)

        #   will return top_n if no relevance threshold set
        if not relevance_threshold:
            if top_n < len(ranked_output):
                final_output = ranked_output[0:top_n]
            else:
                final_output = ranked_output
        else:
            final_output = []
            #   if relevance threshold, will return all results above threshold
            for entries in ranked_output:
                if entries["rerank_score"] >= relevance_threshold:
                    final_output.append(entries)

            #   fallback, if no result above threshold, then will return the min number of results
            if len(final_output) == 0:
                final_output = ranked_output[0:min_return]

        self.register()

        return final_output


class HFEmbeddingModel(BaseModel):

    """HFEmbeddingModel class implements the API for HuggingFace embedding models. """

    def __init__(self, model=None, tokenizer=None, model_name=None, api_key=None, model_card=None,
                 embedding_dims=None, trust_remote_code=False, use_gpu_if_available=True, max_len=None, **kwargs):

        super().__init__(**kwargs)

        self.model_class = "HFEmbeddingModel"
        self.model_category = "embedding"

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

        # insert dynamic pytorch load here
        global GLOBAL_TORCH_IMPORT
        if not GLOBAL_TORCH_IMPORT:

            logger.debug("update: ModelCatalog - HFEmbeddingModel - local dynamic load of torch here")
            if util.find_spec("torch"):

                try:
                    global torch
                    torch = importlib.import_module("torch")
                    GLOBAL_TORCH_IMPORT = True
                except:
                    raise LLMWareException(message="Exception: could not load torch module.")

            else:
                raise LLMWareException(message="Exception: need to import torch to use this class.")

        # end dynamic import here

        if self.model_name and not model:

            # pull from HF
            hf_repo_name = self.model_name

            if not self.model_card:
                self.model_card = ModelCatalog().lookup_model_card(model_name)

            if self.model_card:
                if "hf_repo" in self.model_card:
                    hf_repo_name = self.model_card["hf_repo"]

            pt_loader = PyTorchLoader(api_key=api_key,trust_remote_code=trust_remote_code,custom_loader=None)

            self.model=pt_loader.get_embedding_model(hf_repo_name)
            self.tokenizer=pt_loader.get_tokenizer(hf_repo_name)

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

        self.text_sample = None

        self.post_init()

    def set_api_key(self, api_key, env_var="USER_MANAGED_HF_API_KEY"):

        """ Sets the API key - generally not needed for public HF repositories. """

        os.environ[env_var] = api_key
        logger.info("update: added and stored HF api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_HF_API_KEY"):

        """ Gets API key from os.environ variable. """

        self.api_key = os.environ.get(env_var)

        if not self.api_key:
            logger.error("error: _get_api_key could not successfully retrieve value from: %s ", env_var)

        return self.api_key

    def token_counter(self, text_sample):

        """ Counts tokens in text sample. """

        #   need to support HF tokenizer
        toks = self.tokenizer.encode(text_sample).ids
        return len(toks)

    def embedding (self, text_sample, api_key=None):

        """ Executes embedding inference. """

        self.text_sample = text_sample

        #   call to preview (not implemented by default)
        self.preview()

        # return embeddings only
        if isinstance(self.text_sample,list):
            sequence = self.text_sample

        else:
            sequence = [self.text_sample]

        model_inputs = self.tokenizer(sequence, truncation=True, max_length=self.max_len, return_tensors="pt",padding=True)

        if self.use_gpu:
            input_ids = model_inputs.input_ids.to('cuda')
            attn_mask = model_inputs.attention_mask.to('cuda')
        else:
            input_ids = model_inputs.input_ids.to('cpu')
            attn_mask = model_inputs.attention_mask.to('cpu')

        #   context manager to run inference without saving/calculating grads
        with torch.no_grad():
            model_outputs = self.model(input_ids, attention_mask=attn_mask)

        embedding = model_outputs.last_hidden_state[:,0]

        # normalize hf embeddings
        embeddings_normalized = torch.nn.functional.normalize(embedding, p=2, dim=1)

        if self.use_gpu:
            embeddings_normalized = np.array(embeddings_normalized.detach().to('cpu'))
        else:
            embeddings_normalized = embeddings_normalized.detach().numpy()

        self.register()

        return embeddings_normalized


class HFGenerativeModel(BaseModel):

    """ HFGenerativeModel class implements the HuggingFace generative model API, and is used generally for
     models in HuggingFace repositories, e.g., Dragon, Bling, etc. """

    #   support instantiating HF model in two different ways:
    #       1.  directly passing a previously loaded HF model object and tokenizer object
    #       2.  passing a model_name only, which will then create the model and tokenizer

    def __init__(self, model=None, tokenizer=None, model_name=None, api_key=None, model_card=None,
                 prompt_wrapper=None, instruction_following=False, context_window=2048,
                 use_gpu_if_available=True, trust_remote_code=True, sample=True,max_output=100, temperature=0.3,
                 get_logits=False, api_endpoint=None, **kwargs):

        super().__init__(**kwargs)

        self.model_class = "HFGenerativeModel"
        self.model_category = "generative"
        self.llm_response = None
        self.usage = None
        self.logits = None
        self.output_tokens = None
        self.final_prompt = None

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

        # insert dynamic pytorch load here
        if not api_endpoint:

            global GLOBAL_TORCH_IMPORT
            if not GLOBAL_TORCH_IMPORT:
                if util.find_spec("torch"):

                    try:
                        global torch
                        torch = importlib.import_module("torch")
                        GLOBAL_TORCH_IMPORT = True
                    except:
                        raise LLMWareException(message="Exception: could not load torch module.")

                else:
                    raise LLMWareException(message="Exception: need to import torch to use this class.")

        # end dynamic import here

        # instantiate if model_name passed without actual model and tokenizer
        if model_name and not model and not tokenizer and not api_endpoint:

            hf_repo_name = self.model_name

            if not self.model_card:
                self.model_card = ModelCatalog().lookup_model_card(self.model_name)

            if self.model_card:
                if "hf_repo" in self.model_card:
                    hf_repo_name = self.model_card["hf_repo"]
                    self.hf_tokenizer_name = hf_repo_name

            pt_loader = PyTorchLoader(api_key=api_key, trust_remote_code=trust_remote_code, custom_loader=None)
            self.model = pt_loader.get_generative_model(hf_repo_name)
            self.tokenizer = pt_loader.get_tokenizer(hf_repo_name)

            # set to defaults for HF models in Model Catalog
            # this can be over-ridden post initiation if needed for custom models
            self.prompt_wrapper = "human_bot"
            self.instruction_following = False

        # set specific parameters associated with custom models
        # note - these two parameters will control how prompts are handled - model-specific
        self.prompt_wrapper = prompt_wrapper
        self.instruction_following = instruction_following

        if not model_card:
            # safety - empty iterable rather than 'None'
            model_card = []

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
        if not api_endpoint:
            self.use_gpu = torch.cuda.is_available() and use_gpu_if_available
        else:
            self.use_gpu = False

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
                logger.debug("update: HFGenerative loading - moving model to cuda")

        else:
            if not api_endpoint:
                logger.error("error: HFGenerativeModel - could not identify model  - ", model_name)

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
        self.prompt = ""
        self.context = ""
        self.tool_type = None

        self.api_endpoint = api_endpoint

        self.post_init()

    def set_api_key(self, api_key, env_var="USER_MANAGED_HF_API_KEY"):

        """ Sets the API key - generally not needed for public HF repositories. """

        os.environ[env_var] = api_key
        logger.info("update: added and stored HF api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_HF_API_KEY"):

        """ Gets API key from os.environ variable. """

        self.api_key = os.environ.get(env_var)

        if not self.api_key:
            logger.error("error: _get_api_key could not successfully retrieve value from: %s ", env_var)

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

    def inference(self, prompt, add_context=None, add_prompt_engineering=None, api_key=None,
                  inference_dict=None):

        """ Executes generation inference on model. """

        self.prompt = prompt

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
            logger.warning("warning: this is a function calling model - using .inference may lead to unexpected "
                            "results.   Recommended to use the .function_call method to ensure correct prompt "
                            "template packaging.")

        if inference_dict:

            if "temperature" in inference_dict:
                self.temperature = inference_dict["temperature"]

            if "max_tokens" in inference_dict:
                self.target_requested_output_tokens = inference_dict["max_tokens"]

        #   call to preview (not implemented by default)
        self.preview()

        #   START - route to api endpoint
        if self.api_endpoint:
            return self.inference_over_api_endpoint(self.prompt, context=self.add_context,
                                                    inference_dict=inference_dict)
        #   END - route to api endpoint

        text_prompt = self.prompt

        if self.add_prompt_engineering:
            prompt_enriched = self.prompt_engineer(self.prompt, self.add_context, inference_dict=inference_dict)
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

        #   This simplified greedy sampling generation loop was derived from and inspired by ideas in the
        #   HuggingFace transformers library generation class.
        #   https: //github.com/huggingface/transformers/tree/main/src/transformers/generation
        #   Copyright 2018 The Google AI Language Team Authors and The HuggingFace Inc.team, and NVIDIA Corporation.
        #   Licensed under the Apache License, Version 2.0 (the "License")

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

        # borrow setting from GGUFConfigs
        get_first_token_speed = GGUFConfigs().get_config("get_first_token_speed")
        t_gen_start = time.time()
        first_token_processing_time = -1.0

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

            #   context manager to avoid saving/computing grads in forward pass
            with torch.no_grad():
                outputs = self.model(input_ids=inp0, attention_mask=inp1, past_key_values=pkv,
                                     return_dict=True)

            if new_tokens_generated == 0:
                if get_first_token_speed:
                    first_token_processing_time = time.time() - t_gen_start

            new_tokens_generated += 1

            next_token_logits = outputs.logits[:, -1, :]

            # capture top logits - not currently activated for inference
            # self.register_top_logits(next_token_logits)
            # shape of next_token_logits = torch.Size([1, 32000])
            # logger.debug(f"next token logits shape - {next_token_logits.shape}")

            if self.temperature and self.sample:
                next_token_scores = next_token_logits / self.temperature
            else:
                next_token_scores = next_token_logits

            # get token from logits
            probs = torch.nn.functional.softmax(next_token_scores, dim=-1)

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

                    next_tokens_np = np.array(next_tokens)

                self.output_tokens.append(next_tokens_np[0])

            # finished sentences should have their next token be a padding token
            if eos_token_id is not None:
                next_tokens = next_tokens * unfinished_sequences + pad_token_id * (1 - unfinished_sequences)

            # update generated ids, model inputs, and length for next step
            input_ids = torch.cat([input_ids, next_tokens[:, None]], dim=-1)

            #   testing output in progress starts here
            """
            logger.debug(f"update: input_ids - {input_ids}")
            # outputs_detached = outputs.to('cpu')
            outputs_np = np.array(input_ids[0])
            output_str = self.tokenizer.decode(outputs_np)
            logger.debug(f"update: output string - {output_str}")
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

        if get_first_token_speed:
            usage.update({"first_token_processing_time": first_token_processing_time})

        output_response = {"llm_response": output_str, "usage": usage}

        if self.get_logits:
            output_response.update({"logits": self.logits_record})
            output_response.update({"output_tokens": self.output_tokens})
            self.logits = self.logits_record

        # output inference parameters
        self.llm_response = output_str
        self.usage = usage
        self.final_prompt = text_prompt

        self.register()

        return output_response

    def fc_prompt_engineer(self, context, params=None, function=None):

        """ Prompt engineering for Function Call prompts. """

        if not params:
            params = self.primary_keys

        #   add safety check in looking for default self.function pulled from model card
        if not function:
            if self.function:
                if isinstance(self.function,list):
                    if len(self.function) > 0:
                        function = self.function[0]
                else:
                    function = self.function

        #   if not successful identifying a function, then choose 'classify' by default
        if not function:
            function = "classify"

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

    def function_call(self, context, function=None, params=None, get_logits=True,
                      temperature=-99, max_output=None):

        """ This is the key inference method for SLIM models - takes a context passage and a key list
        which is packaged in the prompt as the keys for the dictionary output"""

        self.context = context

        #   only assign self.function if a function has been passed in the call
        if function:
            self.function = function

        if not self.fc_supported:
            logger.warning("HFGenerativeModel - loaded model does not support function calls.  "
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

        #   call to preview (not implemented by default)
        self.preview()

        if not self.primary_keys:
            logger.warning("warning: function call - no keys provided - function call may yield unpredictable results")

        #   START - route to api endpoint

        if self.api_endpoint:
            return self.function_call_over_api_endpoint(model_name=self.model_name,
                                                        context=self.context,params=self.primary_keys,
                                                        function=self.function,
                                                        api_key=self.api_key,get_logits=self.get_logits)

        #   END - route to api endpoint

        prompt = self.fc_prompt_engineer(self.context, params=self.primary_keys, function=self.function)

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

        #   This simplified greedy sampling generation loop was derived from and inspired by ideas in the
        #   HuggingFace transformers library generation class.
        #   https: //github.com/huggingface/transformers/tree/main/src/transformers/generation
        #   Copyright 2018 The Google AI Language Team Authors and The HuggingFace Inc.team, and NVIDIA Corporation.
        #   Licensed under the Apache License, Version 2.0 (the "License")

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

            with torch.no_grad():
                outputs = self.model(input_ids=inp0, attention_mask=inp1, past_key_values=pkv, return_dict=True)

            new_tokens_generated += 1

            next_token_logits = outputs.logits[:, -1, :]

            # option to capture logits for analysis
            # if self.get_logits: self.register_top_logits(next_token_logits)

            if self.temperature and self.sample:
                next_token_scores = next_token_logits / self.temperature
            else:
                next_token_scores = next_token_logits

            # get token from logits
            probs = torch.nn.functional.softmax(next_token_scores, dim=-1)

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
            logger.debug(f"update: input_ids - {input_ids}")
            # outputs_detached = outputs.to('cpu')
            outputs_np = np.array(input_ids[0])
            output_str = self.tokenizer.decode(outputs_np)
            logger.debug(f"update: output string - {output_str}")
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
                logger.warning("update: automatic conversion of function call output failed, and attempt to "
                                "remediate was not successful - %s ", output_str)
            else:
                logger.info("update: function call output could not be automatically converted, but remediation "
                                "was successful to type - %s ", output_type)

        # INSERT ENDS HERE

        output_response = {"llm_response": output_value, "usage": usage}

        if get_logits:
            output_response.update({"logits": self.logits_record})
            output_response.update({"output_tokens": self.output_tokens})
            self.logits = self.logits_record

        # output inference parameters
        self.llm_response = output_value
        self.usage = usage
        self.final_prompt = prompt

        self.register()

        return output_response

    def inference_over_api_endpoint(self, prompt, context=None, inference_dict=None, get_logits=False):

        """ Called by .inference method when there is an api_endpoint passed in the model constructor. Rather
        than execute the inference locally, it will be sent over API to inference server. """

        self.prompt=prompt
        self.context=context

        #   preview call before invoking inference over rest api
        self.preview()

        import ast
        import requests

        url = self.api_endpoint + "{}".format("/")
        output_raw = requests.post(url, data={"model_name": self.model_name,
                                              "question": self.prompt,
                                              "context": self.context,
                                              "api_key": self.api_key,
                                              "max_output": self.max_output,
                                              "temperature": self.temperature})

        try:

            output = json.loads(output_raw.text)

            #   will attempt to unpack logits - but catch any exceptions and skip
            if "logits" in output:
                try:
                    logits = ast.literal_eval(output["logits"])
                    output["logits"] = logits
                except:
                    output["logits"] = []

            #   will attempt to unpack output tokens - but catch any exceptions and skip
            if "output_tokens" in output:
                try:
                    # ot_int = [int(x) for x in output["output_tokens"]]
                    # output["output_tokens"] = ot_int
                    output_tokens = ast.literal_eval(output["output_tokens"])
                    output["output_tokens"] = output_tokens
                except:
                    output["output_tokens"] = []

        except:
            logger.warning("warning: api inference was not successful")
            output = {"llm_response": "api-inference-error", "usage": {}}

        # output inference parameters
        self.llm_response = output["llm_response"]
        self.usage = output["usage"]
        self.final_prompt = prompt

        if "logits" in output:
            self.logits = output["logits"]
        if "output_tokens" in output:
            self.output_tokens = output["output_tokens"]

        self.register()

        return output

    def function_call_over_api_endpoint(self, context="", tool_type="", model_name="", params="", prompt="",
                                        function=None, endpoint_base=None, api_key=None, get_logits=False):

        """ Called by .function_call method when there is an api_endpoint passed in the model constructor. Rather
        than execute the inference locally, it will be sent over API to inference server. """

        self.context = context
        self.tool_type = tool_type
        self.model_name = model_name

        #   send to api agent server

        import ast
        import requests

        if endpoint_base:
            self.api_endpoint = endpoint_base

        if api_key:
            # e.g., "demo-test"
            self.api_key = api_key

        if not params:
            self.model_name = _ModelRegistry().get_llm_fx_mapping()[tool_type]
            mc = ModelCatalog().lookup_model_card(self.model_name)
            if "primary_keys" in mc:
                params = mc["primary_keys"]
                self.primary_keys = params

        if function:
            self.function = function

        self.prompt = prompt

        #   preview before invoking rest api
        self.preview()

        url = self.api_endpoint + "{}".format("/agent")
        output_raw = requests.post(url, data={"model_name": self.model_name, "api_key": self.api_key,
                                              "tool_type": self.tool_type,
                                              "function": self.function,
                                              "params": self.primary_keys, "max_output": 50,
                                              "temperature": 0.0, "sample": False, "prompt": self.prompt,
                                              "context": self.context, "get_logits": True})

        try:
            # output = ast.literal_eval(output_raw.text)
            output = json.loads(output_raw.text)
            if "logits" in output:
                logits = ast.literal_eval(output["logits"])
                output["logits"] = logits

            if "output_tokens" in output:
                ot_int = [int(x) for x in output["output_tokens"]]
                output["output_tokens"] = ot_int

            # need to clean up logits
        except:
            logger.warning("warning: api inference was not successful")
            output = {}

        logger.info(f"TEST: executed Agent call over API endpoint - {model_name} - {function} - {output}")

        # output inference parameters
        self.llm_response = output["llm_response"]
        self.usage = output["usage"]
        self.final_prompt = prompt

        if "logits" in output:
            self.logits = output["logits"]
        if "output_tokens" in output:
            self.output_tokens = output["output_tokens"]

        self.register()

        return output


class GGUFGenerativeModel(BaseModel):

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
                 sample=True,max_output=100, temperature=0.3, api_endpoint=None, **kwargs):

        super().__init__(**kwargs)

        self.model_class = "GGUFGenerativeModel"
        self.model_category = "generative"
        self.llm_response = None
        self.usage = None
        self.logits = None
        self.output_tokens = None
        self.prompt = None
        self.final_prompt = None

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
            logger.warning(f"update: requested output len - {max_output} > {gguf_configs_max}, which is the "
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

        #   new option to 'force' use of cuda lib, and over-ride safety checks
        if GGUFConfigs().get_config("force_gpu"):
            self.use_gpu = True
        else:
            if sys.platform.lower() not in GGUFConfigs().get_config("cuda_platforms"):
                self.use_gpu = False
            else:
                # min drivers set to the lowest level for CUDA 12.1 on Linux
                min_drivers = [525,60]
                if sys.platform.lower() == "win32":
                    min_drivers = GGUFConfigs().get_config("cuda_windows_driver_min")

                gpu_available = ModelCatalog().gpu_available(driver_min_levels=min_drivers)

                #   use_gpu set to TRUE only if:
                #   (1) cuda_platform (e.g., linux or win32), e.g., not set on Mac OS
                #   (2) use_gpu set to True in GGUFConfigs
                #   (3) use_gpu_if_available flag set to True (by default)
                #   (4) cuda found and drivers current via direct polling of nvidia-smi executable in
                #   ModelCatalog.gpu_available method

                self.use_gpu = (GGUFConfigs().get_config("use_gpu")
                            and sys.platform.lower() in GGUFConfigs().get_config("cuda_platforms")
                            and gpu_available["drivers_current"] and gpu_available["gpu_found"]
                            and use_gpu_if_available)

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
        self.api_endpoint = api_endpoint

        self.error_message = "\nUnable to identify and load GGUF Generative model."

        self.prompt = ""
        self.context = ""
        self.tool_type = None

        self.model_repo_path = None

        self.post_init()

    def load_model_for_inference(self, model_repo_path, model_card = None, **kwargs):

        """ Loads and instantiates model along with other required objects. """

        self.model_repo_path = model_repo_path

        if model_card:
            self.model_card = model_card

        #   validate before loading
        self.validate()

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

        #   sets minimum of 2048, but will extend if context_window is larger (e.g., 4096/8192+)
        self.context_params.n_ctx = max(2048, self.max_total_len)

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

                    if GGUFConfigs().get_config("use_macos_accelerate"):

                        try:
                            import platform
                            macos_ver = platform.mac_ver()
                            if len(macos_ver) > 0:
                                ver = macos_ver[0].split(".")

                                v1 = int(ver[0])
                                v2 = int(ver[1])

                                if v1 < 14:

                                    logger.warning(f"warning: detected older version of macos - {macos_ver} - "
                                                    f"which may produce errors related to the Accelerate framework.\n"
                                                    f"To remove this warning: (1) upgrade to Sonoma (>14.0) or \n(2) set "
                                                    f"GGUF configs to use non Accelerate binary by default:\n"
                                                    f"GGUFConfigs().set_config('use_macos_accelerate', False)")

                        except:
                            pass

                        _lib_paths.append(os.path.join(_base_path, GGUFConfigs().get_config("mac_metal")))

                        fall_back_option = os.path.join(_base_path, GGUFConfigs().get_config("mac_metal_no_acc"))

                    else:
                        _lib_paths.append(os.path.join(_base_path, GGUFConfigs().get_config("mac_metal_no_acc")))

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

                            logger.warning("update: Not successful loading GPU-accelerated lib, "
                                           "so reverting to CPU driver.")

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
            logger.warning("update: GGUFGenerativeModel - input is too long for model context window - truncating")
            min_output_len = 10
            prompt_tokens = prompt_tokens[0:context_window-min_output_len]
            input_len = len(prompt_tokens)

        text = b""

        # first token capture starts here
        get_first_token_speed = GGUFConfigs().get_config("get_first_token_speed")

        token_counter = 0
        t_gen_start = time.time()
        first_token_processing_time = -1.0

        for token in self.generate(prompt_tokens):

            # first token capture
            if get_first_token_speed:
                if token_counter == 0:
                    first_token_processing_time = time.time() - t_gen_start
                    token_counter += 1
            # first token capture ends here

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

        if get_first_token_speed:

            output = {"llm_response": text_str,
                      "usage": {"input": len(prompt_tokens),"output": len(completion_tokens),
                                "total": len(prompt_tokens) + len(completion_tokens), "metric": "tokens",
                                "processing_time": time.time() - t0,
                                "first_token_processing_time": first_token_processing_time}}
        else:
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

                #logger.debug("token: {token}")

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
                    logger.info("update: GGUFGenerativeModel - stopping generation loop - reached limit of max output len")
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
        logger.info("update: added and stored GGUF api_key in environmental variable- %s", env_var)

        return self

    def _get_api_key(self, env_var="USER_MANAGED_GGUF_API_KEY"):

        """ Gets API key - generally not used in GGUF models. """

        self.api_key = os.environ.get(env_var)

        if not self.api_key:
            logger.error("error: _get_api_key could not successfully retrieve value from: %s ", env_var)

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

        self.prompt = prompt

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
            logger.warning("warning: this is a function calling model - using .inference may lead to unexpected "
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

        #   preview before initiating inference over api
        self.preview()

        #   START - route to api endpoint
        if self.api_endpoint:
            return self.inference_over_api_endpoint(self.prompt, context=self.add_context,
                                                    inference_dict=inference_dict)
        #   END - route to api endpoint

        text_prompt = self.prompt

        if self.add_prompt_engineering:
            prompt_enriched = self.prompt_engineer(self.prompt, self.add_context, inference_dict=inference_dict)
            prompt_final = prompt_enriched

            # text_prompt = prompt_final + "\n"

            # most models perform better with no trailing space or line-break at the end of prompt
            #   -- in most cases, the trailing space will be ""
            #   -- yi model prefers a trailing "\n"
            #   -- keep as parameterized option to maximize generation performance
            #   -- can be passed either thru model_card or model config from HF

            text_prompt = prompt_final + self.trailing_space

        output_response = self._inference(text_prompt)

        #   update linked to BaseModel
        self.prompt = prompt
        self.final_prompt = text_prompt
        self.usage = output_response["usage"]
        self.llm_response = output_response["llm_response"]

        if "logits" in output_response:
            self.logits = output_response["logits"]

        self.register()
        #   end - update

        return output_response

    def function_call(self, context, function=None, params=None, get_logits=True,
                      temperature=-99, max_output=None):

        """ This is the key inference method for SLIM models - takes a context passage and a key list
        which is packaged in the prompt as the keys for python dictionary output"""

        if not self.fc_supported:
            logger.warning("warning: GGUFGenerativeModel - loaded model does not support function calls.  "
                            "Please either use the standard .inference method with this model, or use a GGUF "
                            "model that has 'function_calls' key set to True in its model card.")
            return []

        self.context=context

        # start with clean logits_record and output_tokens for each function call
        self.logits_record = []
        self.output_tokens = []

        if get_logits:
            self.get_logits = get_logits

        if params:
            self.primary_keys = params

        if not self.primary_keys:
            logger.warning("warning: GGUF - function call - no keys provided - "
                            "function call may yield unpredictable results")

        if not params:
            params = self.primary_keys

        if not function:
            #   pull from model card
            if self.function:
                if isinstance(self.function,list):
                    if len(self.function) > 0:
                        function = self.function[0]
                else:
                    function = self.function

            if not function:
                function = "classify"

        self.primary_keys = params
        self.function = function

        #   preview before initiating api call
        self.preview()

        #   START - route to api endpoint

        if self.api_endpoint:
            return self.function_call_over_api_endpoint(model_name=self.model_name,
                                                        context=self.context,params=self.primary_keys,
                                                        function=self.function,
                                                        api_key=self.api_key,get_logits=self.get_logits)

        #   END - route to api endpoint

        # prepare SLIM prompt
        class_str = ""
        for key in params:
            class_str += str(key) + ", "
        if class_str.endswith(", "):
            class_str = class_str[:-2]

        f = str(self.function)

        full_prompt = "<human>: " + self.context + "\n" + "<{}> {} </{}>".format(f, class_str, f) + "\n<bot>:"
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
                logger.warning("update: automatic conversion of function call output failed, and attempt to "
                                "remediate was not successful - %s ", output_str)
            else:
                logger.info("update: function call output could not be automatically converted, but remediation "
                                "was successful to type - %s ", output_type)

        #   update linked to BaseModel
        self.prompt = ""
        self.final_prompt = full_prompt
        self.usage = output_response["usage"]
        self.llm_response = output_response["llm_response"]

        if "logits" in output_response:
            self.logits = output_response["logits"]

        self.register()
        #   end - update

        return output_response

    def stream(self, prompt, add_context=None, add_prompt_engineering=None, api_key=None, inference_dict=None,
                  get_logits=False, disable_eos=False):

        """ Main method for text streaming generation. Returns a generator function that yields one
        token at a time for real-time streaming to console or UI. """

        # first prepare the prompt

        self.prompt = prompt

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
            logger.warning("warning: this is a function calling model - using .inference may lead to unexpected "
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

        #   preview before generation
        self.preview()

        # prompt = prompt

        if self.add_prompt_engineering:
            prompt_enriched = self.prompt_engineer(self.prompt, self.add_context, inference_dict=inference_dict)
            prompt_final = prompt_enriched

            # most models perform better with no trailing space or line-break at the end of prompt
            #   -- in most cases, the trailing space will be ""
            #   -- yi model prefers a trailing "\n"
            #   -- keep as parameterized option to maximize generation performance
            #   -- can be passed either thru model_card or model config from HF

            prompt = prompt_final + self.trailing_space

        # output_response = self._inference(text_prompt)

        #   starts _inference here
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
            logger.warning("update: GGUFGenerativeModel - input is too long for model context window - truncating")
            min_output_len = 10
            prompt_tokens = prompt_tokens[0:context_window-min_output_len]
            input_len = len(prompt_tokens)

        text = b""

        # disable_eos = True

        for token in self.generate(prompt_tokens):

            completion_tokens.append(token)

            if not disable_eos:
                if token == self._token_eos:
                    break

            if len(completion_tokens) > self.max_output_len:
                break

            #   stop if combined input + output at context window size
            if (input_len + len(completion_tokens)) >= context_window:
                break

            new_token = self.detokenize([token]).decode('utf-8',errors='ignore')

            yield new_token

        text_str = text.decode("utf-8", errors="ignore")

        #   turned off
        #   self.register()

        return text_str

    def function_call_over_api_endpoint(self, context="", tool_type="", model_name="", params="", prompt="",
                                        function=None, endpoint_base=None, api_key=None, get_logits=False):

        """ Called by .function_call method when there is an api_endpoint passed in the model constructor. Rather
        than execute the inference locally, it will be sent over API to inference server. """

        #   send to api agent server

        self.context=context
        self.tool_type=tool_type

        import ast
        import requests

        if endpoint_base:
            self.api_endpoint = endpoint_base

        if api_key:
            # e.g., "demo-test"
            self.api_key = api_key

        if not params:
            self.model_name = _ModelRegistry().get_llm_fx_mapping()[tool_type]
            mc = ModelCatalog().lookup_model_card(self.model_name)
            if "primary_keys" in mc:
                params = mc["primary_keys"]

        if function:
            self.function = function

        self.prompt = prompt

        self.primary_keys = params

        #   preview before invoking api
        self.preview()

        url = self.api_endpoint + "{}".format("/agent")
        output_raw = requests.post(url, data={"model_name": self.model_name, "api_key": self.api_key,
                                              "tool_type": self.tool_type,
                                              "function": self.function, "params": self.primary_keys,
                                              "max_output": 50,
                                              "temperature": 0.0, "sample": False, "prompt": self.prompt,
                                              "context": self.context, "get_logits": True})

        try:

            output = json.loads(output_raw.text)

            #   will attempt to unpack logits - but catch any exceptions and skip
            if "logits" in output:
                try:
                    logits = ast.literal_eval(output["logits"])
                    output["logits"] = logits
                except:
                    output["logits"] = []

            #   will attempt to unpack output tokens - but catch any exceptions and skip
            if "output_tokens" in output:
                try:
                    ot_int = [int(x) for x in output["output_tokens"]]
                    output["output_tokens"] = ot_int
                    # output_tokens = ast.literal_eval(output["output_tokens"])
                    # output["output_tokens"] = output_tokens
                except:
                    output["output_tokens"] = []

            # output = ast.literal_eval(output_raw.text)
            """
            output = json.loads(output_raw.text)
            if "logits" in output:
                logits = ast.literal_eval(output["logits"])
                logger.debug(f"logits: {logits}")
                output["logits"] = logits
            if "output_tokens" in output:
                ot_int = [int(x) for x in output["output_tokens"]]
                output["output_tokens"] = ot_int
            """

        except:
            logger.warning("warning: api inference was not successful")
            output = {"llm_response": "api-inference-error", "usage": {}}

        #   update linked to BaseModel
        self.prompt = prompt
        self.final_prompt = prompt
        self.usage = output["usage"]
        self.llm_response = output["llm_response"]

        if "logits" in output:
            self.logits = output["logits"]

        self.register()
        #   end - update

        return output

    def inference_over_api_endpoint(self, prompt, context=None, inference_dict=None, get_logits=False):

        """ Called by .inference method when there is an api_endpoint passed in the model constructor. Rather
        than execute the inference locally, it will be sent over API to inference server. """

        self.prompt = prompt
        self.context = context

        #   preview before invoking inference over rest api
        self.preview()

        import ast
        import requests

        url = self.api_endpoint + "{}".format("/")
        output_raw = requests.post(url, data={"model_name": self.model_name,
                                              "question": self.prompt,
                                              "context": self.context,
                                              "api_key": self.api_key,
                                              "max_output": self.max_output_len,
                                              "temperature": self.temperature})

        try:
            output = json.loads(output_raw.text)

            #   will attempt to unpack logits - but catch any exceptions and skip
            if "logits" in output:
                try:
                    logits = ast.literal_eval(output["logits"])
                    output["logits"] = logits
                except:
                    output["logits"] = []

            #   will attempt to unpack output tokens - but catch any exceptions and skip
            if "output_tokens" in output:
                try:
                    # ot_int = [int(x) for x in output["output_tokens"]]
                    # output["output_tokens"] = ot_int
                    output_tokens = ast.literal_eval(output["output_tokens"])
                    output["output_tokens"] = output_tokens
                except:
                    output["output_tokens"] = []

        except:
            logger.warning("warning: api inference was not successful")
            output = {"llm_response": "api-inference-error", "usage": {}}

        #   update linked to BaseModel
        self.prompt = prompt
        self.final_prompt = prompt
        self.usage = output["usage"]
        self.llm_response = output["llm_response"]

        if "logits" in output:
            self.logits = output["logits"]

        self.register()
        #   end - update

        return output


class WhisperCPPModel(BaseModel):

    """ WhisperCPPModel is an implementation of the Whisper voice transcription model running on GGML, rather
    than Pytorch. """

    def __init__(self, model_name=None, model_card=None, use_gpu_if_available=True, **kwargs):

        super().__init__(**kwargs)

        self.model_class = "WhisperCPPModel"
        self.model_category = "generative"
        self.llm_response = None
        self.usage = None
        self.logits = None
        self.output_tokens = None
        self.prompt = None
        self.final_prompt = None

        #   set verbose level in environ level - will be picked up by callback in whisper_cpp
        os.environ["whisper_cpp_verbose"] = GGUFConfigs().get_config("whisper_cpp_verbose")

        self.WHISPER_SR = GGUFConfigs().get_config("whisper_sr")
        self.strategy = GGUFConfigs().get_config("whisper_strategy")
        self.n_threads = GGUFConfigs().get_config("whisper_threads")
        self.language = GGUFConfigs().get_config("whisper_language")
        self.format = GGUFConfigs().get_config("whisper_output_format")
        self.tiny_diarize = GGUFConfigs().get_config("whisper_tiny_diarize")
        self.beam_size = GGUFConfigs().get_config("whisper_beam_size")
        self.greedy_best_of = GGUFConfigs().get_config("whisper_greedy_best_of")
        self.temperature_inc = GGUFConfigs().get_config("whisper_temperature_inc")

        self.remove_segment_markers = GGUFConfigs().get_config("whisper_remove_segment_markers")
        self.model_card = model_card
        self.model_name = model_name
        self._lib = None
        self.model_path = None
        self.context = None
        self.params = None
        self.temperature = 0.0
        self.duration = 0
        self.translate = False

        #   new option to 'force' use of cuda lib, and over-ride safety checks
        if GGUFConfigs().get_config("force_gpu"):
            self.use_gpu = True
        else:
            if not sys.platform.lower().startswith("linux"):
                self.use_gpu = False
            else:
                # min drivers set to the lowest level for CUDA 12.1 on Linux
                min_drivers = [525,60]

                gpu_available = ModelCatalog().gpu_available(driver_min_levels=min_drivers)

                #   use_gpu set to TRUE only if:
                #   (1) cuda_platform (e.g., linux or win32), e.g., not set on Mac OS
                #   (2) use_gpu set to True in GGUFConfigs
                #   (3) use_gpu_if_available flag set to True (by default)
                #   (4) cuda found and drivers current via direct polling of nvidia-smi executable in
                #   ModelCatalog.gpu_available method

                self.use_gpu = (GGUFConfigs().get_config("use_gpu")
                            and sys.platform.lower() in GGUFConfigs().get_config("cuda_platforms")
                            and gpu_available["drivers_current"] and gpu_available["gpu_found"]
                            and use_gpu_if_available)

        self.model_repo_path = None

        self.post_init()

    def load_model_for_inference(self, model_repo_path, model_card = None, **kwargs):

        """ Loads and instantiates model along with other required objects. """

        self.model_repo_path = model_repo_path
        if model_card:
            self.model_card = model_card

        #   validate before loading
        self.validate()

        # load shared library
        self._lib = self._load_shared_library()
        self._lib = self.add_ctypes_configs()

        self._lib.whisper_log_set(whisper_log_callback, ctypes.c_void_p(0))

        if model_card:
            self.model_name = model_card["model_name"].split("/")[-1]
            self.gguf_file = model_card["gguf_file"]  # e.g., "ggml-model-q4_k_m.gguf",
            self.gguf_repo = model_card["gguf_repo"]  # e.g., "llmware/dragon-mistral-7b-v0-gguf"

        self.model_path = os.path.join(model_repo_path, self.gguf_file)
        self.context = self._lib.whisper_init_from_file(self.model_path.encode('utf-8'))
        self.params = self._lib.whisper_full_default_params(self.strategy)

        self.params.n_threads = self.n_threads
        self.params.print_special = True
        self.params.print_progress = False

        # set to True by default - will display in 'real-time' the transcription
        self.params.print_realtime = GGUFConfigs().get_config("whisper_cpp_realtime_display")

        self.params.print_timestamps = True
        self.params.tdrz_enable = self.tiny_diarize
        self.params.progress_callback = whisper_progress_callback(self.callback)
        self.params.temperature_inc = self.temperature_inc
        self.params.token_timestamps = True
        self.params.greedy.best_of = self.greedy_best_of
        self.params.beam_search.beam_size = self.beam_size

        return self

    def _load_shared_library(self):

        """ Loads the libwhisper.cpp backend GGML engine that runs the model. """

        # check first if custom_lib_path - expected to be full path to custom so/dylib file
        custom_path = GGUFConfigs().get_config("whisper_cpp_lib_path")
        fall_back_option = ""
        cdll_args = dict()

        if custom_path:

            if os.path.exists(custom_path):
                _lib_paths = [custom_path]
            else:
                raise ModuleNotFoundException("custom-whisper-cpp-lib")

        else:

            # general case - will look for llama.cpp dynamic library included with llmware

            _base_path = os.path.join(LLMWareConfig.get_config("shared_lib_path"), "whisper")

            _lib_paths = []

            system_platform = sys.platform.lower()

            # Determine the file extension based on the platform
            if system_platform.startswith("linux"):

                if self.use_gpu:
                    _lib_paths.append(os.path.join(_base_path, GGUFConfigs().get_config("whisper_linux_cuda")))

                    # new - will try to use x86 as fallback
                    fall_back_option = os.path.join(_base_path, GGUFConfigs().get_config("whisper_linux_x86"))

                else:
                    _lib_paths.append(os.path.join(_base_path, GGUFConfigs().get_config("whisper_linux_x86")))

            elif system_platform == "darwin":

                machine = os.uname().machine.lower()

                if machine == 'x86_64':
                    raise LLMWareException("ModuleNotFound Exception - detected MacOS on x86_64 (e.g., not M1/M2/M3). "
                                           "LLMWare does not ship with a whisper_cpp module for this platform.  To use "
                                           "WhisperCPPModel will require a custom build whisper_cpp module.  For more "
                                           "details, please go to the llmware github site, or directly to the "
                                           "Whisper CPP source: https://www.github.com/ggerganov/whisper.cpp.git")

                    # _lib_paths.append(os.path.join(_base_path, GGUFConfigs().get_config("whisper_mac_x86")))
                else:

                    if GGUFConfigs().get_config("use_macos_accelerate"):

                        try:
                            import platform
                            macos_ver = platform.mac_ver()
                            if len(macos_ver) > 0:
                                ver = macos_ver[0].split(".")

                                v1 = int(ver[0])
                                v2 = int(ver[1])

                                if v1 < 14:

                                    logger.warning(f"warning: detected older version of macos - {macos_ver} - "
                                                    f"which may produce errors related to the Accelerate framework.\n"
                                                    f"To remove this warning: (1) upgrade to Sonoma (>14.0) or \n(2) set "
                                                    f"GGUF configs to use non Accelerate binary by default:\n"
                                                    f"GGUFConfigs().set_config('use_macos_accelerate', False)")

                        except:
                            pass

                        _lib_paths.append(os.path.join(_base_path, GGUFConfigs().get_config("whisper_mac_metal")))

                        fall_back_option = os.path.join(_base_path, GGUFConfigs().get_config("whisper_mac_metal_no_acc"))

                    else:
                        _lib_paths.append(os.path.join(_base_path, GGUFConfigs().get_config("whisper_mac_metal_no_acc")))

                    # _lib_paths.append(os.path.join(_base_path, GGUFConfigs().get_config("whisper_mac_metal")))

            elif sys.platform == "win32":

                _lib_paths.append(os.path.join(_base_path, GGUFConfigs().get_config("whisper_windows")))

        # Add the library directory to the DLL search path on Windows (if needed)
        # if sys.platform == "win32" and sys.version_info >= (3, 8): os.add_dll_directory(str(_base_path))

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
                            logger.warning("update: Not successful loading primary lib, so reverting to secondary "
                                           "driver (which may be slower).")

                            return ctypes.CDLL(str(fall_back_option), **cdll_args)
                        except:

                            # if fall-back fails
                            raise GGUFLibNotLoadedException("whisper_cpp_backend",
                                                            sys.platform.lower(),
                                                            self.use_gpu,
                                                            _lib_path,
                                                            custom_path)
                    else:
                        raise GGUFLibNotLoadedException("whisper_cpp_backend",sys.platform.lower(),
                                                        self.use_gpu, _lib_path, custom_path)
            else:
                logger.warning(f"update: looking for WhisperCPP lib - path does not exist - {str(_lib_path)}")

        # Try to load the shared library, handling potential errors
        # *** something has gone wrong - could not find the lib files

        raise FileNotFoundError(f"Exception: WhisperCPP Shared library not found at paths - {str(_lib_paths)}")

    # new method starts here

    def inference(self, prompt, inference_dict=None):

        """ Inference on Whisper model takes a single input 'prompt' which is a string corresponding to a
        full file path pointing to the voice file to be transcribed, e.g.,

            `/home/ubuntu/voice_samples/sample.wav

        """

        self.prompt=prompt

        if inference_dict:
            if "translate" in inference_dict:
                self.translate=inference_dict["translate"]

            if "remove_segment_markers" in inference_dict:
                self.remove_segment_markers = inference_dict["remove_segment_markers"]

        #   preview before starting inference
        self.preview()

        #   note: updated dependencies for improved efficiency
        #   previously, used librosa library
        #   replaced librosa with two librosa sub-dependencies that do most of the work
        #   e.g., soundfile, and soxr which results in smaller footprint for deployment

        file = prompt

        if not file.endswith(".wav"):

            logger.info("update: WhisperCPPModel - inference - input file needs to be converted to .wav - "
                         "will try to do right now.")

            new_file_path = Utilities().convert_media_file_to_wav(self.prompt,
                                                                  save_path=LLMWareConfig().get_tmp_path(),
                                                                  file_out="converted_file_tmp.wav")

            if not new_file_path:
                logger.warning("update: WhisperCPPModel - inference - conversion was not successful.  "
                                "The most likely causes of this error - \n"
                                "1.  File type is not supported - the following are the supported file types - "
                                "mp3, m4a, mp4, wma, aac, ogg, flv. \n"
                                "2.  lib ffmpeg is not installed on your system.  This is the core audio processing "
                                "library that handles the file conversion.\n"
                                "--to install on Mac:  brew install ffmpeg \n"
                                "--to install on Linux: sudo apt install ffmpeg \n"
                                "--to install on Windows: see ffmpeg.org/download.html for download/install \n")

                null_output = {"llm_response": "", "segments": []}
                return null_output

            else:
                logger.info(f"update: WhisperCPPModel - inference - file conversion to .wav successful - "
                             f"new file at tmp path - {new_file_path}")

                file = new_file_path

        # loading new dependencies starts here

        try:
            import soundfile as sf
            import soxr
        except:
            raise LLMWareException("WhisperCPPModel class requires dependencies of soundfile and soxr,"
                                   "e.g., `pip install soundfile` and `pip install soxr`")

        sfo = sf.SoundFile(file)

        with sfo as sf_desc:
            sr = sf_desc.samplerate
            frame_duration = -1

            data = sf_desc.read(frames=frame_duration, dtype=np.float32, always_2d=False).T

            if self.WHISPER_SR != sr:

                # y = resample(data, orig_sr=sr_native, target_sr=sr, res_type="soxr_hq")

                ratio = float(sr) / self.WHISPER_SR
                axis = -1
                n_samples = int(np.ceil(data.shape[axis] * ratio))

                yhat = np.apply_along_axis(soxr.resample, axis=axis, arr=data,
                                           in_rate=sr, out_rate=self.WHISPER_SR, quality="soxr_hq")

                data = np.asarray(yhat, dtype=np.float32)

        # new dependencies end here
        # replacing previous:   data, sr = librosa.load(file, sr=self.WHISPER_SR)

        try:
            self.duration = float(data.shape[-1]) / self.WHISPER_SR
            # self.duration = librosa.get_duration(y=data, sr=self.WHISPER_SR)
        except:
            self.duration = float(0.0)

        data.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        self.params.language = self.language.encode('utf-8')
        if prompt:
            self.params.initial_prompt = prompt.encode('utf-8')

        self.params.temperature = self.temperature

        self.params.translate = self.translate

        result = self._generate(data)

        #   output format options

        output = result["text"]

        if self.format == "srt":
            output = '\n'.join([f'{i + 1}\n{self._format_time(s["start"])} --> '
                                f'{self._format_time(s["end"])}\n{s["text"]}\n'
                                for i, s in enumerate(result["segments"])])

        if self.format == "vtt":
            output = '\n'.join([f'{i + 1}\n{self._format_time(s["start"])} --> '
                                f'{self._format_time(s["end"])} align:middle\n{s["text"]}\n'
                                for i, s in enumerate(result["segments"])])

        usage_dict = {"duration-seconds": self.duration, "segments": len(result["segments"]),
                      "language": self.language}

        response = {"llm_response": output, "usage": usage_dict, "segments": result["segments"]}

        #   update linked to BaseModel
        self.prompt = ""
        self.final_prompt = ""
        self.usage = response["usage"]
        self.llm_response = response["llm_response"]

        self.register()
        #   end - update

        return response

    def _generate(self, data):

        """ Executes lib_whisper generation on data from audio file. """

        w = self._lib.whisper_full(ctypes.c_void_p(self.context),
                                   self.params,
                                   data.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                                   len(data))

        if w != 0:
            raise LLMWareException(message=f"Exception: WhisperCPPModel - inference: {w}")

        segments = []
        all_text = ""
        text_chunks = []
        n_segments = self._lib.whisper_full_n_segments(ctypes.c_void_p(self.context))

        for i in range(n_segments):

            t0 = self._lib.whisper_full_get_segment_t0(ctypes.c_void_p(self.context), i)/100.0
            t1 = self._lib.whisper_full_get_segment_t1(ctypes.c_void_p(self.context), i)/100.0
            txt = self._lib.whisper_full_get_segment_text(ctypes.c_void_p(self.context), i).decode('utf-8-sig',
                                                                                                   errors='ignore')

            if self.tiny_diarize:

                # look for [_SOLM_] token to break segment - and will keep aggregating until found
                if "[_SOLM_]" in txt:
                    txt += "\n\n"

            if self.remove_segment_markers:

                #   removes leading [_BEG_] & trailing [_TT_XYZ] special tokens

                txt_split = txt.split("[_TT_")[0]
                txt_split = txt_split.strip()
                if txt_split.startswith("[_BEG_]"):
                    txt_split= txt_split[len("[_BEG_]"):]
                txt = " " + txt_split + " "

            all_text += txt
            text_chunks.append(txt)

            n_tokens = self._lib.whisper_full_n_tokens(ctypes.c_void_p(self.context), i)
            tokens = []

            for j in range(n_tokens):
                token_data = self._lib.whisper_full_get_token_data(ctypes.c_void_p(self.context), i, j)

                tokens.append({
                    "id": token_data.id,
                    "prob": token_data.p,
                    "logprob": token_data.plog,
                    "pt": token_data.pt,
                    "pt_sum": token_data.ptsum,
                })

            segments.append({
                "start": t0,
                "end": t1,
                "text": txt,
                "tokens": tokens,
            })

        result = {"text": all_text.strip(), "text_chunks": text_chunks, "segments": segments}

        return result

    def __dealloc__(self):
        # free the memory
        self._lib.whisper_free(ctypes.c_void_p(self.context))

    def unload_model(self):

        self._lib = None

    @staticmethod
    def _format_time(t):

        """ Helper utility that formats the time. """

        msec = t * 10
        hr = msec / (1000 * 60 * 60)
        msec = msec - hr * (1000 * 60 * 60)
        minu = msec / (1000 * 60)
        msec = msec - minu * (1000 * 60)
        sec = msec / 1000
        msec = msec - sec * 1000

        return f'{int(hr):02}:{int(minu):02}:{int(sec):02}.{int(msec):03}'

    def abort_call_back(self, data):
        do_nothing = 0

    def callback(self, ctx, state, i, p):
        do_nothing = 0

    def add_ctypes_configs(self):

        self._lib.whisper_init_from_file.argtypes = [ctypes.c_char_p]
        self._lib.whisper_init_from_file.restype = ctypes.c_void_p

        self._lib.whisper_full_default_params.argtypes = [ctypes.c_int]
        self._lib.whisper_full_default_params.restype = whisper_full_params

        self._lib.whisper_full.argtypes = [ctypes.c_void_p, whisper_full_params, ctypes.POINTER(ctypes.c_float), ctypes.c_int]
        self._lib.whisper_full.restype = ctypes.c_int

        self._lib.whisper_full_n_segments.argtypes = [ctypes.c_void_p]
        self._lib.whisper_full_n_segments.restype = ctypes.c_int

        self._lib.whisper_full_get_segment_t0.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._lib.whisper_full_get_segment_t0.restype = ctypes.c_int64

        self._lib.whisper_full_get_segment_t1.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._lib.whisper_full_get_segment_t1.restype = ctypes.c_int64

        self._lib.whisper_full_get_segment_text.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._lib.whisper_full_get_segment_text.restype = ctypes.c_char_p

        self._lib.whisper_full_n_tokens.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._lib.whisper_full_n_tokens.restype = ctypes.c_int

        self._lib.whisper_full_get_segment_t0.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._lib.whisper_full_get_segment_t0.restype = ctypes.c_int64

        self._lib.whisper_full_get_segment_t1.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._lib.whisper_full_get_segment_t1.restype = ctypes.c_int64

        self._lib.whisper_full_get_token_data.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        self._lib.whisper_full_get_token_data.restype = whisper_token_data

        self._lib.whisper_full_n_segments.argtypes = [ctypes.c_void_p]
        self._lib.whisper_full_n_segments.restype = ctypes.c_int

        self._lib.whisper_full_get_segment_text.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._lib.whisper_full_get_segment_text.restype = ctypes.c_char_p

        self._lib.whisper_full_n_tokens.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._lib.whisper_full_n_tokens.restype = ctypes.c_int

        self._lib.whisper_full_get_token_data.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        self._lib.whisper_full_get_token_data.restype = whisper_token_data

        self._lib.whisper_free.argtypes = [ctypes.c_void_p]
        self._lib.whisper_free.restype = None

        self._lib.whisper_log_set.artypes = [ctypes.c_void_p, ctypes.c_void_p]
        self._lib.whisper_log_set.restype = None

        return self._lib


class LLMWareSemanticModel(BaseModel):

    """ LLMWareSemanticModel class implements the LLMWareSemanticModel API, which is based on the SentenceTransformer
    architecture. """

    def __init__(self, model_name=None, model=None, embedding_dims=None, max_len=150,
                 model_card=None, api_key=None, **kwargs):

        super().__init__(**kwargs)

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
        self.sentence = None

        if model:
            logger.info("update: SemanticEmbedding model received model - will attempt to load as "
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
                        logger.info("update: Sentence Transformer model with more than two layers - unusual - "
                                     " depending upon the architecture, there may be issues loading the model- %s",
                                     len(model))

                        #   note: the most common case is with a Dense 3rd layer that maps the Pooling output to
                        #   a different dimension - in this case - this should give the dimensions:
                        #
                        #           last_layer_config = model[-1].get_config_dict()
                        #           if "out_features" in last_layer_config:
                        #               self.embedding_dims = last_layer_config["out_features"]

                except:
                    logger.error("error: could not identify model to run embedding - ", model_name)
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

    def load_model_for_inference(self,fp=None, model_card=None, **kwargs):

        """ This path has been deprecated starting with llmware 0.2.12. """

        # if fp: self.model_repo_location = fp

        raise LLMWareException(message="Exception - this load option has been deprecated.   LLMWareSemanticModels "
                                       "should be pulled from a sentence transformer standard repository.")

    def embedding(self, sentence):

        self.sentence = sentence

        #   preview before creating embedding
        self.preview()

        # embedding = self.model.encode(sentence, convert_to_tensor=True)
        embedding = self.model.encode(self.sentence)

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


class ModelResources:

    """ ModelResources is a global state mechanism used in conjunction with deploying the LLMWare Inference
    Server class.   It manages the persistent loading of multiple models behind the server. """

    class _ModelState:
        models_loaded = 0
        models_list = []

    @classmethod
    def load_model(cls, model_name, sample=False, temperature=0.0, get_logits=True, max_output=200, api_key=None,
                   use_gpu=True):

        model_card = ModelCatalog().lookup_model_card(model_name)

        if model_card and model_name not in cls._ModelState.models_list:

            setattr(cls._ModelState, model_name, ModelCatalog().load_model(model_name, api_key=api_key,
                                                                           sample=sample, use_gpu=use_gpu,
                                                                           get_logits=get_logits, max_output=max_output,
                                                                           temperature=temperature))

            cls._ModelState.models_list.append(model_name)
            cls._ModelState.models_loaded += 1

            logger.info(f"update: ModelResources - {cls._ModelState.models_loaded} - "
                         f"{cls._ModelState.models_list}")

    @classmethod
    def unload_model(cls, model_name):
        """ Not implemented currently. """
        return 0

    @classmethod
    def check_if_model_loaded(cls, model_name):

        """ Utility method that checks if the model has already been loaded. """

        if model_name in cls._ModelState.models_list:
            return True
        return False

    @classmethod
    def fetch_model(cls, model_name):

        """ Returns the instantiated model that is already loaded in memory. """

        return getattr(cls._ModelState, model_name)


class LLMWareInferenceServer:

    """ LLMWare Inference Server class implements server-side lightweight inference server with two
    primary APIs currently supported:

        1.  /      - main inference of general purpose LLM deployed on inference server at time of start.
        2.  /agent - supports agent process over API with multiple SLIM models deployed.

    """

    def __init__(self, model_name, model_catalog=None, hf_api_key=None, secret_api_key=None, home_path=None,
                 port=8080, verbose=True, temperature=0.0, sample=False, max_output=100, debug=False):

        self.HOME_PATH = home_path
        self.hf_api_key = hf_api_key
        self.current_api_key = secret_api_key
        self.port = port

        if not model_catalog:
            self.model_catalog = ModelCatalog()
        else:
            self.model_catalog = model_catalog

        self.model_name = model_name
        self.model = self.model_catalog.load_model(model_name, api_key=self.hf_api_key,
                                                   temperature=temperature, sample=sample, max_output=max_output)

        self.verbose = verbose

        import logging
        logging.basicConfig(level=30)
        global inference_server_logger
        inference_server_logger = logging.getLogger("inference_server_logger")

        if debug:
            inference_server_logger.setLevel(level=10)
        else:
            if self.verbose:
                # set logging at "INFO"
                inference_server_logger.setLevel(level=20)
            else:
                # keep logging at "WARNING"
                inference_server_logger.setLevel(level=30)

    def start(self):

        """ Starts the server runtime. """
        # if inference server started, then try to get flask dependency
        try:
            global flask
            from flask import Flask, request, jsonify
        except:
            raise DependencyNotInstalledException("flask")

        app = Flask(__name__, template_folder=self.HOME_PATH, static_folder=self.HOME_PATH)
        app.add_url_rule("/", methods=['GET', 'POST'], view_func=self.index_route)
        app.add_url_rule("/agent", methods=['GET','POST'], view_func=self.agent_route)

        #TODO:  WIP - explicit /load_model path not fully implemented yet
        app.add_url_rule("/load_model", methods=['GET','POST'], view_func=self.load_model_route)

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

    def _llmware_inference(self, prompt, context, model_name):

        """ Executes a LLM model inference from the main index route. """

        t1 = time.time()

        if not ModelResources().check_if_model_loaded(model_name):
            self._load_model(model_name, get_logits=False, sample=False,temperature=0.0, max_output=200)

        model = ModelResources().fetch_model(model_name)

        output = model.inference(prompt, add_context=context, add_prompt_engineering=True)

        if "logits" in output:
            output["logits"] = str(output["logits"])

        t2 = time.time()

        inference_server_logger.info(f"update: model inference output - {output['llm_response']} - {output['usage']}")
        inference_server_logger.info(f"update: total processing time: {t2-t1}")

        return output

    def index_route(self):

        """ Main index route to execute a model inference from the server. """

        # defaults
        api_key = ""
        question = ""
        context = ""
        model_name = ""

        # if inference server started, then try to get flask dependency
        try:
            from flask import Flask, request, jsonify
        except:
            raise DependencyNotInstalledException("flask")

        for keys in request.form:

            inference_server_logger.debug(f"update: keys / values input received - {keys} - {request.form.get(keys)}")

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

            if keys == "model_name":
                model_name = request.form.get(keys)

        t1 = time.time()

        if not question and not context:
            output_str = "Got your message - No content found to process"
            return jsonify({"message": output_str})

        if api_key != self.current_api_key:
            output_str = "Got your message - Thanks for testing - API key not confirmed!"
            return jsonify({"message": output_str})

        if not model_name:
            model_name = self.model_name
        # start processing here

        output = self._llmware_inference(question, context, model_name)

        # cuda.empty_cache()

        return jsonify(output)

    def agent_route(self):

        """ New InferenceServer API Route - to handle an Agent process deployed over a Remote Endpoint server. """

        try:
            from flask import Flask, request, jsonify
        except:
            raise DependencyNotInstalledException("flask")

        context = ""
        fx = ""
        model = ""
        params = []
        get_logits = False
        prompt = ""
        temperature = 0.0
        sample = False
        api_key = ""
        max_output = 50
        tool_type = ""

        for keys in request.form:

            inference_server_logger.debug(f"update: keys / values input received: {keys} - {request.form.get(keys)}")

            if keys == "context":
                context = request.form.get(keys)

            if keys == "tool_type":
                tool_type = request.form.get(keys)

            if keys == "function":
                fx = request.form.get(keys)

            if keys == "model" or keys == "model_name":
                model = request.form.get(keys)

            if keys == "params":
                params = request.form.get(keys)

            if keys == "get_logits":

                get_logits = request.form.get(keys)

                if get_logits in ["False", "false"]:
                    get_logits = False
                if get_logits in ["True", "true"]:
                    get_logits =True

            if keys == "temperature":
                temperature = request.form.get(keys)

            if keys == "sample":
                sample = request.form.get(keys)

            if keys == "question" or keys == "prompt":
                prompt = request.form.get(keys)

            if keys == "max_output_tokens" or keys == "max_output":
                max_output_len = request.form.get(keys)
                try:
                    max_output = int(max_output_len)
                except:
                    max_output = 200

            if keys == "api_key":
                api_key = request.form.get(keys)

        t1 = time.time()

        if not context and not (fx or model):
            output_str = "Got your message - No content found to process"
            return jsonify({"message": output_str})

        if api_key != self.current_api_key:
            output_str = "Got your message - Thanks for testing - API key not confirmed!"
            return jsonify({"message": output_str})

        # start processing here

        output = self._llmware_agent_function_call(context=context, tool_type=tool_type, model_name=model, function=fx,
                                                  temperature=temperature, sample=sample,params=params,
                                                  max_output=max_output, prompt=prompt,get_logits=get_logits)
        # cuda.empty_cache()

        return jsonify(output)

    def _llmware_agent_function_call(self, prompt=None, context=None, tool_type=None, model_name=None,
                                    function=None, temperature=0.0, sample=False, params=None,
                                    max_output=50, get_logits=False):

        """ Executes the function call inside the agent route. """

        if tool_type:
            model_name = _ModelRegistry().get_llm_fx_mapping()[tool_type]

        temperature = float(temperature)
        max_output = int(max_output)

        inference_server_logger.debug(f"update: llmware_agent_function_call - {model_name} - {tool_type}")

        if not ModelResources().check_if_model_loaded(model_name):
            self._load_model(model_name, get_logits=True,sample=False,temperature=0.0,max_output=max_output)

        model = ModelResources().fetch_model(model_name)

        if tool_type not in ["sql", "answer"]:
            # fc = getattr(model, "function_call")
            output = model.function_call(context,function=function,params=[params], get_logits=get_logits,
                                         max_output=max_output, temperature=temperature)
        else:
            # inference = getattr(model, "inference")
            output = model.inference(prompt,add_context=context,add_prompt_engineering="default_with_context",
                                     get_logits=get_logits)

        inference_server_logger.info(f"update: llmware_agent_function_call - model_response - {output['llm_response']} "
                                     f"- {output['usage']}")

        if "logits" in output:
            output["logits"] = str(output["logits"])

        return output

    def load_model_route(self):

        """ Load Model route is an explicit step to load a model into the server persistent state -
        not fully implemented yet - WIP. """

        output = {}
        model_name = ""
        tool = ""

        # if inference server started, then try to get flask dependency
        try:
            from flask import Flask, request, jsonify
        except:
            raise DependencyNotInstalledException("flask")

        for keys in request.form:

            inference_server_logger.debug(f"update: keys / values input received - {keys} - {request.form.get(keys)}")

            if keys == "model" or keys == "model_name":
                model_name = request.form.get(keys)

            if keys == "tool" or keys == "tool_type":
                tool = request.form.get(keys)

        if tool and not model_name:
            model_name = _ModelRegistry().get_llm_fx_mapping()[tool]

        if model_name:
            self._load_model(model_name)
            output = {"model": f"loaded-{model_name}"}

        return jsonify(output)

    def _load_model(self, model_name, sample=False, temperature=0.0, get_logits=False,max_output=200):

        if not ModelResources().check_if_model_loaded(model_name):
            ModelResources().load_model(model_name, sample=sample, temperature=temperature, get_logits=get_logits,
                                        max_output=max_output)
        else:
            inference_server_logger.debug(f"model already loaded - {model_name}")

        return True


class PyTorchLoader:

    """ PyTorchLoader is a wrapper class that consolidates all of the PyTorch model loading functions
    throughout llmware - and provides the ability to create a single custom loader function to over-ride
    the default PyTorch model loading, which relies upon HuggingFace repositories, and the formalisms
    provided by the transformers library in terms of configs and model class code.  This also enables a single
    point to customize the behavior of transformers configurations.   """

    def __init__(self, api_key=None, trust_remote_code=True,custom_loader=None):

        self.model_name = None
        self.api_key=api_key
        self.trust_remote_code = trust_remote_code
        self.custom_loader = custom_loader

    def get_generative_model(self, model_name, **kwargs):

        """ Retrieves and instantiates a Pytorch Generative model.  Takes a model_name as input, which is
        assumed to map to the Huggingface repository name - this name is not necessarily the same as the
        LLMWare model card, which is used to lookup the model in model_configs -> the model_name used here
        should be the hf_repo attribute on the model card. """

        #   will return None if no model found
        model = None

        self.model_name=model_name

        if self.custom_loader:
            model = self.custom_loader.loader(self.model_name,
                                              self.api_key,self.trust_remote_code,caller="generative_model",**kwargs)

        else:

            try:
                # will wrap in Exception if import fails
                from transformers import AutoModelForCausalLM, AutoTokenizer
            except ImportError:
                raise DependencyNotInstalledException("transformers")

            # insert dynamic pytorch load here
            global GLOBAL_TORCH_IMPORT
            if not GLOBAL_TORCH_IMPORT:

                logger.debug("Pytorch loader - local dynamic load of torch here")
                if util.find_spec("torch"):

                    try:
                        global torch
                        torch = importlib.import_module("torch")
                        GLOBAL_TORCH_IMPORT = True
                    except:
                        raise LLMWareException(message="Exception: could not load torch module.")

                else:
                    raise LLMWareException(message="Exception: need to import torch to use this class.")

            if self.api_key:

                if torch.cuda.is_available():
                    model = AutoModelForCausalLM.from_pretrained(model_name, token=self.api_key,
                                                                 trust_remote_code=self.trust_remote_code,
                                                                 torch_dtype="auto")
                else:
                    model = AutoModelForCausalLM.from_pretrained(model_name, token=self.api_key,
                                                                 trust_remote_code=self.trust_remote_code)

            else:
                if torch.cuda.is_available():
                    model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=self.trust_remote_code,
                                                                 torch_dtype="auto")
                else:
                    model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=self.trust_remote_code)

        return model

    def get_embedding_model(self, model_name, **kwargs):

        """ Retrieves and instantiates a Pytorch Embedding model.  Takes a model_name as input, which is
        assumed to map to the Huggingface repository name - this name is not necessarily the same as the
        LLMWare model card, which is used to lookup the model in model_configs -> the model_name used here
        should be the hf_repo attribute on the model card. """

        model = None

        self.model_name = model_name

        if self.custom_loader:
            model = self.custom_loader.loader(self.model_name, self.api_key, self.trust_remote_code, self.custom_loader,
                                              caller="embedding_model", **kwargs)

        else:

            try:
                # will wrap in Exception if import fails
                from transformers import AutoModel
            except ImportError:
                raise DependencyNotInstalledException("transformers")

            # insert dynamic pytorch load here
            global GLOBAL_TORCH_IMPORT
            if not GLOBAL_TORCH_IMPORT:

                logger.debug("Pytorch loader - local dynamic load of torch here")
                if util.find_spec("torch"):

                    try:
                        global torch
                        torch = importlib.import_module("torch")
                        GLOBAL_TORCH_IMPORT = True
                    except:
                        raise LLMWareException(message="Exception: could not load torch module.")

                else:
                    raise LLMWareException(message="Exception: need to import torch to use this class.")

            if self.api_key:

                if torch.cuda.is_available():
                    model = AutoModel.from_pretrained(model_name, token=self.api_key,
                                                      trust_remote_code=self.trust_remote_code,
                                                      torch_dtype="auto")
                else:
                    model = AutoModel.from_pretrained(model_name, token=self.api_key,
                                                      trust_remote_code=self.trust_remote_code)

            else:
                if torch.cuda.is_available():
                    model = AutoModel.from_pretrained(model_name, trust_remote_code=self.trust_remote_code,
                                                      torch_dtype="auto")
                else:
                    model = AutoModel.from_pretrained(model_name, trust_remote_code=self.trust_remote_code)

        return model

    def get_reranker_model(self, model_name, **kwargs):

        """ Retrieves and instantiates a Pytorch Reranker model.  Takes a model_name as input, which is
        assumed to map to the Huggingface repository name - this name is not necessarily the same as the
        LLMWare model card, which is used to lookup the model in model_configs -> the model_name used here
        should be the hf_repo attribute on the model card. """

        model = None

        self.model_name = model_name

        if self.custom_loader:
            model = self.custom_loader.loader(self.model_name, self.api_key, self.trust_remote_code, self.custom_loader,
                                              caller="reranker_model", **kwargs)

        else:

            try:
                # will wrap in Exception if import fails
                from transformers import AutoModelForSequenceClassification
            except ImportError:
                raise DependencyNotInstalledException("transformers")

            # insert dynamic pytorch load here
            global GLOBAL_TORCH_IMPORT
            if not GLOBAL_TORCH_IMPORT:

                logger.debug("Pytorch loader - local dynamic load of torch here")
                if util.find_spec("torch"):

                    try:
                        global torch
                        torch = importlib.import_module("torch")
                        GLOBAL_TORCH_IMPORT = True
                    except:
                        raise LLMWareException(message="Exception: could not load torch module.")

                else:
                    raise LLMWareException(message="Exception: need to import torch to use this class.")

            if self.api_key:

                if torch.cuda.is_available():
                    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=1,
                                                                               token=self.api_key,
                                                                               trust_remote_code=self.trust_remote_code,
                                                                               torch_dtype="auto")
                else:
                    model = AutoModelForSequenceClassification.from_pretrained(model_name,
                                                                               num_labels=1,
                                                                               token=self.api_key,
                                                                               trust_remote_code=self.trust_remote_code)

            else:
                if torch.cuda.is_available():
                    model = AutoModelForSequenceClassification.from_pretrained(model_name,
                                                                               num_labels=1,
                                                                               trust_remote_code=self.trust_remote_code,
                                                                               torch_dtype="auto")
                else:
                    model = AutoModelForSequenceClassification.from_pretrained(model_name,
                                                                               num_labels=1,
                                                                               trust_remote_code=self.trust_remote_code)

        return model

    def get_tokenizer(self, model_name, **kwargs):

        """ Retrieves and instantiates a tokenizer.  Takes a model_name as input, which is
        assumed to map to the Huggingface repository name - this name is not necessarily the same as the
        LLMWare model card, which is used to lookup the model in model_configs -> the model_name used here
        should be the hf_repo attribute on the model card. """

        tokenizer = None

        self.model_name = model_name

        if self.custom_loader:
            tokenizer = self.custom_loader.loader(self.model_name, self.api_key, self.trust_remote_code,
                                                  self.custom_loader, caller="tokenizer", **kwargs)
        else:

            try:
                # will wrap in Exception if import fails
                from transformers import AutoTokenizer
            except ImportError:
                raise DependencyNotInstalledException("transformers")

            if self.api_key:
                tokenizer = AutoTokenizer.from_pretrained(model_name, token=self.api_key,
                                                          trust_remote_code=self.trust_remote_code)
            else:
                tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=self.trust_remote_code)

        return tokenizer


class CustomPTLoader:

    """ CustomPTLoader is a stub class that demonstrates how to create a custom PT loader method that
    can be passed to PyTorchLoader to over-ride the default load from a HuggingFace repository using transformers. """

    def __init__(self, model_name=None, api_key=None, trust_remote_code=True,caller=None):

        self.model_name = model_name
        self.api_key= api_key
        self.trust_remote_code = trust_remote_code
        self.caller = caller

    def loader(self, model_name,api_key=None, trust_remote_code=True, caller=None):

        self.model_name = model_name
        self.api_key= api_key
        self.trust_remote_code=trust_remote_code
        self.caller = caller

        if self.caller == "generative_model":
            return self.load_generative_model()

        if self.caller == "embedding_model":
            return self.load_embedding_model()

        if self.caller == "tokenizer":
            return self.load_tokenizer()

    def load_generative_model(self):

        """ Stub method to enable a custom loading of a generative PyTorch model. """

        model=None
        return model

    def load_embedding_model(self):

        """ Stub method to enable a custom loading of an embedding PyTorch model. """

        model=None
        return model

    def load_tokenizer(self):

        """ Stub method to enable a custom loading a tokenizer. """

        tokenizer=None
        return tokenizer


