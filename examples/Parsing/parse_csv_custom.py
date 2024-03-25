
""" This script illustrates options for parsing csv and tsv files into a Library in LLMWare, including methods for
    mapping custom configured csv or tsv file, which is intended for use with 'pseudo-db' CSV files

    Option #1 - Standard CSV/TSV Parsing

        --  when using a bulk ingest Parsing method, the parser will route csv files to the 'standard'
            TextParser - which will look to extract and 'aggregate' the text from the csv as source content, and
            add to "text" and/or "table" attributes -> no "structure" information or targeted keys are captured

        -- the standard TextParser() is designed for ad hoc extraction of text content

        -- if file is csv, then by default delimiter assumed to be ',' (which can be adjusted)
        -- if file is tsv, then by default delimited assumed to be '\t' (which can be adjusted)

        -- this is illustrated in example 1 and example 2 below.

    Option #2 - Custom Configured CSV/TSV Parsing

        -- if the CSV file is a pseudo-db with structured attributes, then it can be configured using a special
           parsing method, as outlined below in examples 3 and 4.

        -- the benefit of this custom mapping is that key column attributes will be saved as "metadata" in addition
           to the option to provide a custom over-write of doc_ID and block_ID parameters for indexing of text
            chunks in the database

    """

from llmware.parsers import Parser, TextParser
from llmware.library import Library
from llmware.retrieval import Query
from llmware.configs import LLMWareConfig

import time
import ast

#   All three text databases supported (mongo, postgres, and sqlite)
#   if it is highly varied unstructured content, we would recommend Mongo given its flexibility
#   if any validation errors with Postgres or SQLite, then we would recommend either further preprocessing the csv or
#   ... trying with Mongo

LLMWareConfig().set_active_db("mongo")


def standard_csv_parsing(fp, fn, delimiter=","):

    """ Example #1 - This example shows the 'standard' text handler for csv """

    #   the standard csv parser will interpret the output as a table, trying to preserve the 'row-by-row' and
    #   'cell-by-cell' structure (without any keys/labels).   There are several options how the output text will
    #   be aggregated and saved as a single 'text' or 'table' entry:

    #       --batch_size: this is the number of rows that will be aggregated into each text entry
    #           e.g.,   if batch_size == 1, then each row will be a single entry in the database
    #                   if batch_size == 10, then 10 rows will be aggregated into a single 'text' entry in the db

    #       --interpret_as_table:
    #           if true, then text will be packaged as a string wrapping a nested list.
    #           if false, then text will be packaged as a single text stream separated by "\t" between entries

    #       --optional parameters allow configuration of encoding ('utf-8-sig'), errors ('ignore'),
    #           and separator ("\n") (applied at end of each row)

    #   to experiment with the expected output, try the method below, which will not write to the DB, but outputs
    #   a list in memory

    output = TextParser().csv_file_handler(fp,fn,interpret_as_table=False,batch_size=1, delimiter=delimiter)

    return output


def standard_csv_parsing_into_library(fp, library_name):

    """ Example #2 - building on the first example, this example will parse a set of 'standard' CSV files
        directly into the library - if file type is 'tsv' then delimiter automatically applied as '\t' """

    #   create new library
    lib = Library().create_new_library(library_name)

    #   create parser object, and pass the library to use to write the parsing output
    parser = Parser(lib)

    #   directly call the parse_text method, which will parse text files (csv, tsv, json, jsonl, txt, md)
    #   this parsed output will be saved to the database by default

    output = parser.parse_text(fp, interpret_as_table=False,batch_size=1,delimiter=",", encoding="utf-8-sig",
                               write_to_db=True)

    return output


def configured_csv_parsing(fp, fn,library_name):

    """ Example #3 - This example shows how to use mappings for a customized csv """

    #   metadata is a dictionary mapping of key names to columns in the csv file
    #   the 'keys' correspond to the keys that will be added to the library
    #   the 'values' correspond to the columns found in the source CSV (starting with 0 index)

    #   metadata map must have "text" mapping
    #   if "doc_ID" or "block_ID" mapping provided, then will "over-write" the default doc_ID and block_ID and
    #       use the mapping provided in the source CSV

    #   for all other attributes (e.g., not text, doc_ID, block_ID), the keys will be stored in "special_field1" of
    #   the database.  For Mongo, the keys will be stored directly as a dictionary, while for Postgres and SQLite,
    #   it will be stored as text string, which must be converted upon use back into a dictionary (see below for
    #   retrieval example)

    #   step 1 - create metadata mapping,
    #   e.g., number indexes map to columns in the csv, 0-index and negative slicing supported (-1 is last column)
    metadata = {"text": -1, "doc_ID": 0, "key1": 1, "key2": 2, "key3": 3, "key4": 4}
    columns = 6

    #   step 2 - create library
    lib = Library().create_new_library(library_name)
    parser = Parser(lib)

    #   step 3 - invoke parse_csv_config method
    #   -- note: if file is not comma delimited, then set delimiter
    #   -- if file is tab delimited, e.g. tsv, then delimiter = "\t"

    print("step 1 - parsing")
    t0 = time.time()
    parser_output = parser.parse_csv_config(fp, fn, cols=columns, mapping_dict=metadata,delimiter=",")
    print(f"done parsing - time - {time.time() - t0} - summary - {parser_output}")

    return parser_output


def example4_run_query_configured_input(library_name=None, query=""):

    """ Example #4 - once the custom csv/tsv is parsed into a Library, it can be used like any other content with the
    additional attributes available in special_field1- which can be retrieved as demonstrated below.

        -- note: the example below illustrates a 'text_query' but will apply exactly the same for a 'semantic_query'

    """

    # run query
    lib = Library().load_library(library_name)

    q = Query(lib).text_query(query)

    for j, results in enumerate(q):

        meta = ""
        doc_id = -1

        #   the metadata attributes are saved in the database under "special_field1" column
        if "special_field1" in results:
            meta = results["special_field1"]
            if isinstance(meta, str):
                try:
                    meta = ast.literal_eval(meta)
                except:
                    print(f"could not convert meta string back into dictionary - {meta}")

        if "doc_ID" in results:
            doc_id = results["doc_ID"]

        text = results["text"]

        if len(text) > 200:
            text = text[0:200]

        print(f"\nresults - {j} - query - {query}")
        print(f"results - text - {text}")
        print(f"results - doc_ID - {doc_id} - metadata - {meta}")

    print("done")

    return 0

