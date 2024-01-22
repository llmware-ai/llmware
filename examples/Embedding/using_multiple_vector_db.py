
"""This example shows how to use a single library and attach 'mix-and-match' multiple vector databases with
    potentially multiple different embedding models

    Use case:   evaluate and compare multiple combinations of vector databases and embedding models using the
                same core text library - without having to recreate - enables fast experimentation without lock-in.

    Note:
        -- the example belows requires installation of several vector db- Milvus, PGVector, Redis and FAISS
        -- docker-compose scripts for rapid install for Milvus, PGVector and Redis in the llmware repository
        -- no install required for FAISS
        -- please also see the install instructions in the Examples/Embeddings for more install pre-reqs, e.g.,:
                --Milvus: pip install pymilvus
                --Redis-Stack-Server: pip install redis
                --Postgres:  pip install psycopg-binary psycopg pgvector
    """

import os

from llmware.setup import Setup
from llmware.library import Library
from llmware.retrieval import Query
from llmware.models import ModelCatalog

os.environ["USER_MANAGED_OPENAI_API_KEY"] = "<INSERT YOUR OPEN AI KEY HERE>"

os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Avoid a HuggingFace tokenizer warning


#   Note:  this will build a small library that will be used in the embedding examples
def build_lib (library_name, folder="Agreements"):

    # Step 1 - Create library which is the main 'organizing construct' in llmware
    print ("\nupdate: creating library: {}".format(library_name))

    library = Library().create_new_library(library_name)

    # Step 2 - Pull down the sample files from S3 through the .load_sample_files() command
    #   --note: if you need to refresh the sample files, set 'over_write=True'
    print ("update: downloading sample files")

    sample_files_path = Setup().load_sample_files(over_write=False)

    # Step 3 - point ".add_files" method to the folder of documents that was just created
    #   this method parses the documents, text chunks, and captures in MongoDB
    print("update: parsing and text indexing Files")

    #   options:   Agreements | UN-Resolutions-500
    library.add_files(input_folder_path=os.path.join(sample_files_path, folder))

    return library


def multiple_embeddings_and_multiple_vector_dbs(document_folder=None,sample_query="", base_library_name=""):

    print("\nupdate: Step 1- starting here- building library- parsing PDFs into text chunks")

    lib = build_lib(base_library_name, folder=document_folder)

    # optional - check the status of the library card and embedding
    lib_card = lib.get_library_card()
    print("update: library card - ", lib_card)

    print("\nupdate: Step 2 - starting to install embeddings")

    #   mix-and-match with different embedding models and vector db on same library content

    #   We will create 6 different embeddings across 4 different vector databases - using the same library
    #   note: you can run many different models on the same db, or the same model across multiple dbs

    print("\nupdate: Embedding #1 - industry-bert-contracts - on PG_Vector")
    lib.install_new_embedding(embedding_model_name="industry-bert-contracts",vector_db="pg_vector",batch_size=300)

    print("\nupdate: Embedding #2 - mini-lm-sbert - Milvus")
    lib.install_new_embedding(embedding_model_name="mini-lm-sbert", vector_db="milvus", batch_size=200)

    print("\nupdate: Embedding #3 - mini-lm-sbert - on PG_Vector")
    lib.install_new_embedding(embedding_model_name="mini-lm-sbert", vector_db="pg_vector", batch_size=100)

    print("\nupdate: Embedding #4 - text-embedding-ada-002 - FAISS")
    lib.install_new_embedding(embedding_model_name="text-embedding-ada-002", vector_db="faiss", batch_size=500)

    print("\nupdate: Embedding #5 - industry-bert-sec - REDIS")
    lib.install_new_embedding(embedding_model_name="industry-bert-sec", vector_db="redis", batch_size=350)

    # for the last embedding, we will register a pretrained sentence transformer model to use
    #   -- see "using_sentence_transformer.py" for more details
    ModelCatalog().register_sentence_transformer_model(model_name= "all-MiniLM-L6-v2",
                                                       embedding_dims=384, context_window=256)

    # use directly now as an embedding model
    print("\nupdate: Embedding #6 - all-MiniLM-L6-v2 - REDIS")
    lib.install_new_embedding(embedding_model_name="all-MiniLM-L6-v2",vector_db="redis",batch_size=300)

    #   optional - check the embeddings on the library
    print("\nupdate: Embedding record of the Library")
    emb_record = lib.get_embedding_status()
    for j, entries in enumerate(emb_record):
        print("update: embeddings on library: ", j, entries)

    #   Using the Embeddings to Execute Queries
    #
    #   create query object:
    #   1.  if no embedding_model or vector_db passed in constructor, then selects the LAST embedding record, which
    #        is the most recent embedding on the library, and uses that combination of model + vector db
    #
    #   2.  if embedding_model_name only passed, then looks up the first instance of that embedding model
    #       in the embedding record, and will use the associated vector db
    #
    #   3.  if both embedding_model_name and vector_db passed in constructor, then looks up that combo in
    #        embedding record

    q = Query(lib, embedding_model_name="mini-lm-sbert", vector_db="pg_vector")

    #   to execute query against any of the query objects:
    #   --just showing one example
    my_search_results = q.semantic_query(sample_query, result_count=15)

    print("\n\nupdate: Sample Query using Embeddings")

    for i, qr in enumerate(my_search_results):
        print("update: semantic query results: ", i, qr)

    # if you want to delete any of the embeddings  - uncomment the line below
    # lib.delete_installed_embedding("industry-bert-contracts", "pg_vector")

    return 0


if __name__ == "__main__":

    multiple_embeddings_and_multiple_vector_dbs(document_folder="Agreements",
                                                sample_query="what is the base salary?",
                                                base_library_name="multi-embedding-multi-db-test-1")


