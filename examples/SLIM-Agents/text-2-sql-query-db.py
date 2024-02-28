
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
    4.  'Two-step' query (starting on line 133) in which a customer name is pulled from a text using NER, and then
        the name is 'dynamically' added to a natural language string, which is then converted using text-to-sql
        and querying the database.
    5.  All work performed on an integrated 'llmware-sqlite-experimental.db' that can be deleted safely anytime
     as part of experimentation lifecycle.

"""

import os

from llmware.agents import SQLTables, LLMfx
from llmware.models import ModelCatalog
from llmware.configs import LLMWareConfig


def load_slim_sql_tool():

    """ First step is to install the slim-sql-tool locally """

    #   to cache locally the slim-sql-tool with config and test files
    ModelCatalog().get_llm_toolkit(["sql"])

    #   to run tests to confirm correct installation and see the model in action
    #   note: the test results will include some minor errors - useful to learn how to sharpen prompts
    ModelCatalog().tool_test_run("slim-sql-tool")

    return 0


def hello_world_text_2_sql():

    """ Illustrates a 'hello world' text-2-sql inference as part of an agent process. """
    sample_table_schema = "CREATE TABLE customer_info (customer_name text, account_number integer, annual_spend integer)"
    query = "What are the names of all customers with annual spend greater than $1000?"

    agent = LLMfx(verbose=True)
    response = agent.sql(query, sample_table_schema)

    print("update: text-2-sql response - ", response)

    return 0


def build_table(fp, fn, table_name):

    """ This is the key method for taking a CSV file from a folder_path (fp), a proposed new table_name,
    and creating a new table directly from the CSV.  Note: this is useful for rapid prototyping and
    experimentation - but should not be used for any serious production purpose.  """

    sql_db = SQLTables(experimental=True)
    x = sql_db.create_new_table_from_csv(fp,fn,table_name=table_name)
    print("update: successfully created new db table")

    return 1


def delete_table(table_name):

    """ Start fresh in testing - delete table in experimental local SQLite DB """
    sql_db = SQLTables(experimental=True)
    sql_db.delete_table(table_name,confirm_delete=True)

    return True


def delete_db():

    """ Start fresh in testing - deletes SQLite DB and starts over. """

    sql_db = SQLTables(experimental=True)
    sql_db.delete_experimental_db(confirm_delete=True)

    return True


def sql_e2e_test_script(table_name="customers1",create_new_table=False):

    """ This is the end-to-end execution script. """

    #   create table if needed to set up
    if create_new_table:

        sql_tool_repo_path = os.path.join(LLMWareConfig().get_model_repo_path(), "slim-sql-tool")

        if not os.path.exists(sql_tool_repo_path):
            ModelCatalog().load_model("llmware/slim-sql-tool")

        files = os.listdir(sql_tool_repo_path)

        csv_file = "customer_table.csv"

        if csv_file in files:
            build_table(sql_tool_repo_path, csv_file, table_name)
        else:
            print("something has gone wrong - could not find customer_table.csv  with slim-sql-tool file package")

    #   query starts here
    agent = LLMfx()
    agent.load_tool("sql")

    #   Example 1 - direct query

    query_list = ["Which customers are vip customers?",
                  "What is the highest annual spend of any customer?",
                  "Which customer has account number 1234953",
                  "Which customer has the lowest annual spend?",
                  "Is Susan Soinsin a vip customer?"]

    for i, query in enumerate(query_list):

        #   this method is doing all of the work
        #   -- looks up the table schema in the db using the table_name
        #   -- packages the text-2-sql query prompt
        #   -- executes sql method to convert the prompt into a sql query
        #   -- attempts to execute the sql query on the db
        #   -- returns the db results as 'research' output

        response = agent.query_db(query, table=table_name)

    #   Example 2 - use in a chain of inferences

    text = ("This is Susan Soinsin calling - I am really upset about the poor customer service, "
            "and would like to cancel my service.")

    agent.load_tool("ner")
    response = agent.ner(text=text)
    customer_name = "No Customer"

    #   please note: this is just a demo recipe - any real life scenario would require significant preprocessing
    #   and error checking.   :)

    if "llm_response" in response:
        if "people" in response["llm_response"]:
            people = response["llm_response"]["people"]
            if len(people) > 0:
                customer_name = people[0]

    print("ner response: ", customer_name, response)

    # e.g., name = "Susan Soinsin"

    query = f"Is {customer_name} a vip customer?"

    print("query: ", query)

    response = agent.query_db(query, table=table_name)

    print("response: ", response)

    for x in range(0,len(agent.research_list)):
        print("research: ", x, agent.research_list[x])

    return 0


if __name__ == "__main__":

    #   first - load and test the tools
    load_slim_sql_tool()

    #   second - 'hello world' demo of using text2sql model
    hello_world_text_2_sql()

    #   second - run an end-to-end test
    sql_e2e_test_script(table_name="customer1",create_new_table=True)

    #   third - delete and start fresh for further testing
    delete_table("customer1")

