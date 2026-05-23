
""" This example shows how to use the new Llama-3 Model with llmware, as well as how to access quantized versions. """

from llmware.models import ModelCatalog

#                               *** CORE PYTORCH LLAMA-3 MODELS ***

#   llama-3-8b models pre-registered in the model catalog:
#       llama-3-base - "Meta-Llama-3-8B-Instruct" or "llama-3-instruct"
#       llama-3-instruct - "Meta-Llama-3-8B" or "llama-3-base"

#   note: to access these models in llmware requires two pre-registration steps:
#   1.   meta-llama registration - https://llama.meta.com/docs/get-started/ - requires accepting the llama-3 licensing terms
#   2.   huggingface api key (does not require any payment, but you need a free HF account),
#           e.g., hf_key = "hf_...."

#   once you have completed these steps, you can access in llmware as follows:
#   #   llama3_model = ModelCatalog().load_model(selected_llama_model)

#                           *** LLAMA-3 GGUF MODELS ***

#   3 quantized models added to the default Model Catalog:
#       model_name = "bartowski/Meta-Llama-3-8B-Instruct-GGUF"
#       model_name = "QuantFactory/Meta-Llama-3-8B-Instruct-GGUF"
#       model_name = "QuantFactory/Meta-Llama-3-8B-GGUF"

l3_gguf = ModelCatalog().load_model("bartowski/Meta-Llama-3-8B-Instruct-GGUF")

response = l3_gguf.inference("Laws of motion ?")
print("\nllama3-gguf response: ", response)
