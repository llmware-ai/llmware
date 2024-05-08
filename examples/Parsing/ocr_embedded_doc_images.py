
""" Example:   ** Applying OCR to Images in LLMWare Library **

    This example shows how to:

    A.  identify images in a library (post the initial parsing)
    B.  run an OCR against the images to derive the text from the image using the OCR
    C.  insert the text into the database library collection for subsequent retrieval.

    Note: this example uses additional python dependencies:

        -- pip3 install pytesseract

    Note: this example uses an OCR engine, which is outside of the core llmware package.  To install on Ubuntu:

        -- sudo apt install tesseract-ocr
        -- sudo apt install libtesseract-dev

    [Other platforms:
        -- Mac: brew install tesseract
        -- Windows:   GUI download installer - see UB-Mannheim @ www.github.com/UB-Mannheim/tesseract/wiki

    Running this script will NOT make any changes to the original "image" block record in the text collection.
    Rather than update/replace the existing record, the script will create a new supplemental entry for each 'image'.

    Each new record will have the following attributes:

        --"text" block with the text derived from the OCR, including the original source doc_ID, file source name and
        page number for easy reference

        --new block_ID starting at 100000 (safely out of the 'block namespace' of the original document, and easy to
            identify as 'derived' text from an OCR, rather than an original part of the document

        --text chunking applied to the OCR output, especially useful if it is a large image with a lot of text, e.g.,
        a scanned page of a book - if the image contains a large text passage, it will be chunked and saved as
        potentially several individual text blocks, 'chunked' according to the text chunk size parameter.

        --a custom 'string' flag in special_field1 that indicates the text was created by an OCR, and includes a
        reference to the original doc_ID and block_ID

        --optional threshold for length of OCR to text to capture, e.g., if <10 characters captured, then may be
        preferable to skip (higher probability that image is noisy)

"""


from llmware.library import Library
from llmware.configs import LLMWareConfig
from llmware.resources import CollectionRetrieval, CollectionWriter
from llmware.parsers import ImageParser

from importlib import util
if not util.find_spec("pytesseract"):
    print("\nto run this example requires additional dependencies, including pytesseract - see comments above in "
          "this script.  to install pytesseract:  pip3 install pytesseract.")


def ocr_images_in_library(library_name, add_new_text_block=False, chunk_size=400, min_chars=10):

    lib = Library().load_library(library_name)
    image_path = lib.image_path

    #   check here to see the images extracted from the original parsing
    print("update: image source file path: ", image_path)

    #   query the collection DB by content_type == "image"
    image_blocks = CollectionRetrieval(library_name).filter_by_key("content_type", "image")
    doc_update_list = {}
    new_text_created = 0

    #   iterate through the image blocks found
    for i, block in enumerate(image_blocks):

        #   "external_files" points to the image name that will be found in the image_path above for the library
        img_name = block["external_files"]

        #   each doc_ID is unique for the library collection
        doc_id = block["doc_ID"]

        #   block_IDs are unique only for the document, and generally run in sequential ascending order
        block_id = block["block_ID"]

        #   note: _id not used, but it is a good lookup key that can be easily inserted in special_field1 below
        bid = block["_id"]

        #   preserve_spacing == True will keep \n \r \t and other white space
        #   preserve_spacing == False collapses the white space into a single space for 'more dense' text only
        output = ImageParser(text_chunk_size=chunk_size).process_ocr(image_path,img_name,preserve_spacing=False)

        print("update: ocr output: ", output)

        #   note: test before writing to the collection
        if add_new_text_block:

            for text_chunk in output:

                if text_chunk.strip():

                    # optional to keep only more substantial chunks of text
                    if len(text_chunk) > min_chars:

                        #   ad hoc tracker to keep incrementing the block_id for every new image in a particular doc
                        if doc_id in doc_update_list:
                            new_block_id = doc_update_list[doc_id]
                            doc_update_list.update({doc_id: new_block_id+1})
                        else:
                            new_block_id = 100000
                            doc_update_list.update({doc_id: new_block_id+1})

                        new_block = block

                        #   feel free to adapt these attributes to fit for purpose
                        new_block.update({"block_ID": new_block_id})
                        new_block.update({"content_type": "text"})
                        new_block.update({"embedding_flags": {}})
                        new_block.update({"text_search": text_chunk})
                        new_block.update({"special_field1": f"OCR applied to image in document - "
                                                            f"{doc_id} - block - {block_id}"})

                        #   new _id will be assigned by the database directly
                        if "_id" in new_block:
                            del new_block["_id"]

                        print("update: writing new text block - ", new_text_created, doc_id, block_id, text_chunk, new_block)

                        #   creates the new record
                        CollectionWriter(ln).write_new_parsing_record(new_block)

                        new_text_created += 1

    return new_text_created


#   main execution script starts here

if __name__ == "__main__":

    #   select collection db - mongo, sqlite, or postgres
    LLMWareConfig().set_active_db("postgres")

    #   create a library (source documents must have embedded images!)
    ln = "my_library"
    fp = "/path/to/pdf_or_office_files_with_images/"
    lib = Library().create_new_library(ln)

    #   parse the documents
    lib.add_files(fp, get_images=True,get_tables=True, chunk_size=400, max_chunk_size=600,
                  smart_chunking=1, verbose_level=2)

    print("done parsing")

    #   runs ocr on the images in the newly-created library
    #   set add_new_text_block == True to add new rows in the database (otherwise, will just run the OCR in memory)
    new_blocks = ocr_images_in_library(ln,add_new_text_block=False,chunk_size=400, min_chars=10)

    print("done with ocr processing")

    g = CollectionRetrieval(ln).get_whole_collection()

    #   may need to loop through the iterator if extremely large collection (otherwise, pull_all into memory OK)

    blocks = g.pull_all()

    ocr_count = 0

    #   look at the new text entries created and inserted into the collection
    for i, b in enumerate(blocks):
        if b["block_ID"] > 9999:
            print("update: new ocr text entry: ", ocr_count, b["doc_ID"], b["block_ID"], b["content_type"],
                  b["special_field1"], b["text_search"])

            ocr_count += 1

