
"""This example demonstrates the various ways to retrieve data from libraries:
      1. Create a sample library (e.g., UN Resolutions)
      2. Execute a Text Query with Author Name Filter
      3. Display Results
"""

import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup


def create_un_500_sample_library(library_name):

    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files(over_write=False)
    ingestion_folder_path = os.path.join(sample_files_path, "UN-Resolutions-500")
    parsing_output = library.add_files(ingestion_folder_path)

    return library


def text_retrieval_by_author(library, query_text, author):

    #   create a Query instance and pass the previously created Library object
    query = Query(library)

    #   set the keys that should be returned in the results
    query.query_result_return_keys = ["file_source", "page_num", "text", "author_or_speaker"]

    #   perform a text query by author
    query_results = query.text_query_by_author_or_speaker(query_text, author)

    #   display the results
    for i, result in enumerate(query_results):

        file_source = result["file_source"]
        page_num = result["page_num"]
        author = result["author_or_speaker"]
        text = result["text"]

        # shortening for display purpose only
        if len(text) > 150:  text = text[0:150] + " ... "

        print (f"\n> Top result for '{query_text}': {file_source} (page {page_num}), Author: {author}:\nText:{text}")

    return query_results


if __name__ == "__main__":

    library = create_un_500_sample_library("lib_author_filter_1")
    qr_output = text_retrieval_by_author(library=library, query_text='United Nations', author='Andrea Chambers')
