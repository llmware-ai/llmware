
""" This example demonstrates how to 'lookup' and retrieve an entire document, or a selected block, from the
    text collection DB. """

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


def doc_lookup(library):

    print(f"\nExample - Retrieving by Document")

    #   create a Query instance
    q = Query(library)

    #   step 1 - pull all of the blocks for a particular document
    #       -- use either "doc_id" number or "file_source" file name

    my_doc = q.document_lookup(file_source="Nyx EXECUTIVE EMPLOYMENT AGREEMENT.pdf")
    # my_doc = q.document_lookup(doc_id = 1)

    for i, result in enumerate(my_doc):
        print(f"result - {i} - {result['file_source']} - block - {result['block_ID']} - page - {result['page_num']} - text - {result['text']}")

    #   step 2 - to lookup a specific block in a document
    my_block = q.block_lookup(block_id=0, doc_id=1)

    print(f"\nExample - Selecting a specific block")
    print("my block: ", my_block)

    return my_block


if __name__ == "__main__":

    #   use any supported database - mongo, postgres or sqlite
    LLMWareConfig().set_active_db("mongo")

    lib = create_agreements_sample_library("doc_and_blocks_lookup_example")
    my_results = doc_lookup (lib)

