
""" Tests core library functions.   By default, runs on MongoDB - to change:

    `LLMWareConfig().set_active_db("sqlite")

"""


import os
import tempfile
from llmware.configs import LLMWareConfig
from llmware.library import Library, LibraryCatalog
from llmware.setup import Setup


def test_core_library_functions():

    # Library creations
    library_name = "LibraryABC"
    library = Library().create_new_library(library_name)

    # Get all library names:
    all_library_names = []
    for library_card in LibraryCatalog().all_library_cards():
        all_library_names.append(library_card["library_name"])
    
    # Ensure library name exists
    assert library_name in all_library_names

    # Add a few files
    sample_files_path = Setup().load_sample_files()
    library.add_files(os.path.join(sample_files_path,"SmallLibrary"))
    
    # Library Export
    temp_export_dir = tempfile.gettempdir()
    json_export_path = library.export_library_to_jsonl_file(temp_export_dir, "lib_export")
    assert os.path.getsize(json_export_path) > 100
    os.remove(json_export_path)
    
    # dump whole parsed library with only text
    text_export_path = library.export_library_to_txt_file(temp_export_dir, "lib_export")
    assert os.path.getsize(text_export_path) > 100
    os.remove(text_export_path)

    # Delete the library
    library.delete_library(confirm_delete=True)

    # Get all library names:
    all_library_names = []
    for library_card in LibraryCatalog().all_library_cards():
        all_library_names.append(library_card["library_name"])

    # Ensure library name does not exist
    assert library_name not in all_library_names


def test_create_new_library_idempotent_with_unsafe_name():
    """ Regression test for #1155: calling create_new_library twice with the same
        original name that gets remapped by the db-layer's safe_name() (e.g. '-' on
        sqlite/postgres) should load the existing library, not raise an IntegrityError. """

    LLMWareConfig().set_active_db("sqlite")

    library_name = "my-test-library-1155"
    library_1 = Library().create_new_library(library_name)
    library_2 = Library().create_new_library(library_name)

    assert library_1.library_name == library_2.library_name
    library_2.delete_library(confirm_delete=True)


