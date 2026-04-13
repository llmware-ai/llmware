
""" This example shows how to use Windows Local Foundry models.

    pre-reqs:

    1. install local foundry, e.g., `winget install Microsoft.FoundryLocal`
    2. pip3 install foundry-local-sdk
    3. pip3 install openai (openai api used, but not openai model - all runs locally)
"""

from llmware.models import ModelCatalog, WindowsLocalFoundryHandler

# activate the connection and poll foundry-local instance for available models
foundry_handler = WindowsLocalFoundryHandler()
cat = foundry_handler.activate_catalog(True)

# foundry local models now added to the catalog
foundry_models = ModelCatalog().list_models_by_type("WindowsLocalFoundryModel")
for i, mod in enumerate(foundry_models):
    print("--foundry model - ", mod)

all_models = ModelCatalog().list_all_models()

# load foundry model like any other in llmware
# note: this example was used on a Windows Intel x86 Lunar Lake
# -- different platforms will have different supported models

m1 = "Phi-3.5-mini-instruct-openvino-gpu:1-foundry"
m2 = "qwen2.5-0.5b-instruct-generic-cpu:4-foundry"
model = ModelCatalog().load_model(m1, max_output=500)

for token in model.stream("What are the best sites to see in Rome?"):
    print(token, end="")

# stop foundry local server when done
WindowsLocalFoundryHandler().stop_server()


