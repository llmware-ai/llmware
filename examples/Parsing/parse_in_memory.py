
"""This example demonstrates how to parse individual documents into memory
      -- Does not require the use of database
"""

import os
from llmware.parsers import Parser
from llmware.setup import Setup


def parsing_files_into_memory(folder_name):

    print(f"\nExample - Parsing Documents into Memory (no DB required)")

    # Load the llmware sample files
    print (f"\nstep 1 - loading the llmware sample files")
    sample_files_path = Setup().load_sample_files()
    print (f"step 2- llmware sample files saved locally at: {sample_files_path}")

    # Parse individual documents. The output will be a list of blocks (dicts with metadata)
    ingestion_file_path = os.path.join(sample_files_path,folder_name)

    files = os.listdir(ingestion_file_path)

    print(f"\t\t--total of {len(files)} documents found in folder path - will parse each one.")

    for i, doc in enumerate(files):

        parser_output = Parser().parse_one(ingestion_file_path,doc,save_history=False)

        if parser_output:
            print(f"\nupdate: parsed document - {i} - {doc}")
            print(f"update: extracted {len(parser_output)} blocks of information - showing first 10 blocks for display:")

            if len(parser_output) < 10:
                sample_display_len = len(parser_output)
            else:
                sample_display_len = 10

            parser_output = parser_output[0:sample_display_len]

            for j, blocks in enumerate(parser_output):
                text = blocks["text"]
                if len(text) > 100:
                    text = text[0:100] + " ... "
                print(f"update: block - {blocks['block_ID']} - {text}")
        else:
            print(f"\nupdate: did not find any content for file - {doc}")

    return 0


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

    library_name = "parsing_test_lib_0"
    selected_folder = sample_folders[0]
    output = parsing_files_into_memory (selected_folder)
