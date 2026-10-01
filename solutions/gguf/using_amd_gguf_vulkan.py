
""" Using GGUF VULKAN on AMD GPU - this example illustrates how to toggle the llama.cpp backend
    to access the GPU on AMD devices.  A precompiled GGUF VULKAN backend for AMD is included with
    llmware.
"""


from llmware.models import ModelCatalog
from llmware.gguf_configs import GGUFConfigs

#   toggle the default backend for windows x86 llama cpp
#   this will point to the default amd gguf vulkan backend packaged with llmware
GGUFConfigs().set_config("windows_x86_lib", "gguf_win_amd_vulkan")

#   alternatively, you can point to a custom path for your own llama cpp backend
#   enter the full local path to a folder containing the standard llama.cpp binaries
#   e.g., llama.dll, ggml, etc.
#   e.g., GGUFConfigs().set_config("custom_lib_path", "")

gguf_model_name = "llama-3.2-3b-instruct-gguf"

text_out = ""
token_count = 0
prompt = "Explain the main concepts of quantum mechanics."

#   maximum output can be set optionally at any number up to the "max_output_tokens" set
model = ModelCatalog().load_model(gguf_model_name, max_output=500)

for streamed_token in model.stream(prompt):

    text_out += streamed_token
    if text_out.strip():
        print(streamed_token, end="")

    token_count += 1

#   final output text and token count

print("\n\n***total text out***: ", text_out)
print("\n***total tokens***: ", token_count)
