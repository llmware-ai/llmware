
"""This example demonstrates the various ways to retrieve data from libraries:
      1. Basic retrieval
      2. Retrieval with filters
      3. Bulk retrieval
      4. Retrieval State and Export
"""

import os
from llmware.retrieval import Query
from llmware.library import Library
from llmware.setup import Setup


def create_agreements_sample_library(library_name):

    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files(over_write=False)
    ingestion_folder_path = os.path.join(sample_files_path, "Agreements")
    parsing_output = library.add_files(ingestion_folder_path)

    return library


# Sometimes you want to retrieve all data so you can further process it yourself
def perform_bulk_retrieval(library):

    # Create a Query instance
    query = Query(library)

    # Create a list of keys of interest. This can be omitted if you want all keys
    key_dict = ["file_source", "text", "page_num", "author_or_speaker"]

    # Get the whole libary. This returns a list of all blocks
    all_blocks = query.get_whole_library(selected_keys=key_dict)

    print (f"\n> Bulk retrieval Retrieval'")
    print (f"\n{len(all_blocks)} blocks were retrieved")

    return all_blocks


if __name__ == "__main__":

    library = create_agreements_sample_library("lib_agreements_1")
    perform_bulk_retrieval(library)
