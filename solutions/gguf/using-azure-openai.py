
""" This example shows how to use OpenAIConfigs to create a configured OpenAI client, most often used for
Azure OpenAI access."""

import os

from llmware.models import ModelCatalog
from llmware.configs import OpenAIConfig
from openai import AzureOpenAI


#   Set the following environment variables:
#   - AZURE_OPENAI_ENDPOINT       : found on your Azure OpenAI page
#   - AZURE_OPENAI_API_KEY        : found on your Azure OpenAI page
#   - USER_MANAGED_OPENAI_API_KEY : found on you OpenAI API page
#
#   Additionally, with this example, you will need an Azure OpenAI deployment 
#   for gpt-4 and text-embedding-3-small, but feel free to replace these below.
#
#   Make sure to replace the deployment names with your deployments in the
#   AzureOpenAI clients created below.


#   to start - OpenAI client is created in OpenAI Generative and Embedding models classes at the time of inference
#   the client will be created as a standard OpenAI client with the api_keys passed

my_azure_client = OpenAIConfig().get_azure_client()
print("my azure client to start: ", my_azure_client)

#   to configure an AzureOpenAI client, two steps:
#   first, create the client with openai >= 1.0 python SDK, (see above) e.g.:

gpt4_client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),
  api_version="2024-02-01",
  azure_deployment="your-gpt-4-deployment-name"
)

#   second, set the azure client in OpenAIConfigs as below:
OpenAIConfig().set_azure_client(gpt4_client)
print("my azure client - set: ", OpenAIConfig().get_azure_client())

#   now, run the inference like any other in llmware

#   OpenAI Generative call
model = ModelCatalog().load_model("gpt-4")

#   the model will check the value of get_azure_client() in the configs -> if set, then will use
response = model.inference("What is the future of AI")
print("response: ", response)

text_embedding_client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),
  api_version="2024-02-01",
  azure_deployment="your-text-embedding-3-small-deployment-name"
)

OpenAIConfig().set_azure_client(text_embedding_client)

#   OpenAI Embedding call
model = ModelCatalog().load_model("text-embedding-3-small")
embedding = model.embedding(["This is a sample sentence for an embedding test."])
print("embedding: ", embedding)

#   reset so you can use the standard OpenAI client
OpenAIConfig().set_azure_client(None)

model = ModelCatalog().load_model("text-embedding-3-small", api_key=os.getenv("USER_MANAGED_OPENAI_API_KEY"))
embedding = model.embedding(["This is a sample sentence for an embedding test."])
print("embedding: ", embedding)
