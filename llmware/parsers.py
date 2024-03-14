# Copyright 2023 llmware

# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.  You
# may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.
"""The parsers module implements all parsers, i.e. all conversions fom a modality to bloacks in a database.

The module currently implements parsers for websites, images, voices, texts, wikis, and dialogs.
"""


import time
import json
import re
from werkzeug.utils import secure_filename
import os
from zipfile import ZipFile, ZIP_DEFLATED
import shutil
import requests
from urllib.request import urlopen, Request

try:
    from bs4 import BeautifulSoup
except ImportError:
    pass

try:
    import pytesseract
    from pytesseract.pytesseract import TesseractNotFoundError
except ImportError:
    pass

try:
    from pdf2image import convert_from_path
    from pdf2image.exceptions import PDFInfoNotInstalledError
except ImportError:
    pass

import logging
import random
from ctypes import *
import platform

from llmware.configs import LLMWareConfig, LLMWareTableSchema
from llmware.util import Utilities, WikiKnowledgeBase, TextChunker
from llmware.resources import CollectionRetrieval, CollectionWriter, ParserState

from llmware.exceptions import DependencyNotInstalledException, FilePathDoesNotExistException, \
    OCRDependenciesNotFoundException, LLMWareException


class Parser:

    def __init__(self, library=None, account_name="llmware", parse_to_db=False, file_counter=1):

        """ Main class for handling parsing, e.g., conversion of documents and other unstructured files
        into indexed text collection of 'blocks' in database.   For most use cases, Parser does not need
        to be invoked directly - as Library and Prompt are more natural client interfaces. """

        # check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):
            # if not explicitly set up by user, then create folder directory structure
            LLMWareConfig.setup_llmware_workspace()

        # new path for parser history - records of parse job outputs (outside of library construct)
        self.parser_folder = LLMWareConfig.get_parser_path()

        if not os.path.exists(self.parser_folder):
            os.mkdir(self.parser_folder)

        # create tmp workspace for parser
        tmp_path = LLMWareConfig.get_tmp_path()
        parser_tmp_work_folder = os.path.join(tmp_path, "parser_tmp" + os.sep)

        # if tmp path not in place, explicitly create
        if not os.path.exists(tmp_path):
            os.mkdir(tmp_path)
            os.chmod(tmp_path, 0o777)

        # if tmp workspace folder already exists, then delete - start fresh
        if os.path.exists(parser_tmp_work_folder):
            shutil.rmtree(parser_tmp_work_folder)
        os.mkdir(parser_tmp_work_folder)

        self.parser_tmp_folder = parser_tmp_work_folder

        # shift library to optional parameter - allows calls to Parser class without a library declared
        self.account_name = account_name

        # placeholder used if no library passed in constructor
        self.library_name = "default"

        self.library = library
        self.block_size_target_characters = 600

        # will track and increment files processed within same parsing job
        self.file_counter = file_counter

        # by default, parse_to_db = False
        self.parse_to_db = parse_to_db

        self.parser_job_id = ParserState().issue_new_parse_job_id()

        # if library is passed to parser, then assumes will write to library db, if available
        if library:
            self.account_name = library.account_name
            self.library_name = library.library_name
            self.block_size_target_characters = library.block_size_target_characters

            self.parser_image_folder = library.image_path

            # sets parse_to_db == True only if (a) library passed in constructor, and (b) collection db found

            # check if collection datastore is connected
            if CollectionRetrieval(self.library_name,account_name=self.account_name).test_connection():
                # if not check_db_uri(timeout_secs=3):
                self.parse_to_db = True
            else:
                logging.warning("warning: Parser not able to connect to document store collection database"
                                "at uri - %s - will write parsing output to a parsing file.",
                                LLMWareConfig.get_db_uri_string())

                self.parse_to_db = False
        else:
            # if no library passed
            self.parse_to_db = False
            self.parser_image_folder = self.parser_tmp_folder

        # used to pass to the C parsers in pdf/office parsing paths
        self.collection_path = LLMWareConfig.get_db_uri_string()
        self.collection_db_configs = LLMWareConfig.get_db_configs()
        self.collection_db_username = LLMWareConfig.get_db_user_name()
        self.collection_db_password = LLMWareConfig.get_db_pw()

        # 'active' output state tracker
        self.parser_output = []

        self.ACCEPTED_FILE_FORMATS = ["pptx","xlsx","docx","pdf","txt","csv","html","jsonl",
                                      "jpg","jpeg","png","wav","zip", "md"]
        self.office_types = ["PPTX", "pptx", "XLSX", "xlsx", "DOCX", "docx"]
        self.pdf_types = ["PDF", "pdf"]
        self.text_types = ["txt", "csv", "html", "jsonl", "md"]
        self.ocr_types = ["jpg", "jpeg", "png"]
        self.voice_types = ["wav"]
        self.zip_types = ["zip"]
        self.office_work_folder = None
        self.pdf_work_folder = None
        self.text_work_folder = None
        self.voice_work_folder = None
        self.zip_work_folder = None
        self.ocr_work_folder = None
        self.dialog_work_folder = None
        self.website_work_folder = None
        self.supported_parser_types = ["pdf", "office", "text", "voice", "dialog", "web", "image",
                                       "pdf_by_ocr"]

        self.schema = LLMWareTableSchema.get_parser_table_schema()

        if self.parse_to_db:
            # if table does not exist, then create
            if CollectionWriter("parser_events", account_name=self.account_name).check_if_table_build_required():

                # create "status" table
                CollectionWriter("parser_events", account_name=self.account_name).create_table("parser_events",
                                                                                               self.schema)

            # parsers write status update - confirm that status tables created
            if CollectionWriter("status", account_name=self.account_name).check_if_table_build_required():

                CollectionWriter("status",
                                 account_name=self.account_name).create_table("status",
                                                                              LLMWareTableSchema.get_status_schema())

    def clear_state(self):

        """Clears parser state. """

        self.parser_output = []
        return self

    def save_state(self):

        """ Saves parser state. """

        ParserState().save_parser_output(self.parser_job_id, self.parser_output)
        return self

    def _setup_workspace(self, local_work_path):

        """ Internal method to setup workspace for parsing job. """

        # set up local workspace folders
        if not local_work_path:

            if self.library:
                local_work_path = self.library.tmp_path
            else:
                # if no library selected, then default to parser_tmp_folder
                local_work_path = self.parser_tmp_folder

        if not os.path.exists(local_work_path):
            os.makedirs(local_work_path, exist_ok=True)

        office_fp = os.path.join(local_work_path, "process_office_files" + os.sep)
        pdf_fp = os.path.join(local_work_path, "process_pdf_files" + os.sep)
        text_fp = os.path.join(local_work_path, "process_text_files" + os.sep)
        ocr_fp = os.path.join(local_work_path, "process_ocr_files" + os.sep)
        voice_fp = os.path.join(local_work_path, "process_voice_files" + os.sep)
        zip_fp = os.path.join(local_work_path, "process_zip_files" + os.sep)

        office_workspace_fp = os.path.join(local_work_path, "office_tmp" + os.sep)

        # start clean with new directories for both office + pdf
        if os.path.exists(office_fp):
            shutil.rmtree(office_fp, ignore_errors=True)
        os.mkdir(office_fp)
        self.office_work_folder = office_fp

        if os.path.exists(pdf_fp):
            shutil.rmtree(pdf_fp, ignore_errors=True)
        os.mkdir(pdf_fp)
        self.pdf_work_folder = pdf_fp

        if os.path.exists(text_fp):
            shutil.rmtree(text_fp, ignore_errors=True)
        os.mkdir(text_fp)
        self.text_work_folder = text_fp

        if os.path.exists(ocr_fp):
            shutil.rmtree(ocr_fp, ignore_errors=True)
        os.mkdir(ocr_fp)
        self.ocr_work_folder = ocr_fp

        if os.path.exists(voice_fp):
            shutil.rmtree(voice_fp, ignore_errors=True)
        os.mkdir(voice_fp)
        self.voice_work_folder = voice_fp

        if os.path.exists(zip_fp):
            shutil.rmtree(zip_fp, ignore_errors=True)
        os.mkdir(zip_fp)
        self.zip_work_folder = zip_fp

        if os.path.exists(office_workspace_fp):
            shutil.rmtree(office_workspace_fp, ignore_errors=True)
        os.mkdir(office_workspace_fp)
        self.office_tmp = office_workspace_fp

    def _collator(self, input_folder_path, dupe_check=False):

        """ Internal utility method to prepare and organize files for parsing. """

        # run comparison for existing files if dupe_check set True
        # default case - no checking for dupes
        existing_files = []

        # run comparison for existing files if dupe_check set True
        if self.library:
            if dupe_check and os.path.exists(self.library.file_copy_path):
                existing_files = os.listdir(self.library.file_copy_path)

        # counters
        dup_counter = 0
        office_found = 0
        pdf_found = 0
        zip_found = 0
        text_found = 0
        ocr_found = 0
        voice_found = 0

        # list of input files
        input_file_names = os.listdir(input_folder_path)
        files_to_be_processed = []
        duplicate_files = []


        if dupe_check:
            # we get a reduced list of input_file_names if in existing_files is files we try to process
            duplicate_files_tmp = list(set(input_file_names) - set(existing_files))
            # the duplicates are those that where not in duplicate_files_tmp so we take out the tmp from the input_file_names
            # what's left is the duplicates
            duplicate_files =  list(set(input_file_names) - set(duplicate_files_tmp))
            # the counter is the length of the array
            dup_counter = len(duplicate_files)
            # We are done with this and we don't need to n times loop as before
            # we set the imput_file_names to be the reduced list to not to process dupe files
            input_file_names = duplicate_files_tmp




        for filename in input_file_names:

            filetype = filename.split(".")[-1]

            files_to_be_processed.append(filename)

            # copy file into specific channel for targeted parser

            if filetype.lower() in self.office_types:
                shutil.copy(os.path.join(input_folder_path,filename), os.path.join(self.office_work_folder,filename))
                office_found += 1

            if filetype.lower() in self.pdf_types:
                shutil.copy(os.path.join(input_folder_path,filename), os.path.join(self.pdf_work_folder, filename))
                pdf_found += 1

            if filetype.lower() in self.text_types:
                shutil.copy(os.path.join(input_folder_path,filename), os.path.join(self.text_work_folder,filename))
                text_found += 1

            if filetype.lower() in self.ocr_types:
                shutil.copy(os.path.join(input_folder_path,filename), os.path.join(self.ocr_work_folder,filename))
                ocr_found += 1

            if filetype.lower() in self.voice_types:
                shutil.copy(os.path.join(input_folder_path,filename), os.path.join(self.voice_work_folder,filename))
                voice_found += 1

            if filetype.lower() in self.zip_types:
                shutil.copy(os.path.join(input_folder_path,filename), os.path.join(self.zip_work_folder,filename))
                zip_found += 1

        logging.info("update:  Duplicate files (skipped): %s ", dup_counter)
        logging.info("update:  Total uploaded: %s ", len(input_file_names))

        if zip_found > 0:

            # if any zip files found in upload, then unpack and process first
            #       --once zip extracted, push all files into the appropriate work folder for pdf, office, etc.
            #       --inside zip_extract_handler- will update counters

            zip_work_order = self.zip_extract_handler()
            pdf_found += zip_work_order["pdf"]
            office_found += zip_work_order["office"]
            text_found += zip_work_order["text"]
            voice_found += zip_work_order["voice"]
            ocr_found += zip_work_order["ocr"]

        work_order = {"pdf": pdf_found,
                      "office": office_found,
                      "text": text_found,
                      "ocr": ocr_found,
                      "voice": voice_found,
                      "duplicate_files": duplicate_files,
                      "file_list": files_to_be_processed}

        return work_order

    def ingest (self, input_folder_path, dupe_check=True):

        """ Main method for large-scale parsing. Takes only a single input which is the local input folder path
         containing the files to be parsed.

         Optional dupe_check parameter set to True to restrict ingesting a file with the same name as a file
         already in the library. """

        # input_folder_path = where the input files are located

        # first - confirm that library and connection to collection db are in place
        if not self.library or not self.parse_to_db:

            logging.error("error: Parser().ingest() method requires loading a library, e.g., Parser(library=my_library),"
                          "and a connection to a document data store - please try Parse().parse_one set of methods"
                          "to parse a document of any type directly into list of dictionaries in memory, and written"
                          "to /parser_history as a .json file")

            parsing_results = {"processed_files": 0, "rejected_files": 0, "duplicate_files": []}
            return parsing_results

        # prepares workspace for individual parsers
        self._setup_workspace(self.parser_tmp_folder)
        
        # collate and sort the file types in the work path
        work_order = self._collator(input_folder_path, dupe_check=dupe_check)

        #   write to db - True only if library loaded + collection connect in place
        write_to_db = self.parse_to_db

        if work_order["office"] > 0:
            self.parse_office(self.office_work_folder, save_history=False)
            self.uploads(self.office_work_folder)

        if work_order["pdf"] > 0:
            self.parse_pdf(self.pdf_work_folder, save_history=False)
            self.uploads(self.pdf_work_folder)

        if work_order["text"] > 0:
            self.parse_text(self.text_work_folder, save_history=False)
            self.uploads(self.text_work_folder)

        if work_order["ocr"] > 0:
            self.parse_image(self.ocr_work_folder, save_history=False)
            self.uploads(self.ocr_work_folder)

        if work_order["voice"] > 0:
            self.parse_voice(self.voice_work_folder, save_history=False)
            self.uploads(self.voice_work_folder)

        # need to systematically capture list of rejected docs

        processed, not_processed = self.input_ingestion_comparison(work_order["file_list"])

        parsing_results = {"processed_files": processed,
                           "rejected_files": not_processed,
                           "duplicate_files": work_order["duplicate_files"]}

        return parsing_results

    def ingest_to_json(self, input_folder_path):

        """ Mirrors the main ingest method but intended for writing parsing output directly to json when
        'writing_to_db' = False. """

        # prepares workspace for individual parsers
        self._setup_workspace(self.parser_tmp_folder)

        # collate and sort the file types in the work path
        work_order = self._collator(input_folder_path, dupe_check=False)

        #   write to db - True only if library loaded + collection connect in place
        self.parse_to_db = False
        self.library = None

        if work_order["office"] > 0:
            self.parse_office(self.office_work_folder, write_to_db=False, save_history=False)

        if work_order["pdf"] > 0:
            self.parse_pdf(self.pdf_work_folder, write_to_db=False, save_history=False)

        if work_order["text"] > 0:
            self.parse_text(self.text_work_folder, write_to_db=False, save_history=False)

        if work_order["ocr"] > 0:
            self.parse_image(self.ocr_work_folder, write_to_db=False, save_history=False)

        if work_order["voice"] > 0:
            self.parse_voice(self.voice_work_folder, write_to_db=False, save_history=False)

        # need to systematically capture list of rejected docs

        fn = ParserState().save_parser_output(self.parser_job_id, self.parser_output)

        processed, not_processed = self.input_ingestion_comparison_from_parser_state(work_order["file_list"])

        parsing_results = {"processed_files": processed,
                           "rejected_files": not_processed,
                           "parser_output_filename": fn}

        return parsing_results

    def parse_by_type(self, parser_type, input_folder_path, url=None):

        """ Parse files by content type. """

        output = None

        if parser_type in self.supported_parser_types:

            if parser_type == "pdf":
                output = self.parse_pdf(input_folder_path, write_to_db=self.parse_to_db)

            if parser_type == "office":
                output = self.parse_office(input_folder_path, write_to_db=self.parse_to_db)

            if parser_type == "text":
                output = self.parse_text(input_folder_path, write_to_db=self.parse_to_db)

            if parser_type == "voice":
                output = self.parse_voice(input_folder_path, write_to_db=self.parse_to_db)

            if parser_type == "dialog":
                output = self.parse_dialog(input_folder_path, write_to_db=self.parse_to_db)

            if parser_type == "web":
                output = self.parse_website(url, write_to_db=self.parse_to_db)

            if parser_type == "pdf_by_ocr":
                output = self.parse_pdf_by_ocr_images(input_folder_path, write_to_db=self.parse_to_db)

        return output

    def zip_extract_handler(self):

        """ Unzips and extracts files from zip archive -and iteratively push files to specific file path. """

        # tracker for files found inside the zip
        pdf_found = 0
        office_found = 0
        text_found = 0
        ocr_found = 0
        voice_found = 0

        z = ""

        zip_files = os.listdir(self.zip_work_folder)

        for my_zip_names in zip_files:

            # iterate thru all of the .zip files found

            my_zip = self.zip_work_folder + my_zip_names

            # create fresh /tmp file to extract the zip files
            if os.path.exists(os.path.join(self.zip_work_folder,"tmp")):
                shutil.rmtree(os.path.join(self.zip_work_folder,"tmp"), ignore_errors=True)
            os.mkdir(os.path.join(self.zip_work_folder,"tmp"))

            try:
                # unzip and extract into /tmp folder
                z = ZipFile(my_zip, 'r', compression=ZIP_DEFLATED)
                ZipFile.extractall(z, os.path.join(self.zip_work_folder, "tmp"))
                success_code = 1

            except:
                # may fail
                success_code = -1
                logging.info("error: caution - could not open Zip- %s ", my_zip)

            if success_code == 1:

                #   iterate thru all of the files found in the zip archive
                #   apply secure_filename and prep_filename
                #   route to the appropriate work folder, if applicable

                for f in z.namelist():

                    # will apply secure name and cap length, but does not run duplicate file check
                    fn = self.prep_filename(f, max_len=240, secure_name=True)
                    ext = fn.split(".")[-1]

                    if success_code == 1:

                        if ext in ["pptx", "docx", "xlsx"]:
                            shutil.copy(os.path.join(self.zip_work_folder,"tmp" + os.sep,f),
                                        os.path.join(self.office_work_folder,fn))
                            office_found += 1

                        if ext in ["pdf"]:
                            shutil.copy(os.path.join(self.zip_work_folder, "tmp" + os.sep, f),
                                        os.path.join(self.pdf_work_folder,fn))
                            pdf_found += 1

                        if ext in ["txt", "csv"]:
                            shutil.copy(os.path.join(self.zip_work_folder, "tmp" + os.sep, f),
                                        os.path.join(self.text_work_folder,fn))
                            text_found += 1

                        if ext in ["png", "jpg", "jpeg"]:
                            shutil.copy(os.path.join(self.zip_work_folder,"tmp" + os.sep,f),
                                        os.path.join(self.ocr_work_folder,fn))
                            ocr_found += 1

                        if ext in ["wav"]:
                            shutil.copy(os.path.join(self.zip_work_folder,"tmp" + os.sep,f),
                                        os.path.join(self.voice_work_folder, fn))
                            voice_found += 1

        work_order = {"pdf": pdf_found, "office": office_found, "text": text_found, "ocr": ocr_found, "voice": voice_found}

        return work_order

    def convert_parsing_txt_file_to_json(self, file_path=None, fn="pdf_internal_test0.txt"):

        """ Utility method that picks up a .txt file output from Office or PDF parser and converts to a list
        of dictionaries for insertion in an external DB. """

        default_keys = ["block_ID", "doc_ID", "content_type", "file_type", "master_index", "master_index2",
                        "coords_x", "coords_y", "coords_cx", "coords_cy", "author_or_speaker", "modified_date",
                        "created_date", "creator_tool", "added_to_collection", "file_source",
                        "table", "external_files", "text", "header_text", "text_search",
                        "user_tags", "special_field1", "special_field2", "special_field3", "graph_status", "dialog"]

        if not file_path:
            # this is the default path where parser will put the txt file
            file_path = self.parser_tmp_folder

        # test script for parsing txt file
        try:
            output_file = open(os.path.join(file_path, fn), "r", encoding="utf-8-sig",errors="ignore").read()

        except Exception as e:
            print (e)
            logging.warning("warning: Parser - could not find parsing output - %s - %s ", file_path, fn)
            return []

        # this seems to work with a few library sets, but we can probably enhance the 'splitting'
        #   <END_BLOCK>\n marks the end of a block of text with ~28 dictionary keys
        blocks = output_file.split("<END_BLOCK>\n")

        output_list = []

        for i, b in enumerate(blocks):

            # split of "\n<" will split the block into ~28 individual slices
            splitter = b.split("\n<")
            block_dict = {}
            # it is likely redundant to have 'double loop' but it is a little extra insurance
            for j, keys in enumerate(default_keys):
                # iterates thru each of the default keys
                match_found = -1
                for k, entries in enumerate(splitter):

                    key_string = keys + ">: "
                    if entries.startswith(key_string):

                        value = entries[len(key_string):].strip()

                        # remove trailing ','
                        if value.endswith(","):
                            value= value[:-1]

                        block_dict.update({keys: value})
                        match_found = 1
                        break

                if match_found == -1:
                    # note: could not find a key - i, keys, splitter - no action required
                    do_nothing = 1

            if block_dict:
                if len(block_dict) == len(default_keys):
                    output_list.append(block_dict)
                else:
                    logging.warning("update: Parser - potential error- parsing-to-dict conversion - "
                                    "lengths don't match - %s - %s", len(block_dict), len(default_keys))

        return output_list

    def parse_pdf (self, fp, write_to_db=True, save_history=True, image_save=1):

        """ Main PDF parser method - wraps ctypes interface to call PDF parser. """

        output = []

        write_to_filename = "pdf_parse_output_0.txt"

        #   must have three conditions in place - (a) user selects, (b) ping successfully, and (c) library loaded
        if write_to_db and self.parse_to_db and self.library:
            write_to_db_on = 1
            unique_doc_num = -1
        else:
            write_to_db_on = 0
            unique_doc_num = int(self.file_counter)

        #   warning to user that no library loaded in Parser constructor
        if write_to_db and not self.library:
            logging.warning("warning: Parser().parse_pdf - request to write to database but no library loaded "
                            "in Parser constructor.   Will write parsing output to file and will place the "
                            "file in /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logging.error("warning: Parser().parse_pdf - could not connect to database at %s.  Will write "
                          "parsing output to file and will place the file in /parser_history path.",
                          self.collection_path)

        #   function declaration for .add_pdf_main_llmware
        # char * input_account_name,
        # char * input_library_name,
        # char * input_fp,
        # char * db,
        # char * db_uri_string,
        # char * db_name,
        # char * db_user_name,
        # char * db_pw,
        # char * input_images_fp,
        # int input_debug_mode,
        # int input_image_save_mode,
        # int write_to_db_on,
        # char * write_to_filename,
        # int user_blok_size,
        # int unique_doc_num,
        # int status_manager_on,
        # int status_manager_increment,
        # char * status_job_id

        #   if any issue loading module, will be captured at .get_module_pdf_parser()
        _mod_pdf = Utilities().get_module_pdf_parser()

        # pdf_handler = _mod_pdf.add_pdf_main_customize_parallel
        pdf_handler = _mod_pdf.add_pdf_main_llmware_config

        pdf_handler.argtypes = (c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p,
                                c_char_p, c_int, c_int, c_int, c_char_p, c_int,c_int,c_int,c_int,c_char_p)

        pdf_handler.restypes = c_int

        # prepare all of the inputs to invoke the c library

        t0 = time.time()

        # config options pulled from the Library object
        account_name = create_string_buffer(self.account_name.encode('ascii', 'ignore'))
        library_name = create_string_buffer(self.library_name.encode('ascii', 'ignore'))

        # image_fp = self.library.image_path
        image_fp = self.parser_image_folder

        if not image_fp.endswith(os.sep):
            image_fp += os.sep

        image_fp_c = create_string_buffer(image_fp.encode('ascii', 'ignore'))

        input_collection_db_path = LLMWareConfig().get_db_uri_string()

        collection_db_path_c = create_string_buffer(input_collection_db_path.encode('ascii', 'ignore'))

        #   fp = passed as parameter -> this is the input file path folder containing the .PDF docs to be parsed
        if not fp.endswith(os.sep):
            fp += os.sep

        fp_c = create_string_buffer(fp.encode('ascii', 'ignore'))

        # debug_mode global parameter
        #   "on" = 1
        #   "file name only" = 2
        #   "deep debug" = 3
        #   "off" = 0 & all other values

        # pull debug mode 'verbosity' levels from LLMWareConfig
        debug_mode = LLMWareConfig.get_config("debug_mode")

        supported_options = [0, 1, 2, 3]

        if debug_mode not in supported_options:
            debug_mode = 0

        input_debug_mode = c_int(debug_mode)  # default - 0 = "off"
        input_image_save_mode = c_int(image_save)  # default - 1 = "on" | use 0 = "off" in production

        write_to_db_on_c = c_int(write_to_db_on)
        write_to_filename_c = create_string_buffer(write_to_filename.encode('ascii', 'ignore'))

        # pull target block size from library parameters
        user_block_size = c_int(self.block_size_target_characters)  # standard 400-600

        # unique_doc_num -> if <0: interpret as "OFF" ... if >=0 then use and increment doc_id directly
        # unique_doc_num = -1
        unique_doc_num_c = c_int(unique_doc_num)

        # db credentials
        db_user_name = self.collection_db_username
        db_user_name_c = create_string_buffer(db_user_name.encode('ascii', 'ignore'))

        db_pw = self.collection_db_password
        db_pw_c = create_string_buffer(db_pw.encode('ascii', 'ignore'))

        db = LLMWareConfig.get_config("collection_db")

        db = create_string_buffer(db.encode('ascii','ignore'))
        db_name = account_name

        status_manager_on = c_int(1)
        status_manager_increment = c_int(10)
        status_job_id = create_string_buffer("1".encode('ascii','ignore'))

        #
        #                   * main call to pdf library *
        #

        logging.info("update: start parsing of PDF Documents...")

        #   function declaration for .add_pdf_main_llmware
        # char * input_account_name,
        # char * input_library_name,
        # char * input_fp,
        # char * db,
        # char * db_uri_string,
        # char * db_name,
        # char * db_user_name,
        # char * db_pw,
        # char * input_images_fp,
        # int input_debug_mode,
        # int input_image_save_mode,
        # int write_to_db_on,
        # char * write_to_filename,
        # int user_blok_size,
        # int unique_doc_num,
        # int status_manager_on,
        # int status_manager_increment,
        # char * status_job_id

        pages_created = pdf_handler(account_name, library_name, fp_c, db, collection_db_path_c, db_name,
                                    db_user_name_c, db_pw_c,
                                    image_fp_c,
                                    input_debug_mode, input_image_save_mode, write_to_db_on_c,
                                    write_to_filename_c, user_block_size, unique_doc_num_c,
                                    status_manager_on, status_manager_increment, status_job_id)

        logging.info("update:  completed parsing of pdf documents - time taken: %s ", time.time() - t0)

        if write_to_db_on == 0:
            # package up results in Parser State
            parser_output = self.convert_parsing_txt_file_to_json(self.parser_image_folder, write_to_filename)
            if len(parser_output) > 0:
                last_entry = parser_output[-1]
                last_doc_id = last_entry["doc_ID"]

                self.file_counter = int(last_doc_id)

                logging.info("update: adding new entries to parser output state - %s", len(parser_output))

                self.parser_output += parser_output
                output += parser_output

            if save_history:
                ParserState().save_parser_output(self.parser_job_id, parser_output)

        return output

    def parse_pdf_deprecated (self, fp, write_to_db=True, save_history=True, image_save=1):

        """ Deprecated - this is the pdf entry point for PDF binaries packaged up to llmware-0.1.14 -- replaced
        starting with llmware-0.2.0 """

        output = []

        write_to_filename = "pdf_parse_output_0.txt"

        #   must have three conditions in place - (a) user selects, (b) ping successfully, and (c) library loadedd
        if write_to_db and self.parse_to_db and self.library:
            write_to_db_on = 1
            unique_doc_num = -1
        else:
            write_to_db_on = 0
            unique_doc_num = int(self.file_counter)

        #   warning to user that no library loaded in Parser constructor
        if write_to_db and not self.library:
            logging.warning("warning: Parser().parse_pdf - request to write to database but no library loaded "
                            "in Parser constructor.   Will write parsing output to file and will place the "
                            "file in /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logging.error("warning: Parser().parse_pdf - could not connect to database at %s.  Will write "
                          "parsing output to file and will place the file in /parser_history path.",
                          LLMWareConfig().get_db_uri_string())

        #   function declaration for .add_pdf_main_llmware
        #       char * input_account_name,
        #       char * input_library_name,
        #       char * input_fp,
        #       char * input_mongo_db_path,
        #       char * input_images_fp,
        #       int input_debug_mode,
        #       int input_image_save_mode,
        #       int write_to_db_on,
        #       char * write_to_filename,
        #       int user_block_size,
        #       int unique_doc_num,
        #       char * db_user_name,
        #       char * db_pw

        #   if any issue loading module, will be captured at .get_module_pdf_parser()
        _mod_pdf = Utilities().get_module_pdf_parser()

        # pdf_handler = _mod_pdf.add_pdf_main_customize_parallel
        pdf_handler = _mod_pdf.add_pdf_main_llmware

        pdf_handler.argtypes = (c_char_p, c_char_p, c_char_p, c_char_p, c_char_p,
                                c_int, c_int, c_int,
                                c_char_p,
                                c_int, c_int,
                                c_char_p, c_char_p)

        pdf_handler.restypes = c_int

        # prepare all of the inputs to invoke the c library

        t0 = time.time()

        # config options pulled from the Library object
        account_name = create_string_buffer(self.account_name.encode('ascii', 'ignore'))
        library_name = create_string_buffer(self.library_name.encode('ascii', 'ignore'))

        # image_fp = self.library.image_path
        image_fp = self.parser_image_folder

        if not image_fp.endswith(os.sep):
            image_fp += os.sep

        image_fp_c = create_string_buffer(image_fp.encode('ascii', 'ignore'))
        input_collection_db_path = self.collection_path
        collection_db_path_c = create_string_buffer(input_collection_db_path.encode('ascii', 'ignore'))

        #   fp = passed as parameter -> this is the input file path folder containing the .PDF docs to be parsed
        if not fp.endswith(os.sep):
            fp += os.sep

        fp_c = create_string_buffer(fp.encode('ascii', 'ignore'))

        # debug_mode global parameter
        #   "on" = 1
        #   "file name only" = 2
        #   "deep debug" = 3
        #   "off" = 0 & all other values
        
        # pull debug mode 'verbosity' levels from LLMWareConfig
        debug_mode = LLMWareConfig.get_config("debug_mode")
        
        supported_options = [0,1,2,3]
        
        if debug_mode not in supported_options:
            debug_mode = 0

        input_debug_mode = c_int(debug_mode)            # default - 0 = "off"
        input_image_save_mode = c_int(image_save)       # default - 1 = "on" | use 0 = "off" in production

        write_to_db_on_c = c_int(write_to_db_on)
        write_to_filename_c = create_string_buffer(write_to_filename.encode('ascii','ignore'))

        # pull target block size from library parameters
        user_block_size = c_int(self.block_size_target_characters)   # standard 400-600

        # unique_doc_num -> if <0: interpret as "OFF" ... if >=0 then use and increment doc_id directly
        # unique_doc_num = -1
        unique_doc_num_c = c_int(unique_doc_num)

        # db credentials
        db_user_name = self.collection_db_username
        db_user_name_c = create_string_buffer(db_user_name.encode('ascii', 'ignore'))

        db_pw = self.collection_db_password
        db_pw_c = create_string_buffer(db_pw.encode('ascii', 'ignore'))

        #
        #                   * main call to pdf library *
        #

        logging.info("update: start parsing of PDF Documents...")

        #   function declaration for .add_pdf_main_llmware
        #       char * input_account_name,
        #       char * input_library_name,
        #       char * input_fp,
        #       char * input_mongodb_path,
        #       char * input_images_fp,
        #       int input_debug_mode,
        #       int input_image_save_mode,
        #       int write_to_db_on,
        #       char * write_to_filename,
        #       int user_block_size,
        #       int unique_doc_num,
        #       char * db_user_name,
        #       char * db_pw

        pages_created = pdf_handler(account_name, library_name, fp_c, collection_db_path_c, image_fp_c,
                                    input_debug_mode, input_image_save_mode, write_to_db_on_c,
                                    write_to_filename_c, user_block_size, unique_doc_num_c,
                                    db_user_name_c, db_pw_c)

        logging.info("update:  completed parsing of pdf documents - time taken: %s ", time.time() - t0)

        if write_to_db_on == 0:
            # package up results in Parser State
            parser_output = self.convert_parsing_txt_file_to_json(self.parser_image_folder,write_to_filename)
            if len(parser_output) > 0:
                last_entry = parser_output[-1]
                last_doc_id = last_entry["doc_ID"]

                self.file_counter = int(last_doc_id)

                logging.info("update: adding new entries to parser output state - %s", len(parser_output))

                self.parser_output += parser_output
                output += parser_output

            if save_history:
                ParserState().save_parser_output(self.parser_job_id,parser_output)

        return output

    def parse_office_deprecated (self, input_fp, write_to_db=True, save_history=True):

        """ Deprecated - this is the office parser entry point for Office parser binaries packaged up to
        llmware-0.1.14 -- replaced starting with llmware-0.2.0 """

        output = []

        # used internally by parser to capture text
        write_to_filename = "office_parser_output_0.txt"

        #   must have three conditions in place - (a) user selects, (b) ping successfully, and (c) library loadedd
        if write_to_db and self.parse_to_db and self.library:
            write_to_db_on = 1
            unique_doc_num = -1
        else:
            write_to_db_on = 0
            unique_doc_num = int(self.file_counter)

        #   warning to user that no library loaded in Parser constructor
        if write_to_db and not self.library:
            logging.warning("error: Parser().parse_office - request to write to database but no library loaded "
                            "in Parser constructor.   Will write parsing output to file and will place the "
                            "file in Parser /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logging.error("error: Parser().parse_office - could not connect to database at %s.  Will write "
                          "parsing output to file and will place the file in Library /images path.",
                          self.collection_path)

        # designed for bulk upload of office parse into library structure

        if not input_fp.endswith(os.sep):
            input_fp += os.sep

        office_fp = input_fp

        workspace_fp = os.path.join(self.parser_tmp_folder,"office_tmp" + os.sep)

        if not os.path.exists(workspace_fp):
            os.mkdir(workspace_fp)
            os.chmod(workspace_fp, 0o777)

        # need to synchronize as config parameter

        # start timing track for parsing job
        t0 = time.time()

        # only one tmp work folder used currently - can consolidate over time
        for z in range(0, 5):

            if os.path.exists(os.path.join(workspace_fp,str(z))):
                shutil.rmtree(os.path.join(workspace_fp,str(z)), ignore_errors=True)

            if not os.path.exists(os.path.join(workspace_fp,str(z))):
                os.mkdir(os.path.join(workspace_fp,str(z)))
                os.chmod(os.path.join(workspace_fp, str(z)), 0o777)

        # end -initialize workspace

        #   if any issue loading module, will be captured at .get_module_office_parser()
        _mod = Utilities().get_module_office_parser()

        # new endpoint for llmware
        main_handler = _mod.add_files_main_llmware

        #   int add_files_main_llmware:
        #       char * input_account_name,
        #       char * input_library_name,
        #       char * input_fp,
        #       char * workspace_fp,
        #       char * input_mongodb_path,
        #       char * image_fp,
        #       int input_debug_mode,
        #       int write_to_db_on,
        #       char * write_to_filename,
        #       int unique_doc_num,
        #       char *db_user_name,
        #       char *db_pw

        # main_handler = _mod.add_files_main_customize_parallel
        main_handler.argtypes = (c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p,
                                 c_int, c_int,
                                 c_char_p,
                                 c_int,
                                 c_char_p, c_char_p)

        main_handler.restype = c_int

        # three inputs - account_name // library_name // fp to web_dir - files to be processed
        # prep each string:    account_name = create_string_buffer(py_account_str.encode('ascii','ignore'))

        account_name = create_string_buffer(self.account_name.encode('ascii', 'ignore'))
        library_name = create_string_buffer(self.library_name.encode('ascii', 'ignore'))

        fp_c = create_string_buffer(office_fp.encode('ascii', 'ignore'))
        workspace_fp_c = create_string_buffer(workspace_fp.encode('ascii', 'ignore'))

        # debug_mode global parameter
        #   "on" = 1
        #   "file name only" = 2
        #   "deep debug" = 3
        #   "off" = 0 & all other values
        
        debug_mode = LLMWareConfig.get_config("debug_mode")
        
        supported_options = [0,1,2,3]
        
        if debug_mode not in supported_options:
            debug_mode = 0
        
        debug_mode_c = c_int(debug_mode)

        # image_fp = self.library.image_path

        image_fp = self.parser_image_folder
        if not image_fp.endswith(os.sep):
            image_fp += os.sep

        image_fp_c = create_string_buffer(image_fp.encode('ascii', 'ignore'))

        input_collection_db_path = self.collection_path
        collection_path_c = create_string_buffer(input_collection_db_path.encode('ascii', 'ignore'))

        write_to_db_on_c = c_int(write_to_db_on)

        write_to_fn_c = create_string_buffer(write_to_filename.encode('ascii', 'ignore'))

        # unique_doc_num is key parameter - if <0: will pull from incremental db, if >=0, then will start at this value
        # unique_doc_num = -1
        unique_doc_num_c = c_int(unique_doc_num)

        # db credentials
        db_user_name = "llmware"
        db_user_name_c = create_string_buffer(db_user_name.encode('ascii', 'ignore'))

        db_pw = "test-123"
        db_pw_c = create_string_buffer(db_pw.encode('ascii', 'ignore'))

        #   int add_files_main_llmware:
        #       char * input_account_name,
        #       char * input_library_name,
        #       char * input_fp,
        #       char * workspace_fp,
        #       char * input_mongodb_path,
        #       char * image_fp,
        #       int input_debug_mode,
        #       int write_to_db_on,
        #       char * write_to_filename,
        #       int unique_doc_num,
        #       char * db_user_name,
        #       char * db_pw

        logging.info("update: start parsing of office documents...")

        pages_created = main_handler(account_name, library_name, fp_c, workspace_fp_c, collection_path_c, image_fp_c,
                                     debug_mode_c, write_to_db_on_c, write_to_fn_c, unique_doc_num_c,
                                     db_user_name_c, db_pw_c)

        logging.info("update:  completed parsing of office documents - time taken: %s ", time.time() - t0)

        if write_to_db_on == 0:
            # package up results in Parser State
            parser_output = self.convert_parsing_txt_file_to_json(self.parser_image_folder,write_to_filename)
            if len(parser_output) > 0:
                last_entry = parser_output[-1]
                last_doc_id = last_entry["doc_ID"]

                self.file_counter = int(last_doc_id)

                self.parser_output += parser_output
                output += parser_output

            if save_history:
                # save parser state
                ParserState().save_parser_output(self.parser_job_id,parser_output)

        return output

    def parse_office(self, input_fp, write_to_db=True, save_history=True):

        """ Primary method interface into Office parser with more db configuration options - implemented starting
        with llmware-0.2.0 """

        output = []

        # used internally by parser to capture text
        write_to_filename = "office_parser_output_0.txt"

        #   must have three conditions in place - (a) user selects, (b) ping successfully, and (c) library loaded
        if write_to_db and self.parse_to_db and self.library:
            write_to_db_on = 1
            unique_doc_num = -1
        else:
            write_to_db_on = 0
            unique_doc_num = int(self.file_counter)

        #   warning to user that no library loaded in Parser constructor
        if write_to_db and not self.library:
            logging.warning("error: Parser().parse_office - request to write to database but no library loaded "
                            "in Parser constructor.   Will write parsing output to file and will place the "
                            "file in Parser /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logging.error("error: Parser().parse_office - could not connect to database at %s.  Will write "
                          "parsing output to file and will place the file in Library /images path.",
                          self.collection_path)

        # designed for bulk upload of office parse into library structure

        if not input_fp.endswith(os.sep):
            input_fp += os.sep

        office_fp = input_fp

        workspace_fp = os.path.join(self.parser_tmp_folder, "office_tmp" + os.sep)

        if not os.path.exists(workspace_fp):
            os.mkdir(workspace_fp)
            os.chmod(workspace_fp, 0o777)

        # need to synchronize as config parameter

        # start timing track for parsing job
        t0 = time.time()

        # only one tmp work folder used currently - can consolidate over time
        for z in range(0, 5):

            if os.path.exists(os.path.join(workspace_fp, str(z))):
                shutil.rmtree(os.path.join(workspace_fp, str(z)), ignore_errors=True)

            if not os.path.exists(os.path.join(workspace_fp, str(z))):
                os.mkdir(os.path.join(workspace_fp, str(z)))
                os.chmod(os.path.join(workspace_fp, str(z)), 0o777)

        # end -initialize workspace

        #   if any issue loading module, will be captured at .get_module_office_parser()
        _mod = Utilities().get_module_office_parser()

        # new endpoint for llmware
        main_handler = _mod.add_files_main_llmware_opt

        """
        (char * input_account_name,
         char * input_library_name,
         char * input_fp,
         char * workspace_fp,

         char * db,
         char * db_uri_string,
         char * db_name,
         char * db_user_name,
         char * db_pw,

         char * image_fp,
         
         int input_debug_mode,
         int write_to_db_on,
         char * write_to_filename,
         int unique_doc_num,
         int user_blok_size,
         int status_manager_on,
         int status_manager_increment,
         char * status_job_id)
        """

        # main_handler = _mod.add_files_main_customize_parallel
        main_handler.argtypes = (c_char_p, c_char_p, c_char_p, c_char_p, c_char_p,
                                 c_char_p, c_char_p, c_char_p, c_char_p, c_char_p,
                                 c_int, c_int, c_char_p, c_int, c_int, c_int, c_int,
                                 c_char_p)

        main_handler.restype = c_int

        # three inputs - account_name // library_name // fp to web_dir - files to be processed
        # prep each string:    account_name = create_string_buffer(py_account_str.encode('ascii','ignore'))

        account_name = create_string_buffer(self.account_name.encode('ascii', 'ignore'))
        library_name = create_string_buffer(self.library_name.encode('ascii', 'ignore'))

        fp_c = create_string_buffer(office_fp.encode('ascii', 'ignore'))
        workspace_fp_c = create_string_buffer(workspace_fp.encode('ascii', 'ignore'))

        # debug_mode global parameter
        #   "on" = 1
        #   "file name only" = 2
        #   "deep debug" = 3
        #   "off" = 0 & all other values

        debug_mode = LLMWareConfig.get_config("debug_mode")

        supported_options = [0, 1, 2, 3]

        if debug_mode not in supported_options:
            debug_mode = 0

        debug_mode_c = c_int(debug_mode)

        # image_fp = self.library.image_path

        image_fp = self.parser_image_folder
        if not image_fp.endswith(os.sep):
            image_fp += os.sep

        image_fp_c = create_string_buffer(image_fp.encode('ascii', 'ignore'))

        # *** new *** - get db uri string
        input_collection_db_path = LLMWareConfig().get_db_uri_string()
        # print("update: input collection db path - ", input_collection_db_path)
        collection_db_path_c = create_string_buffer(input_collection_db_path.encode('ascii', 'ignore'))
        # *** end - new ***

        write_to_db_on_c = c_int(write_to_db_on)

        write_to_fn_c = create_string_buffer(write_to_filename.encode('ascii', 'ignore'))

        # unique_doc_num is key parameter - if <0: will pull from incremental db, if >=0, then will start at this value
        # unique_doc_num = -1
        unique_doc_num_c = c_int(unique_doc_num)

        # start new

        # pull target block size from library parameters
        user_block_size_c = c_int(self.block_size_target_characters)  # standard 400-600

        # db credentials
        db_user_name = self.collection_db_username
        db_user_name_c = create_string_buffer(db_user_name.encode('ascii', 'ignore'))

        db_pw = self.collection_db_password
        db_pw_c = create_string_buffer(db_pw.encode('ascii', 'ignore'))

        db = LLMWareConfig.get_config("collection_db")

        db = create_string_buffer(db.encode('ascii','ignore'))
        db_name = account_name

        status_manager_on_c = c_int(1)
        status_manager_increment_c = c_int(10)
        status_job_id_c = create_string_buffer("1".encode('ascii','ignore'))

        # end - new
        """
        (char * input_account_name,
         char * input_library_name,
         char * input_fp,
         char * workspace_fp,

         char * db,
         char * db_uri_string,
         char * db_name,
         char * db_user_name,
         char * db_pw,

         char * image_fp,
         int input_debug_mode,
         int write_to_db_on,
         char * write_to_filename,
         int unique_doc_num,
         int user_blok_size,
         int status_manager_on,
         int status_manager_increment,
         char * status_job_id)
        """

        # print("update: start parsing of office documents...")

        pages_created = main_handler(account_name, library_name, fp_c, workspace_fp_c,
                                     db, collection_db_path_c, db_name, db_user_name_c, db_pw_c,
                                     image_fp_c,
                                     debug_mode_c, write_to_db_on_c, write_to_fn_c, unique_doc_num_c,
                                     user_block_size_c, status_manager_on_c, status_manager_increment_c,
                                     status_job_id_c)

        logging.info("update:  completed parsing of office documents - time taken: %s ", time.time() - t0)

        if write_to_db_on == 0:
            # package up results in Parser State
            parser_output = self.convert_parsing_txt_file_to_json(self.parser_image_folder, write_to_filename)
            if len(parser_output) > 0:
                last_entry = parser_output[-1]
                last_doc_id = last_entry["doc_ID"]

                self.file_counter = int(last_doc_id)

                self.parser_output += parser_output
                output += parser_output

            if save_history:
                # save parser state
                ParserState().save_parser_output(self.parser_job_id, parser_output)

        return output

    def parse_text(self, input_fp, write_to_db=True, save_history=True, dupe_check=False,copy_to_library=False):

        """ Main entry point to parser for .txt, .csv, .json and .md files """

        output = []

        #   must have three conditions in place - (a) user selects, (b) ping successfully, and (c) library loaded
        if write_to_db and self.parse_to_db and self.library:
            write_to_db_on = 1
        else:
            write_to_db_on = 0

        #   warning to user that no library loaded in Parser constructor
        if write_to_db and not self.library:
            logging.warning("warning: Parser().parse_text - request to write to database but no library loaded "
                            "in Parser constructor.   Will write parsing output to file and will place the "
                            "file in /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logging.error("warning: Parser().parse_text - could not connect to database at %s.  Will write "
                          "parsing output to file and will place the file in /parser_history path.",
                          self.collection_path)

        # set counters
        blocks_created = 0
        docs_added = 0
        pages_added = 0
        content_type = "text"

        for file in os.listdir(input_fp):

            # by default, will process all files with text file extensions
            go_ahead = True

            if dupe_check:

                #   basic_library_duplicate_check returns TRUE if it finds the file
                if self.basic_library_duplicate_check(file):
                    go_ahead = False

            if go_ahead:

                text_output = []
                # increment and get new doc_id
                if write_to_db_on == 1:
                    self.library.doc_ID = self.library.get_and_increment_doc_id()

                file_type = file.split(".")[-1]

                # sub-routing by type of text file to appropriate handler

                if file_type.lower() in ["txt", "md"]:
                    # will parse as text
                    text_output = TextParser(self).text_file_handler (input_fp, file)
                    content_type = "text"
                    file_type = "txt"

                if file_type.lower() in ["csv"]:
                    # will parse as table
                    interpret_as_table=True
                    text_output = TextParser(self).csv_file_handler(input_fp, file, interpret_as_table=True)
                    content_type = "text"
                    file_type = "csv"
                    if interpret_as_table:
                        content_type = "table"

                if file_type.lower() in ["json","jsonl"]:
                    # will parse each line item as separate entry

                    interpret_as_table=False
                    keys = ["text"]
                    text_output = TextParser(self).jsonl_file_handler(input_fp,file,
                                                                      key_list=keys,
                                                                      interpret_as_table=interpret_as_table,
                                                                      separator="\n")
                    content_type = "text"
                    file_type = "jsonl"
                    if interpret_as_table:
                        content_type = "table"

                # consolidate into single function - breaking down output rows

                if write_to_db_on == 1:
                    new_output, new_blocks, new_pages = self._write_output_to_db(text_output, file,
                                                                                 content_type=content_type,
                                                                                 file_type=file_type)
                else:
                    new_output, new_blocks, new_pages = self._write_output_to_dict(text_output,file,
                                                                                   content_type=content_type,
                                                                                   file_type=file_type)

                # will pass output_blocks as return value
                output += new_output

                docs_added += 1
                blocks_created += new_blocks
                pages_added += new_pages

        # update overall library counter at end of parsing

        if len(output) > 0:
            if write_to_db_on == 1:
                dummy = self.library.set_incremental_docs_blocks_images(added_docs=docs_added,added_blocks=blocks_created,
                                                                        added_images=0, added_pages=pages_added)

            if save_history and write_to_db_on == 0:
                ParserState().save_parser_output(self.parser_job_id, self.parser_output)

            if copy_to_library:
                self.uploads(input_fp)

        return output

    def parse_pdf_by_ocr_images(self, input_fp, write_to_db=True, save_history=True,
                                dupe_check=False,copy_to_library=False):

        """ Alternative PDF parser option for scanned 'image-based' PDFs where digital parsing is not an option. """

        output = []

        #   must have three conditions in place - (a) user selects, (b) ping successfully, and (c) library loadedd

        if write_to_db and self.parse_to_db and self.library:
            write_to_db_on = 1
        else:
            write_to_db_on = 0

        #   warning to user that no library loaded in Parser constructor
        if write_to_db and not self.library:
            logging.warning("warning: Parser().parse_text - request to write to database but no library loaded "
                            "in Parser constructor.   Will write parsing output to file and will place the "
                            "file in /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logging.error("warning: Parser().parse_text - could not connect to database at %s.  Will write "
                          "parsing output to file and will place the file in /parser_history path.",
                          self.collection_path)

        # set counters
        blocks_added = 0
        docs_added = 0
        pages_added = 0

        content_type = "text"

        for file in os.listdir(input_fp):

            # by default, will process all files with text file extensions
            go_ahead = True

            if dupe_check:

                #   basic_library_duplicate_check returns TRUE if it finds the file
                if self.basic_library_duplicate_check(file):
                    go_ahead = False

            if go_ahead:

                ext = file.split(".")[-1]
                if ext == "pdf":
                    doc_fn = secure_filename(file)

                    # get new doc_ID number
                    if write_to_db_on == 1:
                        self.library.doc_ID = self.library.get_and_increment_doc_id()

                    docs_added += 1

                    output_by_page = ImageParser(self).process_pdf_by_ocr(input_fp, file)

                    for j, blocks in enumerate(output_by_page):

                        if write_to_db_on == 1:
                            new_output, new_blocks, _ = self._write_output_to_db(blocks,doc_fn,page_num=(j+1))
                        else:
                            new_output, new_blocks, _ = self._write_output_to_dict(blocks,doc_fn,page_num=(j+1))

                        output += new_output
                        blocks_added += new_blocks
                        pages_added += 1

                        print("update: writing doc - page - ", file, j, len(blocks))

        # update overall library counter at end of parsing

        if write_to_db_on == 1:
            dummy = self.library.set_incremental_docs_blocks_images(added_docs=docs_added,added_blocks=blocks_added,
                                                                    added_images=0, added_pages=pages_added)

        if save_history and write_to_db_on == 0:
            ParserState().save_parser_output(self.parser_job_id, self.parser_output)

        if copy_to_library:
            self.uploads(input_fp)

        return output

    def _write_output_to_db(self, output, file, content_type="text", file_type="text",page_num=1):

        """ Internal utility for preparing parser output to write to DB. """

        db_record_output = []

        # trackers
        blocks_added = 0
        pages_added = 0

        meta = {"author": "", "modified_date": "", "created_date": "", "creator_tool": ""}
        coords_dict = {"coords_x": 0, "coords_y": 0, "coords_cx": 0, "coords_cy": 0}

        counter = 0

        for entries in output:

            if content_type == "text":
                # table entry = "" [7]
                new_entry = (content_type, file_type, (page_num, 0), counter, "", "", file, "", entries, "",
                         "", entries, entries, "", entries, "", "", "", "", "")
            else:
                # could be table if csv file -> in this case, keep both text [11] and table [7]
                new_entry = (content_type, file_type, (page_num, 0), counter, "", "", file, entries, entries, "",
                             "", entries, entries, "", entries, "", "", "", "", "")

            counter += 1

            new_db_entry = self.add_create_new_record(self.library,new_entry, meta, coords_dict)
            db_record_output.append(new_db_entry)

            blocks_added += 1
            self.library.block_ID += 1

        # need to adapt potentially for longer text files
        pages_added = 1

        return db_record_output, blocks_added, pages_added

    def _write_output_to_dict(self, wp_output, input_fn, content_type="text", file_type="text", page_num=1):

        """ Internal utility for preparing parser output to dictionary. """

        output = []
        # consolidate output
        counter = 0
        blocks_added = 0
        pages_added = 0

        meta = {"author": "", "modified_date": "", "created_date": "", "creator_tool": ""}
        coords_dict = {"coords_x": 0, "coords_y": 0, "coords_cx": 0, "coords_cy": 0}

        for j, blocks in enumerate(wp_output):

            if content_type == "text":
                new_entry = ("text", file_type, (page_num, 0), counter, "", "", input_fn, "", blocks, "",
                                 "", blocks, blocks, "", blocks, "", "", "", "", "")
            else:
                # could be table if csv file -> in this case, keep both text [11] and table [7]
                new_entry = ("table", file_type, (page_num, 0), counter, "", "", input_fn, blocks, blocks, "",
                             "", blocks, blocks, "", blocks, "", "", "", "", "")

            # creates a single 'unbound' parsing output dict -> no storage
            parsing_output_dict = self.create_one_parsing_output_dict(counter,
                                                                      new_entry, meta, coords_dict,
                                                                      dialog_value="false")

            output.append(parsing_output_dict)
            blocks_added += 1

        pages_added = 1

        self.parser_output += output

        return output, blocks_added, pages_added

    def add_create_new_record(self, library, new_entry, meta, coords_dict,dialog_value="false",
                              write_to_db=True):

        """ Main 'write' method of new parser text chunk for python-based parsers to write to DB. """

        # assumes that new_entry is packaged in individual handler
        # objective is to keep one single place where new entry gets loaded into db
        # ensure consistency of db data model

        time_stamp = Utilities().get_current_time_now()

        new_entry = {
            "block_ID": library.block_ID,     # note - needs caution
            "doc_ID": library.doc_ID,       # note - needs caution
            "content_type": new_entry[0],
            "file_type": new_entry[1],
            "master_index": new_entry[2][0],
            # change from [1:] to [1]
            "master_index2": new_entry[2][1],
            "coords_x": coords_dict["coords_x"],
            "coords_y": coords_dict["coords_y"],
            "coords_cx": coords_dict["coords_cx"],
            "coords_cy": coords_dict["coords_cy"],
            "author_or_speaker": meta["author"],
            "modified_date": meta["modified_date"],
            "created_date": meta["created_date"],
            "creator_tool": meta["creator_tool"],
            "added_to_collection": time_stamp,
            "file_source": new_entry[6],
            "table": new_entry[7],
            "external_files": new_entry[10],
            "text": new_entry[11],
            "header_text": new_entry[13],
            "text_search": new_entry[14],
            "user_tags": new_entry[15],
            "special_field1": new_entry[17],
            "special_field2": new_entry[18],
            "special_field3": new_entry[19],
            "graph_status": "false",
            "dialog": dialog_value,
            "embedding_flags": {}
        }

        if write_to_db:
            # registry_id = library.collection.insert_one(new_entry).inserted_id
            registry_id = CollectionWriter(library.library_name,
                                           account_name=library.account_name).write_new_parsing_record(new_entry)

        return new_entry

    def create_one_parsing_output_dict(self, block_id,new_entry, meta, coords_dict,dialog_value="false"):

        """ Main method to prepare a new text chunk parser output for python-based parser as dictionary. """

        #   Mirrors the data structure in "self.add_create_new_record"
        #   --does not write_to_db or storage
        #   --does not assume that there is a library index
        #   --creates one parsing output dict that can be used and stored for any purpose (outside of library)

        #   Note: expects explicit passing of a block_id and doc_id as reference numbers

        time_stamp = Utilities().get_current_time_now()

        new_entry = {
            "block_ID": block_id,
            "doc_ID": self.file_counter,
            "content_type": new_entry[0],
            "file_type": new_entry[1],
            "master_index": new_entry[2][0],
            # change from [1:] to [1]
            "master_index2": new_entry[2][1],
            "coords_x": coords_dict["coords_x"],
            "coords_y": coords_dict["coords_y"],
            "coords_cx": coords_dict["coords_cx"],
            "coords_cy": coords_dict["coords_cy"],
            "author_or_speaker": meta["author"],
            "modified_date": meta["modified_date"],
            "created_date": meta["created_date"],
            "creator_tool": meta["creator_tool"],
            "added_to_collection": time_stamp,
            "file_source": new_entry[6],
            "table": new_entry[7],
            "external_files": new_entry[10],
            "text": new_entry[11],
            "header_text": new_entry[13],
            "text_search": new_entry[14],
            "user_tags": new_entry[15],
            "special_field1": new_entry[17],
            "special_field2": new_entry[18],
            "special_field3": new_entry[19],
            "graph_status": "false",
            "dialog": dialog_value,
            "embedding_flags": ""
        }

        return new_entry

    def parse_wiki(self, topic_list, write_to_db=True, save_history=False, target_results=10):

        """ Main entry point to parse a Wikipedia article. """

        output = []

        #   must have three conditions in place - (a) user selects, (b) ping successfully, and (c) library loadedd
        if write_to_db and self.parse_to_db and self.library:
            write_to_db_on = 1
        else:
            write_to_db_on = 0

        #   warning to user that no library loaded in Parser constructor
        if write_to_db and not self.library:
            logging.warning("warning: Parser().parse_text - request to write to database but no library loaded "
                            "in Parser constructor.   Will write parsing output to file and will place the "
                            "file in /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logging.error("warning: Parser().parse_text - could not connect to database at %s.  Will write "
                          "parsing output to file and will place the file in /parser_history path.",
                          self.collection_path)

        # set counters
        blocks_added = 0
        docs_added = 0
        pages_added = 0

        for i, topic in enumerate(topic_list):

            fn = "wiki-topic-" + secure_filename(topic) + ".txt"

            logging.info("update: parse_wiki - %s - %s", topic, fn)

            # increment and get new doc_id
            if write_to_db_on == 1:
                self.library.doc_ID = self.library.get_and_increment_doc_id()

            # topic_results = {"search_results": topic_query_results, "articles": articles_output,
            #                  "text_chunks": text_chunks}

            topic_results = WikiParser(self).add_wiki_topic(topic, target_results=target_results)

            wp_output = topic_results["text_chunks"]

            if write_to_db_on == 1:
                new_output, new_blocks, new_pages = self._write_output_to_db(wp_output, fn, content_type="text",
                                                                             file_type="wiki")

            else:
                new_output, new_blocks, new_pages = self._write_output_to_dict(wp_output,fn, content_type="text",
                                                                               file_type="wiki")
                output += new_output

            docs_added += 1
            blocks_added += new_blocks
            pages_added += new_pages

            for i, articles in enumerate(topic_results["articles"]):

                # need to copy into library_copy path
                if self.library:
                    upload_fp = self.library.file_copy_path
                else:
                    upload_fp = self.parser_tmp_folder

                # save as the article title now
                article_txt = articles["title"]+".txt"
                safe_name = self.prep_filename(article_txt)

                art = open(os.path.join(upload_fp,safe_name), "w", encoding='utf-8')
                art.write(articles["text"])
                art.close()

        if write_to_db_on == 1:
            dummy = self.library.set_incremental_docs_blocks_images(added_docs=docs_added, added_blocks=blocks_added,
                                                                    added_images=0, added_pages=pages_added)

        if save_history and write_to_db_on == 0:
            ParserState().save_parser_output(self.parser_job_id, self.parser_output)

        return output

    def parse_image(self, input_folder, write_to_db=True, save_history=True, dupe_check=False,copy_to_library=False):

        """ Main entry point for OCR based parsing of image files. """

        output = []

        #   must have three conditions in place - (a) user selects, (b) ping successfully, and (c) library loadedd
        if write_to_db and self.parse_to_db and self.library:
            write_to_db_on = 1
        else:
            write_to_db_on = 0

        #   warning to user that no library loaded in Parser constructor
        if write_to_db and not self.library:
            logging.warning("warning: Parser().parse_text - request to write to database but no library loaded "
                            "in Parser constructor.   Will write parsing output to file and will place the "
                            "file in /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logging.error("warning: Parser().parse_text - could not connect to database at %s.  Will write "
                          "parsing output to file and will place the file in /parser_history path.",
                          self.collection_path)

        # set counters
        blocks_added = 0
        docs_added = 0
        pages_added = 0

        for file in os.listdir(input_folder):

            # by default, will process all files with text file extensions
            go_ahead = True

            if dupe_check:

                #   basic_library_duplicate_check returns TRUE if it finds the file
                if self.basic_library_duplicate_check(file):
                    go_ahead = False

            if go_ahead:

                # increment and get new doc_id
                if write_to_db_on == 1:
                    self.library.doc_ID = self.library.get_and_increment_doc_id()

                ip_output = ImageParser(self).process_ocr(input_folder, file)

                if write_to_db_on == 1:
                    new_output, new_blocks, new_pages = self._write_output_to_db(ip_output,file,content_type="text",
                                                                                 file_type="ocr")
                else:
                    new_output, new_blocks, new_pages = self._write_output_to_dict(ip_output,file, content_type="text",
                                                                                   file_type="ocr")
                # return output value in either case
                output += new_output

                docs_added += 1
                blocks_added += new_blocks
                pages_added += new_pages

        if write_to_db_on == 1:
            dummy = self.library.set_incremental_docs_blocks_images(added_docs=docs_added, added_blocks=blocks_added,
                                                                    added_images=0, added_pages=pages_added)

        if save_history and write_to_db_on == 0:
            ParserState().save_parser_output(self.parser_job_id, self.parser_output)

        if copy_to_library:
            self.uploads(input_folder)

        return output

    def parse_voice(self, input_folder, write_to_db=True, save_history=True, dupe_check=False,copy_to_library=False):

        """ Main entry point for parsing voice wav files. """

        output = []

        #   must have three conditions in place - (a) user selects, (b) ping successfully, and (c) library loaded
        if write_to_db and self.parse_to_db and self.library:
            write_to_db_on = 1
        else:
            write_to_db_on = 0

        #   warning to user that no library loaded in Parser constructor
        if write_to_db and not self.library:
            logging.warning("warning: Parser().parse_text - request to write to database but no library loaded "
                            "in Parser constructor.   Will write parsing output to file and will place the "
                            "file in /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logging.error("warning: Parser().parse_text - could not connect to database at %s.  Will write "
                          "parsing output to file and will place the file in /parser_history path.",
                          self.collection_path)

        # set counters
        blocks_added = 0
        docs_added = 0
        pages_added = 0

        for file in os.listdir(input_folder):

            # by default, will process all files with text file extensions
            go_ahead = True

            if dupe_check:

                #   basic_library_duplicate_check returns TRUE if it finds the file
                if self.basic_library_duplicate_check(file):
                    go_ahead = False

            if go_ahead:

                # increment and get new doc_id
                if write_to_db_on == 1:
                    self.library.doc_ID = self.library.get_and_increment_doc_id()

                vp_output = VoiceParser(self).add_voice_file(input_folder, file)

                if write_to_db_on == 1:
                    new_output, new_blocks, new_pages = self._write_output_to_db(vp_output, file, content_type="text",
                                                                                 file_type="voice-wav")
                else:
                    new_output, new_blocks, new_pages = self._write_output_to_dict(vp_output,file, content_type="text",
                                                                                   file_type="voice-wav")
                # return output in either case
                output += new_output

                docs_added += 1
                blocks_added += new_blocks
                pages_added += new_pages

        if write_to_db_on == 1:
            dummy = self.library.set_incremental_docs_blocks_images(added_docs=docs_added, added_blocks=blocks_added,
                                                                    added_images=0, added_pages=pages_added)

        if save_history and write_to_db_on == 0:
            ParserState().save_parser_output(self.parser_job_id, self.parser_output)

        if copy_to_library:
            self.uploads(input_folder)

        return output

    def parse_dialog(self, input_folder, write_to_db=True, save_history=True, dupe_check=False,copy_to_library=True):

        """ Main entry point for parsing AWS dialog transcripts. """

        output = []

        #   must have three conditions in place - (a) user selects, (b) ping successfully, and (c) library loadedd
        if write_to_db and self.parse_to_db and self.library:
            write_to_db_on = 1
        else:
            write_to_db_on = 0

        #   warning to user that no library loaded in Parser constructor
        if write_to_db and not self.library:
            logging.warning("warning: Parser().parse_text - request to write to database but no library loaded "
                            "in Parser constructor.   Will write parsing output to file and will place the "
                            "file in /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logging.error("warning: Parser().parse_text - could not connect to database at %s.  Will write "
                          "parsing output to file and will place the file in /parser_history path.",
                          self.collection_path)

        # set counters
        conversation_turns = 0
        dialog_transcripts_added = 0
        counter = 0

        for file in os.listdir(input_folder):

            # by default, will process all files with text file extensions
            go_ahead = True

            if dupe_check:

                #   basic_library_duplicate_check returns TRUE if it finds the file
                if self.basic_library_duplicate_check(file):
                    go_ahead = False

            if go_ahead:

                if file.endswith(".json"):

                    # increment and get new doc_id
                    if write_to_db_on == 1:
                        self.library.doc_ID = self.library.get_and_increment_doc_id()

                    logging.info(f"update: dialog file - {file}")

                    dp_parse_output = DialogParser(self).parse_aws_json_file_format(input_folder, file)

                    block_id = 0

                    for i, blocks in enumerate(dp_parse_output):

                        logging.info(f"update: dialog turn - {i} {blocks}")

                        # iterate thru each block -> add to metadata
                        speaker_name = blocks["speaker_name"]

                        meta = {"author": speaker_name, "modified_date": "", "created_date": "", "creator_tool": ""}

                        coords_dict = {"coords_x": blocks["start_time"], "coords_y": blocks["stop_time"],
                                       "coords_cx": 0, "coords_cy": 0}

                        text_entry = blocks["text"]

                        # conforming file format with full path of dialog intake path

                        format_type = "aws_json"

                        new_entry = ("text", format_type, (1, 0), counter, "", "", input_folder + file,
                                     text_entry, text_entry, "", "", text_entry, text_entry, "", text_entry,
                                     "", "", "", "", "")

                        counter += 1
                        dialog_transcripts_added += 1
                        conversation_turns += 1

                        if write_to_db_on == 1:
                            entry_output = self.add_create_new_record(self.library, new_entry, meta, coords_dict,
                                                                      dialog_value="true")
                            self.library.block_ID += 1
                        else:
                            entry_output = self.create_one_parsing_output_dict(block_id,new_entry,meta,coords_dict,
                                                                               dialog_value="true")
                            block_id += 1
                            self.parser_output.append(entry_output)

                        # return output in either case
                        output.append(entry_output)

        pages_added = dialog_transcripts_added

        if write_to_db_on == 1:
            dummy = self.library.set_incremental_docs_blocks_images(added_docs=dialog_transcripts_added,
                                                                    added_blocks=conversation_turns,
                                                                    added_images=0,
                                                                    added_pages=pages_added)

            # by default copies transcripts to upload folder
            if copy_to_library:
                self.uploads(input_folder)

        if save_history and write_to_db_on == 0:
            ParserState().save_parser_output(self.parser_job_id, self.parser_output)

        return output

    def parse_website(self, url_base, write_to_db=True, save_history=True, get_links=True, max_links=10):

        """ Main entrypoint for parsing a website. """

        output = []

        #   must have three conditions in place - (a) user selects, (b) ping successfully, and (c) library loadedd
        if write_to_db and self.parse_to_db and self.library:
            write_to_db_on = 1
        else:
            write_to_db_on = 0

        #   warning to user that no library loaded in Parser constructor
        if write_to_db and not self.library:
            logging.warning("warning: Parser().parse_website - request to write to database but no library loaded "
                            "in Parser constructor.   Will write parsing output to file and will place the "
                            "file in /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logging.error("warning: Parser().parse_website - could not connect to database at %s.  Will write "
                          "parsing output to file and will place the file in /parser_history path.",
                          self.collection_path)

        local_work_folder = self.parser_tmp_folder
        # local_work_folder = self.library.tmp_path

        if not os.path.exists(local_work_folder):
            os.mkdir(local_work_folder)

        self.website_work_folder = os.path.join(local_work_folder, "process_website" + os.sep)

        # start clean
        if os.path.exists(self.website_work_folder):
            shutil.rmtree(self.website_work_folder, ignore_errors=True)
        os.mkdir(self.website_work_folder)

        # iterative parse thru website to follow links enabled

        website = WebSiteParser(url_base, reset_img_folder=True, local_file_path=self.website_work_folder)

        if website.success_code == 1:

            # increment and get new doc_id
            if write_to_db_on == 1:
                self.library.doc_ID = self.library.get_and_increment_doc_id()

            entries, img_counter = website.website_main_processor(website.image_counter,
                                                                  output_index=False)

            # if get_links, then pursue internal links and 'add' to indexed output gathered
            if get_links:

                if len(website.internal_links) > 0:

                    max_links = min(len(website.internal_links), max_links)

                    # img_counter = new_image_count

                    for z in range(0, max_links):

                        logging.info("\nupdate: WebSite Parser iterate - "
                                     "child site link - %s - %s - %s", z, url_base, website.internal_links[z])

                        child_site = WebSiteParser(url_base + website.internal_links[z], reset_img_folder=False,
                                                   local_file_path=self.website_work_folder)

                        if child_site.success_code == 1:
                            new_child_entries, img_counter = child_site.website_main_processor(img_counter,
                                                                                               output_index=False)

                            for c in range(0, len(child_site.core_index)):
                                website.core_index.append(child_site.core_index[c])

        # write parser output to storage

        entries_created = 0
        images_created = 0
        running_links = ""
        file_type = "html"

        file_source = str(random.randint(100000, 999999)) + "_" + website.url_main.split(".")[-2] + ".html"
        # file_source = website.url_main.split(".")[-2] + ".html"

        meta = {"author": "", "modified_date": "", "created_date": "", "creator_tool": ""}
        coords_dict = {"coords_x": 0, "coords_y": 0, "coords_cx": 0, "coords_cy": 0}

        # prep loop - consolidate links with text or image
        for z in range(0, len(website.core_index)):

            """
            # core index entry is dictionary
            entry = {"content_type": entry_type,
                     "text": text,
                     "image": {"image_name": img_name, "image_url": img_url},
                     "link": {"link_type": link_type, "link": link},
                     "master_index": master_index,
                     "last_header": last_header}
            """

            content_type = website.core_index[z]["content_type"]

            if content_type == "link":
                link_type = website.core_index[z]["link"]["link_type"]

                if link_type == "internal":
                    # attach internal links to last piece of text or image
                    running_links += website.core_index[z]["link"]["link"] + " , "

            if content_type == "text" or content_type == "image":
                # close out last entry & start new one
                save_entry = 1
                text1_core = website.core_index[z]["text"]
                if not text1_core:
                    text1_core = website.core_index[z]["last_header"]

                # no tables currently extracted in website parser
                content1_core = ""

                text3_format = website.core_index[z]["last_header"]
                text2_spatial = running_links
                links = running_links
                running_links = ""

                master_index = (entries_created, 0)
                coords = master_index
                user_tags = []
                external_files = ""

                if content_type == "image":

                    fp_tmp = self.website_work_folder
                    image_num = website.core_index[z]["image"]["image_name"]

                    if self.library:
                        doc_id = self.library.doc_ID
                        save_file_path = self.library.image_path
                    else:
                        doc_id = self.file_counter
                        save_file_path = self.parser_image_folder

                    new_image_name, created = website._save_image_website(fp_tmp, image_num, doc_id, save_file_path)

                    images_created += 1
                    external_files = new_image_name

                    if not text1_core:
                        # take adjacent header_text, if no text linked to image
                        text1_core = text3_format

                new_entry = (content_type, file_type, master_index, "", "", "",
                             file_source, content1_core,"","", external_files, text1_core,text2_spatial,
                             text3_format,text1_core, user_tags,links,"","" ,"")

                if write_to_db_on == 1:
                    entry_output = self.add_create_new_record(self.library, new_entry,meta,coords_dict)
                else:
                    entry_output = self.create_one_parsing_output_dict(entries_created,
                                                                       new_entry,meta,coords_dict,
                                                                       dialog_value="false")
                    self.parser_output.append(entry_output)
                    output.append(entry_output)
                entries_created += 1

        # once done with all of the record updates- update the master counters
        # need to save new block_ID & new doc_ID
        docs_created = 1
        self.file_counter += 1

        if write_to_db_on == 1:
            dummy = self.library.set_incremental_docs_blocks_images(added_docs=docs_created,
                                                                    added_blocks=entries_created,
                                                                    added_images=images_created,
                                                                    added_pages=1)

        # c.uploads - upload website_file
        fp_tmp = os.path.join(local_work_folder, "process_website" + os.sep)

        website_name = "my_website.html"
        
        # apply secure_filename to remove any extra "/"
        secure_url_name = secure_filename(website.url_main.split(".")[-2])

        out_name = str(random.randint(100000, 999999)) + "_" + secure_url_name + ".html"

        if self.library:
            upload_fp = self.library.file_copy_path
        else:
            upload_fp = self.parser_tmp_folder

        shutil.copy(os.path.join(fp_tmp,website_name), os.path.join(upload_fp, out_name))

        if save_history and write_to_db_on == 0:
            ParserState().save_parser_output(self.parser_job_id, self.parser_output)

        return output

    def uploads(self, tmp_dir, overwrite=False):

        """ Utility method that handles 'uploads' of input files into library structure. """

        # designed for upload of input files into library structure

        if not self.library:
            logging.error("error: Parser().uploads is designed for connecting files "
                          "into library - no library selected - to use, create Parser with library loaded, e.g., "
                          "Parser(library=my_library)")
            return -1

        upload_fp = self.library.file_copy_path
        library_files = os.listdir(upload_fp)
        files = os.listdir(tmp_dir)
        for x in range(0, len(files)):
            safe_name = self.prep_filename(files[x])

            # exclude any folders
            if not os.path.isdir(os.path.join(tmp_dir,files[x])):

                #   will not over-write an existing file unless overwrite flag set
                if overwrite or files[x] not in library_files:
                    shutil.copy(os.path.join(tmp_dir, files[x]), os.path.join(upload_fp, files[x]))

        return len(files)

    def prep_filename(self, fn, secure_name=True, prepend_string=None, postpend_string=None, max_len=None):

        """ Utility function to prepare 'safe' filenames """

        fn_out = fn

        # default - apply basic secure name, e.g., remove / and insert _
        if secure_name:
            fn_out= secure_filename(fn)

        # if requested prepend or postpend
        if prepend_string:
            fn_out= prepend_string + fn_out

        if postpend_string:
            fn_base, ext = fn_out.split(".")
            fn_out = fn_base + postpend_string + ext

        # if max len applied
        if max_len:
            if len(fn_out) > max_len:
                fn_base, ext = fn_out.split(".")
                fn_out = fn_base[0:max_len-len(ext)] + ext

        return fn_out

    def input_ingestion_comparison (self, file_list):

        # shortcut if file_list is just empty
        if len(file_list) < 1:
            return [],[]

        """ Compares input with parsed output to identify any rejected files. """

        # simple approach - compares input file_list from ingestion 'work_order' with state of library collection
        #   --if input file found, then added to 'found_list' -> else, added to 'not_found_list'

        if not self.library:
            logging.error("error: Parser().input_ingestion_comparison is designed for bulk parsing of files "
                          "into library - no library selected - to use, create Parser with library loaded, e.g., "
                          "Parser(library=my_library)")
            return -1

        found_list = []

        doc_fn_raw_list = CollectionRetrieval(self.library_name,
                                              account_name=self.account_name).get_distinct_list("file_source")


        for i, file in enumerate(doc_fn_raw_list):
            if file.split(os.sep)[-1] in file_list:
                found_list.append(file.split(os.sep)[-1])
            # if found_list is equal length of file_list we don't need to look any further
            if len(found_list) == len(file_list):
                break

        not_found_list = list(set(file_list) - set(found_list))

        return found_list, not_found_list

    def input_ingestion_comparison_from_parser_state (self, file_list):

        """ Compares input with parsed output to identify any rejected files. """

        # simple approach - compares input file_list from ingestion 'work_order' with state of library collection
        #   --if input file found, then added to 'found_list' -> else, added to 'not_found_list'

        doc_fn_out = []

        for i, doc_fn in enumerate(self.parser_output):
            if "file_source" in doc_fn:
                if doc_fn["file_source"] not in doc_fn_out:
                    doc_fn_out.append(doc_fn["file_source"])

        found_list = []
        not_found_list = []

        for i, input_file in enumerate(file_list):
            found_file = -1
            for j, ingested_file in enumerate(doc_fn_out):

                # need to confirm 'symmetrical' transformations, e.g., secure_filename and any prepend/postpend
                if input_file == ingested_file:
                    found_file = 1
                    found_list.append(input_file)
                    break
            if found_file == -1:
                not_found_list.append(input_file)

        return found_list, not_found_list

    def parse_one (self, fp, fn, save_history=True):

        """ Parse one 'ad hoc' 'unbound' parsing of a single document in memory -> no library required """

        # check that path exists
        if not os.path.exists(os.path.join(fp, fn)):
            raise FilePathDoesNotExistException(os.path.join(fp,fn))

        output = []

        ext = fn.split(".")[-1].lower()

        if ext == "pdf":
            output = self.parse_one_pdf(fp, fn, save_history=False)

        if ext in self.office_types:
            output = self.parse_one_office(fp, fn, save_history=False)

        if ext in self.text_types:
            output = self.parse_one_text(fp, fn, save_history=False)

        if ext in self.voice_types:
            output = self.parse_one_voice(fp, fn, save_history=False)

        # no history saved by the individual parsers, as it will be saved below
        if save_history:
            if output:
                ParserState().save_parser_output(self.parser_job_id, output)

        if not output:
            logging.warning("No content parsed from document - %s ", fn)

        return output

    def parse_one_office (self, fp, fn, save_history=True):

        """ Parse one office document at selected file path and file name. """

        #   Designed for 'ad hoc' and 'unbound' quick parse of a single office document with no storage
        #   --output provided as list of Dicts in memory with same structure as parsing output

        # check that path exists
        if not os.path.exists(os.path.join(fp, fn)):
            raise FilePathDoesNotExistException(os.path.join(fp,fn))

        workspace_fp = self.parser_tmp_folder

        if not os.path.exists(workspace_fp):
            os.mkdir(workspace_fp)
            os.chmod(workspace_fp, 0o777)

        # safety check - will need to improve + expand for supporting windows path
        if not workspace_fp.endswith(os.sep):
            workspace_fp += os.sep
            logging.warning("warning: workspace_fp did not end with trailing '/' as expected by parser")

        # need to update this
        for z in range(0, 1):

            if os.path.exists(os.path.join(workspace_fp,str(z))):
                shutil.rmtree(os.path.join(workspace_fp,str(z)), ignore_errors=True)

            if not os.path.exists(os.path.join(workspace_fp,str(z))):
                os.mkdir(os.path.join(workspace_fp,str(z)))
                os.chmod(os.path.join(workspace_fp, str(z)), 0o777)

        # end -initialize workspace

        # int add_one_office
        # char * input_account_name,
        # char * input_library_name,
        # char * input_fp,
        # char * input_fn,
        # char * workspace_fp,
        # char * image_fp,
        # char * write_to_filename

        #   if any issue loading module, will be captured at .get_module_office_parser()
        _mod = Utilities().get_module_office_parser()

        main_handler = _mod.add_one_office
        main_handler.argtypes = (c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p)

        main_handler.restype = c_int

        # three inputs - account_name // library_name // fp to web_dir - files to be processed
        # prep each string:    account_name = create_string_buffer(py_account_str.encode('ascii','ignore'))

        if not self.account_name:
            self.account_name = "llmware"

        account_name = create_string_buffer(self.account_name.encode('ascii', 'ignore'))
        library_name = create_string_buffer(self.library_name.encode('ascii', 'ignore'))

        if not fp.endswith(os.sep):
            fp += os.sep

        fp_c = create_string_buffer(fp.encode('ascii', 'ignore'))
        fn_c = create_string_buffer(fn.encode('ascii', 'ignore'))

        workspace_fp_c = create_string_buffer(workspace_fp.encode('ascii', 'ignore'))

        # image_fp = self.library.image_path

        # will need to fix this - C code expects trailing "/"
        # image_fp = self.parser_tmp_folder #   + "/"
        image_fp = self.parser_image_folder

        if not image_fp.endswith(os.sep):
            image_fp += os.sep
            logging.warning("warning: adding '/' to image_fp as expected by c parser")

        image_fp_c = create_string_buffer(image_fp.encode('ascii', 'ignore'))

        write_to_filename = "office_internal_test0.txt"
        write_to_fn_c = create_string_buffer(write_to_filename.encode('ascii', 'ignore'))

        # int add_one_office
        # char * input_account_name,
        # char * input_library_name,
        # char * input_fp,
        # char * input_fn,
        # char * workspace_fp,
        # char * image_fp,
        # char * write_to_filename

        pages_created = main_handler(account_name, library_name, fp_c, fn_c, workspace_fp_c,
                                     image_fp_c, write_to_fn_c)

        # self.library.image_path
        output = self.convert_parsing_txt_file_to_json(file_path=self.parser_tmp_folder,fn=write_to_filename)

        if len(output) > 0:
            self.parser_output += output

        if save_history:
            ParserState().save_parser_output(self.parser_job_id, self.parser_output)

        return output

    def parse_one_pdf (self, fp, fn,  save_history=True):

        """ Parse one pdf document at selected file path and file name. """

        # check that path exists
        if not os.path.exists(os.path.join(fp,fn)):
            raise FilePathDoesNotExistException(os.path.join(fp,fn))

        # c function header - add_one_pdf(
        # char * account_name,
        # char * library_name,
        # char * input_fp,
        # char * input_filename,
        # char * input_images_fp,
        # char * write_to_filename,
        # int user_block_size)

        #   if any issue loading module, will be captured at .get_module_pdf_parser()
        _mod_pdf = Utilities().get_module_pdf_parser()

        pdf_handler = _mod_pdf.add_one_pdf

        # c function header-
        pdf_handler.argtypes = (c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int)

        pdf_handler.restypes = c_int

        # prepare all of the inputs to invoke the c library

        t0 = time.time()

        # config options pulled from the Library object
        if not self.account_name:
            acct_name = "llmware"

        account_name = create_string_buffer(self.account_name.encode('ascii', 'ignore'))

        library_name = create_string_buffer(self.library_name.encode('ascii', 'ignore'))

        #   fp = passed as parameter -> this is the input file path folder containing the .PDF docs to be parsed

        if not fp.endswith(os.sep):
            fp += os.sep

        fp_c = create_string_buffer(fp.encode('ascii', 'ignore'))

        fn_c = create_string_buffer(fn.encode('ascii', 'ignore'))

        # shift output fp to
        # image_fp = self.library.image_path
        image_fp = self.parser_tmp_folder
        if not image_fp.endswith(os.sep):
            image_fp += os.sep

        image_fp_c = create_string_buffer(image_fp.encode('ascii', 'ignore'))

        #   prep parameters passed in the method invocation above
        write_to_filename = "pdf_internal_test0.txt"
        write_to_filename_c = create_string_buffer(write_to_filename.encode('ascii','ignore'))

        # pull target block size from library parameters

        user_block_size = c_int(self.block_size_target_characters)   # standard 400-600

        #
        #                   * main call to pdf library *
        #

        # c function header - add_one_pdf(
        # char * account_name,
        # char * library_name,
        # char * input_fp,
        # char * input_filename,
        # char * input_images_fp,
        # char * write_to_filename,
        # int user_block_size)

        logging.info("update: starting pdf_parser ...")

        pages_created = pdf_handler(account_name, library_name, fp_c, fn_c, image_fp_c,
                                    write_to_filename_c, user_block_size)

        logging.info("update: completed pdf_parser - time taken: %s ", time.time() - t0)

        output = self.convert_parsing_txt_file_to_json(file_path=self.parser_tmp_folder,fn=write_to_filename)

        if len(output) > 0:
            self.parser_output += output

        if save_history:
            ParserState().save_parser_output(self.parser_job_id, self.parser_output)

        return output

    def parse_one_pdf_by_ocr_images(self, input_fp, input_fn, save_history=True):

        """ Parse one 'scanned' pdf document at selected file path and file name. """

        # check that path exists
        if not os.path.exists(os.path.join(input_fp, input_fn)):
            raise FilePathDoesNotExistException(os.path.join(input_fp,input_fn))

        #   Designed for parse of a single PDF_BY_OCR - no storage, no link into Library
        #   --output returned as in-memory list of Dicts

        # set counters
        output = []
        doc_id = 0

        ext = input_fn.split(".")[-1]

        if ext == "pdf":

            doc_fn = secure_filename(input_fn)

            output_by_page = ImageParser(self).process_pdf_by_ocr(input_fp, input_fn)

            meta = {"author": "", "modified_date": "", "created_date": "", "creator_tool": ""}
            coords_dict = {"coords_x": 0, "coords_y": 0, "coords_cx": 0, "coords_cy": 0}

            counter = 0
            for i, pages in enumerate(output_by_page):
                for j, blocks in enumerate(pages):

                    new_entry = ("text", "pdf-ocr", (j+1, 0), counter, "", "", doc_fn, "", blocks, "",
                                         "", blocks, blocks, "", blocks, "", "", "", "", "")

                    # creates a single 'unbound' parsing output dict -> no storage
                    parsing_output_dict = self.create_one_parsing_output_dict(counter,
                                                                              new_entry, meta, coords_dict,
                                                                              dialog_value="false")

                    output.append(parsing_output_dict)
                    self.parser_output.append(parsing_output_dict)

                    counter += 1

        if save_history:
            ParserState().save_parser_output(self.parser_job_id, self.parser_output)

        return output

    def parse_one_image(self, input_fp, input_fn, save_history=True):

        """ Parse one image document at selected file path and file name. """

        #   Designed to parse a single image using OCR - no storage or link to library

        # check that path exists
        if not os.path.exists(os.path.join(input_fp, input_fn)):
            raise FilePathDoesNotExistException(os.path.join(input_fp,input_fn))

        # set counters
        output= []
        counter = 0
        ext = input_fn.split(".")[-1].lower()

        if ext in self.ocr_types:

            doc_fn = secure_filename(input_fn)
            ocr_output = ImageParser(self).process_ocr(input_fp, input_fn)

            meta = {"author": "", "modified_date": "", "created_date": "", "creator_tool": ""}
            coords_dict = {"coords_x": 0, "coords_y": 0, "coords_cx": 0, "coords_cy": 0}

            for j, blocks in enumerate(ocr_output):

                new_entry = ("text", "pdf-ocr", (1, 0), counter, "", "", doc_fn, "", blocks, "",
                                 "", blocks, blocks, "", blocks, "", "", "", "", "")

                # creates a single 'unbound' parsing output dict -> no storage
                parsing_output_dict = self.create_one_parsing_output_dict(counter, new_entry, meta, coords_dict,
                                                                          dialog_value="false")

                output.append(parsing_output_dict)
                self.parser_output.append(parsing_output_dict)

                counter += 1

        if save_history:
            ParserState().save_parser_output(self.parser_job_id, output)

        return output

    def parse_one_text(self, input_fp, input_fn, save_history=True):

        """ Parse one text-based document at selected file path and file name. """

        # check that path exists
        if not os.path.exists(os.path.join(input_fp, input_fn)):
            raise FilePathDoesNotExistException(os.path.join(input_fp,input_fn))

        # set counters
        output = []
        content_type = "text"
        parser_output = []
        counter = 0

        file_type = input_fn.split(".")[-1].lower()

        if file_type not in self.text_types:
            return output

        # sub-routing by type of text file to appropriate handler

        if file_type in ["txt", "md"]:
            # will parse as text
            parser_output = TextParser(self).text_file_handler (input_fp, input_fn)
            content_type = "text"
            file_type = "txt"

        if file_type.lower() in ["csv"]:
            # will parse as table
            interpret_as_table=True
            parser_output = TextParser(self).csv_file_handler(input_fp, input_fn, interpret_as_table=True)
            content_type = "text"
            file_type = "csv"
            if interpret_as_table:
                content_type = "table"

        if file_type.lower() in ["json","jsonl"]:
            # will parse each line item as separate entry

            interpret_as_table=False
            keys = ["text"]
            parser_output = TextParser(self).jsonl_file_handler(input_fp,input_fn,
                                                                key_list=keys,
                                                                interpret_as_table=interpret_as_table,
                                                                separator="\n")
            content_type = "text"
            file_type = "jsonl"
            if interpret_as_table:
                content_type = "table"

        # consolidate output
        meta = {"author": "", "modified_date": "", "created_date": "", "creator_tool": ""}
        coords_dict = {"coords_x": 0, "coords_y": 0, "coords_cx": 0, "coords_cy": 0}

        for j, blocks in enumerate(parser_output):

            if content_type == "text":
                new_entry = ("text", file_type, (1, 0), counter, "", "", input_fn, "", blocks, "",
                                 "", blocks, blocks, "", blocks, "", "", "", "", "")
            else:
                # could be table if csv file -> in this case, keep both text [11] and table [7]
                new_entry = ("table", file_type, (1, 0), counter, "", "", input_fn, blocks, blocks, "",
                             "", blocks, blocks, "", blocks, "", "", "", "", "")

            # creates a single 'unbound' parsing output dict -> no storage
            parsing_output_dict = self.create_one_parsing_output_dict(counter,
                                                                      new_entry, meta, coords_dict,
                                                                      dialog_value="false")

            output.append(parsing_output_dict)
            self.parser_output.append(parsing_output_dict)

            counter += 1

        if save_history:
            ParserState().save_parser_output(self.parser_job_id, self.parser_output)

        return output

    def parse_one_dialog(self, input_fp, input_fn, save_history=True):

        """ Parse one dialog transcript document at selected file path and file name. """

        #   Designed as single dialog parse - no storage or link to library
        #   --note:  only supports AWS dialog standard for now

        # check that path exists
        if not os.path.exists(os.path.join(input_fp, input_fn)):
            raise FilePathDoesNotExistException(os.path.join(input_fp, input_fn))

        # set counters
        counter = 0
        output = []

        ext = input_fn.split(".")[-1].lower()

        if ext == "json":

            dp_output = DialogParser(self).parse_aws_json_file_format(input_fp, input_fn)

            for i, blocks in enumerate(dp_output):

                # iterate thru each block -> add to metadata
                speaker_name = blocks["speaker_name"]

                meta = {"author": speaker_name, "modified_date": "", "created_date": "", "creator_tool": ""}

                coords_dict = {"coords_x": blocks["start_time"],
                               "coords_y": blocks["stop_time"],
                               "coords_cx": 0,
                               "coords_cy": 0}

                text_entry = blocks["text"]

                # conforming file format with full path of dialog intake path

                format_type = "aws_json"

                new_entry = ("text", format_type, (1, 0), counter, "", "", input_fn,
                             text_entry, text_entry, "", "", text_entry, text_entry, "", text_entry,
                             "", "", "", "", "")

                # creates a single 'unbound' parsing output dict -> no storage
                parsing_output_dict = self.create_one_parsing_output_dict(counter,
                                                                          new_entry, meta, coords_dict,
                                                                          dialog_value="true")

                output.append(parsing_output_dict)
                self.parser_output.append(parsing_output_dict)
                counter += 1

        if save_history:
            ParserState().save_parser_output(self.parser_job_id, self.parser_output)

        return output

    def parse_one_voice(self, input_fp, input_fn, save_history=True):

        """ Parse one WAV document at selected file path and file name. """

        #   Designed to parse a single WAV/voice file - no storage or linkage to library

        # check that path exists
        if not os.path.exists(os.path.join(input_fp, input_fn)):
            raise FilePathDoesNotExistException(os.path.join(input_fp,input_fn))

        # set counters
        counter = 0
        output = []

        ext = input_fn.split(".")[-1].lower()

        if ext in self.voice_types:

            parser_output = VoiceParser(self).add_voice_file(input_fp, input_fn)

            meta = {"author": "", "modified_date": "", "created_date": "", "creator_tool": ""}
            coords_dict = {"coords_x": 0, "coords_y": 0, "coords_cx": 0, "coords_cy": 0}

            for j, blocks in enumerate(parser_output):

                new_entry = ("text", "ocr-wav", (1, 0), counter, "", "", input_fn, "", blocks, "",
                             "", blocks, blocks, "", blocks, "", "", "", "", "")

                # creates a single 'unbound' parsing output dict -> no storage
                parsing_output_dict = self.create_one_parsing_output_dict(counter,
                                                                          new_entry, meta, coords_dict,
                                                                          dialog_value="false")

                output.append(parsing_output_dict)
                self.parser_output.append(parsing_output_dict)

        if save_history:
            ParserState().save_parser_output(self.parser_job_id, self.parser_output)

        return output

    def query_parser_state(self, query, results=None, remove_stop_words=True):

        """ Runs an in-memory 'fast search' against a set of parsed output json dictionaries. """

        if not results:
            results = self.parser_output

        output = Utilities().fast_search_dicts(query,results, text_key="text",remove_stop_words=remove_stop_words)

        return output

    # update 012924 - new methods start here for duplicate checking

    def input_build_folder(self, fp_list, exclude_if_already_in_library=True):

        """ Creates a single 'input_build_folder' by consolidating the files across multiple folders, provided in
        input list of file paths.   It will accept only one copy of a particular file, based on the
        first version passed in the fp_list.  If exclude_if_already_in_library == True (default), then
        any files already in the library will also be excluded. """

        #   once the input_build_folder is created, it can be passed to any parsing method

        library_docs = None

        if not self.library:
            exclude_if_already_in_library = False

        if exclude_if_already_in_library:

            # will get a list of all of the distinct files already in the library
            library_docs = CollectionRetrieval(self.library_name,
                                               account_name=self.account_name).get_distinct_list("file_source")

        # create tmp workspace for new_input_folder
        new_input_folder = os.path.join(self.parser_folder, "input_build" + os.sep)

        #   if new_input_folder already created, then delete
        if os.path.exists(new_input_folder):
            shutil.rmtree(new_input_folder)

        #   create and start fresh
        if not os.path.exists(new_input_folder):
            os.mkdir(new_input_folder)
            os.chmod(new_input_folder, 0o777)

        deduped_list = []
        dupe_files = []
        lib_match_list = []

        for folder in fp_list:

            input_files = os.listdir(folder)

            for file in input_files:
                if file not in deduped_list:
                    dupe = 0
                    if exclude_if_already_in_library:
                        for lib_file in library_docs:
                            if os.sep in lib_file:
                                lib_file = lib_file.split(os.sep)[-1]
                            if file == lib_file:
                                dupe = 1
                                lib_match_list.append(file)
                                break
                    if dupe == 0:
                        deduped_list.append(file)
                        shutil.copy(os.path.join(folder,file), os.path.join(new_input_folder,file))
                else:
                    # copies the full path of the file that is being excluded
                    dupe_files.append(os.path.join(folder, file))

        output_info = {"new_input_folder": new_input_folder,
                       "file_count": len(deduped_list),
                       "files_included": deduped_list,
                       "duplicates_removed":dupe_files,
                       "files_in_library_already": lib_match_list}

        return output_info

    def delete_input_build_folder(self):

        """ Deletes an input build folder - at end of parsing transaction(s) using input_builder_folder """

        input_build_folder = os.path.join(self.parser_folder, "input_build" + os.sep)

        #   if new_input_folder already created, then delete
        if os.path.exists(input_build_folder):
            shutil.rmtree(input_build_folder)

        return True

    def duplicate_file_already_in_library(self, fp):

        """ Reviews the files in input folder path, and checks if any of those files have blocks of information
        in the library database collection. """

        existing_docs_in_collection = CollectionRetrieval(self.library_name,
                                                          account_name=self.account_name).get_distinct_list("file_source")

        input_files = os.listdir(fp)

        no_dupes_list = []
        matching_file_names = []

        for file in input_files:

            match_found = 0

            for existing_file in existing_docs_in_collection:

                if os.sep in existing_file:
                    # split to get base file name
                    existing_file = existing_file.split(os.sep)[-1]

                if file == existing_file:
                    matching_file_names.append(file)
                    match_found = 1
                    break

            if match_found == 0:
                no_dupes_list.append(file)

        duplicate_check = {"not_in_library": no_dupes_list, "in_library": matching_file_names}

        return duplicate_check

    def basic_library_duplicate_check(self, fn):

        """ Checks if file is already part of the copied upload files for the library, and returns
        True if file is found, and False if not found, e.g., 'new' to the library """

        in_library = False

        # run comparison with existing files in library copy path
        if self.library:
            if os.path.exists(self.library.file_copy_path):
                existing_files = os.listdir(self.library.file_copy_path)

                if fn in existing_files:
                    in_library = True

        return in_library

    def parse_csv_config(self,fp, fn, cols=None, mapping_dict=None):

        """ Designed for intake of a 'pseudo-db csv table' and will add rows to library with mapped keys.

        Inputs:
            -- csv folder path + csv file name
            -- cols = # of expected column entries in each row of the CSV
            -- mapping dict = assigns key names to columns, starting with 0 for first column
                e.g., {"text": 4, "doc_ID": 2, "key1": 3}

        Requirements:
            -- must have a "text" key in the mapping dictionary
            -- optional doc_ID and block_ID - if found, will over-write the normal library indexes
            -- all other keys will be saved as 'metadata' and added to the library block row in "special_field1"

        Note: this feature is currently only supported for Mongo - SQL DB support will follow.
        """

        # method requires Mongo DB and a library loaded in the Parser
        if LLMWareConfig().get_config("collection_db") != "mongo" or not self.library:
            raise LLMWareException(message="Parsing of a configured CSV file requires (a) use of MongoDB as "
                                           "the text collection parsing database, and (b) a library object to "
                                           "be connected to the parser state.")

        #   if found in mapping dict, then will over-write
        reserved_keys = ["text", "doc_ID", "block_ID"]

        rejected_rows = []
        ds = []

        if not mapping_dict:
            raise LLMWareException(message="Parsing of a configured CSV file requires a mapping dictionary so that "
                                           "the table attributes can be properly mapped.")

        if not cols:
            raise LLMWareException(message="Parsing of a configured CSV file requires a defined column structure and "
                                           "a specified number of columns to ensure accurate mapping.")

        # will iterate through csv file
        input_csv = os.path.join(fp, fn)

        import csv
        record_file = open(input_csv, "r", encoding='utf-8-sig',errors='ignore')
        c = csv.reader(record_file, dialect='excel', doublequote=False, delimiter=',')
        output = []

        #   Should be OK to load in memory up to ~1M rows - beyond that, will need to implement iterator

        for lines in c:
            output.append(lines)
        record_file.close()

        added_row_count = 0
        total_row_count = 0
        added_doc_count = 0

        for i, rows in enumerate(output):

            text = ""
            doc_id = None
            block_id = None
            metadata = {}

            if len(rows) != cols:
                bad_entry = {"index": i, "row": rows}
                rejected_rows.append(bad_entry)

            else:
                # confirmed that row has the correct number of entries

                for keys, values in mapping_dict.items():

                    if keys == "text":
                        if mapping_dict["text"] < len(rows):
                            text = rows[mapping_dict["text"]]

                    if keys == "doc_ID":
                        if mapping_dict["doc_ID"] < len(rows):
                            doc_id = rows[mapping_dict["doc_ID"]]

                    if keys == "block_ID":
                        if mapping_dict["block_ID"] < len(rows):
                            block_id = rows[mapping_dict["block_ID"]]

                    if keys not in reserved_keys:
                        if values < len(rows):
                            metadata.update({keys:rows[values]})

            if text.strip():

                meta = {"author": "", "modified_date": "", "created_date": "", "creator_tool": ""}
                coords_dict = {"coords_x": 0, "coords_y": 0, "coords_cx": 0, "coords_cy": 0}

                # conforming file format with full path of dialog intake path

                new_row_entry = ("text", "custom_csv", (1, 0), total_row_count, "", "", fn,
                                 text, text, "", "", text, text, "", text, "", "", metadata, "", "")

                #   set attributes custom
                if doc_id:
                    try:
                        self.library.doc_ID = int(doc_id)
                        added_doc_count += 1
                    except:
                        logging.warning("update: doc_ID expected to be integer - can not apply custom doc ID -"
                                        "will use default library document increment")

                if block_id:
                    self.library.block_ID = block_id
                else:
                    self.library.block_ID += 1

                #   write row to database
                entry_output = self.add_create_new_record(self.library,
                                                          new_row_entry,
                                                          meta,
                                                          coords_dict,
                                                          dialog_value="false")
                added_row_count += 1

            total_row_count += 1

        # update overall library counter at end of parsing

        if len(output) > 0:

            if added_doc_count == 0:
                added_doc_count += 1

            dummy = self.library.set_incremental_docs_blocks_images(added_docs=added_doc_count,
                                                                    added_blocks=added_row_count,
                                                                    added_images=0, added_pages=0)

        output = {"rows_added": len(ds), "rejected_count": len(rejected_rows), "rejected_rows": rejected_rows}

        return output


