
"""
    This example shows how to use 'Open Chat' inference models that expose an endpoint compatible with the
    OpenAI API - using 'api_base' to configure the endpoint uri

    For example, to integrate a model on LM Studio with standard configuration:
        -- api_base = 'http://localhost:1234/v1'

    Please also note that llmware implements llama.cpp directly, so you can run inference on any GGUF models
    very easily and natively in llmware - see the GGUF example in /Models/using_gguf.py'
"""


from llmware.models import ModelCatalog
from llmware.prompts import Prompt


#   one step process:  add the open chat model to the Model Registry
#   key params:
#       model_name      =   "my_open_chat_model1"
#       api_base        =   uri_path to the proposed endpoint
#       prompt_wrapper  =   alpaca | <INST> | chat_ml | hf_chat | human_bot
#                           <INST>      ->  Llama2-Chat
#                           hf_chat     ->  Zephyr-Mistral
#                           chat_ml     ->  OpenHermes - Mistral
#                           human_bot   ->  Dragon models
#       model_type      =   "chat" (alternative:  "completion")

ModelCatalog().register_open_chat_model("my_open_chat_model1",
                                        api_base="http://localhost:1234/v1",
                                        prompt_wrapper="<INST>",
                                        model_type="chat")

#   once registered, you can invoke like any other model in llmware

prompter = Prompt().load_model("my_open_chat_model1")
response = prompter.prompt_main("What is the future of AI?")


#   you can (optionally) register multiple open chat models with different api_base and model attributes

ModelCatalog().register_open_chat_model("my_open_chat_model2",
                                        api_base="http://localhost:5678/v1",
                                        prompt_wrapper="hf_chat",
                                        model_type="chat")


#   you can also alternate with open ai models - which will 'revert' to the default openai api_base

openai_prompter = Prompt().load_model("gpt-3.5.-turbo-instruct")


#   if you list all of the models in the catalog, you will see the two newly created open chat models

my_models = ModelCatalog().list_all_models()

for i, mods in enumerate(my_models):
    print("models: ", i, mods)


