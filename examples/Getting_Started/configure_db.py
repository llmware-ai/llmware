
""" This example shows how to select and set the collection database. """

from llmware.configs import LLMWareConfig


def set_collection_database():

    #   check the current active db
    active_db = LLMWareConfig().get_active_db()

    print("update: current 'active' collection database - ", active_db)

    #   supported db list
    supported_db = LLMWareConfig().get_supported_collection_db()

    print("update: supported collection databases - ", supported_db)

    #   set the current active db -> once set, any calls to library / parsing will write to this db
    LLMWareConfig.set_active_db("sqlite")

    #   change anytime -> going forward, any new libraries will be written to the new db, but existing libraries
    #   remain on the previous db
    LLMWareConfig.set_active_db("postgres")

    return 0