class WebSiteParser:

    """ WebSiteParser implements a website-scraping parser.   It can be accessed directly, or in many cases, will
    be accessed through Parser or Library classes indirectly. """

    def __init__(self, url_or_fp, link="/", save_images=True, reset_img_folder=False, local_file_path=None,
                 from_file=False, text_only=False):

        # by default, assume that url_or_fp is a url path
        self.url_main = url_or_fp

        # by default, will get images and links
        self.text_only = text_only

        # by passing link - provides option for recursive calls to website for internal links
        if link == "/":
            self.url_link = ""
        else:
            self.url_link = link

        self.url_base = self.url_main + self.url_link

        # check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):
            # if not explicitly set up by user, then create folder directory structure
            LLMWareConfig.setup_llmware_workspace()

        if not local_file_path:
            # need to update this path
            self.local_dir = os.path.join(LLMWareConfig.get_llmware_path(),"process_website/")
        else:
            self.local_dir = local_file_path

        if reset_img_folder:
            if os.path.exists(self.local_dir):
                # important step to remove & clean out any old artifacts in the /tmp/ directory
                shutil.rmtree(self.local_dir)
            os.makedirs(self.local_dir, exist_ok=True)

        if not os.path.exists(self.local_dir):
            os.makedirs(self.local_dir, exist_ok=True)

        if from_file:
            # interpret url as file_path and file_name
            try:
                html = open(url_or_fp, encoding='utf-8-sig', errors='ignore').read()
                bs = BeautifulSoup(html, features="lxml")
                self.html = bs.findAll()
                success_code = 1
                self.text_only = True
            except:
                logging.error("error: WebSite parser- could not find html file to parse at %s ", url_or_fp)
                success_code = -1
                self.text_only = True
        else:
            # this is the most likely default case -interpret url_or_fp as url
            try:
                req = Request(self.url_base, headers={'User-Agent': 'Mozilla/5.0'})
                html = urlopen(req).read()

                bs = BeautifulSoup(html,features="lxml")

                self.bs = bs
                self.html = bs.findAll()

                out_str = ""
                for x in self.html:
                    out_str += str(x) + " "
    
                with open(self.local_dir + "my_website.html", "w", encoding='utf-8') as f:
                    f.write(out_str)
                f.close()

                success_code = 1

            except Exception as e:
                logging.error("error:  website_parser could not find website to open - caught error - %s ", e)
                success_code = -1

        self.save_images = save_images
        self.image_counter = 0
        self.links = []
        self.mc = None
        self.entries = None
        self.core_index = []
        self.header_text = []
        self.internal_links = []
        self.external_links = []
        self.other_links = []

        # meta-data expected in library add process
        self.source = str(self.url_base)
        self.success_code = success_code

    def website_main_processor(self, img_start, output_index=True):

        """ Main processing of HTML scraped content and converting into blocks. """

        output = []
        counter = 0
        # by passing img_start explicitly- enables recursive calls to links/children sites
        img_counter = img_start

        long_running_string = ""

        # new all_text to remove duplications
        all_text = []

        internal_links = []
        external_links = []
        header_text = []
        unique_text_list = []
        unique_header_list = []

        last_text = ""
        last_header = ""

        text = ""

        for elements in self.html:

            content_found = 0
            img = ""
            img_success = 0
            img_url = ""
            img_name = ""

            link = ""
            link_type = ""

            # text = ""

            entry_type = "text"

            # if text only, then skip checks for images and links
            if not self.text_only:

                if "property" in elements.attrs:
                    if elements.attrs["property"] == "og:image":
                        if "content" in elements.attrs:

                            img_extension = elements["content"]
                            img_success, img, img_url, img_name = \
                                self.image_handler(img_extension, elements, img_counter)

                            if img_success == 1:
                                img_counter += 1
                                content_found += 1

                if "src" in elements.attrs:

                    img_extension = elements["src"]
                    img_success, img, img_url, img_name = self.image_handler(img_extension, elements, img_counter)

                    if img_success == 1:
                        img_counter += 1
                        content_found += 1

                if "href" in elements.attrs:

                    if elements.attrs["href"]:
                        link_success, link, link_type = self.link_handler(elements)
                        content_found += 1

                        if link_success == 0:
                            # skip .js files and other formatting in link crawling
                            # link_success == 0 if not .js // ==1 if .js file

                            if link_type == "internal":
                                if link != "/":
                                    if link not in internal_links:
                                        internal_links.append(link)

                            if link_type == "external":
                                external_links.append(link)

            # main check for text
            if elements.get_text():
                get_text = 1

                if "type" in elements.attrs:
                    # skip css and javascript
                    if elements.attrs["type"] == "text/css" or elements.attrs["type"] == "text/javascript":
                        get_text = -1

                if get_text == 1:

                    # text handler
                    s_out = ""

                    # alt for consideration to clean up string
                    # s_out += string.replace('\n', ' ').replace('\r', ' ').replace('\xa0', ' ').replace('\t', ' ')

                    for string in elements.stripped_strings:
                        s_out += string + " "

                    text += s_out

                    if text:
                        header_entry = []

                        if text not in unique_text_list:
                            unique_text_list.append(text)
                            content_found += 1
                            long_running_string += text + " "
                            last_text = text

                        if "h1" in elements.name:
                            header_entry = (counter, "h1", text)

                        if "h2" in elements.name:
                            header_entry = (counter, "h2", text)

                        if "h3" in elements.name:
                            header_entry = (counter, "h3", text)

                        if header_entry:
                            if text not in unique_header_list:
                                last_header = text
                                header_text.append(header_entry)
                                unique_header_list.append(text)

            # if looking for images and links, then prioritize in attribution
            if not self.text_only:
                if img and img_success == 1:
                    entry_type = "image"
                else:
                    if link:
                        entry_type = "link"
                    else:
                        if text:
                            entry_type = "text"
                        else:
                            content_found = 0
            else:
                entry_type = "text"

            if content_found > 0:
                master_index = (self.url_main, self.url_link, counter)
                if not text:
                    text = last_text

                entry = {"content_type": entry_type,
                         "text": text,
                         "image": {"image_name": img_name, "image_url": img_url},
                         "link": {"link_type": link_type, "link": link},
                         "master_index": master_index,
                         "last_header": last_header}

                # entry = (entry_type, text, (img_name, img_url), (link_type, link), master_index, last_header)

                counter += 1
                # save entry if image, or if (A) text > 50 and (B) not a dupe
                if entry_type == "image" or (len(text) > 50 and text not in all_text):
                    output.append(entry)
                    all_text.append(text)
                    text = ""

        self.image_counter = img_counter
        self.internal_links = internal_links
        self.external_links = external_links
        self.header_text = header_text

        if header_text:
            header_text_sorted = sorted(header_text, key=lambda x: x[1])
            self.header_text = header_text_sorted

        self.core_index = output
        self.entries = len(output)

        if not output_index:
            return len(output), img_counter

        return self.core_index

    def link_handler(self, elements):

        """ Handles processing of links found in main page content. """

        link_out = ""
        link_type = ""
        js_skip = 0

        if elements.attrs["href"].endswith(".js"):
            link_out = elements.attrs["href"]
            link_type = "js"
            js_skip = 1

        if elements.attrs["href"].endswith(".ico") or elements.attrs["href"].endswith(".ttf"):
            link_out = elements.attrs["href"]
            link_type = "other_formatting"
            js_skip = 1

        if elements.attrs["href"].endswith(".css"):
            link_out = elements.attrs["href"]
            link_type = "css"
            js_skip = 1

        if elements.attrs["href"].startswith(self.url_base):
            # save relative link only
            link_out = elements.attrs["href"][len(self.url_base):]
            link_type = "internal"

        if str(elements.attrs["href"])[0] == "/":
            # relative link
            if elements.attrs["href"]:
                if not elements.attrs["href"].startswith("//"):
                    link_out = elements.attrs["href"]
                    link_type = "internal"

        if elements.attrs["href"].startswith("https://") and \
                not elements.attrs["href"].startswith(self.url_base):
            # website but not the url_base - external link
            link_out = elements.attrs["href"]
            link_type = "external"

        return js_skip, link_out, link_type

    def image_handler(self, img_extension, elements, img_counter):

        """ Handles and processes images found in main content. """

        success = -1
        img_raw = []
        image_name = ""
        full_url = ""

        try:
            img_raw, response_code, full_url = self._request_image(img_extension, elements)

            if response_code == 200:

                if self.save_images:

                    # need to capture img type, e.g., .jpg
                    img_type = ""
                    if img_extension.endswith("png"): img_type = "png"
                    if img_extension.endswith("jpg") or img_extension.endswith("jpeg"): img_type = "jpg"
                    if img_extension.endswith("tiff"): img_type = "tiff"
                    if img_extension.endswith("svg"): img_type = "svg"

                    # secondary check if not at end - break off at '?' query string
                    if img_type == "":
                        original_img_name = img_extension.split("/")[-1]
                        original_img_name = original_img_name.split("?")[0]
                        if original_img_name.endswith("png"): img_type = "png"
                        if original_img_name.endswith("jpg") or img_extension.endswith("jpeg"): img_type = "jpg"
                        if original_img_name.endswith("tiff"): img_type = "tiff"
                        if original_img_name.endswith("svg"): img_type = "svg"

                    # only save image if valid img format found
                    if img_type in ("png", "jpg", "svg", "tiff"):
                        image_name = "image{}.{}".format(img_counter, img_type)
                        fp = self.local_dir + image_name
                        s = self._save_image(img_raw, fp)
                        success = 1

                    else:
                        logging.info("update:  WebSite -  found image OK but could not "
                                     "figure out img type: %s ", img_extension)

        except:
            logging.info("warning: WebSite - could not retrieve potential image: %s ", elements.attrs["src"])
            success = -1

        return success, img_raw, full_url, image_name

    def _save_image(self, img_raw, fp):

        """ Internal utility to save images found. """

        with open(fp, 'wb') as f:
            img_raw.decode_content = True
            shutil.copyfileobj(img_raw, f)

        return 0

    def _save_image_website(self, fp, img_num, doc_id, save_file_path):

        """ Internal utility for images. """

        # internal method to save image files and track counters

        img_type = img_num.split(".")[-1]
        img_core = img_num[len("image"):].split(".")[0]

        # image name of format:   image{{doc_ID}}_{{img_num}}.png
        new_img_name = "image" + str(doc_id) + "_" + str(img_core) + "." + img_type
        # new_img_name = "image" + str(library.image_ID) + "." + img_type
        created = 0

        img = open(os.path.join(fp,img_num), "rb").read()
        if img:
            f = open(os.path.join(save_file_path,new_img_name), "wb")
            f.write(img)
            f.close()
            created += 1

        return new_img_name, created

    # called by main handler
    def _request_image(self, img_extension, img):

        """ Retrieve images from links. """

        # relative link - refers back to main index page
        # check if url_main gives better performance than .url_base

        url_base = self.url_main
        # url_ext = img.attrs['src']
        url_ext = img_extension

        full_url = url_ext

        if url_ext:
            if url_ext.startswith("https:"):
                # this is an external link - just use the source
                full_url = url_ext

            if url_ext.startswith("/"):
                # relative ID - add url_base to get img

                full_url = url_base + url_ext

        r = requests.get(full_url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})

        return r.raw, r.status_code, full_url

    # not called by the main handler - keep as direct callable method
    def get_all_links(self):

        """ Utility to retrieve all links. """

        internal_links = []
        external_links = []
        other_links = []
        js_links = []

        for content in self.html:

            found = 0
            js = 0

            if "href" in content.attrs:
                if content.attrs["href"]:

                    if content.attrs["href"].endswith(".js"):
                        js_links.append(content.attrs["href"])
                        js = 1

                    if content.attrs["href"].startswith(self.url_base):
                        # save relative link only
                        out = content.attrs["href"][len(self.url_base):]
                        internal_links.append(out)
                        found = 1

                    if str(content.attrs["href"])[0] == "/":
                        # relative link
                        out = content.attrs["href"]
                        if out:
                            # skip double //
                            if not out.startswith("//"):
                                internal_links.append(out)
                        found = 1

                    if content.attrs["href"].startswith("https://") and \
                            not content.attrs["href"].startswith(self.url_base):
                        # website but not the url_base - external link
                        out = content.attrs["href"]
                        external_links.append(out)
                        found = 1

                    if found == 0:
                        other_links.append(content.attrs["href"])

        self.internal_links = internal_links
        self.external_links = external_links
        self.other_links = other_links

        top_links = []

        for z in range(0, len(internal_links)):

            link_tokens = internal_links[z].split("/")
            for y in range(0, len(self.mc)):
                if self.mc[y][0].lower() in link_tokens:
                    if internal_links[z] not in top_links:
                        top_links.append(internal_links[z])
                    break

        link_results = {"internal_links": internal_links, "external_links": external_links,
                        "other_links": other_links, "top_links": top_links}

        return link_results

    # not called by main handler - keep as separate standalone method
    def get_all_img(self, save_dir):

        """ Utility to get all images from html pages. """

        counter = 0
        for content in self.html:
            counter += 1
            if "src" in content.attrs:
                if str(content).startswith("<img"):

                    if content.attrs["src"]:
                        try:
                            img_raw, response_code, full_url = self._request_image(content, self.url_base)

                            if response_code == 200:

                                # need to capture img type, e.g., .jpg
                                original_img_name = content.attrs["src"].split("/")[-1]
                                original_img_name = original_img_name.split("?")[0]
                                img_type = ""
                                if original_img_name.endswith(".png"):
                                    img_type = "png"
                                if original_img_name.endswith(".jpg"):
                                    img_type = "jpg"
                                if original_img_name.endswith(".svg"):
                                    img_type = "svg"
                                if img_type == "":
                                    img_type = original_img_name.split(".")[-1]

                                fp = save_dir + "img{}.{}".format(counter, img_type)
                                s = self._save_image(img_raw, fp)
                                counter += 1
                        except:
                            logging.error("error: failed to find image: %s ", content.attrs["src"])

        return 0


