
""" 'SLICING & DICING like a Data Ninja' - this example shows a variety of parsing, extraction, and packaging
techniques.

    This example builds on the 'Microsoft IR' file set, which is included in the llmware sample files.

        -- published on Microsoft IR website:  https://www.microsoft.com/en-us/investor
        -- zip archives of the investor kit for each of the quarters since 2020

    We will parse the zipped files, which contain ~150 Powerpoints, Word and Excel files.

    Note: parsing ZIP files is easy as they are automatically unzipped, and the individual files are then
    routed to the appropriate parser.

    After completing the parsing:

    1.  OCR the images - we will run an OCR against all of the extracted images and add that text into our
    library collection.

        -NOTE: to complete this OCR step requires two additional dependencies be installed:
                -- pytesseract - `pip3 install pytesseract`
                -- libtesseract - `brew install tesseract` or `sudo apt install libtesseract-dev` or
                                    download executable and install through GUI on Windows

    2.  Extract the tables to CSV - we will export all of the tables we found (which are indexed in the DB),
    and publish out as individual .CSV files.

    3.  Extract all of the images - and take a look at where we can find the individual .PNG and .JPEG files.

    4.  Dump the whole database into a JSONL file.

    5.  Create and configure a 'model-ready' dataset.

"""


from llmware.library import Library
from llmware.configs import LLMWareConfig
from llmware.setup import Setup
from llmware.retrieval import Query
from llmware.dataset_tools import Datasets


def create_microsoft_ir_library(library_name="microsoft_ir_350"):

    """ Pulls the Microsoft IR sample files - parses, text chunks and creates Library. """

    print("update: downloading and caching microsoft investor relations sample files")

    microsoft_ir = Setup().load_selected_sample_files(sample_folder="microsoft_ir")

    print("update: completed downloading files @ files path: ", microsoft_ir)

    my_lib = Library().create_new_library(library_name)

    #   pass the zip archives like any other file in .add_files method
    parsing_output = my_lib.add_files(microsoft_ir, chunk_size=400, max_chunk_size=600,smart_chunking=1,
                                      get_tables=True, get_images=True)

    print("update: parsing output: ", parsing_output)

    #   check out the images extracted
    print("update: images extracted to path: ", my_lib.image_path)

    #   run a quick query
    qr = Query(my_lib).text_query("azure", result_count=10)

    for i, res in enumerate(qr):
        print("results: ", i, res)

    return 0


def slice_and_dice_special(ln):

    #   Step 1 - load a library that we have created
    lib = Library().load_library(ln)

    #   Step 2 - export all of the tables to CSV
    q = Query(lib)
    extracted_tables = q.export_all_tables(output_fp=lib.output_path)

    print("extracted tables summary: ", extracted_tables)

    #   Step 3 - run OCR on all of the extracted images
    #   to run OCR:  need to install pytesseract & lib tesseract

    lib.run_ocr_on_images(add_to_library=True, chunk_size=400, min_size=10, realtime_progress=True)
    print("done with ocr processing")

    #   Step 4 - export the whole library to jsonl file
    output = lib.export_library_to_jsonl_file(lib.output_path, "microsoft_ir_lib")

    #   Step 5 - create dataset
    ds = Datasets(library=lib, testing_split=0.10, validation_split=0.10, ds_id_mode="random_number")
    ds_output = ds.build_text_ds(min_tokens=100, max_tokens=500)

    print("done with dataset")

    return True


#   main execution script starts here

if __name__ == "__main__":

    #   select collection db - mongo, sqlite, or postgres
    LLMWareConfig().set_active_db("sqlite")

    ln = "microsoft_investor_relations_350"

    #   build the library (only required once)
    create_microsoft_ir_library(library_name=ln)

    #   run the slicing and dicing
    slice_and_dice_special(ln)

