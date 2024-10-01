# Copyright 2023-2024 llmware

# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.  You
# may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.


"""The parsers module implements all parsers, i.e. all conversions fom an unstructured document/content type into
set of text chunks, e.g., blocks, indexed with metadata, in a database.

    Parsers can be accessed through at least 3 distinct entry points:

    1.  Library 'add_files' - avoids the need to explicitly instantiate a Parser object, as the Parser is
        instantiated indirectly through the Library class with its convenience universal 'add_files' to Parser
        'ingest' method that collates and parses any supported file types found in the input folder.
        This is the easiest way to handle large-scale ingestion, especially with multiple file types.

    2.  Explicit Parser + Library - create a Parser object, and directly pass a Library object, and then
        use specific parsing methods to parse particular document types into the Library.   This is useful for
        document types where you would like to control the parser parameters, such as a custom csv, custom json,
        or aws transcript.  It can also be useful in special situations to have more explicit control of a
        specific parsing parameter.

    3.  Parse to File - create a Parser object without a Library, and the parsing will be saved in the ParserState,
        and available as a consolidated JSON file.  You can also retrieve parsing outputs in memory, as a list of
        dictionaries, that can be handled directly without any storage.

    The module currently implements parsers for PDF, Office (DOCX, PPTX, XLSX), CSV, JSON/JSONL, MD, TSV,
    WAV, PNG, JPEG,  HTML WebSites, and AWS voice transcripts.
"""

import time
import json
import os
from zipfile import ZipFile, ZIP_DEFLATED
import shutil

import logging
import random
from ctypes import *
import platform

from llmware.configs import LLMWareConfig, LLMWareTableSchema
from llmware.util import Utilities, TextChunker
from llmware.web_services import WikiKnowledgeBase, WebSiteParser
from llmware.resources import CollectionRetrieval, CollectionWriter, ParserState

from llmware.exceptions import DependencyNotInstalledException, FilePathDoesNotExistException, \
    OCRDependenciesNotFoundException, LLMWareException

logger = logging.getLogger(__name__)
logger.setLevel(level=LLMWareConfig().get_logging_level_by_module(__name__))