class ImageParser:

    """ ImageParser for handling OCR of scanned documents - may be called directly, or through Parser. """

    def __init__(self, parser=None, library=None, text_chunk_size=600, look_back_range=300):

        self.parser = parser

        # defaults
        self.text_chunk_size = text_chunk_size
        self.look_back_range = look_back_range

        if library:
            self.text_chunk_size = library.block_size_target_characters + 200
            self.look_back_range = 300

        if parser and not library:
            if parser.library:
                self.text_chunk_size = parser.library.block_size_target_characters + 200
                self.look_back_range = 300

    def process_ocr (self, dir_fp, fn, preserve_spacing=False):

        """ Process a single OCR file in 'dir_fp' and with filename 'fn'. """

        try:
            text_out = pytesseract.image_to_string(os.path.join(dir_fp,fn))
        except TesseractNotFoundError as e:
            raise OCRDependenciesNotFoundException("tesseract")

        if not preserve_spacing:
            text_out = text_out.replace("\n", " ")

        # will chop up the long text into individual blocks
        text_chunks = TextChunker(text_chunk=text_out,
                                  max_char_size=self.text_chunk_size,
                                  look_back_char_range=self.look_back_range).convert_text_to_chunks()

        return text_chunks

    def ocr_to_single_text_file(self,fp):

        """ Runs OCR and converts image files into a single text file. """

        # simple utility method to extract text directly from set of images in folder
        #   --will consolidate into a single text list

        text_list_out = []
        scanned_files = os.listdir(fp)
        for docs in scanned_files:
            try:
                text_out = pytesseract.image_to_string(os.path.join(fp,docs))
            except TesseractNotFoundError as e:
                raise OCRDependenciesNotFoundException("tesseract")
            text_out = text_out.replace("\n", " ")
            logging.info("update: ocr text_out: %s ", text_out)
            text_list_out.append(text_out)

        return text_list_out

    def process_pdf_by_ocr(self, input_fp, file):

        """ Handles special case of running page-by-page OCR on a scanned PDF document. """

        text_output_by_page = []

        # decompose pdf into set of images by page
        try:
            images = convert_from_path(os.path.join(input_fp,file))
        except PDFInfoNotInstalledError as e:
            raise OCRDependenciesNotFoundException("poppler")
        for j, image in enumerate(images):

            # run ocr over page image
            try:
                text = pytesseract.image_to_string(image)
            except TesseractNotFoundError as e:
                raise OCRDependenciesNotFoundException("tesseract")
            # will chop up the long text into individual blocks
            text_chunks = TextChunker(text_chunk=text,
                                      max_char_size=self.text_chunk_size,
                                      look_back_char_range=self.look_back_range).convert_text_to_chunks()

            text_output_by_page.append(text_chunks)

        return text_output_by_page

    def exif_extractor(self, fp):

        """ Special utility to extract exif metadata from photos. """

        #  exif metadata is present in most photos, but not all
        #  if not a photo, it will not have exif data (e.g., camera standard)

        #  most useful exif data is GPS coords, time_stamp and creator device   (not always present)

        success_code = -1
        exif_table = {}
        creator_device = {}
        time_stamps = {}
        
        #   PIL/Pillow required for EXIF image processing - must be installed separately
        
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS, GPSTAGS
            
        except:
            raise DependencyNotInstalledException("PIL")

        try:
            img = Image.open(fp)
            x = img._getexif()
        except:
            return success_code, creator_device, time_stamps, exif_table

        if x:
            success_code = 1

            for tag, value in x.items():

                decoded = TAGS.get(tag, tag)
                exif_table[decoded] = value

                if decoded == "Make":
                    creator_device.update({decoded: value})

                if decoded == "Model":
                    creator_device.update({decoded: value})

                if decoded.startswith("DateTime"):
                    time_stamps.update({decoded: value})

        gps_info = {}
        if exif_table:
            if 'GPSInfo' in exif_table:
                for key in exif_table['GPSInfo'].keys():
                    decode = GPSTAGS.get(key, key)
                    gps_info[decode] = exif_table['GPSInfo'][key]
                    success_code = 1

        return success_code, gps_info, creator_device, time_stamps, exif_table

    def convert_pdf_to_images_by_page(self, input_fp, output_fp, summary_text_fn= "text_summary.txt"):

        """ Converts scanned PDF file into Page-by-Page images. """

        # converts pdf files into set of .png images by page
        #   --will process all of the pdf files in the input_fp

        input_files = os.listdir(input_fp)

        all_text = ""

        for i, files in enumerate(input_files):

            ext = files.split(".")[-1]
            if ext == "pdf":
                try:
                    # decomposes pdf into set of image .png files
                    try:
                        images = convert_from_path(os.path.join(input_fp,files))
                    except PDFInfoNotInstalledError as e:
                        raise OCRDependenciesNotFoundException("poppler")
                    for j, image in enumerate(images):

                        # saves .png images in target output folder
                        fn = str(i) + "_" + str(j) + ".png"
                        image.save(os.path.join(output_fp,fn))
                        try:
                            text = pytesseract.image_to_string(image)
                        except TesseractNotFoundError as e:
                            raise OCRDependenciesNotFoundException("tesseract")
                        all_text += text
                        # all_text += re.sub("[\n\r]"," ", text)
                        logging.info("update: ocr text out - %s ", text)

                    logging.info("update: ocr converted- %s - %s", i, files)
                    all_text += "\n\n"

                except:
                    logging.error("error - could not convert pdf")

        f = open(input_fp + summary_text_fn, "w", encoding='utf-8')
        f.write(all_text)
        f.close()

        return summary_text_fn


