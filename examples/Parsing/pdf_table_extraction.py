
""" This example illustrates how to ** extract financial tables from PDF documents **

   extract_pdf_tables - shows end-to-end flow to automatically extract tables from PDFs
   the sample documents (~15 financial documents - mostly 10Ks and annual reports) are available in public S3 repo

   this example is also reviewed in the llmware YouTube video 'Extract Tables from PDFs'
   Check out this video on the llmware Youtube channel at:  https://www.youtube.com/watch?v=YYcimVQEgO8&t=4s

"""

import os

from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup
from llmware.configs import LLMWareConfig


def extract_pdf_tables(library_name):

    print(f"\nExample: Parsing Financial PDF Documents and Extracting Tables")

    #   Step 1 - create library
    print("\nstep 1 - create library - {}".format(library_name))

    lib = Library().create_new_library(library_name)

    #   Step 2 - pull down the sample files (or insert your own files here)
    #   --note: if you need to pull updated sample files, set 'over_write=True'
    print("step 2 - pull sample files - FinDocs")

    sample_files_path = Setup().load_sample_files(over_write=True)

    #   Step 3 - parse and extract all of the content from the Financial Documents
    print("step 3 - parse, text chunk and text index the documents")

    parsing_output = lib.add_files(input_folder_path=os.path.join(sample_files_path, "FinDocs"))

    #   review the parsing output summary info - all of the text and table blocks are in Mongo collection
    print("update: parsing_output - ", parsing_output)

    #   Step 4 - export all of the content into .jsonl files with metadata
    output_fp = LLMWareConfig().get_tmp_path()
    print("update: Step 4 - exporting all blocks into file path - ", output_fp)

    output1 = lib.export_library_to_jsonl_file(output_fp, "{}_export.jsonl".format(library_name))

    #   Step 5 - export all of the tables as csv with 'amazon'
    print("update: Step 5 - exporting all tables with 'amazon' as csv files into file path - ", output_fp)

    output2 = Query(lib).export_all_tables(query="amazon", output_fp=output_fp)

    return output2


if __name__ == "__main__":

    LLMWareConfig().set_active_db("sqlite")

    p = extract_pdf_tables("pdf_table_lib_example")

