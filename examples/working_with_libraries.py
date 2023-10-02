''' This example demonstrates creating and using libraries
    1. Library creation and loading existig libraries
    2. LibraryCatalog and library cards
    3. Exporting libraires to json or csv
'''
import json
import os
import tempfile
from llmware.configs import LLMWareConfig
from llmware.library import Library, LibraryCatalog
from llmware.setup import Setup

def core_library_functions(library_name):

    # Create a library
    print (f"\n > Creating library {library_name}...")
    library = Library().create_new_library(library_name)

    # Load an existing library. This not required after library creation and is only shown here for reference
    library = Library().load_library(library_name)

    # The LibraryCatalog is used to query all libraries
    print (f"\n > All libraries")
    for library_card in LibraryCatalog().all_library_cards():
        lib_name = library_card["library_name"]
        docs = library_card["documents"]
        print (f"  - {lib_name} ({docs} documents)")

    # Add a few files to our library
    print (f"\n > Adding some files to {library_name}")
    sample_files_path = Setup().load_sample_files()
    library.add_files(os.path.join(sample_files_path,"SmallLibrary"))

    # View the library card to confirm document, block and other counts
    print (f"\n > Library Card")
    library_card = library.get_library_card()
    library_card["_id"] = str(library_card["_id"]) # The _id needs to be converted to a str before printing
    print (json.dumps(library_card, indent=2))
 
    # Library Export to JSON
    print (f"\n > Exporting library to jsonl file...")
    temp_export_dir = tempfile.gettempdir()
    json_export_path = library.export_library_to_jsonl_file(temp_export_dir, "lib_export")
    print (f" - library exported to {json_export_path}")
    
    # Library export to txt file
    print (f"\n > Exporting library to text file...")
    text_export_path = library.export_library_to_txt_file(temp_export_dir, "lib_export")
    print (f" - library exported to {text_export_path}")

    # Delete the library
    print (f"\n > Deleting the library...")
    library.delete_library(confirm_delete=True)

core_library_functions("library_tests")