class Parser:

    def __init__(self, library=None, account_name="llmware", parse_to_db=False, file_counter=1,
                 encoding="utf-8", chunk_size=400, max_chunk_size=600, smart_chunking=1,
                 get_images=True, get_tables=True, strip_header=False, table_grid=True,
                 get_header_text=True, table_strategy=1, verbose_level=2, copy_files_to_library=True,
                 set_custom_logging=-1, use_logging_file=False):

        """ Main class for handling parsing, e.g., conversion of documents and other unstructured files
        into indexed text collection of 'blocks' in database.   For most use cases, Parser does not need
        to be invoked directly - as Library and Prompt are more natural client interfaces. """

        # as of 0.2.7, expanded configuration options offered

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
                logger.warning(f"warning: Parser not able to connect to document store collection database "
                               f"at uri - {LLMWareConfig.get_db_uri_string()} - will write parsing output to "
                               f"a parsing file.")

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
                                      "jpg","jpeg","png","wav","zip", "md", "tsv"]
        self.office_types = ["PPTX", "pptx", "XLSX", "xlsx", "DOCX", "docx"]
        self.pdf_types = ["PDF", "pdf"]
        self.text_types = ["txt", "csv", "html", "jsonl", "md", "tsv"]
        self.ocr_types = ["jpg", "jpeg", "png"]
        self.voice_types = ["wav", "mp3", "mp4", "m4a"]
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

        # new parameters
        self.encoding=encoding
        self.chunk_size = chunk_size
        self.max_chunk_size = max_chunk_size
        self.smart_chunking = smart_chunking
        self.get_images = get_images
        self.get_tables = get_tables
        self.strip_header = strip_header
        self.table_grid = table_grid
        self.table_strategy= table_strategy
        self.get_header_text = get_header_text
        self.verbose_level = verbose_level
        self.copy_files_to_library = copy_files_to_library

        # new logging
        if set_custom_logging > -1:
            self.logger_level = set_custom_logging
            logger.info(f"Parser constructor - setting custom logging level - {self.logger_level}")
        else:
            self.logger_level = LLMWareConfig().get_logging_level_by_module(__name__)

        self.parser_log_name = "parser_log.txt"
        self.use_logging_file = use_logging_file

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

        logger.info(f"update:  Duplicate files (skipped): {dup_counter}")
        logger.info(f"update:  Total uploaded: {len(input_file_names)}")

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

            logger.error("error: Parser().ingest() method requires loading a library, e.g., "
                         "Parser(library=my_library), and a connection to a document data store - please "
                         "try Parse().parse_one set of methods to parse a document of any type directly into "
                         "list of dictionaries in memory, and written to /parser_history as a .json file")

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

            if self.copy_files_to_library:
                self.uploads(self.office_work_folder)

        if work_order["pdf"] > 0:
            self.parse_pdf(self.pdf_work_folder, save_history=False)

            if self.copy_files_to_library:
                self.uploads(self.pdf_work_folder)

        if work_order["text"] > 0:
            self.parse_text(self.text_work_folder, save_history=False)

            if self.copy_files_to_library:
                self.uploads(self.text_work_folder)

        if work_order["ocr"] > 0:
            self.parse_image(self.ocr_work_folder, save_history=False)

            if self.copy_files_to_library:
                self.uploads(self.ocr_work_folder)

        if work_order["voice"] > 0:
            self.parse_voice(self.voice_work_folder, save_history=False)

            if self.copy_files_to_library:
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
                logger.info(f"error: caution - could not open Zip- {my_zip}")

            if success_code == 1:

                #   iterate thru all of the files found in the zip archive
                #   apply secure filename and prep filename
                #   route to the appropriate work folder, if applicable

                for f in z.namelist():

                    # will apply secure name and cap length, but does not run duplicate file check
                    fn = self.prep_filename(f, max_len=240, secure_name=True)
                    ext = fn.split(".")[-1]

                    if success_code == 1:

                        if ext in self.office_types:
                            shutil.copy(os.path.join(self.zip_work_folder,"tmp" + os.sep,f),
                                        os.path.join(self.office_work_folder,fn))
                            office_found += 1

                        if ext in self.pdf_types:
                            shutil.copy(os.path.join(self.zip_work_folder, "tmp" + os.sep, f),
                                        os.path.join(self.pdf_work_folder,fn))
                            pdf_found += 1

                        if ext in self.text_types:
                            shutil.copy(os.path.join(self.zip_work_folder, "tmp" + os.sep, f),
                                        os.path.join(self.text_work_folder,fn))
                            text_found += 1

                        if ext in self.ocr_types:
                            shutil.copy(os.path.join(self.zip_work_folder,"tmp" + os.sep,f),
                                        os.path.join(self.ocr_work_folder,fn))
                            ocr_found += 1

                        if ext in self.voice_types:
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
            logger.warning(f"warning: Parser - could not find parsing output - {file_path} - {fn}")
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
                    logger.debug(f"Parser - convert_parsing_txt_file_to_json - potential error - "
                                 f"parsing-to-dict conversion - lengths don't match - "
                                 f"{len(block_dict)} - {len(default_keys)}")

        return output_list

    def parse_pdf (self, fp, write_to_db=True, save_history=True):

        """ Main PDF parser method (as of 0.2.7) - and updated further starting in version 0.3.2 -
        wraps ctypes interface to call PDF parser - provides new ctypes entrypoint into PDF parser with
        expanded configuration objects, and leveraging new configurations exposed in Parser construction
        and Library().add_files. """

        #   adding changes for v0.3.2 - logger_level and debug_log_file

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
            logger.warning("Parser - parse_pdf - request to write to database but no library loaded "
                           "in Parser constructor.  Will write parsing output to file and will place the "
                           "file in /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logger.warning(f"Parser - parse_pdf - could not connect to database at "
                           f"{self.collection_path}.  Will write parsing output to file and will place the "
                           f"file in /parser_history path.")

        # deprecation warning for aarch64 linux
        system = platform.system().lower()

        if system == "linux":

            try:
                machine = os.uname().machine.lower()
            except:
                machine = "na"

            if machine == 'aarch64':
                logger.warning("Deprecation warning: deprecating support for aarch linux - "
                               "routing parsing request to handler for <=0.2.6.  Note: some features and options "
                               "in versions >=0.2.7 may not be available.")

                return self.parse_pdf_deprecated_026(fp, write_to_db=write_to_db,save_history=save_history)

        if system == "darwin":

            try:
                machine = os.uname().machine.lower()
            except:
                machine = "na"

            if machine == "x86_64":

                logger.warning("Deprecation warning: deprecating support for Mac x86 - routing parsing request "
                               "to handler for <=0.2.6.  Note: some features and options in versions >=0.2.7 "
                               "may not be available.")

                return self.parse_pdf_deprecated_026(fp, write_to_db=write_to_db, save_history=save_history)

        # end - deprecation routing

        #   * function declaration for .add_pdf_main_llmware_config_new *

        #   char * input_account_name
        #   char * input_library_name
        #   char * input_fp
        #   char * db
        #   char * db_uri_string
        #   char * db_name
        #   char * db_user_name
        #   char * db_pw
        #   char * input_images_fp
        #   int input_debug_mode
        #   int input_image_save_mode
        #   int write_to_db_on
        #   char * write_to_filename
        #   int user_blok_size
        #   int unique_doc_num
        #   int status_manager_on
        #   int status_manager_increment
        #   char * status_job_id
        #   int strip_header
        #   int table_extract
        #   int smart_chunking
        #   int max_chunk_size
        #   int encoding_style
        #   int get_header_text
        #   int table_grid
        #   int logger_level
        #   char *debug_log_file

        #   if any issue loading module, will be captured at .get_module_pdf_parser()
        _mod_pdf = Utilities().get_module_pdf_parser()

        # pdf_handler = _mod_pdf.add_pdf_main_customize_parallel
        pdf_handler = _mod_pdf.add_pdf_main_llmware_config_new

        pdf_handler.argtypes = (c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p,
                                c_char_p, c_int, c_int, c_int, c_char_p, c_int,c_int,c_int,c_int,c_char_p,
                                c_int, c_int, c_int, c_int, c_int, c_int, c_int,
                                # new configs - june 14
                                c_int, c_char_p)

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

        # debug_mode deprecated as of 0.3.1 ++
        debug_mode = self.verbose_level

        supported_options = [0, 1, 2, 3]

        if debug_mode not in supported_options:
            debug_mode = 0

        if self.get_images:
            image_save = 1  # TRUE - get images
        else:
            image_save = 0  # FALSE - no images

        input_image_save_mode = c_int(image_save)  # default - 1 = "on" | use 0 = "off" in production

        write_to_db_on_c = c_int(write_to_db_on)
        write_to_filename_c = create_string_buffer(write_to_filename.encode('ascii', 'ignore'))

        user_block_size = c_int(self.chunk_size)  # standard 400-600

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

        # defaults to 0
        if self.strip_header:
            strip_header = c_int(1)
        else:
            strip_header = c_int(0)

        if self.get_tables:
            table_extract = c_int(1)
        else:
            table_extract = c_int(0)

        smart_chunking = c_int(self.smart_chunking)

        # by default - 1 = get header text || turn off = 0
        if self.get_header_text:
            get_header_text = c_int(1)
        else:
            get_header_text = c_int(0)

        if self.table_grid:
            table_grid = c_int(1)
        else:
            table_grid = c_int(0)

        max_chunk_size = c_int(self.max_chunk_size)

        if self.encoding == "ascii":
            encoding_style = c_int(0)
        elif self.encoding == "utf-8":
            encoding_style = c_int(2)
        elif self.encoding == "latin-1":
            encoding_style = c_int(1)
        else:
            encoding_style = c_int(0)

        if self.use_logging_file:

            # parsers use code of 60 to indicate log_to_file stream rather than stdout
            input_debug_mode = c_int(60)
        else:
            input_debug_mode = c_int(0)

        #
        #                   * main call to pdf library *
        #

        logger.info("Parser - parse_pdf - start parsing of PDF Documents...")

        logger_level = c_int(self.logger_level)
        dlf_fp = os.path.join(self.parser_folder, self.parser_log_name)
        debug_log_file = create_string_buffer(dlf_fp.encode('ascii', 'ignore'))

        pages_created = pdf_handler(account_name, library_name, fp_c, db, collection_db_path_c, db_name,
                                    db_user_name_c, db_pw_c,
                                    image_fp_c,
                                    input_debug_mode, input_image_save_mode, write_to_db_on_c,
                                    write_to_filename_c, user_block_size, unique_doc_num_c,
                                    status_manager_on, status_manager_increment, status_job_id,
                                    strip_header, table_extract, smart_chunking, max_chunk_size,
                                    encoding_style, get_header_text, table_grid,
                                    # new params added in 0.3.2
                                    logger_level, debug_log_file
                                    )

        logger.info(f"Parser - parse_pdf - completed parsing of pdf documents - time taken: {time.time()-t0}")

        if write_to_db_on == 0:
            # package up results in Parser State
            parser_output = self.convert_parsing_txt_file_to_json(self.parser_image_folder, write_to_filename)
            if len(parser_output) > 0:
                last_entry = parser_output[-1]
                last_doc_id = last_entry["doc_ID"]

                self.file_counter = int(last_doc_id)

                logger.info(f"Parser - parse_pdf - adding new entries to parser output state - {len(parser_output)}")

                self.parser_output += parser_output
                output += parser_output

            if save_history:
                ParserState().save_parser_output(self.parser_job_id, parser_output)

        return output

    def parse_pdf_deprecated_026 (self, fp, write_to_db=True, save_history=True, image_save=1):

        """ Main PDF parser method through version 0.2.6 - deprecated - wraps ctypes interface to call PDF parser.
        Will be removed in future release. """

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
            logger.warning("warning: Parser().parse_pdf - request to write to database but no library loaded "
                           "in Parser constructor.   Will write parsing output to file and will place the "
                           "file in /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logger.error(f"warning: Parser().parse_pdf - could not connect to database at "
                         f"{self.collection_path}.  Will write parsing output to file and will place "
                         f"the file in /parser_history path.")

        #   * function declaration for .add_pdf_main_llmware *
        #   char * input_account_name
        #   char * input_library_name
        #   char * input_fp
        #   char * db
        #   char * db_uri_string
        #   char * db_name
        #   char * db_user_name
        #   char * db_pw
        #   char * input_images_fp
        #   int input_debug_mode
        #   int input_image_save_mode
        #   int write_to_db_on
        #   char * write_to_filename
        #   int user_blok_size
        #   int unique_doc_num
        #   int status_manager_on
        #   int status_manager_increment
        #   char * status_job_id

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

        logger.info("Parser - start parsing of PDF Documents...")

        pages_created = pdf_handler(account_name, library_name, fp_c, db, collection_db_path_c, db_name,
                                    db_user_name_c, db_pw_c,
                                    image_fp_c,
                                    input_debug_mode, input_image_save_mode, write_to_db_on_c,
                                    write_to_filename_c, user_block_size, unique_doc_num_c,
                                    status_manager_on, status_manager_increment, status_job_id)

        logger.info(f"Parser - completed parsing of pdf documents - time taken: {time.time()-t0}")

        if write_to_db_on == 0:
            # package up results in Parser State
            parser_output = self.convert_parsing_txt_file_to_json(self.parser_image_folder, write_to_filename)
            if len(parser_output) > 0:
                last_entry = parser_output[-1]
                last_doc_id = last_entry["doc_ID"]

                self.file_counter = int(last_doc_id)

                logger.info(f"Parser - adding new entries to parser output state - {len(parser_output)}")

                self.parser_output += parser_output
                output += parser_output

            if save_history:
                ParserState().save_parser_output(self.parser_job_id, parser_output)

        return output

    def parse_pdf_deprecated (self, fp, write_to_db=True, save_history=True, image_save=1):

        """ Deprecated - this is the pdf entry point for PDF binaries packaged up to llmware-0.1.14 -- replaced
        starting with llmware-0.2.0.  Will be removed in future release.  """

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
            logger.warning("Parser - parse_pdf - request to write to database but no library loaded "
                           "in Parser constructor.  Will write parsing output to file and will place the "
                           "file in /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logger.warning(f"Parser - parse_pdf - could not connect to database at "
                         f"{LLMWareConfig().get_db_uri_string()}.  Will write "
                         f"parsing output to file and will place the file in /parser_history path.")

        #   function declaration for .add_pdf_main_llmware
        #       char * input_account_name
        #       char * input_library_name
        #       char * input_fp
        #       char * input_mongo_db_path
        #       char * input_images_fp
        #       int input_debug_mode
        #       int input_image_save_mode
        #       int write_to_db_on
        #       char * write_to_filename
        #       int user_block_size
        #       int unique_doc_num
        #       char * db_user_name
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

        logger.info("Parser - start parsing of PDF Documents...")

        pages_created = pdf_handler(account_name, library_name, fp_c, collection_db_path_c, image_fp_c,
                                    input_debug_mode, input_image_save_mode, write_to_db_on_c,
                                    write_to_filename_c, user_block_size, unique_doc_num_c,
                                    db_user_name_c, db_pw_c)

        logger.info(f"Parser - completed parsing of pdf documents - time taken: {time.time()-t0}")

        if write_to_db_on == 0:
            # package up results in Parser State
            parser_output = self.convert_parsing_txt_file_to_json(self.parser_image_folder,write_to_filename)
            if len(parser_output) > 0:
                last_entry = parser_output[-1]
                last_doc_id = last_entry["doc_ID"]

                self.file_counter = int(last_doc_id)

                logger.info(f"Parser - adding new entries to parser output state - {len(parser_output)}")

                self.parser_output += parser_output
                output += parser_output

            if save_history:
                ParserState().save_parser_output(self.parser_job_id,parser_output)

        return output

    def parse_office_deprecated (self, input_fp, write_to_db=True, save_history=True):

        """ Deprecated - this is the office parser entry point for Office parser binaries packaged up to
        llmware-0.1.14 -- replaced starting with llmware-0.2.0.  Will be removed in future release. """

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
            logger.warning("Parser - parse_office - request to write to database but no library loaded "
                           "in Parser constructor.  Will write parsing output to file and will place the "
                           "file in Parser /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logger.warning(f"Parser - parse_office - could not connect to database at "
                           f"{self.collection_path}.  Will write parsing output to file and will place the "
                           f"file in Library /images path.")

        # designed for bulk upload of office parse into library structure

        if not input_fp.endswith(os.sep):
            input_fp += os.sep

        office_fp = input_fp

        workspace_fp = os.path.join(self.parser_tmp_folder,"office_tmp" + os.sep)

        if not os.path.exists(workspace_fp):
            os.mkdir(workspace_fp)
            os.chmod(workspace_fp, 0o777)

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

        #   * add_files_main_llmware function declaration *

        #       char * input_account_name
        #       char * input_library_name
        #       char * input_fp
        #       char * workspace_fp
        #       char * input_mongodb_path
        #       char * image_fp
        #       int input_debug_mode
        #       int write_to_db_on
        #       char * write_to_filename
        #       int unique_doc_num
        #       char *db_user_name
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

        logger.info("Parser - parse_office - start parsing of office documents...")

        pages_created = main_handler(account_name, library_name, fp_c, workspace_fp_c, collection_path_c, image_fp_c,
                                     debug_mode_c, write_to_db_on_c, write_to_fn_c, unique_doc_num_c,
                                     db_user_name_c, db_pw_c)

        logger.info(f"Parser - completed parsing of office documents - time taken: {time.time()-t0}")

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

        """ Primary method interface into Office parser with more configuration options - expanded most
        recently in version 0.3.2 """

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
            logger.warning("Parser - parse_office - request to write to database but no library loaded "
                           "in Parser constructor.  Will write parsing output to file and will place the "
                           "file in Parser /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logger.warning(f"Parser - parse_office - could not connect to database at "
                           f"{self.collection_path}.  Will write parsing output to file and will place the "
                           f"file in Library /images path.")

        #   deprecation warning for aarch64 linux

        system = platform.system().lower()

        if system == "linux":

            try:
                machine = os.uname().machine.lower()
            except:
                machine = "na"

            if machine == 'aarch64':
                logger.warning("Deprecation warning: deprecating support for aarch linux - "
                               "routing parsing request to handler for <=0.2.6.  Note: some features and options "
                               "in versions >=0.2.7 may not be available.")

                return self.parse_office_deprecated_027(input_fp, write_to_db=write_to_db,save_history=save_history)

        if system == "darwin":

            try:
                machine = os.uname().machine.lower()
            except:
                machine = "na"

            if machine == "x86_64":
                logger.warning("Deprecation warning: deprecating support for Mac x86 - routing parsing request "
                               "to handler for <=0.2.6.  Note: some features and options in versions >=0.2.7 "
                               "may not be available.")

                return self.parse_office_deprecated_027(input_fp, write_to_db=write_to_db, save_history=save_history)

        # end - deprecation routing

        # designed for bulk upload of office parse into library structure

        if not input_fp.endswith(os.sep):
            input_fp += os.sep

        office_fp = input_fp

        workspace_fp = os.path.join(self.parser_tmp_folder, "office_tmp" + os.sep)

        if not os.path.exists(workspace_fp):
            os.mkdir(workspace_fp)
            os.chmod(workspace_fp, 0o777)

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

        main_handler = _mod.add_files_main_llmware_opt_full

        #   * function declaration for add_files_main_llmware_opt_full *

        #   char * input_account_name
        #   char * input_library_name
        #   char * input_fp
        #   char * workspace_fp
        #   char * db
        #   char * db_uri_string
        #   char * db_name
        #   char * db_user_name
        #   char * db_pw
        #   char * image_fp
        #   int input_debug_mode
        #   int write_to_db_on
        #   char * write_to_filename
        #   int unique_doc_num
        #   int user_blok_size
        #   int status_manager_on
        #   int status_manager_increment
        #   char * status_job_id
        #   int strip_header
        #   int table_extract
        #   int smart_chunking
        #   int max_chunk_size
        #   int encoding_style
        #   int get_header_text
        #   int table_grid
        #   int save_images
        #   int logger_level
        #   char* debug_file

        main_handler.argtypes = (c_char_p, c_char_p, c_char_p, c_char_p, c_char_p,
                                 c_char_p, c_char_p, c_char_p, c_char_p, c_char_p,
                                 c_int, c_int, c_char_p, c_int, c_int, c_int, c_int,
                                 c_char_p, c_int, c_int, c_int, c_int, c_int, c_int,
                                 c_int, c_int, c_int, c_char_p)

        main_handler.restype = c_int

        account_name = create_string_buffer(self.account_name.encode('ascii', 'ignore'))
        library_name = create_string_buffer(self.library_name.encode('ascii', 'ignore'))

        fp_c = create_string_buffer(office_fp.encode('ascii', 'ignore'))
        workspace_fp_c = create_string_buffer(workspace_fp.encode('ascii', 'ignore'))

        # debug_mode deprecated as of 0.3.1++
        debug_mode = self.verbose_level

        supported_options = [0, 1, 2, 3]

        if debug_mode not in supported_options:
            debug_mode = 0

        debug_mode_c = c_int(debug_mode)

        image_fp = self.parser_image_folder
        if not image_fp.endswith(os.sep):
            image_fp += os.sep

        image_fp_c = create_string_buffer(image_fp.encode('ascii', 'ignore'))

        # get db uri string
        input_collection_db_path = LLMWareConfig().get_db_uri_string()
        collection_db_path_c = create_string_buffer(input_collection_db_path.encode('ascii', 'ignore'))

        write_to_db_on_c = c_int(write_to_db_on)

        write_to_fn_c = create_string_buffer(write_to_filename.encode('ascii', 'ignore'))

        # unique_doc_num is key parameter - if <0: will pull from incremental db, if >=0, then will start at this value
        # unique_doc_num = -1
        unique_doc_num_c = c_int(unique_doc_num)

        # pull target block size from library parameters
        user_block_size_c = c_int(self.chunk_size)

        # db credentials
        db_user_name = self.collection_db_username
        db_user_name_c = create_string_buffer(db_user_name.encode('ascii', 'ignore'))

        db_pw = self.collection_db_password
        db_pw_c = create_string_buffer(db_pw.encode('ascii', 'ignore'))

        db = LLMWareConfig.get_config("collection_db")

        db = create_string_buffer(db.encode('ascii', 'ignore'))
        db_name = account_name

        status_manager_on_c = c_int(1)
        status_manager_increment_c = c_int(10)
        status_job_id_c = create_string_buffer("1".encode('ascii', 'ignore'))

        # defaults to 0
        if self.strip_header:
            strip_header = c_int(1)
        else:
            strip_header = c_int(0)

        if self.get_tables:
            table_extract = c_int(1)
        else:
            table_extract = c_int(0)

        smart_chunking = c_int(self.smart_chunking)

        # by default - 1 = get header text || turn off = 0
        if self.get_header_text:
            get_header_text = c_int(1)
        else:
            get_header_text = c_int(0)

        if self.table_grid:
            table_grid = c_int(1)
        else:
            table_grid = c_int(0)

        if self.encoding == "ascii":
            encoding_style = c_int(0)
        elif self.encoding == "utf-8":
            encoding_style = c_int(2)
        else:
            encoding_style = c_int(2)

        max_chunk_size = c_int(self.max_chunk_size)

        if self.get_images:
            save_images = c_int(1)  # TRUE - get images
        else:
            save_images = c_int(0)  # FALSE - no images

        logger.info("Parser - parse_office - start parsing of office documents...")

        if self.use_logging_file:
            input_debug_mode = c_int(60)
        else:
            input_debug_mode = c_int(0)

        logger_level = c_int(self.logger_level)

        dlf_fp = os.path.join(self.parser_folder, self.parser_log_name)

        debug_log_file = create_string_buffer(dlf_fp.encode('ascii', 'ignore'))

        pages_created = main_handler(account_name, library_name, fp_c, workspace_fp_c,
                                     db, collection_db_path_c, db_name, db_user_name_c, db_pw_c,
                                     image_fp_c,
                                     input_debug_mode, write_to_db_on_c, write_to_fn_c, unique_doc_num_c,
                                     user_block_size_c, status_manager_on_c, status_manager_increment_c,
                                     status_job_id_c, strip_header, table_extract, smart_chunking,
                                     max_chunk_size, encoding_style, get_header_text, table_grid,
                                     save_images, logger_level, debug_log_file)

        logger.info(f"Parser - parse_office - completed parsing of office documents - time taken: {time.time()-t0}")

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

    def parse_office_deprecated_031(self, input_fp, write_to_db=True, save_history=True):

        """ Primary method interface into Office parser with more db configuration options - implemented starting
        with llmware-0.2.8 and deprecated as of v0.3.2 - will be removed in future releases. """

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
            logger.warning("Parser - parse_office - request to write to database but no library loaded "
                           "in Parser constructor.  Will write parsing output to file and will place the "
                           "file in Parser /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logger.warning(f"Parser - parse_office - could not connect to database at "
                           f"{self.collection_path}.  Will write parsing output to file and will place the "
                           f"file in Library /images path.")

        # deprecation warning for aarch64 linux
        system = platform.system().lower()

        if system == "linux":

            try:
                machine = os.uname().machine.lower()
            except:
                machine = "na"

            if machine == 'aarch64':
                logger.warning("Deprecation warning: deprecating support for aarch linux - "
                               "routing parsing request to handler for <=0.2.6.  Note: some features and options "
                               "in versions >=0.2.7 may not be available.")

                return self.parse_office_deprecated_027(input_fp, write_to_db=write_to_db, save_history=save_history)

        # end - deprecation routing

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
        main_handler = _mod.add_files_main_llmware_opt_full

        #   * function declaration for add_files_main_llmware_opt_full *

        #   char * input_account_name
        #   char * input_library_name
        #   char * input_fp
        #   char * workspace_fp
        #   char * db
        #   char * db_uri_string
        #   char * db_name
        #   char * db_user_name
        #   char * db_pw
        #   char * image_fp
        #   int input_debug_mode
        #   int write_to_db_on
        #   char * write_to_filename
        #   int unique_doc_num
        #   int user_blok_size
        #   int status_manager_on
        #   int status_manager_increment
        #   char * status_job_id
        #   int strip_header
        #   int table_extract
        #   int smart_chunking
        #   int max_chunk_size
        #   int encoding_style
        #   int get_header_text
        #   int table_grid
        #   int save_images

        main_handler.argtypes = (c_char_p, c_char_p, c_char_p, c_char_p, c_char_p,
                                 c_char_p, c_char_p, c_char_p, c_char_p, c_char_p,
                                 c_int, c_int, c_char_p, c_int, c_int, c_int, c_int,
                                 c_char_p, c_int, c_int, c_int, c_int, c_int, c_int,
                                 c_int, c_int)

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

        # debug_mode = LLMWareConfig.get_config("debug_mode")
        debug_mode = self.verbose_level

        supported_options = [0, 1, 2, 3]

        if debug_mode not in supported_options:
            debug_mode = 0

        debug_mode_c = c_int(debug_mode)

        image_fp = self.parser_image_folder
        if not image_fp.endswith(os.sep):
            image_fp += os.sep

        image_fp_c = create_string_buffer(image_fp.encode('ascii', 'ignore'))

        # get db uri string
        input_collection_db_path = LLMWareConfig().get_db_uri_string()
        collection_db_path_c = create_string_buffer(input_collection_db_path.encode('ascii', 'ignore'))

        write_to_db_on_c = c_int(write_to_db_on)

        write_to_fn_c = create_string_buffer(write_to_filename.encode('ascii', 'ignore'))

        # unique_doc_num is key parameter - if <0: will pull from incremental db, if >=0, then will start at this value
        # unique_doc_num = -1
        unique_doc_num_c = c_int(unique_doc_num)

        # start new

        # pull target block size from library parameters
        # user_block_size_c = c_int(self.block_size_target_characters)  # standard 400-600
        user_block_size_c = c_int(self.chunk_size)

        # db credentials
        db_user_name = self.collection_db_username
        db_user_name_c = create_string_buffer(db_user_name.encode('ascii', 'ignore'))

        db_pw = self.collection_db_password
        db_pw_c = create_string_buffer(db_pw.encode('ascii', 'ignore'))

        db = LLMWareConfig.get_config("collection_db")

        db = create_string_buffer(db.encode('ascii', 'ignore'))
        db_name = account_name

        status_manager_on_c = c_int(1)
        status_manager_increment_c = c_int(10)
        status_job_id_c = create_string_buffer("1".encode('ascii', 'ignore'))

        # defaults to 0
        if self.strip_header:
            strip_header = c_int(1)
        else:
            strip_header = c_int(0)

        if self.get_tables:
            table_extract = c_int(1)
        else:
            table_extract = c_int(0)

        smart_chunking = c_int(self.smart_chunking)

        # by default - 1 = get header text || turn off = 0
        if self.get_header_text:
            get_header_text = c_int(1)
        else:
            get_header_text = c_int(0)

        if self.table_grid:
            table_grid = c_int(1)
        else:
            table_grid = c_int(0)

        if self.encoding == "ascii":
            encoding_style = c_int(0)
        elif self.encoding == "utf-8":
            encoding_style = c_int(2)
        else:
            encoding_style = c_int(2)

        max_chunk_size = c_int(self.max_chunk_size)

        if self.get_images:
            save_images = c_int(1)  # TRUE - get images
        else:
            save_images = c_int(0)  # FALSE - no images

        logger.info("Parser - start parsing of office documents...")

        pages_created = main_handler(account_name, library_name, fp_c, workspace_fp_c,
                                     db, collection_db_path_c, db_name, db_user_name_c, db_pw_c,
                                     image_fp_c, debug_mode_c, write_to_db_on_c, write_to_fn_c, unique_doc_num_c,
                                     user_block_size_c, status_manager_on_c, status_manager_increment_c,
                                     status_job_id_c, strip_header, table_extract, smart_chunking,
                                     max_chunk_size, encoding_style, get_header_text, table_grid,
                                     save_images)

        logger.info(f"Parser - completed parsing of office documents - time taken: {time.time() - t0}")

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

    def parse_office_deprecated_027(self, input_fp, write_to_db=True, save_history=True):

        """ Deprecated - primary method interface into Office parser with more db configuration options -
        implemented starting with llmware-0.2.0 and deprecated as of 0.2.7 - will be removed in future
        releases. """

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
            logger.warning("Parser - parse_office - request to write to database but no library loaded "
                           "in Parser constructor.  Will write parsing output to file and will place the "
                           "file in Parser /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logger.warning(f"Parser - parse_office - could not connect to database at "
                           f"{self.collection_path}.  Will write parsing output to file and will place the "
                           f"file in Library /images path.")

        # designed for bulk upload of office parse into library structure

        if not input_fp.endswith(os.sep):
            input_fp += os.sep

        office_fp = input_fp

        workspace_fp = os.path.join(self.parser_tmp_folder, "office_tmp" + os.sep)

        if not os.path.exists(workspace_fp):
            os.mkdir(workspace_fp)
            os.chmod(workspace_fp, 0o777)

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

        #   * function declaration for add_files_main_llmware_opt *

        #   char * input_account_name
        #   char * input_library_name
        #   char * input_fp
        #   char * workspace_fp
        #   char * db
        #   char * db_uri_string
        #   char * db_name
        #   char * db_user_name
        #   char * db_pw
        #   char * image_fp
        #   int input_debug_mode
        #   int write_to_db_on
        #   char * write_to_filename
        #   int unique_doc_num
        #   int user_blok_size
        #   int status_manager_on
        #   int status_manager_increment
        #   char * status_job_id)

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

        # get db uri string
        input_collection_db_path = LLMWareConfig().get_db_uri_string()
        collection_db_path_c = create_string_buffer(input_collection_db_path.encode('ascii', 'ignore'))

        write_to_db_on_c = c_int(write_to_db_on)

        write_to_fn_c = create_string_buffer(write_to_filename.encode('ascii', 'ignore'))

        # unique_doc_num is key parameter - if <0: will pull from incremental db, if >=0, then will start at this value
        # unique_doc_num = -1
        unique_doc_num_c = c_int(unique_doc_num)

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

        logger.info("Parser - parse_office - start parsing of office documents...")

        pages_created = main_handler(account_name, library_name, fp_c, workspace_fp_c,
                                     db, collection_db_path_c, db_name, db_user_name_c, db_pw_c,
                                     image_fp_c, debug_mode_c, write_to_db_on_c, write_to_fn_c, unique_doc_num_c,
                                     user_block_size_c, status_manager_on_c, status_manager_increment_c,
                                     status_job_id_c)

        logger.info(f"Parser - completed parsing of office documents - time taken: {time.time()-t0}")

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

    def parse_text(self, input_fp, write_to_db=True, save_history=True, dupe_check=False,copy_to_library=False,
                   text_chunk_size=None, key_list=None, interpret_as_table=False,delimiter=",", separator="\n",
                   batch_size=1, encoding="utf-8-sig", errors="ignore"):

        """ Main entry point to parser for .txt, .csv, .json, .jsonl, .tsv and .md files """

        output = []

        #   must have three conditions in place - (a) user selects, (b) ping successfully, and (c) library loaded
        if write_to_db and self.parse_to_db and self.library:
            write_to_db_on = 1
        else:
            write_to_db_on = 0

        #   warning to user that no library loaded in Parser constructor
        if write_to_db and not self.library:
            logger.warning("Parser - parse_text - request to write to database but no library loaded "
                           "in Parser constructor.  Will write parsing output to file and will place the "
                           "file in /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logger.warning(f"Parser - parse_text - could not connect to database at "
                           f"{self.collection_path}.  Will write parsing output to file and will place the file "
                           f"in /parser_history path.")

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

                logger.info(f"Parser - parse_text file - processing - {file}")

                file_type = file.split(".")[-1]

                # sub-routing by type of text file to appropriate handler

                if file_type.lower() in ["txt", "md"]:
                    # will parse as text
                    text_output = TextParser(self,text_chunk_size=text_chunk_size).text_file_handler (input_fp, file)
                    content_type = "text"
                    file_type = "txt"

                if file_type.lower() in ["csv", "tsv"]:

                    if file_type.lower() == "tsv":
                        delimiter= "\t"

                    text_output = ( TextParser(self,text_chunk_size=text_chunk_size).
                                   csv_file_handler(input_fp, file, interpret_as_table=interpret_as_table,
                                                    delimiter=delimiter, batch_size=batch_size, encoding=encoding,
                                                    errors=errors) )

                    content_type = "text"
                    file_type = file_type.lower()
                    if interpret_as_table:
                        content_type = "table"

                if file_type.lower() in ["json","jsonl"]:
                    # will parse each line item as separate entry

                    interpret_as_table=False
                    if not key_list:
                        key_list = ["text"]
                    text_output = TextParser(self).jsonl_file_handler(input_fp,file,
                                                                      key_list=key_list,
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

        #   must have three conditions in place - (a) user selects, (b) ping successfully, and (c) library loaded

        if write_to_db and self.parse_to_db and self.library:
            write_to_db_on = 1
        else:
            write_to_db_on = 0

        #   warning to user that no library loaded in Parser constructor
        if write_to_db and not self.library:
            logger.warning("Parser - parse_text - request to write to database but no library loaded "
                           "in Parser constructor.  Will write parsing output to file and will place the "
                           "file in /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logger.warning(f"Parser - parse_text - could not connect to database at "
                           f"{self.collection_path}.  Will write parsing output to file and will place the "
                           f"file in /parser_history path.")

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

                    doc_fn = Utilities().secure_filename(file)

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

                        logger.info(f"Parser - parse_pdf_by_ocr_images - writing doc - page - "
                                    f"{file} - {j} - {len(blocks)}")

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
                if not isinstance(entries,str):
                    entries = str(entries)

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
                              write_to_db=True, custom_doc_id=None, custom_block_id=None):

        """ Main 'write' method of new parser text chunk for python-based parsers to write to DB. """

        # assumes that new_entry is packaged in individual handler
        # objective is to keep one single place where new entry gets loaded into db
        # ensure consistency of db data model

        if custom_doc_id:
            new_doc_id = custom_doc_id
        else:
            new_doc_id = library.doc_ID

        if custom_block_id:
            new_block_id = custom_block_id
        else:
            new_block_id = library.block_ID

        time_stamp = Utilities().get_current_time_now()

        new_entry = {
            "block_ID": new_block_id,     # note - needs caution
            "doc_ID": new_doc_id,       # note - needs caution
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

        #   must have three conditions in place - (a) user selects, (b) ping successfully, and (c) library loaded
        if write_to_db and self.parse_to_db and self.library:
            write_to_db_on = 1
        else:
            write_to_db_on = 0

        #   warning to user that no library loaded in Parser constructor
        if write_to_db and not self.library:
            logger.warning("Parser - parse_text - request to write to database but no library loaded "
                           "in Parser constructor.  Will write parsing output to file and will place the "
                           "file in /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logger.warning(f"Parser - parse_text - could not connect to database at "
                           f"{self.collection_path}.  Will write parsing output to file and will place the "
                           f"file in /parser_history path.")

        # set counters
        blocks_added = 0
        docs_added = 0
        pages_added = 0

        for i, topic in enumerate(topic_list):

            fn = "wiki-topic-" + Utilities().secure_filename(topic) + ".txt"

            logger.info(f"Parser - parse_wiki - {topic} - {fn}")

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

        #   must have three conditions in place - (a) user selects, (b) ping successfully, and (c) library loaded
        if write_to_db and self.parse_to_db and self.library:
            write_to_db_on = 1
        else:
            write_to_db_on = 0

        #   warning to user that no library loaded in Parser constructor
        if write_to_db and not self.library:
            logger.warning("Parser - parse_text - request to write to database but no library loaded "
                           "in Parser constructor.  Will write parsing output to file and will place the "
                           "file in /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logger.warning(f"Parser - parse_text - could not connect to database at "
                           f"{self.collection_path}.  Will write parsing output to file and will place the "
                           f"file in /parser_history path.")

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

    def parse_voice(self, input_folder, write_to_db=True, save_history=True, dupe_check=False,copy_to_library=False,
                    chunk_by_segment=True, remove_segment_markers=True, real_time_progress=True):

        """ Main entry point for parsing voice wav files. """

        output = []

        #   must have three conditions in place - (a) user selects, (b) ping successfully, and (c) library loaded
        if write_to_db and self.parse_to_db and self.library:
            write_to_db_on = 1
        else:
            write_to_db_on = 0

        #   warning to user that no library loaded in Parser constructor
        if write_to_db and not self.library:
            logger.warning("Parser - parse_voice - request to write to database but no library loaded "
                           "in Parser constructor.  Will write parsing output to file and will place the "
                           "file in /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logger.warning(f"Parser - parse_voice - could not connect to database at "
                           f"{self.collection_path}.  Will write parsing output to file and will place the "
                           f"file in /parser_history path.")

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

                #   increment and get new doc_id
                if write_to_db_on == 1:
                    self.library.doc_ID = self.library.get_and_increment_doc_id()

                logger.info(f"Parser - parse_voice file - processing - {file}")

                vp_output = VoiceParser(self,
                                        chunk_size=self.chunk_size,
                                        max_chunk_size=self.max_chunk_size,
                                        chunk_by_segment=chunk_by_segment,
                                        remove_segment_markers=remove_segment_markers,
                                        real_time_progress=real_time_progress).add_voice_file(input_folder, file)

                if not chunk_by_segment:
                    text_chunks_only = []
                    for chunks in vp_output:
                        text_chunks_only.append(chunks["text"])

                    if write_to_db_on == 1:
                        new_output, new_blocks, new_pages = self._write_output_to_db(text_chunks_only, file,
                                                                                     content_type="text",
                                                                                     file_type="voice-wav")
                    else:
                        new_output, new_blocks, new_pages = self._write_output_to_dict(text_chunks_only, file,
                                                                                       content_type="text",
                                                                                       file_type="voice-wav")

                    output += new_output
                    docs_added += 1
                    blocks_added += new_blocks
                    pages_added += new_pages
                    self.file_counter += 1

                else:

                    for i, blocks in enumerate(vp_output):

                        # iterate thru each block -> add to metadata
                        speaker_name = blocks["speaker"]

                        meta = {"author": speaker_name, "modified_date": "", "created_date": "", "creator_tool": ""}

                        coords_dict = {"coords_x": blocks["start_time"], "coords_y": blocks["end_time"],
                                       "coords_cx": blocks["start_segment"], "coords_cy": blocks["end_segment"]}

                        text_entry = blocks["text"]

                        format_type = "voice-wav"

                        new_entry = ("text", format_type, (1, 0), i, "", "", file,
                                     "", text_entry, "", "", text_entry, text_entry, "", text_entry,
                                     "", "", "", "", "")

                        #TODO: adding dialog and diarization roles in speech parsing

                        if write_to_db_on == 1:
                            entry_output = self.add_create_new_record(self.library, new_entry, meta, coords_dict,
                                                                      dialog_value="false")
                            self.library.block_ID += 1
                        else:
                            entry_output = self.create_one_parsing_output_dict(i,new_entry,meta,coords_dict,
                                                                               dialog_value="false")
                            self.parser_output.append(entry_output)

                        # return output in either case
                        output.append(entry_output)

                    blocks_added += len(vp_output)
                    pages_added += 0
                    docs_added += 1
                    self.file_counter += 1

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

        #   must have three conditions in place - (a) user selects, (b) ping successfully, and (c) library loaded
        if write_to_db and self.parse_to_db and self.library:
            write_to_db_on = 1
        else:
            write_to_db_on = 0

        #   warning to user that no library loaded in Parser constructor
        if write_to_db and not self.library:
            logger.warning("Parser - parse_dialog - request to write to database but no library loaded "
                           "in Parser constructor.  Will write parsing output to file and will place the "
                           "file in /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logger.warning(f"Parser - parse_dialog - could not connect to database at "
                           f"{self.collection_path}.  Will write parsing output to file and will place "
                           f"the file in /parser_history path.")

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

                    logger.info(f"Parser - parse_dialog - dialog file - {file}")

                    dp_parse_output = DialogParser(self).parse_aws_json_file_format(input_folder, file)

                    block_id = 0

                    for i, blocks in enumerate(dp_parse_output):

                        logger.debug(f"Parser - parse_dialog - dialog turn - {i} {blocks}")

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

        #   must have three conditions in place - (a) user selects, (b) ping successfully, and (c) library loaded
        if write_to_db and self.parse_to_db and self.library:
            write_to_db_on = 1
        else:
            write_to_db_on = 0

        #   warning to user that no library loaded in Parser constructor
        if write_to_db and not self.library:
            logger.warning("Parser - parse_website - request to write to database but no library loaded "
                           "in Parser constructor.  Will write parsing output to file and will place the "
                           "file in /parser_history path.")

        #   warning to user that database connection not found
        if write_to_db and not self.parse_to_db:
            logger.warning(f"Parser - parse_website - could not connect to database at "
                           f"{self.collection_path}.  Will write parsing output to file and will place the "
                           f"file in /parser_history path.")

        local_work_folder = self.parser_tmp_folder

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

            #  if get_links, then pursue internal links and 'add' to indexed output gathered

            if get_links:

                if len(website.internal_links) > 0:

                    max_links = min(len(website.internal_links), max_links)

                    for z in range(0, max_links):

                        logger.debug(f"Parser - parse_website - iterate - "
                                     f"child site link - {z} - {url_base} - {website.internal_links[z]}")

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

        # upload website_file
        fp_tmp = os.path.join(local_work_folder, "process_website" + os.sep)

        website_name = "my_website.html"
        
        # apply secure filename to remove any extra "/"
        secure_url_name = Utilities().secure_filename(website.url_main.split(".")[-2])

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
            logger.error("Parser - uploads is designed for connecting files into library - "
                         "no library selected - to use, create Parser with library loaded, e.g., "
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
            fn_out= Utilities().secure_filename(fn)

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

        """ Compares input with parsed output to identify any rejected files. """

        # shortcut if file_list is just empty
        if len(file_list) < 1:
            return [],[]

        # simple approach - compares input file_list from ingestion 'work_order' with state of library collection
        #   --if input file found, then added to 'found_list' -> else, added to 'not_found_list'

        if not self.library:
            logger.error("Parser - input_ingestion_comparison is designed for bulk parsing of files "
                         "into library - no library selected - to use, create Parser with library loaded, e.g., "
                         "Parser(library=my_library)")
            return -1

        found_list = []

        doc_fn_raw_list = CollectionRetrieval(self.library_name,
                                              account_name=self.account_name).get_distinct_list("file_source")

        for i, file in enumerate(doc_fn_raw_list):

            if file.split(os.sep)[-1] in file_list:
                # excludes zip files that have been unzipped into core files in the parsing proces
                found_list.append(file.split(os.sep)[-1])

            # if found_list is equal length of file_list we don't need to look any further
            if len(found_list) == len(file_list):
                break

        not_found_list = list(set(file_list) - set(found_list))

        #   will strip any .zip files from rejected list, since the individual files are dynamically extracted
        #   and parsed, and if there is an error opening the zip it is raised as an exception

        ex_zip_nf_list = []
        for f in not_found_list:
            if not f.endswith(".zip"):
                ex_zip_nf_list.append(f)

        return found_list, ex_zip_nf_list

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

                # need to confirm 'symmetrical' transformations, e.g., secure filename and any prepend/postpend
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
            logger.warning(f"Parser - parse_one - no content parsed from document - {fn}")

        return output

    def parse_one_office (self, fp, fn, save_history=True):

        """ Parse one office document at selected file path and file name. """

        #   Designed for 'ad hoc' and 'unbound' quick parse of a single office document with no storage
        #   --  output provided as list of Dicts in memory with same structure as parsing output
        #   --  updated with expanded configuration options for logging (0.3.2+)

        # check that path exists
        if not os.path.exists(os.path.join(fp, fn)):
            raise FilePathDoesNotExistException(os.path.join(fp,fn))

        # deprecation warning for aarch64 linux and mac x86

        system = platform.system().lower()

        if system == "linux":

            try:
                machine = os.uname().machine.lower()
            except:
                machine = "na"

            if machine == 'aarch64':
                logger.warning("Deprecation warning: deprecating support for aarch linux - "
                               "routing parsing request to handler for <=0.2.6.  Note: some features and options "
                               "in versions >=0.2.7 may not be available.")

                return self.parse_one_office_deprecated_031_no_opts(fp, fn, save_history=save_history)

        if system == "darwin":

            try:
                machine = os.uname().machine.lower()
            except:
                machine = "na"

            if machine == "x86_64":
                logger.warning("Deprecation warning: deprecating support for Mac x86 - routing parsing request "
                               "to handler for <=0.2.6.  Note: some features and options in versions >=0.2.7 "
                               "may not be available.")

                return self.parse_one_office_deprecated_031_no_opts(fp, fn,save_history=save_history)

        # end - deprecation routing

        workspace_fp = self.parser_tmp_folder

        if not os.path.exists(workspace_fp):
            os.mkdir(workspace_fp)
            os.chmod(workspace_fp, 0o777)

        #   safety check - will need to improve + expand for supporting windows path
        if not workspace_fp.endswith(os.sep):
            workspace_fp += os.sep
            logger.warning("Parser - parse_one_office - workspace_fp did not end with "
                           "trailing '/' as expected by parser")

        #   set up workspace for parser
        for z in range(0, 1):

            if os.path.exists(os.path.join(workspace_fp,str(z))):
                shutil.rmtree(os.path.join(workspace_fp,str(z)), ignore_errors=True)

            if not os.path.exists(os.path.join(workspace_fp,str(z))):
                os.mkdir(os.path.join(workspace_fp,str(z)))
                os.chmod(os.path.join(workspace_fp, str(z)), 0o777)

        #   * function declaration - add_one_office_opt_full *

        #   char * input_account_name
        #   char * input_library_name
        #   char * input_fp
        #   char * input_fn
        #   char * workspace_fp
        #   char * image_fp
        #   char * write_to_filename
        #   int * unique_doc_num
        #   int * user_blok_size
        #   int strip_header
        #   int table_extract
        #   int smart_chunking
        #   int max_chunk_size
        #   int encoding_style
        #   int get_header_text
        #   int table_grid
        #   int save_images
        #   int logger_level
        #   char * debug_log_file
        #   int input_debug_mode

        #   if any issue loading module, will be captured at .get_module_office_parser()
        _mod = Utilities().get_module_office_parser()

        main_handler = _mod.add_one_office_opt_full

        main_handler.argtypes = (c_char_p, c_char_p, c_char_p, c_char_p, c_char_p,
                                 c_char_p, c_char_p, c_int, c_int, c_int, c_int, c_int,
                                 c_int, c_int, c_int, c_int, c_int, c_int, c_char_p, c_int)

        main_handler.restype = c_int

        # pull target block size from library parameters
        user_block_size_c = c_int(self.chunk_size)

        if not self.account_name:
            self.account_name = "llmware"

        account_name = create_string_buffer(self.account_name.encode('ascii', 'ignore'))
        library_name = create_string_buffer(self.library_name.encode('ascii', 'ignore'))

        if not fp.endswith(os.sep):
            fp += os.sep

        fp_c = create_string_buffer(fp.encode('ascii', 'ignore'))
        fn_c = create_string_buffer(fn.encode('ascii', 'ignore'))

        workspace_fp_c = create_string_buffer(workspace_fp.encode('ascii', 'ignore'))

        image_fp = self.parser_image_folder

        if not image_fp.endswith(os.sep):
            image_fp += os.sep
            logger.warning("Parser - parse_one_office - adding '/' to image_fp as expected by c parser")

        image_fp_c = create_string_buffer(image_fp.encode('ascii', 'ignore'))

        write_to_filename = "office_internal_test0.txt"
        write_to_fn_c = create_string_buffer(write_to_filename.encode('ascii', 'ignore'))

        # defaults to 0
        if self.strip_header:
            strip_header = c_int(1)
        else:
            strip_header = c_int(0)

        if self.get_tables:
            table_extract = c_int(1)
        else:
            table_extract = c_int(0)

        smart_chunking = c_int(self.smart_chunking)

        # by default - 1 = get header text || turn off = 0
        if self.get_header_text:
            get_header_text = c_int(1)
        else:
            get_header_text = c_int(0)

        if self.table_grid:
            table_grid = c_int(1)
        else:
            table_grid = c_int(0)

        if self.encoding == "ascii":
            encoding_style = c_int(0)
        elif self.encoding == "utf-8":
            encoding_style = c_int(2)
        else:
            encoding_style = c_int(2)

        max_chunk_size = c_int(self.max_chunk_size)

        if self.get_images:
            save_images = c_int(1)  # TRUE - get images
        else:
            save_images = c_int(0)  # FALSE - no images

        logger.debug("Parser - parse_one_office - start parsing of office document...")

        #   placeholder for now - not used
        unique_doc_num_c = c_int(34)

        if self.use_logging_file:
            input_debug_mode = c_int(60)
        else:
            input_debug_mode = c_int(0)

        if self.logger_level <= 10:
            logger_level = c_int(self.logger_level)
        else:
            #   unless in debug mode, suppress informational updates from parsers
            logger_level = c_int(40)

        dlf_fp = os.path.join(self.parser_folder, self.parser_log_name)
        debug_log_file = create_string_buffer(dlf_fp.encode('ascii', 'ignore'))

        pages_created = main_handler(account_name, library_name, fp_c, fn_c, workspace_fp_c, image_fp_c,
                                     write_to_fn_c, unique_doc_num_c, user_block_size_c,
                                     strip_header, table_extract, smart_chunking, max_chunk_size,
                                     encoding_style, get_header_text, table_grid, save_images,
                                     logger_level, debug_log_file, input_debug_mode)

        # self.library.image_path
        output = self.convert_parsing_txt_file_to_json(file_path=self.parser_tmp_folder,fn=write_to_filename)

        if len(output) > 0:
            self.parser_output += output

        if save_history:
            ParserState().save_parser_output(self.parser_job_id, self.parser_output)

        return output

    def parse_one_office_deprecated_031_no_opts (self, fp, fn, save_history=True):

        """ Deprecated starting with llmware v 0.3.2 - entry point to parse one office document at
        the selected file path and file name - fewer config options available.  Will be removed in future
        releases. """

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
            logger.warning("Parser - parse_one_office - workspace_fp did not end with trailing '/' "
                           "as expected by parser")

        # setup parser workspace
        for z in range(0, 1):

            if os.path.exists(os.path.join(workspace_fp,str(z))):
                shutil.rmtree(os.path.join(workspace_fp,str(z)), ignore_errors=True)

            if not os.path.exists(os.path.join(workspace_fp,str(z))):
                os.mkdir(os.path.join(workspace_fp,str(z)))
                os.chmod(os.path.join(workspace_fp, str(z)), 0o777)

        #   * function declaration - add_one_office *

        #   char * input_account_name
        #   char * input_library_name
        #   char * input_fp
        #   char * input_fn
        #   char * workspace_fp
        #   char * image_fp
        #   char * write_to_filename

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
            logger.warning("warning: adding '/' to image_fp as expected by c parser")

        image_fp_c = create_string_buffer(image_fp.encode('ascii', 'ignore'))

        write_to_filename = "office_internal_test0.txt"
        write_to_fn_c = create_string_buffer(write_to_filename.encode('ascii', 'ignore'))

        #   main call into office parser
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

        #   0.3.2 - adding expanded configs with text chunking and logging options

        # check that path exists
        if not os.path.exists(os.path.join(fp,fn)):
            raise FilePathDoesNotExistException(os.path.join(fp,fn))

        # deprecation warning for aarch64 linux and mac x86

        system = platform.system().lower()

        if system == "linux":

            try:
                machine = os.uname().machine.lower()
            except:
                machine = "na"

            if machine == 'aarch64':
                logger.warning("Deprecation warning: deprecating support for aarch linux - "
                               "routing parsing request to handler for <=0.2.6.  Note: some features and options "
                               "in versions >=0.2.7 may not be available.")

                return self.parse_one_pdf_deprecated_031(fp, fn, save_history=save_history)

        if system == "darwin":

            try:
                machine = os.uname().machine.lower()
            except:
                machine = "na"

            if machine == "x86_64":
                logger.warning("Deprecation warning: deprecating support for Mac x86 - routing parsing request "
                               "to handler for <=0.2.6.  Note: some features and options in versions >=0.2.7 "
                               "may not be available.")

                return self.parse_one_pdf_deprecated_031(fp, fn, save_history=save_history)

        # end - deprecation routing

        #   if any issue loading module, will be captured at .get_module_pdf_parser()
        _mod_pdf = Utilities().get_module_pdf_parser()

        pdf_handler = _mod_pdf.add_one_pdf_opts

        #   * function declaration - add_one_pdf_opts *

        #   char * account_name
        #   char * library_name
        #   char * input_fp
        #   char * input_filename
        #   char * input_images_fp
        #   char * write_to_filename
        #   int user_blok_size
        #   int unique_doc_num
        #   int strip_header
        #   int table_extract
        #   int smart_chunking
        #   int max_chunk_size
        #   int encoding_style
        #   int get_header_text
        #   int table_grid
        #   int save_images
        #   int logger_level
        #   char * debug_log_file
        #   int input_debug_mode

        pdf_handler.argtypes = (c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int,
                                c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int,
                                c_char_p, c_int)

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

        image_fp = self.parser_tmp_folder
        if not image_fp.endswith(os.sep):
            image_fp += os.sep

        image_fp_c = create_string_buffer(image_fp.encode('ascii', 'ignore'))

        #   prep parameters passed in the method invocation above
        write_to_filename = "pdf_internal_test0.txt"
        write_to_filename_c = create_string_buffer(write_to_filename.encode('ascii','ignore'))

        # pull target block size from library parameters
        user_block_size = c_int(self.chunk_size)

        # defaults to 0
        if self.strip_header:
            strip_header = c_int(1)
        else:
            strip_header = c_int(0)

        if self.get_tables:
            table_extract = c_int(1)
        else:
            table_extract = c_int(0)

        smart_chunking = c_int(self.smart_chunking)

        # by default - 1 = get header text || turn off = 0
        if self.get_header_text:
            get_header_text = c_int(1)
        else:
            get_header_text = c_int(0)

        if self.table_grid:
            table_grid = c_int(1)
        else:
            table_grid = c_int(0)

        if self.encoding == "ascii":
            encoding_style = c_int(0)
        elif self.encoding == "utf-8":
            encoding_style = c_int(2)
        else:
            encoding_style = c_int(2)

        max_chunk_size = c_int(self.max_chunk_size)

        if self.get_images:
            save_images = c_int(1)  # TRUE - get images
        else:
            save_images = c_int(0)  # FALSE - no images

        unique_doc_num_c = c_int(34)

        if self.use_logging_file:
            input_debug_mode = c_int(60)
        else:
            input_debug_mode = c_int(0)

        if self.logger_level <= 10:
            logger_level = c_int(self.logger_level)
        else:
            #   unless in debug mode, then suppress information updates from parsers
            logger_level = c_int(40)

        dlf_fp = os.path.join(self.parser_folder, self.parser_log_name)
        debug_log_file = create_string_buffer(dlf_fp.encode('ascii', 'ignore'))

        logger.debug("Parser - parse_one_pdf - starting pdf_parser ...")

        #   main call into pdf parser

        pages_created = pdf_handler(account_name, library_name, fp_c, fn_c, image_fp_c,
                                    write_to_filename_c, user_block_size,
                                    unique_doc_num_c, strip_header, table_extract, smart_chunking,
                                    max_chunk_size, encoding_style, get_header_text, table_grid,
                                    save_images, logger_level, debug_log_file, input_debug_mode)

        logger.debug(f"Parser - parse_one_pdf - completed pdf_parser - time taken: {time.time()-t0}")

        output = self.convert_parsing_txt_file_to_json(file_path=self.parser_tmp_folder,fn=write_to_filename)

        if len(output) > 0:
            self.parser_output += output

        if save_history:
            ParserState().save_parser_output(self.parser_job_id, self.parser_output)

        return output

    def parse_one_pdf_deprecated_031 (self, fp, fn,  save_history=True):

        """ Deprecated as of 0.3.2 - parse one pdf document at selected file path and file name - provides
        fewer configuration options for text chunking and logging. """

        # check that path exists
        if not os.path.exists(os.path.join(fp,fn)):
            raise FilePathDoesNotExistException(os.path.join(fp,fn))

        #   * function declaration - add_one_pdf *

        #   char * account_name
        #   char * library_name
        #   char * input_fp
        #   char * input_filename
        #   char * input_images_fp
        #   char * write_to_filename
        #   int user_block_size

        #   if any issue loading module, will be captured at .get_module_pdf_parser()
        _mod_pdf = Utilities().get_module_pdf_parser()

        pdf_handler = _mod_pdf.add_one_pdf

        pdf_handler.argtypes = (c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int)
        pdf_handler.restypes = c_int

        #   prepare input variables

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

        image_fp = self.parser_tmp_folder
        if not image_fp.endswith(os.sep):
            image_fp += os.sep

        image_fp_c = create_string_buffer(image_fp.encode('ascii', 'ignore'))

        #   prep parameters passed in the method invocation above
        write_to_filename = "pdf_internal_test0.txt"
        write_to_filename_c = create_string_buffer(write_to_filename.encode('ascii','ignore'))

        # pull target block size from library parameters

        user_block_size = c_int(self.block_size_target_characters)   # standard 400-600

        logger.info("Parser - parse_one_pdf - starting pdf_parser ...")

        #   main call into the pdf parser

        pages_created = pdf_handler(account_name, library_name, fp_c, fn_c, image_fp_c,
                                    write_to_filename_c, user_block_size)

        logger.info(f"Parser - parse_one_pdf - completed pdf_parser - time taken: {time.time()-t0}")

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

            doc_fn = Utilities().secure_filename(input_fn)

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

            doc_fn = Utilities().secure_filename(input_fn)
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

        if file_type.lower() in ["csv", "tsv"]:
            # will parse as table
            interpret_as_table=True

            if file_type.lower() == "tsv":
                separator="\t"
            else:
                separator=","

            parser_output = TextParser(self).csv_file_handler(input_fp, input_fn, interpret_as_table=True,
                                                              delimiter=separator)

            content_type = "text"
            # file_type = "csv"
            file_type = file_type.lower()
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

    def parse_one_voice(self, input_fp, input_fn, save_history=True,
                        chunk_by_segment=True, remove_segment_markers=True, real_time_progress=True):

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

            parser_output = VoiceParser(self,
                                        chunk_size=self.chunk_size,
                                        max_chunk_size=self.max_chunk_size,
                                        chunk_by_segment=chunk_by_segment,
                                        remove_segment_markers=remove_segment_markers,
                                        real_time_progress=real_time_progress).add_voice_file(input_fp, input_fn)

            if not chunk_by_segment:
                text_chunks_only = []
                for chunks in parser_output:
                    text_chunks_only.append(chunks["text"])

                new_output, new_blocks, new_pages = self._write_output_to_dict(text_chunks_only, input_fn,
                                                                               content_type="text", file_type="voice-wav")

                self.parser_output.append(new_output)
                output += new_output

            else:

                for i, blocks in enumerate(parser_output):

                    # iterate thru each block -> add to metadata
                    speaker_name = blocks["speaker"]

                    meta = {"author": speaker_name, "modified_date": "", "created_date": "", "creator_tool": ""}

                    coords_dict = {"coords_x": blocks["start_time"], "coords_y": blocks["end_time"],
                                   "coords_cx": blocks["start_segment"], "coords_cy": blocks["end_segment"]}

                    text_entry = blocks["text"]

                    # conforming file format with full path of dialog intake path

                    format_type = "voice-wav"

                    new_entry = ("text", format_type, (1, 0), i, "", "", input_fn,
                                 "", text_entry, "", "", text_entry, text_entry, "", text_entry,
                                 "", "", "", "", "")

                    entry_output = self.create_one_parsing_output_dict(i, new_entry, meta, coords_dict,
                                                                       dialog_value="false")

                    self.parser_output.append(entry_output)

                    # return value is output
                    output.append(entry_output)

        if save_history:
            ParserState().save_parser_output(self.parser_job_id, self.parser_output)

        return output

    def query_parser_state(self, query, results=None, remove_stop_words=True):

        """ Runs an in-memory 'fast search' against a set of parsed output json dictionaries. """

        if not results:
            results = self.parser_output

        output = Utilities().fast_search_dicts(query,results, text_key="text",remove_stop_words=remove_stop_words)

        return output

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

    def parse_csv_config(self,fp, fn, cols=None, mapping_dict=None, delimiter=","):

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

        # method requires library loaded in the Parser

        if not self.library:
            raise LLMWareException(message="Parsing of a configured CSV file requires a library object to "
                                           "be connected to the parser state.")

        #   if found in mapping dict, then will over-write
        reserved_keys = ["text", "doc_ID", "block_ID"]

        rejected_rows = []

        if not mapping_dict:
            raise LLMWareException(message="Parsing of a configured CSV file requires a mapping dictionary so that "
                                           "the table attributes can be properly mapped.")

        if not cols:
            raise LLMWareException(message="Parsing of a configured CSV file requires a defined column structure and "
                                           "a specified number of columns to ensure accurate mapping.")

        # file type
        ft = fn.split(".")[-1].lower()
        if ft == "tsv":
            delimiter="\t"

        # will iterate through csv file
        input_csv = os.path.join(fp, fn)

        output = Utilities.file_load(input_csv,delimiter=delimiter,encoding='utf-8-sig',errors='ignore')

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

                # note: if using SQL-based DB, then will save the metadata as a text string
                if LLMWareConfig().get_config("collection_db") in ["sqlite", "postgres"]:
                    metadata = str(metadata)

                new_row_entry = ("text", "custom_csv", (1, 0), total_row_count, "", "", fn,
                                 text, text, "", "", text, text, "", text, "", "", metadata, "", "")

                #   set attributes custom
                if doc_id:
                    try:
                        self.library.doc_ID = int(doc_id)
                        added_doc_count += 1
                    except:
                        logger.debug(f"Parser - parse_csv_config - doc_ID expected to be integer - "
                                     f"can not apply custom doc ID - {doc_id} - will use default "
                                     f"library document increment")

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

        output = {"rows_added": added_row_count, "rejected_count": len(rejected_rows), "rejected_rows": rejected_rows}

        return output

    def parse_json_config(self,fp, fn, mapping_dict=None):

        """ Designed for intake of a 'pseudo-db json/jsonl table' and will add rows to library with mapped keys.

        Inputs:
            -- json folder path + json file name
            -- cols = # of expected column entries in each row of the CSV
            -- mapping dict = assigns llmware library key names to keys in the json
                e.g., {"text": "output", "doc_ID": "ID", "key1": "special_field1", "key2": "special_field2", "key3":"special_field3"}

        Requirements:
            -- must have a "text" key in the mapping dictionary
            -- optional doc_ID and block_ID - if found, will over-write the normal library indexes
            -- all other keys will be saved as 'metadata' and added to the library block row in "special_field1"

        Note: this feature is currently only supported for Mongo - SQL DB support will follow.
        """

        # method requires a library loaded in the Parser

        if not self.library:
            raise LLMWareException(message="Parsing of a configured CSV file requires a library object to "
                                           "be connected to the parser state.")

        #   if found in mapping dict, then will over-write
        reserved_keys = ["text", "doc_ID", "block_ID"]

        rejected_rows = []

        if not mapping_dict:
            raise LLMWareException(message="Parsing of a configured JSON/JSONL file requires a mapping dictionary so that "
                                           "the table attributes can be properly mapped.")

        # will iterate through json/jsonl file
        ft = fn.split(".")[-1].lower()

        if ft not in ["json", "jsonl"]:
            raise LLMWareException(message=f"File type not recognized as JSON/JSONL - {ft}")

        output = []

        if ft == "json":
            output = json.load(open(os.path.join(fp, fn), "r"))

        if ft == "jsonl":
            my_file = open(os.path.join(fp, fn), 'r', encoding='utf-8-sig',errors='ignore')

            output = []
            for i, lines in enumerate(my_file):
                row_tmp = json.loads(lines)
                output.append(row_tmp)

            my_file.close()

        added_row_count = 0
        total_row_count = 0
        added_doc_count = 0

        for i, rows in enumerate(output):

            text = ""
            doc_id = None
            block_id = None
            metadata = {}

            for keys, values in mapping_dict.items():

                if keys == "text":
                    if values in rows:
                        text = rows[values]

                if keys == "doc_ID":
                    if values in rows:
                        doc_id = rows[values]

                if keys == "block_ID":
                    if values in rows:
                        block_id = rows[values]

                if keys not in reserved_keys:
                    metadata.update({keys:rows[values]})

            if text.strip():

                meta = {"author": "", "modified_date": "", "created_date": "", "creator_tool": ""}
                coords_dict = {"coords_x": 0, "coords_y": 0, "coords_cx": 0, "coords_cy": 0}

                # conforming file format with full path of dialog intake path
                metadata = str(metadata)

                new_row_entry = ("text", "custom_json", (1, 0), total_row_count, "", "", fn,
                                 text, text, "", "", text, text, "", text, "", "", metadata, "", "")

                #   set attributes custom
                if doc_id:
                    try:
                        self.library.doc_ID = int(doc_id)
                        added_doc_count += 1
                    except:
                        logger.debug(f"Parser - parse_json_config - doc_ID expected to be integer - "
                                     f"can not apply custom doc ID - {doc_id} - will use default library "
                                     f"document increment")

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

        output = {"rows_added": added_row_count, "rejected_count": len(rejected_rows), "rejected_rows": rejected_rows}

        return output

    def ocr_images_in_library(self, add_to_library=False, chunk_size=400, min_size=10,
                              realtime_progress=True):

        """ Assumes that a Library is passed in the Parser constructor, and that the Library already contains
        some parsed content with at least some images found.   This method will identify the images extracted
        across the entire library, and then run an OCR against each image looking for text to extract, apply
        text chunking rules, and then save the new OCR-extracted text in the library database.

        Output, by default, is verbose and displays real-time progress from the OCR to be able to evaluate the
        quality before confirming `add_to_library = True`.   To remove the verbose screen output, set
        `realtime_progress = False`. """

        if not self.library:
            raise LLMWareException(message="Exception: Parser - ocr_images_in_library - is intended to be used "
                                           "in conjunction with a loaded Library.   To use, you can call the "
                                           "Library class convenience method - .ocr_on_images method.")

        from importlib import util
        if not util.find_spec("pytesseract"):
            raise LLMWareException(message="Exception: Parser - ocr_images_in_library - requires additional "
                                           "dependencies to be installed on your system.  \nTo use this method, "
                                           "please implement two prerequisites:"
                                           "\n1. pytesseract - pip3 install pytesseract"
                                           "\n2. lib tesseract - core library and can be installed:"
                                           "\n        -mac os:  brew install tesseract"
                                           "\n        -ubuntu:  sudo apt install libtesseract-dev"
                                           "\n        -windows: use GUI download installer")

        library_name = self.library.library_name
        image_path = self.library.image_path

        #   check here to see the images extracted from the original parsing
        if realtime_progress:
            logger.info(f"update: image source file path: {image_path}")

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
            output = ImageParser(text_chunk_size=chunk_size).process_ocr(image_path, img_name, preserve_spacing=False)

            if realtime_progress:
                logger.info(f"Parser - ocr_images_in_library - realtime progress- ocr output: {output}")

            #   good to do a test run with 'add_to_library' == False before writing to the collection
            if add_to_library:

                for text_chunk in output:

                    if text_chunk.strip():

                        # optional to keep only more substantial chunks of text
                        if len(text_chunk) > min_size:

                            #   ad hoc tracker to keep incrementing the block_id for every new image in a particular doc
                            if doc_id in doc_update_list:
                                new_block_id = doc_update_list[doc_id]
                                doc_update_list.update({doc_id: new_block_id + 1})
                            else:
                                new_block_id = 100000
                                doc_update_list.update({doc_id: new_block_id + 1})

                            new_block = block

                            #   feel free to adapt these attributes to fit for purpose
                            new_block.update({"block_ID": new_block_id})
                            new_block.update({"content_type": "text"})
                            new_block.update({"embedding_flags": {}})
                            new_block.update({"text_search": text_chunk})

                            #   writes a special entry in 'special_field1' of the database
                            #   this special entry captures the link back to the original 'image' block
                            #   it can be unpacked by splitting on '&' and '-' to retrieve the doc_id and block_id

                            output = f"document-{doc_id}&block-{block_id}"
                            new_block.update({"special_field1": output})

                            #   new _id will be assigned by the database directly
                            if "_id" in new_block:
                                del new_block["_id"]

                            if realtime_progress:
                                logger.info(f"Parser - ocr_images_in_library - new text block - {new_text_created} - "
                                            f"{doc_id} - {block_id} - {text_chunk} - {new_block}")

                            #   creates the new record
                            CollectionWriter(library_name).write_new_parsing_record(new_block)

                            new_text_created += 1

        return new_text_created


class ImageParser:

    """ ImageParser for handling OCR of scanned documents - may be called directly, or through Parser.
    Current implementation requires separate install of tesseract and pytesseract. """

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
            import pytesseract
            from pytesseract.pytesseract import TesseractNotFoundError
        except ImportError:
            raise DependencyNotInstalledException("pytesseract")

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

        try:
            import pytesseract
            from pytesseract.pytesseract import TesseractNotFoundError
        except ImportError:
            raise DependencyNotInstalledException("pytesseract")

        text_list_out = []
        scanned_files = os.listdir(fp)

        for docs in scanned_files:

            try:
                text_out = pytesseract.image_to_string(os.path.join(fp,docs))
            except TesseractNotFoundError as e:
                raise OCRDependenciesNotFoundException("tesseract")
            text_out = text_out.replace("\n", " ")
            logger.info(f"ImageParser - ocr_to_single_file - ocr text_out: {text_out}")
            text_list_out.append(text_out)

        return text_list_out

    def process_pdf_by_ocr(self, input_fp, file):

        """ Handles special case of running page-by-page OCR on a scanned PDF document. """

        text_output_by_page = []

        try:
            import pytesseract
            from pytesseract.pytesseract import TesseractNotFoundError
        except ImportError:
            raise DependencyNotInstalledException("pytesseract")

        try:
            from pdf2image import convert_from_path
            from pdf2image.exceptions import PDFInfoNotInstalledError
        except ImportError:
            raise DependencyNotInstalledException("pdf2image")

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

        try:
            import pytesseract
            from pytesseract.pytesseract import TesseractNotFoundError
        except ImportError:
            raise DependencyNotInstalledException("pytesseract")

        try:
            from pdf2image import convert_from_path
            from pdf2image.exceptions import PDFInfoNotInstalledError
        except ImportError:
            raise DependencyNotInstalledException("pdf2image")

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
                        logger.info(f"update: ocr text out - {text}")

                    logger.info(f"update: ocr converted- {i} - {files}")
                    all_text += "\n\n"

                except:
                    logger.error("error - could not convert pdf")

        f = open(input_fp + summary_text_fn, "w", encoding='utf-8')
        f.write(all_text)
        f.close()

        return summary_text_fn


class VoiceParser:

    """ VoiceParser handles wav files to convert into text blocks. """

    def __init__(self, parser=None, library=None, text_chunk_size=600, look_back_range=300,
                 chunk_size=400, max_chunk_size=600, chunk_by_segment=True, remove_segment_markers=True,
                 real_time_progress=True):

        self.parser = parser

        #   chunking parameters
        self.chunk_size=chunk_size
        self.max_chunk_size = max_chunk_size
        self.chunk_by_segment = chunk_by_segment
        self.remove_segment_markers = remove_segment_markers
        self.real_time_progress = real_time_progress

        # defaults - for pure 'Text Chunking' - deprecating approach, but keeping as option for now
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

        from llmware.gguf_configs import GGUFConfigs

        #   default model -> "whisper-cpp-base-english"
        self.selected_speech_model_name = GGUFConfigs().get_config("whisper_default_model")

        #   will update global GGUFConfigs based on real_time_progress preference
        GGUFConfigs().set_config("whisper_cpp_realtime_display", self.real_time_progress)

    def voice_to_text(self,fp_input, fn, sr_input=16000):

        """Voice to text parsing conversion - looks up and calls the Model and gets inference response. """

        from llmware.models import ModelCatalog

        self.speech_model = ModelCatalog().load_model(self.selected_speech_model_name)

        inference_dict = {"remove_segment_markers": self.remove_segment_markers}

        response = self.speech_model.inference(os.path.join(fp_input,fn),inference_dict=inference_dict)

        #   response dictionary has several keys - "llm_response" | "segments" | "usage"

        #   still exploring the best way to release memory once processing completed
        self.speech_model.__dealloc__()
        del self.speech_model
        self.speech_model = None

        return response

    def add_voice_file(self, input_fp, fn):

        """ Parse voice file. """

        output = []

        #   16000 is standard default encoding rate for .wav -> may need further test/experiment
        response = self.voice_to_text(input_fp, fn, 16000)

        if not self.chunk_by_segment:

            # this is initial strategy- deprecating for chunk_by_segment
            text_out = response["text"]
            # will chop up the long text into individual blocks
            text_chunks = TextChunker(text_chunk=text_out,
                                      max_char_size=self.text_chunk_size,
                                      look_back_char_range=self.look_back_range).convert_text_to_chunks()

            for i, chunk in enumerate(text_chunks):

                new_entry = {"text": chunk, "start_time": 0, "end_time": 0, "speaker": "", "index": i,
                             "start_segment": 0, "end_segment": 0, "type": "text_only"}

                output.append(new_entry)
        else:
            # aggregate by segment within size parameters
            if "segments" not in response:
                logger.warning("VoiceParser - no 'segments' found in response from WhisperCPP.")
                return []

            char_counter = 0
            time_start = 0.0
            start_segment = 0
            t = ""

            for i, segment in enumerate(response["segments"]):

                current_segment_len = len(segment["text"])

                if (char_counter + current_segment_len) >= self.chunk_size:

                    # add to output list

                    t += " " + segment["text"]
                    new_entry = {"text": t, "start_time": time_start, "end_time": segment["end"],
                                 "speaker": "", "index": i, "start_segment": start_segment, "end_segment": i,
                                 "type": "segments"}
                    output.append(new_entry)
                    t = ""
                    char_counter = 0
                    time_start = segment["end"]
                    start_segment = i+1
                else:
                    if len(t) > 0 and ord(t[-1]) != 32:
                        t += " " + segment["text"]
                    else:
                        t += segment["text"]

                    char_counter = len(t)

            # pick up last block of text
            if len(t) > 0:
                last_segment = response["segments"][-1]
                new_entry = {"text": t, "start_time": time_start, "end_time": last_segment["end"],
                             "speaker": "", "index": len(response["segments"]), "start_segment": start_segment,
                             "end_segment": len(response["segments"]), "type": "segments"}
                output.append(new_entry)

        return output


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

    def jsonl_file_handler (self, dir_fp,sample_file, key_list=None, interpret_as_table=False,separator="\n"):

        """ Parse JSON or JSONL file. """

        # will extract each line in jsonl as separate sample
        #   --based on key_list and interpret_as_table

        output = []
        my_file = []

        ft = sample_file.split(".")[-1].lower()

        if ft not in ["json", "jsonl"]:
            logger.warning(f"TextParser - jsonl_file_parser did not find a recognized json/jsonl file type - "
                           f"{sample_file}")
            return output

        if ft == "json":
            my_file = json.load(open(os.path.join(dir_fp, sample_file), "r"))

        if ft == "jsonl":
            file = open(os.path.join(dir_fp,sample_file), 'r', encoding='utf-8-sig',errors='ignore')

            output = []
            for i, lines in enumerate(file):
                row_tmp = json.loads(lines)
                my_file.append(row_tmp)

            file.close()

        if not key_list:
            # as default, if no key_list, then look for "text" attribute in jsonl by default
            key_list = ["text"]

        for i, lines in enumerate(my_file):

            row_tmp = lines

            if not interpret_as_table:
                row_text = ""
                for keys in key_list:
                    if keys in row_tmp:
                        row_text += str(row_tmp[keys]) + separator
                output.append(row_text)

            else:
                row_table = []
                for keys in key_list:
                    if keys in row_tmp:
                        row_table.append(str(row_tmp[keys]))
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

    def csv_file_handler (self, dir_fp,sample_file, interpret_as_table=True, delimiter=",",
                          encoding='utf-8-sig',errors='ignore', batch_size=1, separator="\t"):

        """ Parse .csv or .tsv file - depending upon separator, e.g., ',' or '\t' """

        ft = sample_file.split(".")[-1].lower()
        if ft == "tsv":
            delimiter = "\t"

        # will split the table by rows and columns (\n for rows and ',' for cells in row)
        t = Utilities.file_load(os.path.join(dir_fp,sample_file),
                                delimiter=delimiter, encoding=encoding, errors=errors)

        tables_out= []

        if len(t) < batch_size:
            tables_out = [t]
        else:
            table_chunks = len(t) // batch_size

            if batch_size > table_chunks * len(t):
                # there is a remainder, so create one additional partial chunk with last set of rows
                table_chunks += 1

            starter = 0
            increment = 0

            for x in range(0,table_chunks):
                starter = starter + increment
                increment = min(len(t)-starter, batch_size)
                stopper = starter + increment

                if interpret_as_table:
                    tmp= t[starter:stopper]
                else:
                    tmp = ""
                    for x in range(starter, stopper):
                        for y in range(0,len(t[x])):
                            tmp += str(t[x][y]) + separator
                        tmp = tmp[:-len(separator)]
                        tmp += "\n"

                tables_out.append(tmp)

        return tables_out


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
            logger.error("DialogParser currently only supports AWS Transcribe dialog format - For more "
                         "information, please see Amazon Web Services Transcription - "
                         "https://docs.aws.amazon.com/transcribe/latest/dg/how-input.html#how-it-works-output")

            return block_output

        # end - quick format check

        # speaker label conversation snippets
        conversation_snippets = f["results"]["items"]

        if len(conversation_snippets) == 0:
            # no results to parse
            logger.error("DialogParser - unexpected parsing error - AWS JSON dialog transcript empty")
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

