
""" This example demonstrates how to parse PDF documents consisting of scanned pages using OCR

    Parsing a PDF-by-OCR is much slower and loses metadata, compared with a digital parse - but this is a
    necessary fall-back for many 'paper-scanned' PDFs, or in the relatively rare cases in which
    digital parsing is not successful

    NOTE:  there are several dependencies that must be installed to run this example:

    pip install:
        -- pip3 install pytesseract
        -- pip3 install pdf2image

    core libraries:
        -- tesseract: e.g., (Mac OS) - brew install tesseract or (Linux) - sudo apt install tesseract
        -- poppler:   e.g., (Mac OS) - brew install poppler or (Linux) - sudo apt-get install -y poppler-utils
                     for Windows download see - https://poppler.freedesktop.org/

"""

import os
import time

from llmware.parsers import Parser
from llmware.setup import Setup
from llmware.configs import LLMWareConfig

from importlib import util
if not util.find_spec("pytesseract") or not util.find_spec("pdf2image"):
    print("\nto run this example, please install pytesseract and pdf2image - and there may be core libraries "
          "that need to be installed as well - see comments above more details.")


def parsing_pdf_by_ocr ():

    print(f"Example - Parsing PDF with Scanned Pages")

    LLMWareConfig().set_active_db("sqlite")

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

