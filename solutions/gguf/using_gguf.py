
from llmware.prompts import Prompt
from llmware.models import ModelCatalog

#   Registered by default
#   --dragon models:  dragon-mistral-7b-gguf | dragon-yi-6b-gguf | dragon-llama-7b-gguf
#   --The Bloke leading 7b chat models:  llama2-chat | openhermes | zephyr | starling


#   example 1 - how to use a default gguf model in llmware
def use_default_gguf_model():

    selected_gguf_model = "llmware/dragon-mistral-7b-gguf"
    prompter = Prompt().load_model(selected_gguf_model)

    response = prompter.prompt_main("How old am I?", context="I am 36 years old.")

    print("response: ", response)

    return response


response = use_default_gguf_model()


#   example 2 - how to use any GGUF model from The Bloke on HuggingFace
def register_gguf_model():

    prompter = Prompt()

    your_model_name = "my_gguf_model_1"
    hf_repo_name = "TheBloke/model_name"
    model_file = "abc.gguf"

    prompter.model_catalog.register_gguf_model(your_model_name,hf_repo_name, model_file, prompt_wrapper="open_chat")
    prompter.load_model(your_model_name)

    return 0


#   example 3 - how to use build-from-source custom/optimized llama.cpp
def build_your_own_llama_cpp_lib():

    import os
    os.environ["GGUF_CUSTOM_LIB_PATH"] = "/path/to/your/custom/lib"

    return 0

