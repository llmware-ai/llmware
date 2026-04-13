
"""This example demonstrates working with MongoDB Atlas.  You can use Mongo Atlas in 2 ways:

1. Only as a vector DB (and use local or another mongo for data storage)
   In this case, you can set the following environment variable:
      MONGO_ATLAS_CONNECTION_URI=mongo+srv://<username>:<password>@<cluster-domain>...

2. For both vector and data storage
   In this case, you can set the following environment configuration:
      LLMWareConfig().set_config("collection_db_uri", "mongo+srv://<username>:<password>@<cluster-domain>..."

This example demonstrates the 2nd approach.

"""

import os
from llmware.configs import LLMWareConfig
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup


# Use MongoDB Atlas for both data storage and vector embedding storage/search


def using_mongo_atlas(mongo_atlas_connection_string):

    LLMWareConfig().set_config("collection_db_uri", mongo_atlas_connection_string)

    # Create a library and populate it with some sample documents

    library_name = "test_mongo_atlas"
    print(f"\n > Creating library {library_name}...")

    library = Library().create_new_library(library_name)
    print(f"\n > Loading the llmware Sample Files...")

    sample_files_path = Setup().load_sample_files()
    print(f"\n > Adding some files to the library...")

    library.add_files(input_folder_path=os.path.join(sample_files_path, "Agreements"))

    # Create vector embeddings using Mongo Atlas
    print(f"\n > Generating embedding vectors (using the 'mini-lm-sbert' model) and storing them (in 'Mongo Atlas')...")
    library.install_new_embedding(embedding_model_name="mini-lm-sbert", vector_db="mongo_atlas")

    # Do a semantic search in the library
    print(f"\n > Running a query for 'Salary'...")
    query_results = Query(library).semantic_query(query="salary", result_count=10, results_only=True)

    print(f"\n\nResults for 'Salary' in {library_name}:\n")
    for query_result in query_results:
        print(
            "File: " + query_result["file_source"] + " (Page " + str(query_result["page_num"]) + "):\n" + query_result[
                "text"] + "\n")

    return query_results


if __name__ == "__main__":

    # Set this env var appropriately or just paste in your Mongo Atlas connection string:
    mongo_config = os.environ["MONGO_ATLAS_CONNECTION_URI"]

    output = using_mongo_atlas(mongo_config)






