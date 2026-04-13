
"""This example illustrates the basic capabilities of the Model Catalog and how to use"""

from llmware.models import ModelCatalog
from llmware.prompts import Prompt

# 1 - to list all of the models registered by default in llmware
mc = ModelCatalog().list_all_models()

print("\nAll-Models-List")
for i, models in enumerate(mc):
    print("update: models - ", i, models)


# 2 - to list all generative local models
gl_mc = ModelCatalog().list_generative_local_models()

print("\nGenerative-Local-Models-List")
for i, models in enumerate(gl_mc):
    print("update: gen local models - ", i, models)


# 3 - to add models to the catalog, e.g., sentence transformer

ModelCatalog().register_sentence_transformer_model("all-MiniLM-L6-v2", embedding_dims=384,
                                                   context_window=256)

"""
ModelRegistry().add_model_list({"model_name": "all-MiniLM-L6-v2", "model_category": "embedding",
                                "embedding_dims":384, "context_window":256, "model_family": "LLMWareSemanticModel",
                                "display_name": "MiniLM", "model_location": "st_repo"})
"""

# to confirm that model was added
model_card = ModelCatalog().lookup_model_card("all-MiniLM-L6-v2")
print("\nupdate: Registered new embedding model  - ", model_card)

# 4 - embedding models
emb_models = ModelCatalog().list_embedding_models()

# note: newly created 'all-MiniLM-L6-v2' will now be included
print("\nEmbedding-Models-List")
for i, models in enumerate(emb_models):
    print("update: embedding models - ", i, models)

# 5 - to delete model from catalog
ModelCatalog().delete_model_card("gpt-3.5-turbo")

# 6 - to load any model in the catalog
new_model = ModelCatalog().load_model("all-MiniLM-L6-v2")

# 7 - equivalent 'load_model' with any prompt
#   -- note:  if this model is not installed locally, this will pull it down into local cache
prompter = Prompt().load_model("llmware/bling-1b-0.1")

