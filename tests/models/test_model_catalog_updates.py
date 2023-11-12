
import os
import time

from llmware.models import ModelCatalog, LLMWareModel
from llmware.prompts import Prompt, HumanInTheLoop
from llmware.configs import LLMWareConfig

def test_add_new_model_name_to_catalog_directly():

    # new model name
    new_model_card = {"model_name": "llmware2", "display_name": "LLMWare-GPT2", "model_family": "LLMWareModel",
                      "model_category": "generative_api", "model_location": "api", "is_trainable": "no",
                      "context_window": 2048}

    mc = ModelCatalog()
    mc.register_new_model_card(new_model_card)

    # Iterate through updated model catalog and ensure new model is present
    new_model_found = False
    for i, model in enumerate(mc.global_model_list):
        print(f"\n{i+1}. {model['model_name']}")
        if model['model_name'] == new_model_card["model_name"]:
            new_model_found = True 
    
    assert new_model_found == True


def test_add_new_model_name_to_catalog_in_prompt():

    # New model
    new_model_card = {"model_name": "llmware2", "display_name": "LLMWare-GPT2", "model_family": "LLMWareModel",
                      "model_category": "generative_api", "model_location": "api", "is_trainable": "no", "context_window": 2048}

    # create new Prompt object, which now has its own copy of the ModelCatalog() object
    prompter = Prompt()

    # register new model_card in the catalog associated with the prompt
    prompter.model_catalog.register_new_model_card(new_model_card)

    # Iterate through updated model catalog and ensure new model is present
    new_model_card = prompter.model_catalog.lookup_model_card(new_model_card["model_name"])
    assert new_model_card is not None
