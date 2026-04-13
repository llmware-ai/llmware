import marimo

__generated_with = "0.5.2"
app = marimo.App()


@app.cell
def __():
    import marimo as mo
    return mo,


@app.cell
def __(mo):
    mo.md(""""    Fast Start Example #2 - Embeddings - applying an embedding model to enable natural language queries

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

    """)
    return


@app.cell
def __(mo):
    mo.md(f"\n**Step 0** - Import libraries, set database, initialize libraries, create sample folder, select embedding model")
    return


@app.cell
def __():
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
    return (
        LLMWareConfig,
        Library,
        ModelCatalog,
        Query,
        Setup,
        Status,
        os,
        util,
    )


@app.cell
def __(LLMWareConfig):
    LLMWareConfig().set_active_db("sqlite")
    LLMWareConfig().set_vector_db("chromadb")
    return


@app.cell
def __(ModelCatalog):
    embedding_models = ModelCatalog().list_embedding_models()
    embedding_model = "mini-lm-sbert"
    return embedding_model, embedding_models


@app.cell
def __():
    library_name = "example2_library"
    return library_name,


@app.cell
def __(mo):
    mo.md(" \n**1** - Create library")
    return


@app.cell
def __(mo):
    mo.md(" \n**Step 1** - Create library which is the main 'organizing construct' in llmware")
    return


@app.cell
def __(Library, library_name):
    print ("\nupdate: Creating library: {}".format(library_name))

    library = Library().create_new_library(library_name)

    #   check the embedding status 'before' installing the embedding
    embedding_record = library.get_embedding_status()
    print("embedding record - before embedding ", embedding_record)
    return embedding_record, library


@app.cell
def __(mo):
    mo.md("\n**Step 2** - Pull down the sample files from S3 through the .load_sample_files() command")
    return


@app.cell
def __(Setup):
    #   --note: if you need to refresh the sample files, set 'over_write=True'
    print ("update: Downloading Sample Files")

    sample_files_path = Setup().load_sample_files(over_write=False)
    return sample_files_path,


@app.cell
def __(mo):
    mo.md("\n **Step 3** - point .add_files method to the folder of documents that was just created")
    return


@app.cell
def __(library, os, sample_files_path):
    #   this method parses the documents, text chunks, and captures in database

    print("update: Parsing and Text Indexing Files")

    library.add_files(input_folder_path=os.path.join(sample_files_path, "Agreements"),
                      chunk_size=400, max_chunk_size=600, smart_chunking=1)
    return


@app.cell
def __(mo):
    mo.md("\n **2** - Install Vector Embeddings")
    return


@app.cell
def __(LLMWareConfig, embedding_model, library):
    """ This method is the core example of installing an embedding on a library.
        -- two inputs - (1) a pre-created library object and (2) the name of an embedding model """

    library_name_ = library.library_name
    vector_db = LLMWareConfig().get_vector_db()

    print(f"\nupdate: Starting the Embedding: "
          f"library - {library_name_} - "
          f"vector_db - {vector_db} - "
          f"model - {embedding_model}")
    return library_name_, vector_db


@app.cell
def __(Status, embedding_model, library, library_name_, vector_db):

    #   *** this is the one key line of code to create the embedding ***
    library.install_new_embedding(embedding_model_name=embedding_model, vector_db=vector_db,batch_size=100)

    #   note: for using llmware as part of a larger application, you can check the real-time status by polling Status()
    #   --both the EmbeddingHandler and Parsers write to Status() at intervals while processing
    update = Status().get_embedding_status(library_name_, embedding_model)
    print("update: Embeddings Complete - Status() check at end of embedding - ", update)

    return update,


@app.cell
def __(Query, library):

    # Start using the new vector embeddings with Query
    sample_query = "incentive compensation"
    print("\n\nupdate: Run a sample semantic/vector query: {}".format(sample_query))

    #   queries are constructed by creating a Query object, and passing a library as input
    query_results = Query(library).semantic_query(sample_query, result_count=20)
    return query_results, sample_query


@app.cell
def __(library, query_results):
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
    embedding_record_ = library.get_embedding_status()

    print("\nupdate:  embedding record - ", embedding_record_)
    return (
        document_source,
        embedding_record_,
        entries,
        i,
        page_num,
        text,
        vector_distance,
    )


if __name__ == "__main__":
    app.run()