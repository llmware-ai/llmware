
"""
This 'getting started' example demonstrates how to use basic semantic retrieval with the Query class
      1. Create a sample library
      2. Run a basic semantic query
      3. View the results
"""

import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup
from llmware.configs import LLMWareConfig


def create_fin_docs_sample_library(library_name):

    print(f"update: creating library - {library_name}")

    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files(over_write=False)
    ingestion_folder_path = os.path.join(sample_files_path, "FinDocs")
    parsing_output = library.add_files(ingestion_folder_path)

    print(f"update: building embeddings - may take a few minutes the first time")

    #   note: if you have installed Milvus or another vector DB, please feel free to substitute
    #   note: if you have any memory constraints on laptop:
    #       (1) reduce embedding batch_size or ...
    #       (2) substitute "mini-lm-sbert" as embedding model

    library.install_new_embedding(embedding_model_name="industry-bert-sec", vector_db="chromadb",batch_size=200)

    return library


def basic_semantic_retrieval_example (library):

    # Create a Query instance
    q = Query(library)

    # Set the keys that should be returned - optional - full set of keys will be returned by default
    q.query_result_return_keys = ["distance","file_source", "page_num", "text"]

    # perform a simple query
    my_query = "ESG initiatives"
    query_results1 = q.semantic_query(my_query, result_count=20)

    # Iterate through query_results, which is a list of result dicts
    print(f"\nQuery 1 -  {my_query}")
    for i, result in enumerate(query_results1):
        print("results - ", i, result)

    # perform another query
    my_query2 = "stock performance"
    query_results2 = q.semantic_query(my_query2, result_count=10)

    print(f"\nQuery 2 - {my_query2}")
    for i, result in enumerate(query_results2):
        print("results - ", i, result)

    # perform another query
    my_query3 = "cloud computing"

    # note: use of embedding_distance_threshold will cap results with distance < 1.0
    query_results3 = q.semantic_query(my_query3, result_count=50, embedding_distance_threshold=1.0)

    print(f"\nQuery 3 - {my_query3}")
    for i, result in enumerate(query_results3):
        print("result - ", i, result)

    return [query_results1, query_results2, query_results3]


if __name__ == "__main__":

    print(f"Example - Running a Basic Semantic Query")

    LLMWareConfig().set_active_db("sqlite")

    # step 1- will create library + embeddings with Financial Docs
    lib = create_fin_docs_sample_library("lib_semantic_query_1")

    # step 2- run query against the library and embeddings
    my_results = basic_semantic_retrieval_example(lib)
