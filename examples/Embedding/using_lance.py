
"""This example demonstrates creating vector embeddings (used for doing semantic queries)
      Note: lancedb is not used in the example below as it requires an API key.  If you have a lancedb account, you can set these two variables:
         os.environ.get("USER_MANAGED_lancedb_API_KEY") = <your-lancedb-api-key>
         os.environ.get("USER_MANAGED_lancedb_ENVIRONMENT") = <your-lancedb-environment> (for example "gcp-starter")
"""

import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup


def embeddings_lancedb (library_name):

    # Create and populate a library
    print (f"\nstep 1 - creating and populating library: {library_name}...")
    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files()
    library.add_files(input_folder_path=os.path.join(sample_files_path, "Agreements"))

    # To create vector embeddings you just need to specify the embedding model and the vector embedding DB
    # For examples of using HuggingFace and SentenceTransformer models, see those examples in this same folder

    embedding_model = "mini-lm-sbert"

    print (f"\n > Generating embedding vectors and storing in lancedb ...")

    #   note: the only code change to use a different vector_db is changing the name in this method below
    library.install_new_embedding(embedding_model_name=embedding_model, vector_db="lancedb")

    # Then when doing semantic queries, the most recent vector DB used for embeddings will be used.

    # We just find the best 3 hits for "Salary"
    q = Query(library)
    print (f"\n > Running a query for 'Salary'...")
    query_results = q.semantic_query(query="Salary", result_count=10, results_only=True)

    print("query-",query_results)

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

    return query_results


if __name__ == "__main__":

    library_name = "embedding_test_0"

    # note: these two environmental variables will be checked to apply your lancedb keys
    # os.environ["USER_MANAGED_lancedb_API_KEY"] = "your-lancedb-api-key"
    # os.environ["USER_MANAGED_lancedb_ENVIRONMENT"] = "your-lancedb-environment"

    embeddings_lancedb("embedding_test")


