
import sys

from llmware.models import ModelCatalog, LLMWareInferenceServer

# note: will need to pip install transformers & flask

custom_models = [

        # add custom models - in this case - not needed, since these are directly in the new catalog
        # -- this creates the opportunity for us to offer 'privately available' versions of models

        {"model_name": "llmware/bling-sheared-llama-2.7b-0.1", "display_name": "dragon-sheared_llama_2.7b",
         "model_family": "HFGenerativeModel", "model_category": "generative-api", "model_location": "api",
         "is_trainable": "no", "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
         "temperature": 0.3},

        {"model_name": "llmware/bling-red-pajamas-3b-0.1", "display_name": "dragon-rp-3b",
         "model_family": "HFGenerativeModel", "model_category": "generative-api", "model_location": "api",
         "is_trainable": "no", "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
         "temperature": 0.3}

    ]


if __name__ == "__main__":

    custom_model_catalog = ModelCatalog()
    for model_card in custom_models:
        custom_model_catalog.register_new_model_card(model_card)

    model_selection = "llmware/bling-red-pajamas-3b-0.1"

    # different models can be selected by adding as parameter on the launch command line
    if len(sys.argv) > 1:
        model_selection = sys.argv[1]

    print("update: model selection - ", model_selection)

    #   pulls down and instantiates the selected model and then launches a very simple Flask-based API server
    #   --on the client side, will need the uri_string for the server + the secret_api_key

    LLMWareInferenceServer(model_selection,
                           model_catalog=custom_model_catalog,
                           secret_api_key="demo-test",
                           home_path="/home/paperspace/").start()

