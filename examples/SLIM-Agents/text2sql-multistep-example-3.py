

""" This example shows a multi-step SQL query use case - this is an 'innovation scenario' and should be viewed
as a good starting recipe for building your own more complex workflows involving text2sql queries.

    The example shows the following steps:

    1.  Generating a SQL table from a sample CSV file included with the slim-sql-tool install.
    2.  'Two-step' query (starting on line 133) in which a customer name is pulled from a text using NER, and then
        the name is 'dynamically' added to a natural language string, which is then converted using text-to-sql
        and querying the database.
    3.  All work performed on an integrated 'llmware-sqlite-experimental.db' that can be deleted safely anytime
     as part of experimentation lifecycle.

"""

import os

from llmware.agents import SQLTables, LLMfx
from llmware.models import ModelCatalog
from llmware.configs import LLMWareConfig

llmware_path = LLMWareConfig().get_llmware_path()


def sql_two_step_query_example(table_name="customers1",create_new_table=False):

    """ This is the end-to-end execution script. """

    #   create table if needed to set up
    if create_new_table:

        sql_tool_repo_path = os.path.join(LLMWareConfig().get_model_repo_path(), "slim-sql-tool")

        if not os.path.exists(sql_tool_repo_path):
            ModelCatalog().load_model("llmware/slim-sql-tool")

        files = os.listdir(sql_tool_repo_path)

        csv_file = "customer_table.csv"

        if csv_file in files:
            sql_db = SQLTables(experimental=True)
            sql_db.create_new_table_from_csv(sql_tool_repo_path, csv_file, table_name=table_name)
            print("update: successfully created new db table")

        else:
            print("something has gone wrong - could not find customer_table.csv  with slim-sql-tool file package")

    #   query starts here
    agent = LLMfx()
    agent.load_tool("sql")
    agent.load_tool("ner")

    #   Multi-step example - extract NER -> create natural language query -> convert SQL -> lookup

    text = ("This is Susan Soinsin calling - I am really upset about the poor customer service, "
            "and would like to cancel my service.")

    #   Step 1 - extract the customer name using NER
    response = agent.ner(text=text)
    customer_name = "No Customer"

    #   please note: this is just a demo recipe - any real life scenario would require significant preprocessing
    #   and error checking.   :)

    if "llm_response" in response:
        if "people" in response["llm_response"]:
            people = response["llm_response"]["people"]
            if len(people) > 0:
                customer_name = people[0]

    print("update: ner response - identified the following people names -  ", customer_name, response)

    #   Step 2 - use the customer name found in the NER analysis to construct a natural language query
    query = f"Is {customer_name} a vip customer?"

    print("update: dynamically created query: ", query)

    response = agent.query_db(query, table=table_name)

    print("update: response: ", response)

    for x in range(0,len(agent.research_list)):
        print("research: ", x, agent.research_list[x])

    return 0

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


if __name__ == "__main__":

    #   second - run an end-to-end test
    sql_two_step_query_example (table_name="customer1",create_new_table=True)

    #   third - delete and start fresh for further testing
    delete_table("customer1")