class VoiceParser:

    """ VoiceParser handles wav files to convert into text blocks. """

    def __init__(self, parser=None, library=None, text_chunk_size=600, look_back_range=300):

        self.parser = parser

        # defaults
        self.text_chunk_size = text_chunk_size
        self.look_back_range = look_back_range

        if library:
            self.text_chunk_size = library.block_size_target_characters + 200
            self.look_back_range = 300

        if parser and not library:
            if parser.library:
                self.text_chunk_size = parser.library.block_size_target_characters + 200
                self.look_back_range = 300

        self.speech_model = None
        self.speech_tokenizer = None

    def load_speech_to_text_model(self, speech_model=None, speech_tokenizer=None):

        """ Warning: llmware does not ship with a built-in speech-to-text engine - speech model dependency must
         be loaded separately. """

        #   Here is a sample script to import a popular speech-to-text engine in conjunction with llmware:
        #
        #   try:
        #       import torch
        #       import torchaudio
        #       import sentencepiece
        #       import soundfile
        #       from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer
        #   except:
        #        logging.error("error: key voice dependencies not found")
        #
        #   tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-base-960h")
        #   model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

        #   return model, tokenizer

        self.speech_model = speech_model
        self.speech_tokenizer = speech_tokenizer

        return speech_model, speech_tokenizer

    # current script easy to adapt to other speech models - designed for Wav2Vec
    def voice_to_text(self,fp_input, fn, sr_input=16000):

        """Voice to text parsing conversion. Requires loading of separate dependency. """

        if not self.speech_model:
            raise DependencyNotInstalledException("speech_to_text_model")

        try:
            import torch
            import librosa      # note: not in llmware install - needs to be added separately
        except:
            raise DependencyNotInstalledException("librosa")

        audio, rate = librosa.load(os.path.join(fp_input, fn), sr=sr_input)

        model, tokenizer = self.load_speech_to_text_model()
        input_values = tokenizer(audio, return_tensors="pt").input_values
        logits = model(input_values).logits
        prediction = torch.argmax(logits, dim=-1)
        transcription = tokenizer.batch_decode(prediction)[0]

        return transcription

    def add_voice_file(self, input_fp, fn):

        """ Parse voice file. """

        #   16000 is standard default encoding rate for .wav -> will need to test/experiment
        text_out = self.voice_to_text(input_fp, fn, 16000)

        # will chop up the long text into individual blocks
        text_chunks = TextChunker(text_chunk=text_out,
                                  max_char_size=self.text_chunk_size,
                                  look_back_char_range=self.look_back_range).convert_text_to_chunks()

        return text_chunks


