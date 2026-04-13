
""" This example illustrates parsing, text chunking, embedding and then executing in a RAG prompt process using
~80 legal documents.  The example was originally developed for a joint webinar hosted with Milvus.

    Please feel free to substitute other vector databases in the example, if you prefer.

    The example uses sample documents (~80 legal template contracts) that can be pulled down with the command:
           sample_files_path = Setup().load_sample_files()
"""


import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup
from llmware.status import Status
from llmware.prompts import Prompt
from llmware.configs import LLMWareConfig


def rag (library_name):

    # Step 0 - Configuration - we will use these in Step 4 to install the embeddings
    embedding_model = "industry-bert-contracts"
    vector_db = "milvus"

    # Step 1 - Create library which is the main 'organizing construct' in llmware
    print ("\nupdate: Step 1 - Creating library: {}".format(library_name))

    library = Library().create_new_library(library_name)

    # Step 2 - Pull down the sample files from S3 through the .load_sample_files() command
    #   --note: if you need to refresh the sample files, set 'over_write=True'
    print ("update: Step 2 - Downloading Sample Files")

    sample_files_path = Setup().load_sample_files(over_write=False)
    contracts_path = os.path.join(sample_files_path, "Agreements")

    # Step 3 - point ".add_files" method to the folder of documents that was just created
    #   this method parses all of the documents, text chunks, and captures in MongoDB
    print("update: Step 3 - Parsing and Text Indexing Files")

    library.add_files(input_folder_path=contracts_path)

    # Step 4 - Install the embeddings
    print("\nupdate: Step 4 - Generating Embeddings in {} db - with Model- {}".format(vector_db, embedding_model))

    library.install_new_embedding(embedding_model_name=embedding_model, vector_db=vector_db)

    # note: for using llmware as part of a larger application, you can check the real-time status by polling Status()
    #   --both the EmbeddingHandler and Parsers write to Status() at intervals while processing
    update = Status().get_embedding_status(library_name, embedding_model)
    print("update: Embeddings Complete - Status() check at end of embedding - ", update)

    print("\nupdate: Loading 1B parameter BLING model for LLM inference")

    prompter = Prompt().load_model("llmware/bling-1b-0.1")
    query = "what is the executive's base annual salary"

    results = Query(library).semantic_query(query, result_count=50, embedding_distance_threshold=1.0)

    for i, res in enumerate(results):

        print("update: ", i, res["file_source"], res["distance"], res["text"])

    for i, contract in enumerate(os.listdir(contracts_path)):

        qr = []

        if contract != ".DS_Store":

            print("\nContract Name: ", i, contract)

            for j, entries in enumerate(results):
                if entries["file_source"] == contract:
                    print("Top Retrieval: ", j, entries["distance"], entries["text"])
                    qr.append(entries)

            source = prompter.add_source_query_results(query_results=qr)
            response = prompter.prompt_with_source(query, prompt_name="default_with_context", temperature=0.3)

            for resp in response:
                if "llm_response" in resp:
                    print("\nupdate: llm answer - ", resp["llm_response"])

            # start fresh for next document
            prompter.clear_source_materials()


if __name__ == "__main__":

    #   feel free to change to sqlite or postgres (if installed)
    LLMWareConfig().set_active_db("mongo")

    # pick any name for the library
    user_selected_name = "contracts_rag10"
    rag(user_selected_name)


