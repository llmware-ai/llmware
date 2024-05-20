from llmware.agents import LLMfx
from llmware.models import ModelCatalog

def create_table_schema():
    
    table_name = input("Enter the table name: ")
    fields = []

    while True:
        field_name = input("Enter a field name (or press Enter to finish): ")
        if not field_name:
            break
        field_type = input(f"Enter the data type for '{field_name}' (text, integer, etc...): ")
        fields.append(f"{field_name} {field_type}")

    field_str = ", ".join(fields)
    sql_statement = f"CREATE TABLE {table_name} ({field_str})"
    
    return sql_statement

def print_in_green(text):
    print("\033[34m" + text + "\033[0m")

if __name__ == "__main__":

    ModelCatalog().get_llm_toolkit(["sql"])

    agent = LLMfx(verbose=False)

    print_in_green("Welcome to ChatSQL!")
    print_in_green("ChatSQL will help you in your SQL learning journey.")
    print("Let's start by creating a table to query.")

    table_schema = create_table_schema()
    print_in_green("Table schema created!")
    print("Here is the SQL statement to create the table:")
    print_in_green(table_schema)

    print("Now let's query the table.")
    print("Enter a query or press Enter to exit.")

    while True:
        query = input("You: ")
        if query == "":
            break
        response = agent.sql(query, table_schema)
        print_in_green(f"ChatSQL: {response['llm_response']}")
    
    print_in_green("Thank you for using ChatSQL!")

