""" Tests for custom account configuration over-rides to set up additional accounts, besides the default 'llmware'.

    By default, the test will run on MongoDB - to change the database (including no-install) - add:

    `LLMWareConfig().set_active_db("sqlite")

    """

import os

from llmware.configs import LLMWareConfig
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup


def test_setup_custom_account():

    #   creation of custom accounts -> 'implicit' creation allowed in llmware (no permission checks)
    #   assumed that upstream application will manage permission scope and account management

    account_name = "custom_account123"
    library_name = "custom_lib123"
  
    # Create library and add files
    library = Library().create_new_library(library_name, account_name=account_name)
    sample_files_path = Setup().load_sample_files()
    library.add_files(os.path.join(sample_files_path,"SmallLibrary"))

    # Ensure the library's path was created with the right account name
    assert account_name in library.library_main_path
    
    # additional check - build knowledge graph - confirm that artifacts in /nlp folder in custom account path
    library.generate_knowledge_graph()
    assert len(os.listdir(library.nlp_path)) > 0

    # Do a query 
    results = Query(library).text_query("salary")
    assert len(results) > 0
    
