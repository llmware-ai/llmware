
"""This example demonstrates how to use a page number filter to narrow search retrievals by specific
    documents and pages - using document_filter and page_lookup methods in the Query class. """

import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup
from llmware.configs import LLMWareConfig


def create_agreements_sample_library(library_name):

    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files(over_write=False)
    ingestion_folder_path = os.path.join(sample_files_path, "Agreements")
    parsing_output = library.add_files(ingestion_folder_path)

    return library


def page_lookup(library):

    print(f"\nExample - Retrieving by Document and Page Number")

    #   create a Query instance
    q = Query(library)

    #   step 1 - select a set of documents from the library
    #   -- this can be accomplished in several ways, e.g.,
    #       (A) doc_id_list = [1,2,3,4,5] -> will select documents with doc_ID = 1,2,3,4,5
    #       (B) run a document filter query, e.g., doc_id_list = Query(library).document_filter("my_query")
    #       (C) leave blank -> will retrieve all of the doc id from the library

    #   in this case, will run a document_filter query to generate a doc_id_list with contracts with the name "apollo"
    my_query = "apollo"
    doc_id_list = q.document_filter(my_query)

    print(f"\nstep 1 - build doc_id_list with query - {my_query} - ", doc_id_list)

    #   define a target page list - useful for template documents with key names/phrases in specific places
    page_list = [1,12]

    print(f"step 2 - execute page lookup for pages - {page_list}\n")

    query_results = q.page_lookup(page_list=page_list, doc_id_list=doc_id_list)

    for i, result in enumerate(query_results):
        print(f"result - {i} - {result['file_source']} - page - {result['page_num']} - text - {result['text']}")

    return query_results


if __name__ == "__main__":

    LLMWareConfig().set_active_db("sqlite")

    lib = create_agreements_sample_library("lib_page_filter_example")
    my_results = page_lookup (lib)

