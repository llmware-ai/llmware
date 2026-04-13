
""" This example illustrates parsing, text chunking, embedding and then querying ~80 legal documents.  The
example was originally developed for a joint webinar hosted with Milvus.   Please feel free to substitute
other vector databases in the example, if you prefer, along with changing the text collection DB from Mongo to
either SQLite or Postgres.

    The example uses sample documents (~80 legal template contracts) that can be pulled down with the command:
           sample_files_path = Setup().load_sample_files()
"""


import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup
from llmware.status import Status
from llmware.configs import LLMWareConfig


def parse_and_generate_vector_embeddings(library_name):

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

    # Step 3 - point ".add_files" method to the folder of documents that was just created
    #   this method parses all of the documents, text chunks, and captures in MongoDB
    print("update: Step 3 - Parsing and Text Indexing Files")

    library.add_files(input_folder_path=os.path.join(sample_files_path, "AgreementsLarge"))

    # Step 4 - Install the embeddings
    print("\nupdate: Step 4 - Generating Embeddings in {} db - with Model- {}".format(vector_db, embedding_model))

    library.install_new_embedding(embedding_model_name=embedding_model, vector_db=vector_db)

    # note: for using llmware as part of a larger application, you can check the real-time status by polling Status()
    #   --both the EmbeddingHandler and Parsers write to Status() at intervals while processing
    update = Status().get_embedding_status(library_name, embedding_model)
    print("update: Embeddings Complete - Status() check at end of embedding - ", update)

    # Step 5 - start using the new vector embeddings with Query
    sample_query = "incentive compensation"
    print("\n\nupdate: Step 5 - Query: {}".format(sample_query))

    query_results = Query(library).semantic_query(sample_query, result_count=20)

    for i, entries in enumerate(query_results):

        # each query result is a dictionary with many useful keys

        text = entries["text"]
        document_source = entries["file_source"]
        page_num = entries["page_num"]
        vector_distance = entries["distance"]

        #  for display purposes only, we will only show the first 100 characters of the text
        if len(text) > 125:  text = text[0:125] + " ... "

        print("\nupdate: query results - {} - document - {} - page num - {} - distance - {} "
              .format( i, document_source, page_num, vector_distance))

        print("update: text sample - ", text)


if __name__ == "__main__":

    LLMWareConfig().set_active_db("mongo")

    # pick any name for the library
    user_selected_name = "contracts"
    parse_and_generate_vector_embeddings(user_selected_name)

