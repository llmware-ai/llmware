
""" This example shows an end-to-end recipe for creating a CustomTable, and then creating an Agent process that
    will query the table using natural language.

    Please note that this example is a 'generalized' and updated version of an earlier example -
    "text2sql-end-to-end-2.py" - now using the more powerful CustomTables class integrated into the LLMfx process

    The example shows the following steps:

    1.  Creating a custom table resource from a sample CSV file, included in the slim-sql-tool kit, and also
        available in the Examples section with Structured_Tables (customer_table.csv)

    2  Asking basic natural language questions:
        A.  Looks up the table schema
        B.  Packages the table schema with query
        C.  Runs inference to convert text into SQL
        D.  Queries the database with the generated SQL
        E.  Returns result

    3.  Using CustomtTable class, this can be run on either Postgres or SQLite DB.

    Note: as you substitute for your own CSV and JSON, check out the other examples in this section for loading
    configuration ideas and options.

"""

import os

from llmware.agents import LLMfx
from llmware.resources import CustomTable
from llmware.configs import LLMWareConfig


def build_table(db=None, table_name=None,load_fp=None,load_file=None):

    """ Simple example script to take a CSV or JSON/JSONL and create a DB Table. """

    custom_table = CustomTable(db=db, table_name=table_name)
    analysis = custom_table.validate_csv(load_fp, load_file)
    print("update: analysis from validate_csv: ", analysis)

    if load_file.endswith(".csv"):
        output = custom_table.load_csv(load_fp, load_file)
    elif load_file.endswith(".jsonl") or load_file.endswith(".json"):
        output = custom_table.load_json(load_fp, load_file)
    else:
        print("file type not supported for db load")
        return -1

    print("update: output from loading file: ", output)

    sample_range = min(10, len(custom_table.rows))
    for x in range(0,sample_range):
        print("update: sample rows: ", x, custom_table.rows[x])

    #  stress the schema data type and remediate - use more samples for more accuracy
    updated_schema = custom_table.test_and_remediate_schema(samples=20, auto_remediate=True)

    print("update: updated schema: ", updated_schema)

    #   insert the rows in the DB
    custom_table.insert_rows()

    return 1


def agent_natural_language_sql_query(query_list, db=None, table_name=None):

    """ Query a CustomTable in natural language. """

    #   query starts here
    agent = LLMfx()
    agent.load_tool("sql", sample=False, get_logits=True, temperature=0.0)

    #  Pass direct queries to the DB

    for i, query in enumerate(query_list):

        #   query_custom_table method is doing all of the work
        #   -- looks up the table schema in the db using the table_name
        #   -- packages the text-2-sql query prompt
        #   -- executes sql method to convert the prompt into a sql query
        #   -- attempts to execute the sql query on the db
        #   -- returns the db results as 'research' output

        response = agent.query_custom_table(query,db=db,table=table_name)

    for x in range(0,len(agent.research_list)):
        print("research: ", x, agent.research_list[x])

    return agent.research_list


if __name__ == "__main__":

    #   input parameters - db, table_name, path to csv or json/jsonl file
    db = "postgres"
    table_name = "customer_table"

    #   for hello_world, please pull down the customer_table.csv found in the examples repository
    input_fp = "/local/path/to/csv/"
    input_fn = "customer_table.csv"

    #   builds table - only needs to be done once
    build_table(db=db, table_name=table_name, load_fp=input_fp, load_file=input_fn)

    #   list of queries to ask the csv or json/jsonl
    #   -- note: these queries are useful but purposefully straightforward with relatively clear alignment
    #      to the data schema

    query_list = ["Which customers have vip customer status of yes?",
                  "What is the highest annual spend of any customer?",
                  "Which customer has account number 1234953",
                  "Which customer has the lowest annual spend?",
                  "Is Susan Soinsin a vip customer?"]

    #   agent process to execute the query list
    agent_natural_language_sql_query(query_list, db=db, table_name=table_name)
