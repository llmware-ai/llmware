from llmware.library import Library # type: ignore
from llmware.retrieval import Query
from llmware.setup import Setup
from llmware.status import Status
from llmware.configs import LLMWareConfig

from importlib import util
if not util.find_spec("chromadb"):
    print("\nto run this example with chromadb, you need to install the chromadb python sdk:  pip3 install chromadb")


def setup_library(library_name):

    """ Note: this setup_library method is provided to enable a self-contained example to create a test library """

    print ("\nupdate: Creating library: {}".format(library_name))

    library = Library().create_new_library(library_name)

    embedding_record = library.get_embedding_status()
    print("embedding record - before embedding ", embedding_record)

    # sample_files_path = Setup().load_sample_files(over_write=False)

    library.add_files(input_folder_path='./files',
                      chunk_size=400, max_chunk_size=600, smart_chunking=1)

    return library


def install_vector_embeddings(library, embedding_model, sample_query):

    """ This method is the core example of installing an embedding on a library.
        -- two inputs - (1) a pre-created library object and (2) the name of an embedding model """

    library_name = library.library_name
    vector_db = LLMWareConfig().get_vector_db()

    print(f"\nupdate: Starting the Embedding: "
          f"library - {library_name} - "
          f"vector_db - {vector_db} - "
          f"model - {embedding_model}")

    #   *** this is the one key line of code to create the embedding ***
    library.install_new_embedding(embedding_model_name=embedding_model, vector_db=vector_db,batch_size=100)

    #   note: for using llmware as part of a larger application, you can check the real-time status by polling Status()
    #   --both the EmbeddingHandler and Parsers write to Status() at intervals while processing
    update = Status().get_embedding_status(library_name, embedding_model)
    # print("update: Embeddings Complete - Status() check at end of embedding - ", update)

    # Start using the new vector embeddings with Query
    # sample_query = " No  citizen  of  Nepal  may  be  deprived  of  the  right to obtain citizenship"
    # print("\n\nupdate: Run a sample semantic/vector query: {}".format(sample_query))

    #   queries are constructed by creating a Query object, and passing a library as input
    query_results = Query(library).semantic_query(sample_query, result_count=20)

    # Initialize an empty list to store the first five dictionaries
    first_five_dicts = []

    # Iterate over the query results and extract the necessary fields
    for i, entries in enumerate(query_results):
        # Extract the fields from the current dictionary
        text = entries["text"]
        document_source = entries["file_source"]
        page_num = entries["page_num"]
        vector_distance = entries["distance"]
        
        # Create a new dictionary with the extracted fields
        current_dict = {
            "context": text,
            "page_num": page_num,
            "file_source": document_source,
            "distance": vector_distance
        }
        
        # Append the new dictionary to the list if it's one of the first five
        if i < 5:
            first_five_dicts.append(current_dict)

    return first_five_dicts


