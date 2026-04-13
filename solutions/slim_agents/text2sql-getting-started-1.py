
""" This 'getting started' example shows the basics of how to start using text2sql model:

    1.   Loading "slim-sql-tool" and running initial tests to confirm installation.

    2.   'Hello World' demonstration of how to 'package' a text2sql prompt combining a
        natural language query with a SQL table schema and run a basic inference to generate SQL output

"""


from llmware.agents import LLMfx
from llmware.models import ModelCatalog


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

    return response


if __name__ == "__main__":

    #   first - load and test the tools
    load_slim_sql_tool()

    #   second - 'hello world' demo of using text2sql model
    hello_world_text_2_sql()

