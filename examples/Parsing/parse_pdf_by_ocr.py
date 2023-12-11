
""" This example demonstrates how to parse PDF documents consisting of scanned pages using OCR
      1. Note: uses pdf2image library - requires separate install locally of lib tesseract
      2. This is a useful fall-back for scanned documents, if not possible to parse digitally
"""

import os
import time

from llmware.parsers import Parser
from llmware.setup import Setup


def parsing_pdf_by_ocr ():

    print(f"Example - Parsing PDF with Scanned Pages")

    # Load the llmware sample files
    print (f"\nstep 1 - loading the llmware sample files")
    sample_files_path = Setup().load_sample_files()
    print (f"step 2 - llmware sample files saved locally at: {sample_files_path}")

    # Parse individual documents. The output will be a list of blocks (dicts with metadata)
    ingestion_file_path = os.path.join(sample_files_path,"Agreements")

    files = os.listdir(ingestion_file_path)

    parser = Parser()

    for i, doc in enumerate(files):

        t0 = time.time()

        print(f"\nProcessing file - {i} - {doc}")

        parser_output = parser.parse_one_pdf_by_ocr_images(ingestion_file_path, doc,save_history=True)

        if parser_output:
            print(f"Completed parsing - {doc} - time - {time.time()-t0} - blocks created - {len(parser_output)}")

            # to see the full output of the blocks created - uncomment this section
            """
            for j, entries in enumerate(parser_output):
                print(f"parsed blocks created: {j} - {entries}")
            """

    return 0


if __name__ == "__main__":

    x = parsing_pdf_by_ocr()

