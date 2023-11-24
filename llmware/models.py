
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
import traceback
import ast
from collections import OrderedDict
from tqdm.auto import trange
import time

import torch
from torch.utils.data import Dataset
import torch.nn.functional as F
from torch import Tensor, nn
from tqdm.autonotebook import trange
import math
import inspect

import torch.utils.checkpoint
from torch.nn import CrossEntropyLoss, BCEWithLogitsLoss

from llmware.util import Utilities, PromptCatalog
from llmware.configs import LLMWareConfig
from llmware.resources import CloudBucketManager
from llmware.exceptions import ModelNotFoundException, LLMInferenceResponseException, DependencyNotInstalledException

# api model imports
import openai, anthropic, ai21, cohere

global_model_repo_catalog_list = [

    # embedding models
    {"model_name": 'mini-lm-sbert', "display_name": "Sentence_Transformers (MPNet-Base)", "model_family": "LLMWareSemanticModel",
     "model_category": "embedding", "model_location": "llmware_repo", "is_trainable": "yes", "embedding_dims": 384},

    {"model_name": 'industry-bert-insurance', "display_name": "Insurance_LLMWare_Accelerator", "model_family": "LLMWareSemanticModel",
     "model_category": "embedding", "model_location": "llmware_repo", "is_trainable": "yes", "embedding_dims": 768},

    {"model_name": 'industry-bert-contracts', "display_name": "Contracts_LLMWare_Accelerator", "model_family": "LLMWareSemanticModel",
     "model_category": "embedding", "model_location": "llmware_repo", "is_trainable": "yes", "embedding_dims": 768},

    {"model_name": 'industry-bert-asset-management', "display_name": "Asset_Management_LLMWare_Accelerator",
     "model_family": "LLMWareSemanticModel",
     "model_category": "embedding", "model_location": "llmware_repo", "is_trainable": "yes", "embedding_dims": 768},

    {"model_name": 'industry-bert-sec', "display_name": "SEC_LLMWare_Accelerator", "model_family": "LLMWareSemanticModel",
     "model_category": "embedding", "model_location": "llmware_repo", "is_trainable": "yes", "embedding_dims": 768},

    # add open ai embeddings
    {"model_name": 'text-embedding-ada-002', "display_name": "OpenAI-Embedding", "model_family": "OpenAIEmbeddingModel",
     "model_category": "embedding", "model_location": "api", "is_trainable": "no", "context_window": 2048,
     "embedding_dims": 1536},

    # add cohere embeddings
    {"model_name": 'medium', "display_name": "Cohere-Medium-Embedding", "model_family": "CohereEmbeddingModel",
     "model_category": "embedding", "model_location": "api", "is_trainable": "no","context_window": 2048,
     "embedding_dims": 4096},

    {"model_name": 'xlarge', "display_name": "Cohere-XLarge-Embedding", "model_family": "CohereEmbeddingModel",
     "model_category": "embedding", "model_location": "api", "is_trainable": "no", "context_window": 2048,
     "embedding_dims": 4096},

    # insert new cohere embedding model - v3 - announced first week of November 2023
    {"model_name": 'embed-english-v3.0', "display_name": "Cohere-English-v3", "model_family": "CohereEmbeddingModel",
     "model_category": "embedding", "model_location": "api", "is_trainable": "no", "context_window": 2048,
     "embedding_dims": 1024},

    {"model_name": 'embed-multilingual-v3.0', "display_name": "Cohere-Multi-Lingual-v3", "model_family": "CohereEmbeddingModel",
     "model_category": "embedding", "model_location": "api", "is_trainable": "no", "context_window": 2048,
     "embedding_dims": 1024},

    {"model_name": 'embed-english-light-v3.0', "display_name": "Cohere-English-v3", "model_family": "CohereEmbeddingModel",
     "model_category": "embedding", "model_location": "api", "is_trainable": "no", "context_window": 2048,
     "embedding_dims": 384},

    {"model_name": 'embed-multilingual-light-v3.0', "display_name": "Cohere-English-v3", "model_family": "CohereEmbeddingModel",
     "model_category": "embedding", "model_location": "api", "is_trainable": "no", "context_window": 2048,
     "embedding_dims": 384},

    {"model_name": 'embed-english-v2.0', "display_name": "Cohere-English-v3",
     "model_family": "CohereEmbeddingModel",
     "model_category": "embedding", "model_location": "api", "is_trainable": "no", "context_window": 2048,
     "embedding_dims": 4096},

    {"model_name": 'embed-english-light-v2.0', "display_name": "Cohere-English-v3",
     "model_family": "CohereEmbeddingModel",
     "model_category": "embedding", "model_location": "api", "is_trainable": "no", "context_window": 2048,
     "embedding_dims": 1024},

    {"model_name": 'embed-multilingual-v2.0', "display_name": "Cohere-English-v3",
     "model_family": "CohereEmbeddingModel",
     "model_category": "embedding", "model_location": "api", "is_trainable": "no", "context_window": 2048,
     "embedding_dims": 768},
    # end - new cohere embeddings

    # add google embeddings
    # textembedding-gecko@001
    {"model_name": 'textembedding-gecko@latest', "display_name": "Google-Embedding", "model_family": "GoogleEmbeddingModel",
     "model_category": "embedding","model_location": "api", "is_trainable": "no", "context_window": 4000,
     "embedding_dims": 768},

    # generative-api models
    {"model_name": 'claude-v1', "display_name": "Anthropic Claude-v1", "model_family": "ClaudeModel",
     "model_category": "generative-api", "model_location": "api", "is_trainable": "no",
     "context_window": 8000},
    {"model_name": 'claude-instant-v1', "display_name": "Anthropic Claude-Instant-v1", "model_family": "ClaudeModel",
     "model_category": "generative-api","model_location": "api", "is_trainable": "no",
     "context_window": 8000},
    {"model_name": 'command-medium-nightly', "display_name": "Cohere Command Medium", "model_family": "CohereGenModel",
     "model_category": "generative-api","model_location": "api", "is_trainable": "no",
     "context_window": 2048},
    {"model_name": 'command-xlarge-nightly', "display_name": "Cohere Command XLarge", "model_family": "CohereGenModel",
     "model_category": "generative-api","model_location": "api", "is_trainable": "no",
     "context_window": 2048},

    {"model_name": 'summarize-xlarge', "display_name": "Cohere Summarize Xlarge", "model_family": "CohereGenModel",
     "model_category":"generative-api","model_location": "api", "is_trainable": "no",
     "context_window": 2048},
    {"model_name": 'summarize-medium', "display_name": "Cohere Summarize Medium", "model_family": "CohereGenModel",
     "model_category":"generative-api","model_location": "api", "is_trainable": "no",
     "context_window": 2048},
    {"model_name": 'j2-jumbo-instruct', "display_name": "Jurassic-2-Jumbo-Instruct", "model_family": "JurassicModel",
     "model_category":"generative-api", "model_location": "api", "is_trainable": "no",
     "context_window": 2048},
    {"model_name": 'j2-grande-instruct', "display_name": "Jurassic-2-Grande-Instruct", "model_family": "JurassicModel",
     "model_category":"generative-api","model_location": "api", "is_trainable": "no",
     "context_window": 2048},
    {"model_name": 'text-bison@001', "display_name": "Google Palm", "model_family": "GoogleGenModel",
     "model_category": "generative-api","model_location": "api", "is_trainable": "no",
     "context_window": 8192},
    {"model_name": 'chat-bison@001', "display_name": "Google Chat", "model_family": "GoogleGenModel",
     "model_category": "generative-api","model_location": "api", "is_trainable": "no",
     "context_window": 8192},
    {"model_name": 'text-davinci-003', "display_name": "GPT3-Davinci", "model_family": "OpenAIGenModel",
     "model_category": "generative-api","model_location": "api", "is_trainable": "no",
     "context_window": 4096},
    {"model_name": 'text-curie-001', "display_name": "GPT3-Curie", "model_family": "OpenAIGenModel",
     "model_category": "generative-api","model_location": "api", "is_trainable": "no",
     "context_window": 2048},
    {"model_name": 'text-babbage-001', "display_name": "GPT3-Babbage", "model_family": "OpenAIGenModel",
     "model_category": "generative-api","model_location": "api", "is_trainable": "no",
     "context_window": 2048},
    {"model_name": 'text-ada-001', "display_name": "GPT3-Ada", "model_family": "OpenAIGenModel",
     "model_category": "generative-api","model_location": "api", "is_trainable": "no",
     "context_window": 2048},
    {"model_name": "gpt-3.5-turbo", "display_name": "ChatGPT", "model_family": "OpenAIGenModel",
     "model_category": "generative-api","model_location": "api", "is_trainable": "no",
     "context_window": 4000},

    # gpt-4 add
    {"model_name": "gpt-4", "display_name": "GPT-4", "model_family": "OpenAIGenModel",
     "model_category": "generative-api", "model_location": "api", "is_trainable": "no",
     "context_window": 8000},

    # gpt-3.5-turbo-instruct
    {"model_name": "gpt-3.5-turbo-instruct", "display_name": "GPT-3.5-Instruct", "model_family": "OpenAIGenModel",
     "model_category": "generative-api", "model_location": "api", "is_trainable": "no",
     "context_window": 4000},

    # new gpt-4 models announced in November 2023
    {"model_name": "gpt-4-1106-preview", "display_name": "GPT-4-Turbo", "model_family": "OpenAIGenModel",
     "model_category": "generative_api", "model_location": "api", "is_trainable": "no",
     "context_window": 128000},

    {"model_name": "gpt-3.5-turbo-1106", "display_name": "GPT-3.5-Turbo", "model_family": "OpenAIGenModel",
     "model_category": "generative_api", "model_location": "api", "is_trainable": "no",
     "context_window": 16385},
    # end - gpt-4 model update

    # generative AIB models - aib-read-gpt - "main model"
    {"model_name": "aib-read-gpt", "display_name": "AIB-READ-GPT", "model_family": "AIBReadGPTModel",
     "model_category": "generative-api", "model_location": "api", "is_trainable": "no",
     "context_window": 2048},

    # HF embedding models
    {"model_name": "HF-Embedding", "display_name": "HF-Embedding", "model_family": "HFEmbeddingModel",
     "model_category": "semantic-hf", "model_location": "api", "is_trainable": "no",
     "context_window": 2048},

    # HF generative models
    {"model_name": "HF-Generative", "display_name": "HF-Generative", "model_family": "HFGenerativeModel",
     "model_category": "generative-hf", "model_location": "api", "is_trainable": "no",
     "context_window": 2048},

    # base supporting models and components
    {"model_name": "bert", "display_name": "Bert", "model_family": "BaseModel", "model_category": "base",
     "is_trainable": "no","model_location": "llmware_repo"},
    {"model_name": "roberta", "display_name": "Roberta", "model_family": "BaseModel", "model_category": "base",
     "is_trainable": "no","model_location": "llmware_repo"},
    {"model_name": "gpt2", "display_name": "GPT-2", "model_family": "BaseModel", "model_category": "base",
     "is_trainable": "no","model_location": "llmware_repo"},

    # add api-based llmware custom model
    {"model_name": "llmware-inference-server", "display_name": "LLMWare-GPT", "model_family": "LLMWareModel", "model_category":
     "generative_api", "model_location": "api", "is_trainable": "no", "context_window": 2048},

    # core llmware bling open source models available in catalog directly
    {"model_name": "llmware/bling-1.4b-0.1", "display_name": "Bling-Pythia-1.4B", "model_family": "HFGenerativeModel",
     "model_category": "generative_api", "model_location": "api", "is_trainable": "no", "context_window": 2048,
     "instruction_following": False, "prompt_wrapper": "human_bot", "temperature": 0.3, "trailing_space":""},

    {"model_name": "llmware/bling-1b-0.1", "display_name": "Bling-Pythia-1.0B", "model_family": "HFGenerativeModel",
     "model_category": "generative_api", "model_location": "api", "is_trainable": "no", "context_window": 2048,
     "instruction_following": False, "prompt_wrapper": "human_bot", "temperature": 0.3, "trailing_space": ""},

    {"model_name": "llmware/bling-falcon-1b-0.1", "display_name": "Bling-Falcon-1.3B", "model_family": "HFGenerativeModel",
     "model_category": "generative_api", "model_location": "api", "is_trainable": "no", "context_window": 2048,
     "instruction_following": False, "prompt_wrapper": "human_bot", "temperature": 0.3, "trailing_space": ""},

    {"model_name": "llmware/bling-sheared-llama-1.3b-0.1", "display_name": "Bling-Sheared-LLama-1.3B",
     "model_family": "HFGenerativeModel", "model_category": "generative_api", "model_location": "api",
     "is_trainable": "no", "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": ""},

    {"model_name": "llmware/llmware/bling-red-pajamas-3b-0.1", "display_name": "Bling-Pythia-1.4B",
     "model_family": "HFGenerativeModel", "model_category": "generative_api", "model_location": "api",
     "is_trainable": "no", "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": ""},

    {"model_name": "llmware/bling-sheared-llama-2.7b-0.1", "display_name": "Bling-Sheared-Llama-2.7B",
     "model_family": "HFGenerativeModel", "model_category": "generative_api", "model_location": "api",
     "is_trainable": "no", "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": ""},

    {"model_name": "llmware/bling-stable-lm-3b-4e1t-v0", "display_name": "Bling-Stable-LM-3B",
     "model_family": "HFGenerativeModel", "model_category": "generative_api", "model_location": "api",
     "is_trainable": "no", "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": ""},

    {"model_name": "llmware/bling-cerebras-1.3b-0.1", "display_name": "Bling-Cerebras-1.3B",
     "model_family": "HFGenerativeModel", "model_category": "generative_api", "model_location": "api",
     "is_trainable": "no", "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": ""},
     
    # create dragon models
    {"model_name": "llmware/dragon-yi-6b-v0", "display_name": "Dragon-Yi-6B",
     "model_family": "HFGenerativeModel", "model_category": "generative_api", "model_location": "api",
     "is_trainable": "no", "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": "\n"},

    {"model_name": "llmware/dragon-stablelm-7b-v0", "display_name": "Dragon-StableLM-7B",
     "model_family": "HFGenerativeModel", "model_category": "generative_api", "model_location": "api",
     "is_trainable": "no", "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": ""},

    {"model_name": "llmware/dragon-mistral-7b-v0", "display_name": "Dragon-Mistral-7B",
     "model_family": "HFGenerativeModel", "model_category": "generative_api", "model_location": "api",
     "is_trainable": "no", "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": ""},

    {"model_name": "llmware/dragon-red-pajama-7b-v0", "display_name": "Dragon-Red-Pajama-7B",
     "model_family": "HFGenerativeModel", "model_category": "generative_api", "model_location": "api",
     "is_trainable": "no", "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": ""},

    {"model_name": "llmware/dragon-deci-6b-v0", "display_name": "Dragon-Deci-6B",
     "model_family": "HFGenerativeModel", "model_category": "generative_api", "model_location": "api",
     "is_trainable": "no", "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": ""},

    {"model_name": "llmware/dragon-falcon-7b-v0", "display_name": "Dragon-Falcon-7B",
     "model_family": "HFGenerativeModel", "model_category": "generative_api", "model_location": "api",
     "is_trainable": "no", "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": ""},

    {"model_name": "llmware/dragon-llama-7b-v0", "display_name": "Dragon-Llama-7B",
     "model_family": "HFGenerativeModel", "model_category": "generative_api", "model_location": "api",
     "is_trainable": "no", "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": ""}

]


