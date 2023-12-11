
"""This example demonstrates the various ways to retrieve data from libraries:
      1. Create a sample 'FinDocs' library
      2. Execute a search (text in this case - but could be any query)
      3. Generate bibliography of all of the query results
"""

import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup


def create_fin_docs_sample_library(library_name):
    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files(over_write=False)
    ingestion_folder_path = os.path.join(sample_files_path, "FinDocs")
    parsing_output = library.add_files(ingestion_folder_path)

    return library


# A bibliography is the list of documents and their pages referenced in a set of query results.
# The format is: [{'Gaia EXECUTIVE EMPLOYMENT AGREEMENT.pdf': [3, 5, 2, 4, 1]}]

def get_bibliography_from_query_results(library, query_text):

    # Create a Query instance
    query = Query(library)

    # Perform a simple query
    query_results = query.text_query(query_text, result_count=20, exact_mode=False)

    # Get a bibliography
    biblio = query.bibliography_builder_from_qr(query_results=query_results)

    # Print out the bibliography
    print (f"\n> Bibliography for '{query_text}':\n{biblio}")

    return biblio


if __name__ == "__main__":

    library = create_fin_docs_sample_library("lib_biblio_1")
    query_text = "amazon web services"
    biblio = get_bibliography_from_query_results(library,query_text)

    print("update: biblio created - ", biblio)