class TextParser:

    """ TextParser to parse .txt, .json, .csv, and .md files - can be called directly or through main Parser class. """

    def __init__(self, parser=None, library=None, text_chunk_size=600, look_back_range=300):

        self.parser = parser

        # defaults
        self.text_chunk_size = text_chunk_size
        self.look_back_range = look_back_range

        if library:
            self.text_chunk_size = library.block_size_target_characters + 200
            self.look_back_range = 300

        if parser and not library:
            if parser.library:
                self.text_chunk_size = parser.library.block_size_target_characters + 200
                self.look_back_range = 300

    def jsonl_file_handler (self, dir_fp,sample_file, key_list=None, interpret_as_table=False,
                            separator="\n"):

        """ Parse JSONL file. """

        # will extract each line in jsonl as separate sample
        #   --based on key_list and interpret_as_table

        output = []
        my_file = open(os.path.join(dir_fp, sample_file), 'r', encoding='utf-8-sig',errors='ignore')

        if not key_list:
            # as default, if no key_list, then look for "text" attribute in jsonl by default
            key_list = ["text"]

        for i, lines in enumerate(my_file):

            row_tmp = json.loads(lines)

            if not interpret_as_table:
                row_text = ""
                for keys in key_list:
                    if keys in row_tmp:
                        row_text += row_tmp[keys] + separator
                output.append(row_text)

            else:
                row_table = []
                for keys in key_list:
                    if keys in row_tmp:
                        row_table.append(keys)
                output.append(row_table)

        return output

    def text_file_handler (self, dir_fp, sample_file):

        """ Parse .txt file. """

        text_out = open(os.path.join(dir_fp,sample_file), "r", encoding='utf-8-sig', errors='ignore').read()

        # will chop up the long text into individual text chunks
        text_chunks = TextChunker(text_chunk=text_out,
                                  max_char_size=self.text_chunk_size,
                                  look_back_char_range=self.look_back_range).convert_text_to_chunks()

        return text_chunks

    def csv_file_handler (self, dir_fp,sample_file, max_rows=100, interpret_as_table=True):

        """ Parse .csv file. """

        if interpret_as_table:

            # will split the table by rows and columns (\n for rows and ',' for cells in row)
            t = Utilities().file_load(os.path.join(dir_fp,sample_file))
            tables_out= []

            if len(t) < max_rows:
                tables_out = [t]
            else:
                table_chunks = len(t) // max_rows
                if max_rows > table_chunks * len(t):
                    # there is a remainder, so create one additional partial chunk with last set of rows
                    table_chunks += 1
                starter = 0
                stopper = 0
                for x in range(0,table_chunks):
                    starter = starter + stopper
                    stopper = starter + min(len(t)-starter, max_rows)
                    tables_out.append(t[starter:stopper])

            return tables_out

        else:
            # chunk and split as a big piece of text
            raw_csv = open(os.path.join(dir_fp,sample_file), "r", encoding='utf-8-sig', errors='ignore').read()
            # replace ',' & '\n' & '\r' with spaces
            text_out = re.sub("[,\n\r]", " ", raw_csv)

            # will chop up the long text into individual text chunks
            text_chunks = TextChunker(text_chunk=text_out,
                                      max_char_size=self.text_chunk_size,
                                      look_back_char_range=self.look_back_range).convert_text_to_chunks()

            return text_chunks


