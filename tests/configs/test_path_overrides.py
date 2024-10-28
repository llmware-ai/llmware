""" Tests paths both for a standard account setup and custom account setup.

    Note: by default, this test will run on MongoDB - to switch DB used - add one-line:

    `LLMWareConfig().set_active_db("sqlite")

"""

import os

from llmware.configs import LLMWareConfig
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup


def test_standard_account_setup():

    library_name = "test_standard_account_setup"
    library = Library().create_new_library(library_name)

    # add files
    sample_files_path = Setup().load_sample_files()
    library.add_files(os.path.join(sample_files_path,"SmallLibrary"))
    
    # run test query
    results = Query(library).text_query("base salary")

    assert len(results) > 0, "Expected results to be greater than 0 for standard account setup."


# Test overriding llmware_data folder
def test_setup_custom_location():

    #   upstream application creating custom home path, e.g., aibloks
    new_home_folder = "llmware_data_custom"
    LLMWareConfig.set_home(os.path.join(LLMWareConfig.get_home(), new_home_folder))

    new_llmware_path = "aibloks_data"
    LLMWareConfig.set_llmware_path_name(new_llmware_path)

    # Make folders if they don't already exist
    if not os.path.exists(LLMWareConfig().get_home()):
        os.mkdir(LLMWareConfig().get_home())
        if not os.path.exists(LLMWareConfig().get_llmware_path()):
            LLMWareConfig.setup_llmware_workspace()

    assert new_home_folder in LLMWareConfig.get_home(), "Custom home folder not set correctly."
    assert new_home_folder in LLMWareConfig.get_llmware_path() and new_llmware_path in LLMWareConfig.get_llmware_path(), "Custom LLMWare path not set correctly."
    assert new_home_folder in LLMWareConfig.get_library_path() and new_llmware_path in LLMWareConfig.get_library_path(), "Library path not set correctly."

    # test with library setup and adding files
    library_name = "library_with_custom_path"
    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files()
    library.add_files(os.path.join(sample_files_path,"Agreements"))

    assert new_home_folder in library.library_main_path, "Custom path not found in library main path."

    results = Query(library).text_query("salary")

    assert len(results) > 0


