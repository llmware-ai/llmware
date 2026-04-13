
""" This example shows the basic recipe for creating a CustomTable with LLMWare and a few of the basic methods
    to quickly get started.

    In this example, we will build a very simple 'hello world' Files table, which we will build upon in a future
    example by aggregating a more interesting and useful set of attributes from a LLMWare Library collection.

    CustomTable is designed to work with the text collection databases supported by LLMWare:

        SQL DBs     ---     Postgres and SQLIte
        NoSQL DB    ---     Mongo DB

    Even though Mongo does not require a schema for inserting and retrieving information, the CustomTable method
    will expect a defined schema to be provided (good best practice, in any case).  """

from llmware.resources import CustomTable


def hello_world_custom_table():

    #   simple schema for a table to track Files/Documents
    #   note: the schema is a python dictionary, with named keys, and the value corresponding to the data type
    #   for sqlite and postgres, any standard sql data type should generally work

    files_schema = {"custom_doc_num": "integer",
                    "file_name": "text",
                    "comments": "text"}

    #   create a CustomTable object
    db_name = "sqlite"
    table_name = "files_table_1000"
    ct = CustomTable(db=db_name,table_name=table_name, schema=files_schema)

    #   insert a few sample rows - each row is a dictionary with keys from the schema, and the *actual* values
    r1 = {"custom_doc_num": 1, "file_name": "technical_manual.pdf", "comments": "very useful overview"}
    ct.write_new_record(r1)

    r2 = {"custom_doc_num": 2, "file_name": "work_presentation.pptx", "comments": "need to save for future reference"}
    ct.write_new_record(r2)

    r3 = {"custom_doc_num": 3, "file_name": "dataset.json", "comments": "will use in next project"}
    ct.write_new_record(r3)

    #   to see the entries - pull all items from the table
    all_results = ct.get_all()

    print("\nTEST #1 - Retrieving All Elements")
    for i, res in enumerate(all_results):
        print("results: ", i, res)

    #   look at the database schema
    schema = ct.get_schema()

    print("\nTEST #2 - Getting the Table Schema")
    print("schema: ", schema)

    schema_str = ct.sql_table_create_string()

    print("table create sql: ", schema_str)

    #   perform a basic lookup with 'key' and 'value'
    f = ct.lookup("custom_doc_num", 2)

    print("\nTEST #3 - Basic Lookup - 'custom_doc_num' = 2")
    print("lookup: ", f)

    #   if you prefer SQL, pass a SQL query directly (note: this will only work on Postgres and SQLite)

    if db_name == "sqlite":

        # note: our standard 'unpacking' of a row of sqlite includes the rowid attribute
        custom_query = f"SELECT rowid, * FROM {table_name} WHERE custom_doc_num = 3;"

    elif db_name == "postgres":
        custom_query = f"SELECT * FROM {table_name} WHERE custom_doc_num = 3;"

    elif db_name == "mongo":
        custom_query = {"custom_doc_num": 3}
    else:
        print("must use either sqlite, postgres or mongo")
        return -1

    cf = ct.custom_lookup(custom_query)

    print("\nTEST #4 - Custom SQL Lookup - 'custom_doc_num' = 3")
    print("custom query lookup: ", cf)

    print("\nTEST #5 - Making Updates and Deletes")

    #   to delete a record
    ct.delete_record("custom_doc_num", 1)
    print("deleted record")

    #   to update the values of a record
    ct.update_record({"custom_doc_num": 2}, "file_name", "work_presentation_update_v2.pptx")
    print("updated record")

    updated_all_results = ct.get_all()

    for i, res in enumerate(updated_all_results):
        print("updated results: ", i, res)

    print("\nTEST #6 - Delete Table - uncomment and set confirm=True")
    #   done?  delete the table and start over
    #   -- note: confirm=True must be set
    #   ct.delete_table(confirm=False)

    #   look at all tables in the database
    tables = ct.list_all_tables()

    print("\nTEST #7 - View all of the tables on the DB")
    for i, t in enumerate(tables):
        print("tables:" ,i, t)

    return 0


if __name__ == "__main__":

    hello_world_custom_table()