class WikiParser:

    """ WikiParser handles the retrieval and packaging of content from Wikipedia. """

    def __init__(self, parser=None, library=None, text_chunk_size=600, look_back_range=300):

        self.wiki = WikiKnowledgeBase()

        self.parser = parser
        self.library = library

        self.text_chunk_size = text_chunk_size
        self.look_back_range = look_back_range

        if library:
            self.text_chunk_size = self.library.block_size_target_characters + 200
            self.look_back_range = 300

        if parser and not library:
            if parser.library:
                self.text_chunk_size = parser.library.block_size_target_characters + 200
                self.look_back_range = 300

    def add_wiki_topic(self, topic, target_results=10):

        """ Parse a selected Wikipedia content by topic and requested target results. """

        # used in both Parser / Library, as well as directly in Prompts (integrate as "Source" into Prompt)

        articles_output = []
        text_only = ""
        blocks = []
        topic_query_results = self.wiki.search_wikipedia(topic,result_count=target_results, suggestion=False)

        text_chunks_all = []

        for j, title in enumerate(topic_query_results):
            article = self.wiki.get_article(title["title"])
            article.update({"topic": topic})
            articles_output.append(article)

            text_chunks = TextChunker(text_chunk=article["text"],
                                      max_char_size=self.text_chunk_size,
                                      look_back_char_range=self.look_back_range).convert_text_to_chunks()

            for i, chunk in enumerate(text_chunks):
                new_block = {"file_source": title["title"], "page_num": max(1, i // 5), "text": chunk}
                blocks.append(new_block)

            text_chunks_all += text_chunks

        topic_results = {"search_results": topic_query_results, "articles": articles_output,
                         "text_chunks": text_chunks_all, "blocks": blocks}

        return topic_results


class DialogParser:

    """ DialogParser handles parsing of dialog voice transcription, specifically for AWS currently. """

    def __init__(self, parser=None, library=None, text_chunk_size=600, look_back_range=300):

        self.parser = parser
        self.library = library

        self.text_chunk_size = text_chunk_size
        self.look_back_range = look_back_range

        if library:
            self.text_chunk_size = self.library.block_size_target_characters + 200
            self.look_back_range = 300

        if parser and not library:
            if parser.library:
                self.text_chunk_size = parser.library.block_size_target_characters + 200
                self.look_back_range = 300

        # currently only has support for AWS dialog format
        self.supported_format_types = ["aws"]

    # map to aws transcript json output format
    def parse_aws_json_file_format(self, input_folder, fn_json):

        """ Parse AWS JSON file. """

        f = json.load(open(os.path.join(input_folder, fn_json), "r", encoding='utf-8-sig',errors='ignore'))

        # aws standard call transcript format:  ["results"]["items"] -> key conversation elements to aggregate
        #   note:  we will need many more documents for testing
        #       --possible that AWS call transcript has different formats and/or has evolved over time!

        block_output = []

        # quick format check - will need to enhance over time

        format_validated = False

        if "results" in f:
            if "items" in f["results"]:
                format_validated = True

        # improve validation of format + user message back with link to AWS documents
        if not format_validated:
            logging.error("error: DialogParser currently only supports AWS Transcribe dialog format - For more "
                          "information, please see Amazon Web Services Transcription - "
                          "https://docs.aws.amazon.com/transcribe/latest/dg/how-input.html#how-it-works-output ")

            return block_output

        # end - quick format check

        # speaker label conversation snippets
        conversation_snippets = f["results"]["items"]

        if len(conversation_snippets) == 0:
            # no results to parse
            logging.error("error:  unexpected - AWS JSON dialog transcript empty")
            return block_output

        text= ""
        current_speaker = "spk_0"
        start_time = float(0)
        end_time = float(0)

        for i, items in enumerate(conversation_snippets):

            if i == 0:
                current_speaker = items["speaker_label"]
                start_time = float(items["start_time"])
                end_time = float(items["end_time"])
                # initialize text with the first word
                text=""
                if "alternatives" in items:
                    if "content" in items["alternatives"][0]:
                        text = items["alternatives"][0]["content"]

            else:
                # general case after first snippet
                new_block = False

                # if found switch in speakers - write block and re-set
                if "speaker_label" in items:
                    if items["speaker_label"] != current_speaker:

                        new_block = True

                        new_entry = {"speaker_name": current_speaker,
                                     "speaker_id": current_speaker, "text": text,
                                     "start_time": start_time, "stop_time": end_time}

                        block_output.append(new_entry)
                        current_speaker = items["speaker_label"]
                        start_time = float(items["start_time"])
                        end_time = float(items["end_time"])
                        # re-initialize text with the first word of the new speaker
                        text = ""
                        if "alternatives" in items:
                            if "content" in items["alternatives"][0]:
                                text = items["alternatives"][0]["content"]

                if not new_block:
                    if "alternatives" in items:
                        if "content" in items["alternatives"][0]:
                            if items["type"] == "punctuation":
                                text += items["alternatives"][0]["content"]
                            else:
                                # general case - type = "pronunciation"  [insert space]
                                text += " " + items["alternatives"][0]["content"]

                    if "end_time" in items:
                        end_time = float(items["end_time"])

        # pick up the last block, if any
        if text:
            new_entry = {"speaker_name": current_speaker, "speaker_id": current_speaker, "text": text,
                         "start_time": start_time, "stop_time": end_time}
            block_output.append(new_entry)

        return block_output

