

import os

from llmware.configs import LLMWareConfig
from llmware.library import Library
from llmware.retrieval import Query


def test_standard_account_setup():

    # will use default 'llmware' path to create library

    print("Test:  Standard Account Setup")

    lib_name = "new_test_lib_1005_4"
    lib = Library().create_new_library(lib_name)

    print("update: test_standard_account_setup - lib name & account name - ", lib.account_name, lib.library_name)

    # add files
    input_fp = "/path/to/contract/files/"
    results = lib.add_files(input_fp)
    print("update: confirm that parsing results are OK - ", results)

    # run test query
    results = Query(lib).text_query("base salary")

    for i, entry in enumerate(results):
        print("update: query results: ", i, entry["doc_ID"], entry["block_ID"], entry)

    return 0


# test_standard_account_setup()


def test_setup_custom_location():

    print("Test: Custom Setup - Overwrite File Path Home Location")

    #   upstream application creating custom home path, e.g., aibloks
    new_home_path = "aibloks0"
    LLMWareConfig.set_home(os.path.join(LLMWareConfig.get_home(), new_home_path))

    new_llmware_path = "aibloks_data"
    LLMWareConfig.set_llmware_path_name(new_llmware_path)
    print("update: new llmware path - ", LLMWareConfig.get_llmware_path())

    if not os.path.exists(LLMWareConfig().get_home()):
        os.mkdir(LLMWareConfig().get_home())

        if not os.path.exists(LLMWareConfig().get_llmware_path()):
            LLMWareConfig.setup_llmware_workspace()

    print("update: initial config - post-setup - .home_path", LLMWareConfig.get_home())
    print("update: initial config - post-setup - .llmware_path", LLMWareConfig.get_llmware_path())
    print("update: initial config - post-setup - .library_path", LLMWareConfig.get_library_path())
    print("update: initial config - post-setup - .collection_db_uri", LLMWareConfig.get_config("collection_db_uri"))

    # test with library setup
    lib_name = "new_test_lib_1005_441"
    lib = Library().create_new_library(lib_name)

    # add files
    input_fp = "/path/to/contract/files/"
    results = lib.add_files(input_fp)
    print("update: confirm that parsing results are OK - ", results)
    results = Query(lib).text_query("base salary")

    for i, entry in enumerate(results):
        print("update: query results: ", i, entry["doc_ID"], entry["block_ID"], entry)

    return 0


# test_setup_custom_location()


def test_setup_custom_account():

    #   creation of custom accounts -> 'implicit' creation allowed in llmware (no permissioning checks)
    #   assumed that upstream application will manage permissioning and account management

    print("Test: Setup of Custom Accounts")

    account_name = "account-1005-432"
    lib_name = "contracts1005_432"

    lib = Library().create_new_library(lib_name, account_name=account_name)

    print("update: library name & account name - ", lib.account_name, lib.library_name)

    input_fp = "/path/to/contract/files/"
    results = lib.add_files(input_fp)
    print("update: confirm that parsing results are OK - ", results)

    # additional check - build knowledge graph - confirm that artifacts in /nlp folder in custom account path
    lib.generate_knowledge_graph()

    # test query
    results = Query(lib).text_query("base salary")

    for i, entry in enumerate(results):
        print("update: query results: ", i, entry["doc_ID"], entry["block_ID"], entry)

    return 0


# test_setup_custom_account()





