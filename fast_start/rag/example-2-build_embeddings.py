
"""    Fast Start Example #2 - Embeddings - applying an embedding model to enable natural language queries

    In this example, we will show the basic recipe for creating embeddings on a library:

    1.  Create a sample library (see Example #1 for more details)
    2   Select an embedding model
    3.  Select a vector db
    4.  Install the embeddings
    5.  Run a semantic test query

    For purpose of this 'fast start', we will use a no-install option of 'sqlite' as our text collection database

    Note: to run this example with a sentence transformers 'local' open source embedding model,
    you may need to install additional dependencies:

        `pip3 install transformers`
        `pip3 install torch`

    We would recommend any of the following 'no-install' vector db options:

        -- milvus lite:  `pip3 install pymilvus`      [available starting in llmware>=0.3.0 on Mac/Linux]
        -- chromadb:     `pip3 install chromadb`
        -- lancedb:      `pip3 install lancedb`
        -- faiss:        `pip3 install faiss`

    -- This same basic recipe will work with any of the vector db and collection db by simply changing the name

"""


import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup
from llmware.status import Status
from llmware.models import ModelCatalog
from llmware.configs import LLMWareConfig, MilvusConfig

from importlib import util

#   generate warnings if key dependencies not involved
if not util.find_spec("torch") or not util.find_spec("transformers"):
    print("\nto run this example, with the selected embedding model, please install transformers and torch, e.g., "
          "\n`pip install torch`"
          "\n`pip install transformers`")

if not (util.find_spec("chromadb") or util.find_spec("pymilvus") or util.find_spec("lancedb") or util.find_spec("faiss")):
    print("\nto run this example, you will need to pip install the vector db drivers. see comments above.")


def setup_library(library_name):

    """ Note: this setup_library method is provided to enable a self-contained example to create a test library """

    #   Step 1 - Create library which is the main 'organizing construct' in llmware
    print ("\nupdate: Creating library: {}".format(library_name))

    library = Library().create_new_library(library_name)

    #   check the embedding status 'before' installing the embedding
    embedding_record = library.get_embedding_status()
    print("embedding record - before embedding ", embedding_record)

    #   Step 2 - Pull down the sample files from S3 through the .load_sample_files() command
    #   --note: if you need to refresh the sample files, set 'over_write=True'
    print ("update: Downloading Sample Files")

    sample_files_path = Setup().load_sample_files(over_write=False)

    #   Step 3 - point ".add_files" method to the folder of documents that was just created
    #   this method parses the documents, text chunks, and captures in database

    print("update: Parsing and Text Indexing Files")

    library.add_files(input_folder_path=os.path.join(sample_files_path, "Agreements"),
                      chunk_size=400, max_chunk_size=600, smart_chunking=1)

    return library


def install_vector_embeddings(library, embedding_model_name):

    """ This method is the core example of installing an embedding on a library.
        -- two inputs - (1) a pre-created library object and (2) the name of an embedding model """

    library_name = library.library_name
    vector_db = LLMWareConfig().get_vector_db()

    print(f"\nupdate: Starting the Embedding: "
          f"library - {library_name} - "
          f"vector_db - {vector_db} - "
          f"model - {embedding_model_name}")

    #   *** this is the one key line of code to create the embedding ***
    library.install_new_embedding(embedding_model_name=embedding_model, vector_db=vector_db,batch_size=100)

    #   note: for using llmware as part of a larger application, you can check the real-time status by polling Status()
    #   --both the EmbeddingHandler and Parsers write to Status() at intervals while processing
    update = Status().get_embedding_status(library_name, embedding_model)
    print("update: Embeddings Complete - Status() check at end of embedding - ", update)

    # Start using the new vector embeddings with Query
    sample_query = "incentive compensation"
    print("\n\nupdate: Run a sample semantic/vector query: {}".format(sample_query))

    #   queries are constructed by creating a Query object, and passing a library as input
    query_results = Query(library).semantic_query(sample_query, result_count=20)

    for i, entries in enumerate(query_results):

        #   each query result is a dictionary with many useful keys

        text = entries["text"]
        document_source = entries["file_source"]
        page_num = entries["page_num"]
        vector_distance = entries["distance"]

        #   to see all of the dictionary keys returned, uncomment the line below
        #   print("update: query_results - all - ", i, entries)

        #  for display purposes only, we will only show the first 125 characters of the text
        if len(text) > 125:  text = text[0:125] + " ... "

        print("\nupdate: query results - {} - document - {} - page num - {} - distance - {} "
              .format( i, document_source, page_num, vector_distance))

        print("update: text sample - ", text)

    #   lets take a look at the library embedding status again at the end to confirm embeddings were created
    embedding_record = library.get_embedding_status()

    print("\nupdate:  embedding record - ", embedding_record)

    return 0


if __name__ == "__main__":

    #   Fast Start configuration - will use no-install embedded sqlite
    #   -- if you have installed Mongo or Postgres, then change the .set_active_db accordingly

    LLMWareConfig().set_active_db("sqlite")

    #   Select a 'no install' vector db

    #   note: starting with llmware>=0.3.0, we support the new milvus lite - you can ignore or comment out if
    #   using a different vector db - and note: only available on mac/linux
    MilvusConfig().set_config("lite", True)

    #   select one of:  'milvus' | 'chromadb' | 'lancedb' | 'faiss'
    #   note: if you run into an error with chromadb, please update to the latest version of llmware==0.3.10 which fixes the issue  
    LLMWareConfig().set_vector_db("chromadb")

    #  Step 1 - this example requires us to have a library created - two options:

    #  if you completed example-1 - then load the library you created in that example, e.g., "example1_library"
    #  uncomment the line below:
    #  library = Library().load_library("example1_library")

    #  alternatively, to use this example as self-contained, then create a new library from scratch:
    library = setup_library("example2_library")

    #   Step 2 - Select any embedding model in the LLMWare catalog

    #   to see a list of the embedding models supported, uncomment the line below and print the list
    embedding_models = ModelCatalog().list_embedding_models()

    #   for i, models in enumerate(embedding_models):
    #       print("embedding models: ", i, models)

    #   for this first embedding, we will use a very popular and fast sentence transformer
    #   -- these models require `pip3 install transformers` and `pip3 install torch`
    embedding_model = "mini-lm-sbert"

    #   note: if you want to swap out "mini-lm-sbert" for Open AI 'text-embedding-ada-002', then:
    #   1.  you do not need to import transformers or torch
    #   2.  you should `pip3 install openai`
    #   3.  you should uncomment these lines:
    #   embedding_model = "text-embedding-ada-002"
    #   os.environ["USER_MANAGED_OPENAI_API_KEY"] = "<insert-your-openai-api-key>"

    #   run the core script
    install_vector_embeddings(library, embedding_model)



