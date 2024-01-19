
"""This example shows how to easily create multiple embeddings over the same library with llmware

    This recipe can be especially useful when trying to compare the effectiveness of a particular
    embedding model for a specific domain or library corpus and to run other comparative experiments
    without being 'locked-in' to a particular model.

    Note: the example uses four different embedding models:

        1.  mini-lm-sbert - a favorite small, fast Sentence Transformer included in the llmware model catalog by default
        2.  text-embedding-ada-002 - the popular OpenAI embedding model
        3.  industry-bert-sec - an industry fine-tuned embedding model, in the llmware model catalog
        4.  all-mpnet-base-v2 - one of the most popular Sentence Transformers (which we will register and add to the
            model catalog on the fly

        To use OpenAI Ada will require an Open API key - if you do not have one, feel free to comment out or
        select a different model.  Any Sentence Transformer or Huggingface embedding model can be used.

"""


import os

from llmware.setup import Setup
from llmware.library import Library
from llmware.retrieval import Query
from llmware.models import ModelCatalog

os.environ["USER_MANAGED_OPENAI_API_KEY"] = "<INSERT YOUR OPEN API KEY HERE>"

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
    print("update: parsing and text indexing files")

    #   options:   Agreements | UN-Resolutions-500
    library.add_files(input_folder_path=os.path.join(sample_files_path, folder))

    return library


#   use multiple embedding models on the same library and the same vector db

def multiple_embeddings_same_db_same_lib(document_folder=None,sample_query=None,vector_db=None, base_library_name=None):

    print("\nupdate: Step 1- starting here- building library- parsing PDFs into text chunks")

    lib = build_lib(base_library_name, folder=document_folder)

    # optional - check the status of the library card and embedding
    lib_card = lib.get_library_card()
    print("update: library card - ", lib_card)

    print("\nupdate: Step 2 - starting to install embeddings")

    #   alt embedding models - "mini-lm-sbert" | industry-bert-contracts |  text-embedding-ada-002
    #   note: if you want to use text-embedding-ada-002, you will need an OpenAI key and enter into os.environ variable
    #   e.g., os.environ["USER_MANAGED_OPENAI_API_KEY"] = "<insert your key>"

    #   Note: batch size can be configured based on memory of machine and optimized for performance
    #   -- generally, between 100-500 is a safe range to optimize performance/memory

    print(f"\nupdate: Embedding #1 - mini-lm-sbert - {vector_db}")
    lib.install_new_embedding(embedding_model_name="mini-lm-sbert", vector_db=vector_db, batch_size=200)

    print(f"\nupdate: Embedding #2 - text-embedding-ada-002 - {vector_db}")
    lib.install_new_embedding(embedding_model_name="text-embedding-ada-002", vector_db=vector_db, batch_size=500)

    print(f"\nupdate: Embedding #3 - industry-bert-sec - {vector_db}")
    lib.install_new_embedding(embedding_model_name="industry-bert-sec", vector_db=vector_db, batch_size=100)

    # for the last embedding, we will register a popular open source sentence transformer model to use
    #   -- see "using_sentence_transformer.py" for more details

    ModelCatalog().register_sentence_transformer_model(model_name="all-mpnet-base-v2",
                                                       embedding_dims=768, context_window=384)

    # use directly now as an embedding model
    print(f"\nupdate: Embedding #4 - all-mpnet-base-v2 - {vector_db}")
    lib.install_new_embedding(embedding_model_name="all-mpnet-base-v2",vector_db=vector_db,batch_size=300)

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
    #        embedding record.

    query1 = Query(lib, embedding_model_name="mini-lm-sbert")
    query2 = Query(lib, embedding_model_name="text-embedding-ada-002")

    #   to execute query against any of the query objects
    minilm_results = query1.semantic_query(sample_query, result_count=12)
    ada_results = query2.semantic_query(sample_query, result_count=12)

    print("\n\nupdate: Sample Query using Embeddings")

    print("\nupdate: Embedding Model # 1 - MiniLM SBERT Results")
    for i, qr1 in enumerate(minilm_results):
        print("update: minilm semantic query results: ", i, qr1["distance"], qr1)

    print("\nupdate: Embedding Model # 2- Ada Results")
    for j, qr2 in enumerate(ada_results):
        print("update: ada semantic query results: ", j, qr2["distance"], qr2)

    return 0


if __name__ == "__main__":

    #   document folder options:  Agreements | UN-Resolutions-500
    #   note: Agreements = ~15 contracts = ~1272 embeddings - takes ~5 minutes to run (without GPU)
    #   note: UN-Resolutions-500 = 500 documents = ~12500 embeddings - takes ~15-20 minutes to run (without GPU)
    #       -- good sample query for UN-Resolutions, e.g. "what are key initiatives to promote sustainability?"
    #
    #   try substituting different vector-db, e.g, "pg_vector" | "redis" | "faiss"

    multiple_embeddings_same_db_same_lib(document_folder="Agreements",
                                         sample_query="what is the sale bonus?",
                                         vector_db="milvus",
                                         base_library_name="multi_embeddings_test_lib_0")



