
""" This example shows the basics of working with Libraries.  Library is the main organizing construct for
unstructured information in LLMWare.   Users can create one large library with all types of different content, or
can create multiple libraries with each library comprising a specific logical collection of information on a
particular subject matter, project/case/deal, or even different accounts/users/departments.

    Each Library consists of the following components:

    1. Collection on a Database - this is the core of the Library, and is created through parsing of documents, which
    are then automatically chunked and indexed in a text collection database.  This is the basis for retrieval,
    and the collection that will be used as the basis for tracking any number of vector embeddings that can be
    attached to a library collection.

    2. File archives - found in the llmware_data path, within Accounts, there is a folder structure for each Library.
    All file-based artifacts for the Library are organized in these folders, including copies of all files added in
    the library (very useful for retrieval-based applications), images extracted and indexed from the source
    documents, as well as derived artifacts such as nlp and knowledge graph and datasets.

    3. Library Catalog - each Library is registered in the LibraryCatalog table, with a unique library_card that has
    the key attributes and statistics of the Library.

    When a Library object is passed to the Parser, the parser will automatically route all information into the
    Library structure.

    The Library also exposes convenience methods to easily install embeddings on a library, including tracking of
    incremental progress.

    To parse into a Library, there is the very useful convenience methods, "add_files" which will invoke the Parser,
    collate and route the files within a selected folder path, check for duplicate files, execute the parsing,
    text chunking and insertion into the database, and update all of the Library state automatically.

    Libraries are the main index constructs that are used in executing a Query.   Pass the library object when
    constructing the Query object, and then all retrievals (text, semantic and hybrid) will be executed against
    the content in that Library only.

"""

import json
import os
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
    temp_export_dir = LLMWareConfig().get_tmp_path()
    json_export_path = library.export_library_to_jsonl_file(temp_export_dir, "lib_export")
    print (f" - library exported to {json_export_path}")
    
    # Library export to txt file
    print (f"\n > Exporting library to text file...")
    text_export_path = library.export_library_to_txt_file(temp_export_dir, "lib_export")
    print (f" - library exported to {text_export_path}")

    # check out the images extracted
    print (f"\n images extracted and saved at local path - {library.image_path}")

    # Delete the library
    # print (f"\n > Deleting the library...")
    # note: for safety: set the confirm_delete=True when/if you want to delete
    library.delete_library(confirm_delete=False)


if __name__ == "__main__":

    #   set the database to be used to store Library text collection
    #   3 supported options:  MongoDB, Postgres, SQLite
    #   MongoDB and Postgres require separate install, while SQLite is no-install/setup

    LLMWareConfig().set_active_db("sqlite")

    core_library_functions("library_tests2")

