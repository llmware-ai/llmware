
""" This example shows how to use OpenAIConfigs to create a configured OpenAI client, most often used for
Azure OpenAI access."""

import os

from llmware.models import ModelCatalog
from llmware.configs import OpenAIConfig
from openai import AzureOpenAI, OpenAI


#   to start - OpenAI client is created in OpenAI Generative and Embedding models classes at the time of inference
#   the client will be created as a standard OpenAI client with the api_keys passed

my_azure_client = OpenAIConfig().get_azure_client()
print("my azure client to start: ", my_azure_client)

#   to configure an AzureOpenAI client, two steps:
#   first, create the client with openai >= 1.0 python SDK, (see above) e.g.:

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),
  api_version="2024-02-01"
)

#   second, set the azure client in OpenAIConfigs as below:
OpenAIConfig().set_azure_client(client)
print("my azure client - set: ", OpenAIConfig().get_azure_client())

#   now, run the inference like any other in llmware

#   OpenAI Generative call
model = ModelCatalog().load_model("gpt-4")

#   the model will check the value of get_azure_client() in the configs -> if set, then will use
response = model.inference("What is the future of AI")
print("response: ", response)

#   OpenAI Embedding call
model = ModelCatalog().load_model("text-embedding-3-small")
embedding = model.embedding(["This is a sample sentence for an embedding test."])
print("embedding: ", embedding)

#   reset so you can use the standard OpenAI client
OpenAIConfig().set_azure_client(None)

model = ModelCatalog().load_model("text-embedding-3-small", api_key="your openai api key")
embedding = model.embedding(["This is a sample sentence for an embedding test."])
print("embedding: ", embedding)

