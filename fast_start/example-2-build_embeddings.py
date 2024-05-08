
""""    Fast Start Example #2 - Embeddings - applying an embedding model to enable natural language queries

    In this example, we will show the basic recipe for creating embeddings on a library:

    1.  Create a sample library (see Example #1 for more details)
    2   Select an embedding model
    3.  Select a vector db
    4.  Install the embeddings
    5.  Run a semantic test query

    For purpose of this 'fast start', we will use a no-install option of 'chromadb' and 'sqlite'

    Note: we have updated the no-install vector db option to 'chromadb' from 'faiss' starting in
    llmware>=0.2.12, due to better support on Python 3.12

    Note: you may need to install chromadb's python driver:  `pip3 install chromadb`

    -- This same basic recipe will work with any of the vector db and collection db by simply changing the name

"""


import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup
from llmware.status import Status
from llmware.models import ModelCatalog
from llmware.configs import LLMWareConfig

from importlib import util
if not util.find_spec("chromadb"):
    print("\nto run this example with chromadb, you need to install the chromadb python sdk:  pip3 install chromadb")


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

    #   note: as of llmware==0.2.12, we have shifted from faiss to chromadb for the Fast Start examples
    #   --if you are using a Python version before 3.12, please feel free to substitute for "faiss"
    #   --for versions of Python >= 3.12, for the Fast Start examples (e.g., no install required), we
    #   recommend using chromadb or lancedb
    #   please double-check: `pip3 install chromadb` or pull the latest llmware version to get automatically

    #   -- if you have installed any other vector db, just change the name, e.g, "milvus" or "pg_vector"

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
    embedding_model = "mini-lm-sbert"

    #   note: if you want to swap out "mini-lm-sbert" for Open AI 'text-embedding-ada-002', uncomment these lines:
    #   embedding_model = "text-embedding-ada-002"
    #   os.environ["USER_MANAGED_OPENAI_API_KEY"] = "<insert-your-openai-api-key>"

    #   run the core script
    install_vector_embeddings(library, embedding_model)



