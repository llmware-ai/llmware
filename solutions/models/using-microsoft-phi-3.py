
""" This example shows how to use the new Microsoft Phi-3 model. """

from llmware.models import ModelCatalog

#   phi-3 models pre-registered in the model catalog (as of Tues, April 23 when model launched):
#       phi-3 - "microsoft/Phi-3-mini-4k-instruct"
#       phi-3-128k - "microsoft/Phi-3-mini-128k-instruct"
#       phi-3-gguf - "microsoft/Phi-3-mini-4k-instruct-gguf"

#   first let's try the pytorch version
#   note: if not running on a cuda machine, you may see warnings about flash_attn not present
#   ... and it will be a little slow to load

phi3 = ModelCatalog().load_model("phi-3")       # use "phi-3-128k" for the 128k context
response = phi3.inference("I am going to Mumbai. What should I see?")
print("\nresponse: ", response)

#   second, use the gguf version
phi3_gguf = ModelCatalog().load_model("phi-3-gguf")

response = phi3_gguf.inference("I am going to Mumbai.  What should I see?")
print("\ngguf response: ", response)

#   now, try with a context sample
context = "The stock is now soaring to $120 per share after great earnings."
response = phi3_gguf.inference("What is the current stock price?", add_context=context)

print("\ngguf response: ", response)

