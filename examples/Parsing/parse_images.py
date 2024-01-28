
""" This example demonstrates how to parse images using OCR into a Library
    1.  This uses the tesseract OCR engine - which must be loaded as a prerequisite native lib
    2.  This illustrates how to explicitly parse an image file (png, jpeg)
    3.  If image files are included in an overall ".add_files", then they will be handled as images automatically
"""

import os
from llmware.library import Library, LibraryCatalog
from llmware.parsers import Parser, ImageParser
from llmware.setup import Setup


# Demonstrate adding files to a library, which implicitly parses them and creates blocks
def parsing_image_sources_into_library(library_name):

    print(f"Example - Parsing Images")

    #   load the llmware sample files
    #   -- to pull updated sample files, set: 'over_write=True'

    sample_files_path = Setup().load_sample_files(over_write=False)
    print (f"Step 2 - loading the llmware sample files and saving at: {sample_files_path}")

    #   note: to replace with your own documents, just point to a local folder path with the documents
    # Perform OCR to extract text from iamges (e.g scanned documents)
    image_file_path = os.path.join(sample_files_path, "Images")

    parser = Parser()

    for i, images in enumerate(os.listdir(image_file_path)):

        # image_file = "Apache2_License.png"
        print(f"\n > Parsing {images}")
        image_parsed_output = parser.parse_one_image(image_file_path, images,save_history=True)
        block_text = image_parsed_output[0]["text"]
        print(f"\nFirst block found in image:\n{block_text}")

    print(f"\nText Blocks extracted in total: ", len(parser.parser_output))

    return 0


if __name__ == "__main__":

    lib_name = "my_image_library_0"

    x = parsing_image_sources_into_library(lib_name)

