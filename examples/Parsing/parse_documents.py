
"""This 'Getting Started' example demonstrates how to parse document files into a library
      1. Create a library
      2. Assemble input files into a single folder path (fp)
      3. Pass the folder path to library.add_files(fp) to automatically parse, text chunk, index
"""

import os
from llmware.library import Library
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

    #   note: to replace with your own documents, just point to a local folder path with the documents
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

    return parsing_output


if __name__ == "__main__":

    #  note on sample documents - downloaded by Setup()
    #       UN-Resolutions-500 is 500 pdf documents
    #       Invoices is 40 pdf invoice samples
    #       Agreements is ~15 contract documents
    #       AgreementsLarge is ~80 contract documents
    #       FinDocs is ~15 financial annual reports and earnings
    #       SmallLibrary is a mix of ~10 pdf and office documents

    # this is a list of document folders that will be pulled down by calling Setup()
    sample_folders = ["Agreements", "Invoices", "UN-Resolutions-500", "SmallLibrary", "FinDocs", "AgreementsLarge"]

    LLMWareConfig().set_active_db("sqlite")

    library_name = "parsing_test_lib"
    selected_folder = sample_folders[0]
    output = parsing_documents_into_library(library_name, selected_folder)