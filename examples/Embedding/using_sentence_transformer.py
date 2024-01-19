
"""This example shows how to use sentence transformers as a vector embedding model with llmware"""

"""Note: this example illustrates capability from llmware==0.1.13 - please update pip install, or pull from repo"""


import os

from llmware.setup import Setup
from llmware.library import Library
from llmware.retrieval import Query
from llmware.models import ModelCatalog


def build_lib (library_name, folder="Agreements"):

    # Step 1 - Create library which is the main 'organizing construct' in llmware
    print ("\nupdate: Step 1 - Creating library: {}".format(library_name))

    library = Library().create_new_library(library_name)

    # Step 2 - Pull down the sample files from S3 through the .load_sample_files() command
    #   --note: if you need to refresh the sample files, set 'over_write=True'
    print ("update: Step 2 - Downloading Sample Files")

    sample_files_path = Setup().load_sample_files(over_write=False)

    # Step 3 - point ".add_files" method to the folder of documents that was just created
    #   this method parses the documents, text chunks, and captures in MongoDB
    print("update: Step 3 - Parsing and Text Indexing Files")

    #   options:   Agreements | UN-Resolutions-500
    library.add_files(input_folder_path=os.path.join(sample_files_path, folder))

    return library


# start script

print("update: Step 1- starting here- building library- parsing PDFs into text chunks")

lib = build_lib("st_embedding_0_454")

#   register a model from the sentence transformers library/repository

#   note: "all-MiniLM-L6-v2" is from the SentenceTransformer catalog, e.g.,
#       -- https://www.sbert.net/docs/pretrained_models.html
#       -- key inputs to register:
#           -- "model_name" - should be an existing pre-trained model in the SentenceTransformer catalog
#           -- "embedding_dims" - this is the output dimensions, included in the sbert model card info
#           -- "context_window" - included in the sbert model card info
#           -- *** "model_location" - "st_repo" is reserved word to tell llmware to look in sentence transformers ***
#           -- *** "model_family" - "LLMWareSemanticModel" - knows how to load and embed with sentence transformers ***

#   another sentence transformer to try:  "all-mpnet-base-v2" - embedding_dims = 768 - context_window = 384

sentence_transformer_pretrained_model_name = "all-MiniLM-L6-v2"
embedding_dims = 384
context_window = 256

ModelCatalog().register_sentence_transformer_model(model_name=sentence_transformer_pretrained_model_name,
                                                   embedding_dims=embedding_dims, context_window=context_window)

"""
ModelCatalog().add_model_list({"model_name": sentence_transformer_pretrained_model_name,
                                "embedding_dims":embedding_dims,
                                "context_window":context_window,
                                "model_category": "embedding",
                                "model_family": "LLMWareSemanticModel",
                                "display_name": "MySentenceTransformer", "model_location": "st_repo"})
"""

# to confirm that model has been added to the catalog
mc = ModelCatalog().list_all_models()
model_card = ModelCatalog().lookup_model_card(sentence_transformer_pretrained_model_name)
print("update: model card - ", model_card)

# use directly now as an embedding model
lib.install_new_embedding(embedding_model_name=sentence_transformer_pretrained_model_name,
                          vector_db="milvus",batch_size=300)

#   optional - check the status of the library card and embedding
lib_card = lib.get_library_card()
print("update: -- after embedding process - check updated library card - ", lib_card)

#   create query object (note: including embedding_model is optional - only needed if multiple embeddings on library)
query_st = Query(lib, embedding_model_name=sentence_transformer_pretrained_model_name)

#   run multiple queries using query_pgv
my_search_results = query_st.semantic_query("What is the sale bonus?", result_count = 24)

for i, qr in enumerate(my_search_results):
    print("update: semantic query results: ", i, qr)

# if you want to delete the embedding  - uncomment the line below - including the model_name and vector_db
# lib.delete_installed_embedding(sentence_transformer_pretrained_model_name, "milvus")

#   optional - check the embeddings on the library
emb_record = lib.get_embedding_status()
for j, entries in enumerate(emb_record):
    print("update: embeddings on library: ", j, entries)

