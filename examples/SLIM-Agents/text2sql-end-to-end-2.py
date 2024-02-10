

""" This example shows an end-to-end recipe for querying SQL database using only natural language.

    The example shows the following steps:

    1.  Loading "slim-sql-tool" and running initial tests to confirm installation.
    2.  Generating a SQL table from a sample CSV file included with the slim-sql-tool install.
    3.  Asking basic natural language questions:
        A.  Looks up the table schema
        B.  Packages the table schema with query
        C.  Runs inference to convert text into SQL
        D.  Queries the database with the generated SQL
        E.  Returns result
    3.  All work performed on an integrated 'llmware-sqlite-experimental.db' that can be deleted safely anytime
     as part of experimentation lifecycle.

"""

import os

from llmware.agents import SQLTables, LLMfx
from llmware.models import ModelCatalog
from llmware.configs import LLMWareConfig


def sql_e2e_test_script(table_name="customers1",create_new_table=False):

    """ This is the end-to-end execution script. """

    #   create table if needed to set up
    if create_new_table:

        # looks to pull sample csv 'customer_table.csv' from slim-sql-tool model package files
        sql_tool_repo_path = os.path.join(LLMWareConfig().get_model_repo_path(), "slim-sql-tool")

        if not os.path.exists(sql_tool_repo_path):
            ModelCatalog().load_model("llmware/slim-sql-tool")

        files = os.listdir(sql_tool_repo_path)
        csv_file = "customer_table.csv"

        if csv_file in files:

            #   to create a testing table from a csv
            sql_db = SQLTables(experimental=True)
            sql_db.create_new_table_from_csv(sql_tool_repo_path, csv_file, table_name=table_name)
            #   end - creating table

            print("update: successfully created new db table")
        else:
            print("something has gone wrong - could not find customer_table.csv inside the slim-sql-tool file package")

    #   query starts here
    agent = LLMfx()
    agent.load_tool("sql")

    #  Pass direct queries to the DB

    query_list = ["Which customers are vip customers?",
                  "What is the highest annual spend of any customer?",
                  "Which customer has account number 1234953",
                  "Which customer has the lowest annual spend?",
                  "Is Susan Soinsin a vip customer?"]

    for i, query in enumerate(query_list):

        #   query_db method is doing all of the work
        #   -- looks up the table schema in the db using the table_name
        #   -- packages the text-2-sql query prompt
        #   -- executes sql method to convert the prompt into a sql query
        #   -- attempts to execute the sql query on the db
        #   -- returns the db results as 'research' output

        response = agent.query_db(query, table=table_name)

    for x in range(0,len(agent.research_list)):
        print("research: ", x, agent.research_list[x])

    return 0

def delete_table(table_name):

    """ Start fresh in testing - delete table in experimental local SQLite DB """

    sql_db = SQLTables(experimental=True)
    sql_db.delete_table(table_name, confirm_delete=True)

    return True


def delete_db():

    """ Start fresh in testing - deletes SQLite DB and starts over. """

    sql_db = SQLTables(experimental=True)
    sql_db.delete_experimental_db(confirm_delete=True)

    return True


if __name__ == "__main__":

    ModelCatalog().get_llm_toolkit()

    #   run an end-to-end test
    sql_e2e_test_script(table_name="customer1",create_new_table=True)

    #   third - delete and start fresh for further testing
    delete_table("customer1")

