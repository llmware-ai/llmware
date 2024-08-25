
""" Fast Start Example #1 - Library - converting document files into an indexed knowledge collection.

    In this example, we will illustrate a basic recipe for completing the following steps:

      1. Create a library as an organizing construct for your knowledge-base
      2. Download sample files for a Fast Start - easy to 'swap out' and replace with your own files
      3. Use library.add_files method to automatically parse, text chunk and index the documents
      4. Run a basic text query against your new Library
"""

import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup
from llmware.configs import LLMWareConfig


def parsing_documents_into_library(library_name, sample_folder):

    print(f"\nExample - Parsing Files into Library")

    #   create new library
    print (f"\nStep 1 - creating library {library_name}")
    library = Library().create_new_library(library_name)

    #   load the llmware sample files
    #   -- note: if you have used this example previously, UN-Resolutions-500 is new path
    #   -- to pull updated sample files, set: 'over_write=True'

    sample_files_path = Setup().load_sample_files(over_write=False)
    print (f"Step 2 - loading the llmware sample files and saving at: {sample_files_path}")

    #   note: to replace with your own documents, just point to a local folder path that has the documents
    ingestion_folder_path = os.path.join(sample_files_path, sample_folder)

    print (f"Step 3 - parsing and indexing files from {ingestion_folder_path}")

    #   add files is the key ingestion method - parses, text chunks and indexes all files in folder
    #       --will automatically route to correct parser based on file extension
    #       --supported file extensions:  .pdf, .pptx, .docx, .xlsx, .csv, .md, .txt, .json, .wav, and .zip, .jpg, .png

    parsing_output = library.add_files(ingestion_folder_path)

    print (f"Step 4 - completed parsing - {parsing_output}")

    #   check the updated library card
    updated_library_card = library.get_library_card()
    doc_count = updated_library_card["documents"]
    block_count = updated_library_card["blocks"]
    print(f"Step 5 - updated library card - documents - {doc_count} - blocks - {block_count} - {updated_library_card}")

    #   check the main folder structure created for the library - check /images to find extracted images
    library_path = library.library_main_path
    print(f"Step 6 - library artifacts - including extracted images - saved at folder path - {library_path}")

    #   use .add_files as many times as needed to build up your library, and/or create different libraries for
    #   different knowledge bases

    #   now, your library is ready to go and you can start to use the library for running queries
    #   if you are using the "Agreements" library, then a good easy 'hello world' query is "base salary"
    #   if you are using one of the other sample folders (or your own), then you should adjust the query

    #   queries are always created the same way, e.g., instantiate a Query object, and pass a library object
    #   --within the Query class, there are a variety of useful methods to run different types of queries

    test_query = "base salary"

    print(f"\nStep 7 - running a test query - {test_query}\n")

    query_results = Query(library).text_query(test_query, result_count=10)

    for i, result in enumerate(query_results):

        #   note: each result is a dictionary with a wide range of useful keys
        #   -- we would encourage you to take some time to review each of the keys and the type of metadata available

        #   here are a few useful attributes
        text = result["text"]
        file_source = result["file_source"]
        page_number = result["page_num"]
        doc_id = result["doc_ID"]
        block_id = result["block_ID"]
        matches = result["matches"]

        #   -- if print to console is too verbose, then pick just a few keys for print
        print("query results: ", i, result)

    return parsing_output


if __name__ == "__main__":

    #  note on sample documents - downloaded by Setup()
    #       UN-Resolutions-500 is 500 pdf documents
    #       Invoices is 40 pdf invoice samples
    #       Agreements is ~15 contract documents
    #       AgreementsLarge is ~80 contract documents
    #       FinDocs is ~15 financial annual reports and earnings
    #       SmallLibrary is a mix of ~10 pdf and office documents

    #   optional - set the active DB to be used - by default, it is "mongo"
    #   if you are just getting started, and have not installed a separate db, select "sqlite"

    LLMWareConfig().set_active_db("sqlite")

    #   if you want to see a different log view, e.g., see a list of each parsed files 'in progress',
    #   you can set a different debug mode view anytime

    #   debug_mode options -
    #       0 - default - shows status manager (useful in large parsing jobs) and errors will be displayed
    #       2 - file name only - shows file name being parsed, and errors only

    #   for purpose of this example, let's change so we can see file-by-file progress
    LLMWareConfig().set_config("debug_mode", 2)

    #   this is a list of document folders that will be pulled down by calling Setup()
    sample_folders = ["Agreements", "Invoices", "UN-Resolutions-500", "SmallLibrary", "FinDocs", "AgreementsLarge"]

    library_name = "example1_library"

    #   select one of the sample folders
    selected_folder = sample_folders[0]     # e.g., "Agreements"

    #   run the example
    output = parsing_documents_into_library(library_name, selected_folder)


