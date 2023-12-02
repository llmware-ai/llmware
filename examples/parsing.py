''' This example demonstrates the parsing capablities of llmware
      1. Parsing files into libraries
      2. Parsing files into Memory
      3. Paraing files to json
'''

import os
from llmware.configs import LLMWareConfig
from llmware.library import Library
from llmware.parsers import Parser, WebSiteParser, WikiParser
from llmware.resources import LibraryCatalog
from llmware.setup import Setup

# Demonstrate adding files to a library, which implicitly parses them and creates blocks
def parsing_files_into_library(library_name):

    # Create new library
    print (f"\n > Creating library {library_name}...")
    library = Library().create_new_library(library_name)

    # Load the llmware sample files
    print (f"\n > Loading the llmware sample files...")

    # note: if you have used this example previously, UN-Resolutions-500 is new path
    #   -- to pull updated sample files, set: 'over_write=True'

    sample_files_path = Setup().load_sample_files(over_write=False)
    pdf_file_path = os.path.join(sample_files_path,"UN-Resolutions-500")
    office_file_path = os.path.join(sample_files_path,"Agreements")
    
    # Add files from a local path (this will pull in all supported file types:
    #  .pdf, .pptx, .docx, .xlsx, .csv, .txt, .json, .wav, and .zip, .jpg, .png
    print (f"\n > Adding (parsing) files from {pdf_file_path}...")
    library.add_files(pdf_file_path)
    
    # Add only files of a speciic type
    print (f"\n > Adding (parsing) Office files only, from {office_file_path}...")
    library.add_office(office_file_path)
    
    # Note: An alternate method is to call the Parser directly and pass in the library. For example:
    #Parser(library=library).parse_pdf(sample_files_path)
    #Parser(library=library).parse_office(sample_files_path)

    # Add other/specialized content to library
    print (f"\n > Adding Website and Wiki content....")
    website_results = library.add_website("https://www.politico.com")
    wikipedia_results = library.add_wiki("Joe Biden")

    # Note: The default size of blocks is set to 400 characters (~100 tokens).  This can be configured by 
    # setting the following value prior to adding files and the parsers will use it has a guide when creating blocks
    library.block_size_target_characters = 800

    # Print the library stats
    library_card = LibraryCatalog().get_library_card(library_name)
    blocks = library_card["blocks"]
    documents = library_card["documents"]
    images = library_card["images"]
    print (f"\n > Library Stats")
    print (f"  - {blocks} blocks, {documents} documents, {images} images")
    print (f"      Note: images extracted during parsing can be found here: {library.image_path}")

# For some use cases you may only need to parse one or a few files.
# You can do so completely in memory and no state/parsing output will be saved
def parsing_files_into_memory():

    # Load the llmware sample files
    print (f"\n > Loading the llmware sample files...")
    sample_files_path = Setup().load_sample_files()
    
    # Parse individual documents. The output will be a list of blocks (dicts with metadata)
    pdf_file_path = os.path.join(sample_files_path,"SmallLibrary")
    pdf_file = "Gaia EXECUTIVE EMPLOYMENT AGREEMENT.pdf"
    print (f"\n > Parsing {pdf_file}")
    pdf_parsed_output = Parser().parse_one_pdf(pdf_file_path, pdf_file)
    page_number = pdf_parsed_output[0]["master_index"]
    block_text = pdf_parsed_output[0]["text"]
    print(f"\nFirst block found on page {page_number}:\n{block_text}")

    # Parse an MS Office document.  The parser handles .pptx, .docx and .xlsx
    office_file_path = os.path.join(sample_files_path,"SmallLibrary")
    office_file = "Janis-Joplin-s-Biography.docx"
    print (f"\n > Parsing {office_file}")
    office_parsed_output = Parser().parse_one_office(office_file_path, office_file)
    page_number = office_parsed_output[0]["master_index"]
    block_text = office_parsed_output[0]["text"]
    print(f"\nFirst block found on page {page_number}:\n{block_text}")
    
    # Perform OCR to extract text from iamges (e.g scanned documents) 
    image_file_path = os.path.join(sample_files_path,"Images")
    image_file = "Apache2_License.png"
    print (f"\n > Parsing {image_file}")
    image_parsed_output = Parser().parse_one_image(image_file_path, image_file)
    block_text = image_parsed_output[0]["text"]
    print(f"\nFirst block found in image:\n{block_text}")

    # Parse website
    website = "https://politico.com"
    print (f"\n > Parsing {website}")
    website_parsed_output = Parser().parse_website(website, write_to_db=False,save_history=False,get_links=False)
    block_text = website_parsed_output[0]["text"]
    print(f"\nFirst block found in website:\n{block_text}")

    # Parse wiki
    wiki_topic = "Canada"
    print (f"\n > Parsing wiki article '{wiki_topic}'")
    wiki_parsed_output = Parser().parse_wiki([wiki_topic],  write_to_db=False,save_history=False, target_results = 10)
    block_text = wiki_parsed_output[0]["text"]
    print(f"\nFirst block found in wiki:\n{block_text}")


# Parse an entire folder to json (import all supported file types)
def parse_to_json():

    # Load the llmware sample files
    print (f"\n > Loading the llmware sample files...")
    sample_files_path = Setup().load_sample_files()
    input_folder = os.path.join(sample_files_path,"SmallLibrary")

    # Create a parser
    parser = Parser()
    
    # Parse entire folder to json
    print (f"\n > Parsing folder: {input_folder}...")
    blocks  = parser.ingest_to_json(input_folder)
    print (f"Total Blocks: {len(parser.parser_output)}")
    print (f"Files Parsed:")
    for processed_file in blocks["processed_files"]:
        print(f"  - {processed_file}")

parsing_files_into_library("parsing_tests")
parsing_files_into_memory()
parse_to_json()