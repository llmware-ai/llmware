
"""This example demonstrates how to parse documents in memory and output directly to json file
      -- Does not require the use of database
      -- Useful for parsing-on-the-fly and then extracting output into another step in a pipeline
"""

import os
from llmware.parsers import Parser
from llmware.setup import Setup


def parse_to_json(selected_folder):

    print(f"\nExample - Parsing Batch of Documents Directly to JSON file")

    #   initialize default - will be used for output
    my_json_file_name = ""
    processed_files_list = []

    #   load the llmware sample files
    print (f"\nstep 1 - loading the llmware sample files")
    sample_files_path = Setup().load_sample_files()
    input_folder = os.path.join(sample_files_path,selected_folder)

    #   create a parser
    parser = Parser()

    print (f"step 2 - parsing all of the files in parsing input folder: {input_folder}")

    #   parse entire folder to json
    parsing_output = parser.ingest_to_json(input_folder)

    #   display the output
    if parsing_output:
        if "parser_output_filename" in parsing_output:
            my_json_file_name = parsing_output["parser_output_filename"]

        if "processed_files" in parsing_output:
            processed_files_list = parsing_output["processed_files"]
    else:
        print("update: unexpected error - parsing did not get completed")

    print (f"step 3 - parsing completed")
    print (f"  - parsing history file path: {parser.parser_folder}")
    print (f"  - parsing output created: {my_json_file_name}")
    print (f"  - files processed: {processed_files_list}")
    print (f"  - total blocks created: {len(parser.parser_output)}")    # note: this is in the parser state

    return parsing_output


if __name__ == "__main__":

    #  note on sample documents - downloaded by Setup()
    #       UN-Resolutions-500 is 500 pdf documents
    #       Invoices is 40 pdf invoice samples
    #       Agreements is ~15 contract documents
    #       AgreementsLarge is ~80 contract documents
    #       FinDocs is ~15 financial annual reports and earnings
    #       SmallLibrary is a mix of ~10 pdf and office documents

    # this is a list of document folders that will be pulled down by calling Setup()
    sample_folders = ["Agreements", "Invoices", "UN-Resolutions-500", "SmallLibrary", "FinDocs", "AgreementsLarge"]

    selected_folder = sample_folders[0]
    output = parse_to_json (selected_folder)

