---
layout: default
title: Structured Tables
parent: Examples
nav_order: 9
description: overview of the major modules and classes of LLMWare  
permalink: /examples/structured_tables
---
# Structured Tables - Introduction by Examples
We introduce ``llmware`` through self-contained examples.

```python

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
```


These examples illustrate the use of the CustomTable class to quickly create SQL tables that can be used in conjunction with LLM-based workflows.  

1.  [**Intro to CustomTables**](https://www.github.com/llmware-ai/llmware/tree/main/examples/Structured_Tables/create_custom_table-1.py)  

    - Getting started with using CustomTables 

2.  [**Loading CSV into CustomTables**](https://www.github.com/llmware-ai/llmware/tree/main/examples/Structured_Tables/loading_csv_into_custom_table-2a.py)  

    - Loading CSV into CustomTables

3.  [**Loading CSV into Library (Configured)**](https://www.github.com/llmware-ai/llmware/tree/main/examples/Structured_Tables/loading_csv_w_config_options-2b.py)  

    - Loading CSV into Library  

4.  [**Loading JSON into CustomTables**](https://www.github.com/llmware-ai/llmware/tree/main/examples/Stuctured_Tables/loading_json_custom_table-3a.py)  

    - Loading JSON into CustomTable database 

5   [**Loading JSON into Library (Configured)**](https://www.github.com/llmware-ai/llmware/tree/main/examples/Stuctured_Tables/loading_json_w_config_options-3b.py)  

    - Loading JSON into a library with configuration  


For more examples, see the [structured tables example]((https://www.github.com/llmware-ai/llmware/tree/main/examples/Structured_Tables/) in the main repo.   

Check back often - we are updating these examples regularly - and many of these examples have companion videos as well.  



# More information about the project - [see main repository](https://www.github.com/llmware-ai/llmware.git)


# About the project

`llmware` is &copy; 2023-{{ "now" | date: "%Y" }} by [AI Bloks](https://www.aibloks.com/home).

## Contributing
Please first discuss any change you want to make publicly, for example on GitHub via raising an [issue](https://github.com/llmware-ai/llmware/issues) or starting a [new discussion](https://github.com/llmware-ai/llmware/discussions).
You can also write an email or start a discussion on our Discrod channel.
Read more about becoming a contributor in the [GitHub repo](https://github.com/llmware-ai/llmware/blob/main/CONTRIBUTING.md).

## Code of conduct
We welcome everyone into the ``llmware`` community.
[View our Code of Conduct](https://github.com/llmware-ai/llmware/blob/main/CODE_OF_CONDUCT.md) in our GitHub repository.

## ``llmware`` and [AI Bloks](https://www.aibloks.com/home)
``llmware`` is an open source project from [AI Bloks](https://www.aibloks.com/home) - the company behind ``llmware``.
The company offers a Software as a Service (SaaS) Retrieval Augmented Generation (RAG) service.
[AI Bloks](https://www.aibloks.com/home) was founded by [Namee Oberst](https://www.linkedin.com/in/nameeoberst/) and [Darren Oberst](https://www.linkedin.com/in/darren-oberst-34a4b54/) in October 2022.

## License

`llmware` is distributed by an [Apache-2.0 license](https://www.github.com/llmware-ai/llmware/blob/main/LICENSE).

## Thank you to the contributors of ``llmware``!
<ul class="list-style-none">
{% for contributor in site.github.contributors %}
  <li class="d-inline-block mr-1">
     <a href="{{ contributor.html_url }}">
        <img src="{{ contributor.avatar_url }}" width="32" height="32" alt="{{ contributor.login }}">
    </a>
  </li>
{% endfor %}
</ul>


---
<ul class="list-style-none">
    <li class="d-inline-block mr-1">
        <a href="https://discord.gg/MhZn5Nc39h"><span><i class="fa-brands fa-discord"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://www.youtube.com/@llmware"><span><i class="fa-brands fa-youtube"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://huggingface.co/llmware"><span><img src="assets/images/hf-logo.svg" alt="Hugging Face" class="hugging-face-logo"/></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://www.linkedin.com/company/aibloks/"><span><i class="fa-brands fa-linkedin"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://twitter.com/AiBloks"><span><i class="fa-brands fa-square-x-twitter"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://www.instagram.com/aibloks/"><span><i class="fa-brands fa-instagram"></i></span></a>
    </li>
</ul>
---