def build_json_models_manifest(manifest_dict, fp, fn="llmware_supported_models_manifest.json"):

    json_dict = json.dumps(manifest_dict,indent=1)
    with open(os.path.join(fp,fn), "w") as outfile:
        outfile.write(json_dict)

    return 0


class ModelCatalog:

    #   ModelCatalog responsible for model lookup of (1) Model Card, and (2) Finding Model Class

    def __init__(self):

        #   ModelCatalog is simple, flexible mechanism to track registered models
        #   Easy to create "model repo" with mix of model types and instantiation approaches
        #   Builds on standard model classes with standard inference

        self.model_classes = [
                                # generative model classes
                                "OpenAIGenModel", "ClaudeModel", "GoogleGenModel",
                                "CohereGenModel", "JurassicModel", "AIBReadGPTModel",
                                "HFGenerativeModel", "LLMWareModel",

                                # embedding model classes
                                "LLMWareSemanticModel",
                                "OpenAIEmbeddingModel", "CohereEmbeddingModel",
                                "GoogleEmbeddingModel", "HFEmbeddingModel"
                             ]

        self.global_model_list = global_model_repo_catalog_list

        self.account_name = None
        self.library_name= None

    def pull_latest_manifest(self):
        # will add to check manifest in global repo and make available for pull down
        return 0

    def register_new_model_card(self, model_card_dict):

        # validate keys
        if "model_family" not in model_card_dict:
            # error - could not add new model card
            raise ModelNotFoundException("no-model-family-identified")

        else:
            if model_card_dict["model_family"] not in self.model_classes:
                # error
                raise ModelNotFoundException("model-family-not-recognized")

            else:

                # format of new model card registered in model catalog
                """
                model_card = {"model_name": "llmware", "display_name": "LLMWare-GPT", "model_family": "LLMwareModel", "model_category":
                    "generative_api", "model_location": "api", "is_trainable": "no", "context_window": 2048}
                """

                self.global_model_list.append(model_card_dict)

        return 0

    def setup_custom_llmware_inference_server(self, uri_string, secret_key=None):

        #   Examples:
        #       os.environ["LLMWARE_GPT_URI"] = "http://111.111.1.111:8080"
        #       os.environ["USER_MANAGED_LLMWARE_GPT_API_KEY"] = "demo-pass-test-key"

        # set environ variables with the URL and password key
        os.environ["LLMWARE_GPT_URI"] = uri_string
        os.environ["USER_MANAGED_LLMWARE_GPT_API_KEY"] = secret_key

        return 1

    def lookup_model_card (self, selected_model_name):

        model_card = None

        # first check in the global_model_repo + confirm location
        for models in self.global_model_list:
            if models["model_name"] == selected_model_name:
                model_card = models
                model_card.update({"standard":True})
                break

        #   if model not found, then return None, and downstream calling function responsible for handling

        return model_card

    def locate_and_retrieve_model_bits (self, model_card):

        # check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):
            # if not explicitly set up by user, then create folder directory structure
            LLMWareConfig.setup_llmware_workspace()

        model_name = model_card["model_name"]

        if not os.path.exists(LLMWareConfig.get_model_repo_path()):
            os.mkdir(LLMWareConfig.get_model_repo_path())

        model_location = os.path.join(LLMWareConfig.get_model_repo_path(), model_name)

        if os.path.exists(model_location):
            model_parts_in_folder = os.listdir(model_location)
            if len(model_parts_in_folder) > 0:
                return model_location

        logging.info("update: ModelCatalog - this model - %s - is not in local repo - %s, so pulling "
                        "from global repo - please note that this may take a little time to load "
                        "for the first time.", model_name, LLMWareConfig.get_model_repo_path())

        logging.info("update: ModelCatalog - pulling model from global repo - %s ", model_name)

        CloudBucketManager().pull_single_model_from_llmware_public_repo(model_name)

        logging.info("update: ModelCatalog - done pulling model into local folder - %s ", model_location)

        if os.path.exists(model_location):
            return model_location
        
        raise ModelNotFoundException(model_name)

    def _instantiate_model_class_from_string(self, model_class, model_name, model_card, api_key=None):

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
                                                                                      api_key=api_key)

            # placeholder for HF models
            if model_class == "HFGenerativeModel":
                my_model = HFGenerativeModel(model_name=model_name,api_key=api_key, trust_remote_code=True)

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
                    
            if model_class == "HFEmbeddingModel": my_model = HFEmbeddingModel(model_name=model_name,
                                                                              api_key=api_key)

        return my_model

    # completes all preparatory steps, and returns 'ready-for-inference' model
    def load_model (self, selected_model, api_key=None):

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
        if model_card["model_location"] != "api":
            loading_directions = self.locate_and_retrieve_model_bits(model_card)
            my_model = my_model.load_model_for_inference(loading_directions)
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

    # enables passing of a 'loaded' sentence transformer model
    def load_sentence_transformer_model(self,model, model_name):
        model = LLMWareSemanticModel(model=model,model_name=model_name)
        return model

    # integrate hf model passed
    def load_hf_embedding_model(self, model, tokenizer):
        model = HFEmbeddingModel(model, tokenizer)
        return model

    #   integrate pretrained decoder-based hf 'causal' model
    #   Provide options to control model preprocessing prompt behavior
    def load_hf_generative_model(self, model,tokenizer,prompt_wrapper=None,
                                 instruction_following=False):

        model = HFGenerativeModel(model, tokenizer, prompt_wrapper=prompt_wrapper,
                                  instruction_following=instruction_following)

        return model

    # master handler to be used by any calling function, especially Retrieval / Query
    def load_embedding_model (self, model_name=None,
                              model=None, tokenizer=None,from_hf=False,
                              from_sentence_transformers=False):

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

            if not model:
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

    def list_embedding_models(self):

        embedding_models = []

        for x in self.global_model_list:
            if x["model_category"] == "embedding":
                embedding_models.append(x)

        return embedding_models

    def list_generative_models(self):

        gen_models = []

        for x in self.global_model_list:
            if x["model_category"].startswith("generative"):
                gen_models.append(x)

        gen_models = sorted(gen_models, key=lambda x: x["model_name"], reverse=False)

        return gen_models

    def list_all_models(self):

        all_models = []
        for x in self.global_model_list:
            all_models.append(x)

        all_models = sorted(all_models, key=lambda x: x["model_category"], reverse=False)

        return all_models

    def model_lookup(self,model_name):
        my_model = None

        for models in self.global_model_list:
            if models["model_name"] == model_name:
                my_model = models
                break

        return my_model

    def get_model_by_name(self, model_name, api_key=None):

        my_model = None

        for models in self.global_model_list:

            if models["model_name"] == model_name:
                selected_model = models
                my_model = self._instantiate_model_class_from_string(selected_model["model_family"],
                                                                     model_name, models,api_key=api_key)
                break

        return my_model


