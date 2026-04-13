
""" This example shows how to select and set the collection database. The collection DB is used as the primary
source of storing text chunks from parsing runs, and organizing into Libraries.  LLMWare supports three
collection databases:  MongoDB, Postgres, and SQLite.

    For a fast no-install start, we would recommend SQLite.

    If you prefer SQL and massive scalability, we would recommend Postgres.

    If you prefer no-SQL and combo of scale and flexibility, we would recommend MongoDB.

    The LLMWare functions, methods and interfaces to each of the DBs are exactly the same with a
    high-level abstraction interface provided within LLMWare CollectionRetrieval and CollectionWriter classes
    that handle the implementation-specific details of writing and retrieving from each of these data sources.

    While semantic retrieval requires the use of a separate vector database and creating an embedding for the
    content in the Library, once the library is created, text search retrieval is available automatically so text
    Queries can be run immediately after Parsing.

"""

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

