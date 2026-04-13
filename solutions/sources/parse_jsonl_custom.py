
""" This script illustrates options for parsing JSON and JSONL files into a Library in LLMWare, including the ability
    to provide a custom configured mapping intended for use with 'pseudo-db' structured JSON and JSONL files

    Option # 1- Standard JSON/JSON parsing -

        --  when using a bulk ingest Parsing method, the parser will route json and jsonl files to the 'standard'
            TextParser - which will look for a "text" key in the JSON/JSONL to extract as the intended text

        --  if no 'text' key found, then the parse will return an empty output list []

        --  you can provide an optional key_list parameter to TextParser, which will then by default capture the
            selected fields and aggregate to form the text input, e.g.,

            TextParser().jsonl_file_handler(fp,fn, key_list=["context", "source", "ID"]

            ... where "context", "source" and "ID" represent keys found in the source json/jsonl file

        -- the standard TextParser() is designed for ad hoc extraction of text content, not to preserve the keys

        -- use of this method is shown in the first example below

    Option # 2- Custom Configured JSON/JSONL parsing -

        -- in addition to the standard parsing method, there is the ability to customize the mappings for a
        JSON/JSONL file in which the keys are intended to be used for follow-up lookup and retrieval

        -- Parser().parse_json_config method - this is shown in the second and third examples below

    """


from llmware.parsers import Parser, TextParser
from llmware.library import Library
from llmware.retrieval import Query
from llmware.configs import LLMWareConfig

import time
import ast

#   All three text databases supported (mongo, postgres, and sqlite)
#   if it is highly varied unstructured content, we would recommend Mongo given its flexibility
#   if any validation errors with Postgres or SQLite, then we would recommend either preprocessing the json or
#   ... trying with Mongo

LLMWareConfig().set_active_db("mongo")


def standard_json_parsing(fp, fn):

    """ This example shows the 'standard' text handler for json/jsonl """

    #   the selected keys should map to dictionary keys found in the JSON/JSONL
    #   if no keys passed, then by default, parser will only look for a "text" key
    #   the parser objective is extracting/aggregating the content of the file, not using the 'structure' of the keys
    #   if interpret_as_table is True, then returns each row as a LIST of elements, corresponding to the selected keys
    #   if interpret_as_table is False, then returns a text string, which is concatenation of the text found in each
    #   key, and will use the value of the separator to combine each key,
    #   e.g., value1 + separator + value2 + separator ...

    selected_keys = ["key1", "key2", "key3"]    # e.g., "context", "source", "ID" or other keys in json

    output = TextParser().jsonl_file_handler(fp,fn,key_list=selected_keys,interpret_as_table=False,separator="\n")

    return output


def configured_json_parsing(fp, fn, library_name):

    """ This example shows how to use mappings for a customized json/jsonl """

    #   metadata is a dictionary mapping of key names to keys in the json file
    #   the 'keys' correspond to the keys that will be added to the library
    #   the 'values' correspond to the keys that will be found in the JSON/JSONL source file

    #   metadata must have "text" mapping
    #   if "doc_ID" or "block_ID" mapping provided, then will "over-write" the default doc_ID and block_ID and
    #   use the mapping provided in the source JSON/JSONL

    #   for all other attributes (e.g., not text, doc_ID, block_ID), the keys will be stored in "special_field1" of
    #   the database.  For Mongo, the keys will be stored directly as a dictionary, while for Postgres and SQLite,
    #   it will be stored as text string, which must be converted upon use back into a dictionary (see below for
    #   retrieval example)

    #   step 1 - create metadata mapping
    #   -- must have 'text' key mapped to key in json source
    #   -- all other keys are 'optional' and can be any number from 0 - N
    #   -- generally, key2, etc. should map to the name of the key in the JSON file, although you are free to re-name

    metadata= {"text": "json_source_key_mapping_to_main_text_input",
               "key2": "json_source_key2",
               "key3": "key3"}

    #  step 2 - create new library
    lib = Library().create_new_library(library_name)
    parser = Parser(lib)

    # step 3 - invoke parse_json_config method
    print("step 1 - parsing")
    t0 = time.time()
    parser_output = parser.parse_json_config(fp, fn, mapping_dict=metadata)
    print(f"done parsing - time - {time.time() - t0} - summary - {parser_output}")

    return parser_output


def run_query_configured_input (library_name=None,query=""):

    """ Once the custom json/jsonl is parsed into a Library, it can be used like any other content with the
    additional json/jsonl attributes available in special_field1- which can be retrieved as demonstrated below.

        -- note: the example below illustrates a 'text_query' but will apply exactly the same for a 'semantic_query'
    """

    # run query
    lib = Library().load_library(library_name)

    q = Query(lib).text_query(query)

    for j, results in enumerate(q):

        meta = ""
        doc_id = -1

        #   the mapped keys from the json file are all stored in "special_field1" of the library dictionary entry
        #   and can be retrieved as a string that can be mapped back into a dictionary as outlined below

        if "special_field1" in results:
            meta = results["special_field1"]
            if isinstance(meta,str):
                try:
                    meta = ast.literal_eval(meta)
                except:
                    print(f"could not convert meta string back into dictionary - {meta}")

        if "doc_ID" in results:
            doc_id = results["doc_ID"]

        text = results["text"]

        print(f"\nresults - {j} - query - {query}")
        print(f"results - text - {text}")
        print(f"results - doc_ID - {doc_id} - metadata - {meta}")

    print("done")

    return 0