class OpenAIGenModel:

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
        tokenizer = Utilities().get_default_tokenizer
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

        usage = {}
        time_start = time.time()

        try:

            if self.model_name in ["gpt-3.5-turbo","gpt-4"]:

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

        # will look to capture usage metadata
        #   "usage" = {"completion_tokens", "prompt_tokens", "total_tokens"}

        output_response = {"llm_response": text_out, "usage": usage}

        return output_response


class ClaudeModel:

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

        with open(temp_json_path, "w") as f:
            f.write(self.api_key.replace("\n", "\\n"))

        return temp_json_path


class JurassicModel:

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

    def load_model_for_inference(self, model_name=None, fp=None):
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

    def load_model_for_inference(self, model_name=None, fp=None):
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

        return embedding


class CohereEmbeddingModel:

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
        with open(temp_json_path, "w") as f:
            f.write(self.api_key.replace("\n", "\\n"))
        return temp_json_path


class HFEmbeddingModel:

    def __init__(self, model=None, tokenizer=None, model_name=None, api_key=None,
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

    #   support instantiating HF model in two different ways:
    #       1.  directly passing a previously loaded HF model object and tokenizer object
    #       2.  passing a model_name only, which will then create the model and tokenizer

    def __init__(self, model=None, tokenizer=None, model_name=None, api_key=None,
                 prompt_wrapper=None, instruction_following=False, context_window=2048,
                 use_gpu_if_available=True, trust_remote_code=False):

        # pull in expected hf input
        self.model_name = model_name
        self.model = model
        self.tokenizer= tokenizer

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

        # note - these two parameters will control how prompts are handled - model-specific
        self.prompt_wrapper = prompt_wrapper
        self.instruction_following = instruction_following
        
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


class LLMWareSemanticModel:

    def __init__(self, model_name=None, model=None, embedding_dims=None, max_seq_length=150,api_key=None):

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

    def load_model_for_inference(self,fp=None):

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

    def __init__(self, model_path, max_seq_length=150, do_lower_case= False, model_size="standard"):
        super().__init__()

        # need to look up model config first
        try:
            self.config = json.load(open(os.path.join(model_path,"config.json"), "r"))

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

    def __init__(self, model_name, model_catalog=None, hf_api_key=None, secret_api_key=None, home_path=None):

        # parameter samples
        #   hf_api_key="hf_...",
        #   secret_api_key="...",
        #   home_path="/home/ubuntu/"

        self.HOME_PATH = home_path
        self.hf_api_key = hf_api_key
        self.current_api_key = secret_api_key

        if not model_catalog:
            self.model_catalog = ModelCatalog()
        else:
            self.model_catalog = model_catalog

        self.model = self.model_catalog.load_model(model_name, api_key=self.hf_api_key)

        """
        print("update: creating LLMWareInferenceServer - model config - ", self.model.model_name,
              self.model.prompt_wrapper, self.model.temperature, self.model.instruction_following,
              self.model.eos_token_id)
        """

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
        my_port = 8080
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


