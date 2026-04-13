
"""This example demonstrates the Query State mechanisms and ability to generate reports across multiple queries:

      1. Create a library
      2. Run multiple queries - saving query state
      3. Generate reports from query state and export
"""

import os
from llmware.configs import LLMWareConfig
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup


def create_un_500_sample_library(library_name):

    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files(over_write=False)
    ingestion_folder_path = os.path.join(sample_files_path, "UN-Resolutions-500")
    parsing_output = library.add_files(ingestion_folder_path)

    return library


# Demonstrate some methods involved with persisting and loading Query state as well as export
def query_state_and_export(library):

    # Create a Query instance with history persistence
    query = Query(library, save_history=True)

    # Capture the query_id
    query_id = query.query_id

    # Run a series of queries
    query_results = query.text_query("sustainable development", result_count=20)
    query_results = query.text_query("africa", result_count=26)
    query_results = query.text_query("pandemic risk", result_count=15)

    # Save state - this will write the query state as JSON file in /query_history path
    query.save_query_state()

    # Generate Retrieval Report.  The report will be stored in the llmware_data/query_history folder
    csv_file = query.generate_csv_report()
    csv_file_path = os.path.join(LLMWareConfig().get_query_path(), csv_file)

    print (f"\nSaving Retrieval State and Export'")
    print (f"Export for query id '{query_id}': {csv_file_path}")

    # Additionally here is how can clear state and reload based on a query_id:
    query.clear_query_state()
    query.load_query_state(query_id)

    return 0


if __name__ == "__main__":

    lib = create_un_500_sample_library("lib_query_state_1")
    query_state_and_export(lib)



