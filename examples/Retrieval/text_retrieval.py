
"""
This 'getting started' example demonstrates how to use basic text retrieval with the Query class
      1. Create a sample library
      2. Run a basic text query
      3. View the results
"""

import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup


def create_invoices_sample_library(library_name):

    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files(over_write=False)
    ingestion_folder_path = os.path.join(sample_files_path, "Invoices")
    parsing_output = library.add_files(ingestion_folder_path)

    return library


def basic_text_retrieval_example (library):

    # Step 2 - the Query class executes queries against a Library

    # Create a Query instance
    q = Query(library)

    # Set the keys that should be returned - optional - full set of keys will be returned by default
    q.query_result_return_keys = ["file_source", "page_num", "matches", "doc_ID", "block_ID", "content_type", "text"]

    # Perform a simple query
    my_query = "total amount"
    query_results = q.text_query(my_query, result_count=20)

    print(f"\nQuery: {my_query}")

    # Iterate through query_results, which is a list of result dicts
    for i, result in enumerate(query_results):
        print("results - ", i, result)

    return query_results


if __name__ == "__main__":

    print(f"\nExample - Basic Text Query")

    lib = create_invoices_sample_library("lib_text_retrieval_example_2")

    my_results = basic_text_retrieval_example(lib)
