
""" This example shows how to parse .zip archives that include a mix of different file types - as an example,
    we will use a set of Microsoft Investor Relations files, published on the Microsoft IR website -

      --  https://www.microsoft.com/en-us/investor

    We will pull a consolidated set of zip archives from llmware sample files repository that consists of
    zip archives downloaded directly from the Microsoft IR set as the investor kit for each of the quarters
    since 2020.

    Parsing ZIP archives is easy - they are automatically opened, and the source files are then routed to the
    appropriate parser.

"""

from llmware.library import Library
from llmware.configs import LLMWareConfig
from llmware.setup import Setup
from llmware.retrieval import Query

#   feel free to use postgres or mongo, if installed
LLMWareConfig().set_active_db("sqlite")

print("update: downloading and caching microsoft investor relations sample files")

microsoft_ir = Setup().load_selected_sample_files(sample_folder="microsoft_ir")

print("update: completed downloading files @ files path: ", microsoft_ir)

my_lib = Library().create_new_library("microsoft_investor_relations_1")

#   pass the zip archives like any other file in .add_files method
parsing_output = my_lib.add_files(microsoft_ir)

print("update: parsing output: ", parsing_output)

#   check out the images extracted
print("update: images extracted to path: ", my_lib.image_path)

#   optional - run an OCR against all of the images in the library - check out the example:
#   --  examples/Parsing/ocr_embedded_doc_images.py

#   run a quick query
qr = Query(my_lib).text_query("azure", result_count=10)

for i, res in enumerate(qr):
    print("results: ", i, res)

