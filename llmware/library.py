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

"""The library module implements the logic for managing unstructured information (the text).

The module implements the two classes Library and LibraryCatalog. Library is responsible for organizing a
collection of text and is the interface for the Parser and Embedding classes. In addition, the Library object
is passed to the Query and Prompt objects. The Library class uses the LibraryCatalog for creating, deleting,
updating, and other tasks pertaining to Libraries via the Library Card.
"""

import shutil
import os
import json
import logging

from llmware.configs import LLMWareConfig, LLMWareTableSchema
from llmware.util import Utilities
from llmware.graph import Graph
from llmware.parsers import Parser
from llmware.models import ModelCatalog
from llmware.resources import CollectionRetrieval, CollectionWriter, CloudBucketManager
from llmware.embeddings import EmbeddingHandler
from llmware.exceptions import LibraryNotFoundException, ImportingSentenceTransformerRequiresModelNameException, \
    UnsupportedEmbeddingDatabaseException, InvalidNameException

logger = logging.getLogger(__name__)


class Library:

    """Implements the interface to manage a collection of unstructured information as a ``Library``, i.e. a
    library is an indexed collection of texts, tables and images extracted from parsed files.

    Returns
    -------
    library : Library
        A new ``Library`` object.
    """

    def __init__(self):

        # default settings for basic parameters
        self.account_name = None
        self.library_name = None

        # base file paths in each library
        self.library_main_path = None

        # each of these paths hang off library_main_path
        self.file_copy_path = None
        self.image_path = None
        self.dataset_path = None
        self.nlp_path = None
        self.output_path = None
        self.tmp_path = None
        self.embedding_path = None

        # default key structure of block -> re-order for nicer display
        self.default_keys = ["block_ID", "doc_ID", "content_type", "file_type","master_index","master_index2",
                             "coords_x", "coords_y", "coords_cx", "coords_cy", "author_or_speaker", "modified_date",
                             "created_date", "creator_tool", "added_to_collection", "file_source",
                             # changing to 'table_block' and 'text_block'
                             "table_block", "external_files", "text_block", "header_text", "text_search",
                             "user_tags", "special_field1", "special_field2", "special_field3","graph_status","dialog",
                             "embedding_flags"]

        self.library_block_schema = LLMWareTableSchema().get_block_schema()

        # default library card elements
        self.default_library_card = ["library_name", "embedding_status", "embedding_model", "embedding_db",
                                     "embedded_blocks", "embedding_dims", "time_stamp",
                                     "knowledge_graph", "unique_doc_id", "documents", "blocks", "images", "pages",
                                     "tables"]

        self.block_size_target_characters = 400

        # attributes used in parsing workflow
        self.doc_ID = 0
        self.block_ID = 0

        # check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):

            # if not explicitly set up by user, then create folder directory structure
            LLMWareConfig.setup_llmware_workspace()

        # add checks for /tmp and /accounts in place
        library_path = LLMWareConfig.get_library_path()
        tmp_path = LLMWareConfig.get_tmp_path()

        if not os.path.exists(library_path):
            os.mkdir(library_path)
            os.chmod(library_path, 0o777)

        if not os.path.exists(tmp_path):
            os.mkdir(tmp_path)
            os.chmod(tmp_path, 0o777)

    # explicit constructor to create a new library
    def create_new_library(self, library_name, account_name="llmware"):
        """Explicit constructor to create a new library with selected name.

            If a library with the same name already exists, it will load the existing library.

            Checks if library_name is safe. If not, it will change library_name to a safe name. 

            Parameters
            ----------
            library_name : str
                name of the library to create

            account_name : str, default="llmware"
                name of the account associated with the library

            Returns
            -------
            library : Library
                A new ``Library`` object representing the newly created or loaded existing library
        """

        # note: default behavior - if library with same name already exists, then it loads existing library

        self.library_name = library_name
        self.account_name = account_name

        # apply safety check to library_name path
        library_name = Utilities().secure_filename(library_name)

        library_exists = self.check_if_library_exists(library_name,account_name)

        if library_exists:
            # do not create
            logger.info(f"update: library already exists - returning library - {library_name} - {account_name}")

            return self.load_library(library_name, account_name)

        # assign self.library_name to the 'safe' library_name
        self.library_name = library_name

        # allow 'dynamic' creation of a new account path
        account_path = os.path.join(LLMWareConfig.get_library_path(), account_name)
        if not os.path.exists(account_path):
            os.makedirs(account_path,exist_ok=True)

        # safety check for name based on db
        safe_name = CollectionRetrieval(library_name,account_name=self.account_name).safe_name(library_name)

        if safe_name != library_name:

            logger.warning(f"warning: selected library name is being changed for safety on selected resource - "
                           f"{safe_name}")

            if isinstance(safe_name,str):
                library_name = safe_name
                self.library_name = safe_name

            else:
                raise InvalidNameException(library_name)

        self.library_main_path = os.path.join(LLMWareConfig.get_library_path(), account_name, library_name)

        # add new file dir for this collection
        self.file_copy_path = os.path.join(self.library_main_path,"uploads" + os.sep )
        self.image_path = os.path.join(self.library_main_path, "images" + os.sep)
        self.dataset_path = os.path.join(self.library_main_path, "datasets" + os.sep)
        self.nlp_path = os.path.join(self.library_main_path, "nlp" + os.sep)
        self.output_path = os.path.join(self.library_main_path, "output" + os.sep)
        self.tmp_path = os.path.join(self.library_main_path, "tmp" + os.sep)
        self.embedding_path = os.path.join(self.library_main_path, "embedding" + os.sep)

        library_folder = os.path.exists(self.library_main_path)

        # this is a new library to create -> build file paths for work products
        if not library_folder:
            os.mkdir(self.library_main_path)
            os.mkdir(self.file_copy_path)
            os.mkdir(self.image_path)
            os.mkdir(self.dataset_path)
            os.mkdir(self.nlp_path)
            os.mkdir(self.output_path)
            os.mkdir(self.tmp_path)
            os.mkdir(self.embedding_path)
            os.chmod(self.dataset_path, 0o777)
            os.chmod(self.nlp_path, 0o777)
            os.chmod(self.output_path, 0o777)
            os.chmod(self.tmp_path, 0o777)
            os.chmod(self.embedding_path, 0o777)

        new_library_entry = {"library_name": self.library_name,

                             #  track embedding status - each embedding tracked as new dict in list
                             #  --by default, when library created, no embedding in place

                             "embedding": [{"embedding_status": "no", "embedding_model": "none", "embedding_db": "none",
                                            "embedded_blocks":0, "embedding_dims":0, "time_stamp": "NA"}],

                             # knowledge graph
                             "knowledge_graph": "no",

                             # doc trackers
                             "unique_doc_id": 0, "documents": 0, "blocks": 0, "images": 0, "pages": 0, "tables": 0,

                             # options to create and set different accounts
                             "account_name": self.account_name
                             }

        # LibraryCatalog will register the new library card
        new_library_card = LibraryCatalog(self).create_new_library_card(new_library_entry)

        if CollectionWriter(self.library_name,account_name=self.account_name).check_if_table_build_required():

            CollectionWriter(self.library_name,account_name=self.account_name).create_table(self.library_name,
                                                                                            self.library_block_schema)

        # update collection text index in collection after adding documents
        CollectionWriter(self.library_name,account_name=self.account_name).build_text_index()

        return self

    def load_library(self, library_name, account_name="llmware"):
        """Load an existing library by invoking the library string name.

            Parameters
            ----------
            library_name : str
                Name of the library to load

            account_name : str, default="llmware"
                Name of the account associated with the library
        
            Returns
            -------
            library : Library
                A new ``Library`` object representing the loaded library
        """

        # first check that library exists
        library_exists = self.check_if_library_exists(library_name, account_name=account_name)

        if not library_exists:
            logger.error(f"error: library/account not found - {library_name} - {account_name}")
            raise LibraryNotFoundException(library_name, account_name)

        self.library_name = library_name
        self.account_name = account_name
        self.library_main_path = os.path.join(LLMWareConfig.get_library_path(), account_name, library_name)

        # add new file dir for this collection
        self.file_copy_path = os.path.join(self.library_main_path, "uploads" + os.sep)
        self.image_path = os.path.join(self.library_main_path, "images" + os.sep)
        self.dataset_path = os.path.join(self.library_main_path, "datasets" + os.sep)
        self.nlp_path = os.path.join(self.library_main_path, "nlp" + os.sep)
        self.output_path = os.path.join(self.library_main_path, "output" + os.sep)
        self.tmp_path = os.path.join(self.library_main_path, "tmp" + os.sep)
        self.embedding_path = os.path.join(self.library_main_path, "embedding" + os.sep)

        os.makedirs(self.library_main_path, exist_ok=True)
        os.makedirs(self.file_copy_path,exist_ok=True)
        os.makedirs(self.image_path,exist_ok=True)
        os.makedirs(self.dataset_path,exist_ok=True)
        os.makedirs(self.nlp_path,exist_ok=True)
        os.makedirs(self.output_path,exist_ok=True)
        os.makedirs(self.tmp_path,exist_ok=True)
        os.makedirs(self.embedding_path,exist_ok=True)

        return self

    def get_library_card(self, library_name=None, account_name="llmware"):
        """Retrieves the library card dictionary with key attributes of library.

            Parameters
            ----------
            library_name : str, default=None
                Name of the library to retrieve. If not provided, uses self.library_name

            account_name : str, default="llmware"
                Name of the account associated to the library. If not provided, uses self.account_name
        
            Returns
            -------
            library_card : dict or None
                The library card dictionary containing key atrributes of the library. If not found, returns None
        """

        library_card = None

        if library_name:
            lib_lookup_name = library_name
            acct_lookup_name = account_name
        else:
            lib_lookup_name = self.library_name
            acct_lookup_name = self.account_name

        if lib_lookup_name and acct_lookup_name:
            library_card= LibraryCatalog().get_library_card(lib_lookup_name, account_name=acct_lookup_name)

        if not library_card:
            logger.warning(f"warning:  error retrieving library card - not found - {library_name} - {account_name}")

        return library_card

    def check_if_library_exists(self, library_name, account_name="llmware"):
        """Check if library exists by library string name.
        
            Parameters
            ----------
            library_name : str
                Name of library to check.

            account_name : str, default="llmware"
                Name of account associated with library.

            Returns
            -------
            library_card : dict or None
                The library card dict if the library exists. If not found, returns None.

        """

        # first look in library catalog
        library_card = LibraryCatalog().get_library_card(library_name, account_name=account_name)

        # check file path
        lib_path = os.path.join(LLMWareConfig.get_library_path(), account_name, library_name)
        library_folder = os.path.exists(lib_path)

        # if all checks consistent
        if library_card and library_folder:
            # library exists and is in good state
            return library_card

        if not library_card and not library_folder:
            # library does not exist conclusively
            return None

        # may be error state - some artifacts exist and others do not
        if library_card:
            # view the library_card as the definitive record
            return library_card

        return library_card

    def update_embedding_status (self, status_message, embedding_model, embedding_db,
                                 embedded_blocks=0, embedding_dims=0,time_stamp="NA",delete_record=False):
        """Invoked at the end of the embedding job to update the library card and embedding record -- generally,
        this method does not need to be invoked directly.
        
            Parameters
            ----------
            status_message : str
                Status message for the embedding process. If "delete", the record will be marked for deletion.

            embedding_model : str
                Name of the embedding model used.

            embedding_db : str
                Name of the embedding database used.

            embedded_blocks : int, default=0
                Number of embedded blocks.

            embedding_dims : int, default=0
                Dimensions of the embedding.

            time_stamp : str, default="NA"
                Timestamp of the embedding process.

            delete_record : bool, default=False
                If True, marks the record for deletion.

            Returns
            -------
            bool
                True if the embedding status was successfully updated.
        """

        #   special handling for updating "embedding" in update_library_card
        #   -- append/insert this new embedding dict to the end of the embedding list

        if status_message == "delete":
            delete_record = True

        update_dict = {"embedding": {"embedding_status": status_message,
                                     "embedding_model": embedding_model,
                                     "embedding_db": embedding_db,
                                     "embedding_dims": embedding_dims,
                                     "embedded_blocks": embedded_blocks,
                                     "time_stamp": time_stamp}}

        updater = LibraryCatalog(self).update_library_card(self.library_name, update_dict,
                                                           delete_record=delete_record, account_name=self.account_name)

        return True

    def get_embedding_status (self):
        """Pulls the embedding record for the current library from the library card.
        
            Returns
            -------
            embedding_record : list or None
                The embedding record, which is a list of dictionaries containing embedding status, model, and database.
                If the library card or embedding record is not found, returns None.
        """

        library_card = LibraryCatalog(self).get_library_card(self.library_name, account_name=self.account_name)

        if not library_card:

            logger.error(f"error: library/account not found - {self.library_name} - {self.account_name}")
            raise LibraryNotFoundException(self.library_name, self.account_name)

        # embedding record will be a list of {"embedding_status" | "embedding_model" | "embedding_db"}
        logger.info(f"update: library_card - {library_card}")

        if "embedding" in library_card:
            embedding_record = library_card["embedding"]
        else:
            logger.warning(f"warning: could not identify embedding record in library card - {library_card}")
            embedding_record = None

        return embedding_record

    def get_knowledge_graph_status (self):
        """Gets the status of creating the knowledge graph for the current library from the library card.
        
            Returns
            -------
            status_message : str
                The status of the knowledge graph creation for the current library.
        """

        library_card = LibraryCatalog(self).get_library_card(self.library_name, self.account_name)

        if not library_card:
            logger.error(f"error: library/account not found - {self.library_name} - {self.account_name}")
            raise LibraryNotFoundException(self.library_name, self.account_name)

        status_message = library_card["knowledge_graph"]

        return status_message

    def set_knowledge_graph_status (self, status_message):
        """Updates the knowledge graph status on the library card after creating a knowledge graph.
        
            Parameters
            ----------
            status_message : str
                The status message to set for the knowledge graph.

            Returns
            -------
            bool
                True if the knowledge graph status was successfully updated.
        """

        update_dict = {"knowledge_graph": status_message}
        updater = LibraryCatalog(self).update_library_card(self.library_name,update_dict, account_name=self.account_name)

        return True

    def get_and_increment_doc_id(self):
        """Convenience method in library class - mirrors method in LibraryCatalog - increments, tracks and provides a
        unique doc id for the library.
        
            Returns
            -------
            unique_doc_id : int
                The new unique document ID for the library.
        """

        unique_doc_id = LibraryCatalog(self).get_and_increment_doc_id(self.library_name)
        return unique_doc_id

    def set_incremental_docs_blocks_images(self, added_docs=0, added_blocks=0, added_images=0, added_pages=0,
                                           added_tables=0):
        """Updates the library card with incremental counters after completing a parsing job.
        
            Parameters
            ----------
            added_docs : int, default=0
                Number of documents added.

            added_blocks : int, default=0
                Number of blocks added.

            added_images : int, default=0
                Number of images added.

            added_pages : int, default=0
                Number of pages added.

            added_tables : int, default=0
                Number of tables added.

            Returns
            -------
            bool
                True if the incremental counters were successfully updated.
        """

        # updates counting parameters at end of parsing
        updater = LibraryCatalog(self).set_incremental_docs_blocks_images(added_docs=added_docs,
                                                                          added_blocks=added_blocks,
                                                                          added_images=added_images,
                                                                          added_pages=added_pages,
                                                                          added_tables=added_tables)

        return True

    def add_file(self, file_path):
        """Ingests, parses, text chunks and indexes a single selected file to a library -
        provide the full path to file.
        
            Parameters
            ----------
            file_path : str
                The full path to the file to be ingested and indexed.

            Returns
            -------
            self : Library
                The updated ``Library`` object after adding the file.
        """

        # Ensure the input path exists
        os.makedirs(LLMWareConfig.get_input_path(), exist_ok=True)
        
        file_name = os.path.basename(file_path)
        target_path = os.path.join(LLMWareConfig.get_input_path(), file_name)

        shutil.copyfile(file_path,target_path)
        return self.add_files()

    def add_files (self, input_folder_path=None, encoding="utf-8",chunk_size=400,
                   get_images=True,get_tables=True, smart_chunking=1, max_chunk_size=600,
                   table_grid=True, get_header_text=True, table_strategy=1, strip_header=False,
                   verbose_level=2, copy_files_to_library=True, set_custom_logging=-1,
                   use_logging_file=False):

        """Main method to integrate documents into a Library - pass a local filepath folder and all files will be
        routed to appropriate parser by file type extension.
        
            Parameters
            ----------
            input_folder_path : str, default=None
                The path to the folder containing files to be ingested. If not provided, defaults to None.

            encoding : str, default="utf-8"
                The encoding to use for reading files.

            chunk_size : int, default=400
                The size of text chunks to create during parsing.

            get_images : bool, default=True
                Whether to extract images from the documents.

            get_tables : bool, default=True
                Whether to extract tables from the documents.

            smart_chunking : int, default=1
                The strategy for smart chunking of text.

            max_chunk_size : int, default=600
                The maximum size of text chunks.

            table_grid : bool, default=True
                Whether to use a grid for tables.

            get_header_text : bool, default=True
                Whether to extract header text from the documents.

            table_strategy : int, default=1
                The strategy to use for table extraction.

            strip_header : bool, default=False
                Whether to strip headers from the documents.

            verbose_level : int, default=2
                The level of verbosity for logging.

            copy_files_to_library : bool, default=True
                Whether to copy the files to the library.

            set_custom_logging : int, default=-1, will apply a custom logging level between 0-50 for the
                parsing job.

            use_logging_file : bool, default=False
                Whether parse should log to stdout (default) or to file (set to True)

            Returns
            -------
            output_results : dict or None
                A dictionary containing the results of the document integration process, including counts of added documents,
                blocks, images, pages, tables, and rejected files. If the library card could not be identified, returns None.
                """

        if not input_folder_path:
            input_folder_path = LLMWareConfig.get_input_path()

        # get overall counters at start of process
        lib_counters_before = self.get_library_card()

        parsing_results = Parser(library=self,
                                 encoding=encoding,
                                 chunk_size=chunk_size,
                                 max_chunk_size=max_chunk_size,
                                 smart_chunking=smart_chunking,
                                 get_tables=get_tables,
                                 get_images=get_images,
                                 get_header_text=get_header_text,
                                 table_strategy=table_strategy,
                                 strip_header=strip_header,
                                 table_grid=table_grid,
                                 verbose_level=verbose_level,
                                 copy_files_to_library=copy_files_to_library,
                                 set_custom_logging=set_custom_logging,
                                 use_logging_file=use_logging_file).ingest(input_folder_path,dupe_check=True)

        logger.debug(f"update: parsing results - {parsing_results}")

        # post-processing:  get the updated lib_counters
        lib_counters_after = self.get_library_card()

        # parsing_results = {"processed_files" | "rejected_files" | "duplicate_files"}
        output_results = None

        if lib_counters_after and lib_counters_before:
            output_results = {"docs_added": lib_counters_after["documents"] - lib_counters_before["documents"],
                              "blocks_added": lib_counters_after["blocks"] - lib_counters_before["blocks"],
                              "images_added": lib_counters_after["images"] - lib_counters_before["images"],
                              "pages_added": lib_counters_after["pages"] - lib_counters_before["pages"],
                              "tables_added": lib_counters_after["tables"] - lib_counters_before["tables"],
                              "rejected_files": parsing_results["rejected_files"]}
        else:
            logger.error("error: unexpected - could not identify the library_card correctly")

        logger.info(f"update: output_results - {output_results}")

        # update collection text index in collection after adding documents
        # LibraryCollection(self).create_index()
        CollectionWriter(self.library_name,account_name=self.account_name).build_text_index()

        return output_results

    def export_library_to_txt_file(self, output_fp=None, output_fn=None, include_text=True, include_tables=True,
                                   include_images=False):
        """Exports library collection of indexed text chunks to a txt file.
        
            Parameters
            ----------
            output_fp : str, default=None
                The file path where the output file will be saved. If not provided, defaults to None.

            output_fn : str, default=None
                The name of the output file. If not provided, defaults to None.

            include_text : bool, default=True
                Whether to include text content in the export.

            include_tables : bool, default=True
                Whether to include tables in the export.

            include_images : bool, default=False
                Whether to include images in the export.

            Returns
            -------
            file_location : str
                The location of the exported txt file.
        """

        if not output_fp:
            output_fp = self.output_path

        if not output_fn:
            output_fn = self.library_name + "_" + str(Utilities().get_current_time_now())

        filter_list = []
        if include_text: filter_list.append("text")
        if include_tables: filter_list.append("table")
        if include_images: filter_list.append("image")

        if not filter_list:
            # go with default - text only
            filter_list = ["text"]

        results = CollectionRetrieval(self.library_name,
                                      account_name=self.account_name).filter_by_key_value_range("content_type",filter_list)

        file_location = os.path.join(output_fp, output_fn + ".txt")
        output_file = open(file_location, "w", encoding='utf-8')
        text_field = "text_search"
        for elements in results:
            new_entry = elements[text_field].strip() + "\n"
            output_file.write(new_entry)

        output_file.close()

        return file_location

    def export_library_to_jsonl_file(self, output_fp, output_fn, include_text=True, include_tables=True,
                                     include_images=False, dict_keys=None):
        """Exports collection of text chunks to a jsonl file.
        
            Parameters
            ----------
            output_fp : str
                The file path where the output file will be saved.

            output_fn : str
                The name of the output file.

            include_text : bool, default=True
                Whether to include text content in the export.

            include_tables : bool, default=True
                Whether to include tables in the export.

            include_images : bool, default=False
                Whether to include images in the export.

            dict_keys : list of str, default=None
                The keys to include in the JSONL entries. If not provided, defaults to None.

            Returns
            -------
            file_location : str
                The location of the exported JSONL file.
        """

        if not output_fp:
            output_fp = self.output_path

        if not output_fn:
            output_fn = self.library_name + "_" + str(Utilities().get_current_time_now())

        # expects dict_keys to be a list of dictionary keys
        if not dict_keys:
            dict_keys = self.default_keys

        filter_list = []
        if include_text: filter_list.append("text")
        if include_tables: filter_list.append("table")
        if include_images: filter_list.append("image")

        if not filter_list:
            # go with default - text only
            filter_list = ["text"]

        results = CollectionRetrieval(self.library_name,
                                      account_name=self.account_name).filter_by_key_value_range("content_type", filter_list)

        file_location = os.path.join(output_fp, output_fn + ".jsonl")
        output_file = open(file_location, "w", encoding='utf-8')

        for elements in results:

            # package up each jsonl entry as dict with selected keys to extract
            new_dict_entry = {}
            for keys in dict_keys:
                if keys in elements:
                    new_dict_entry.update({keys:elements[keys]})

            if new_dict_entry:
                jsonl_row = json.dumps(new_dict_entry)
                output_file.write(jsonl_row)
                output_file.write("\n")

        output_file.close()

        return file_location

    def pull_files_from_cloud_bucket (self, aws_access_key=None, aws_secret_key=None, bucket_name=None):
        """Pull files from private S3 bucket into local cache for further processing.
        
            Parameters
            ----------
            aws_access_key : str, default=None
                The AWS access key for connecting to the S3 bucket.

            aws_secret_key : str, default=None
                The AWS secret key for connecting to the S3 bucket.

            bucket_name : str, default=None
                The name of the S3 bucket from which to pull files.

            Returns
            -------
            files_copied : list
                A list of file paths that were copied from the S3 bucket to the local cache.
        """

        files_copied = CloudBucketManager().connect_to_user_s3_bucket (aws_access_key, aws_secret_key,
                                                                       bucket_name, LLMWareConfig.get_input_path())

        return files_copied

    def generate_knowledge_graph(self):
        """Builds a statistical co-occurrence matrix for a library.
        
            Returns
            -------
            int
                Returns 0 after successfully generating the knowledge graph and updating the status.
        """

        kg = Graph(library=self).build_graph()
        self.set_knowledge_graph_status("yes")

        return 0

    def install_new_embedding (self, embedding_model_name=None, vector_db=None,
                               from_hf= False, from_sentence_transformer=False, model=None, tokenizer=None, model_api_key=None,
                               vector_db_api_key=None, batch_size=500, max_len=None, use_gpu=True):
        """Main method for installing a new embedding on a library.
        
            Parameters
            ----------
            embedding_model_name : str, default=None
                The name of the embedding model to use.

            vector_db : str, default=None
                The name of the vector database to use.

            from_hf : bool, default=False
                Whether the model is from Hugging Face.

            from_sentence_transformer : bool, default=False
                Whether the model is a Sentence Transformer.

            model : object, default=None
                The pre-loaded model to use.

            tokenizer : object, default=None
                The tokenizer associated with the pre-loaded model.

            model_api_key : str, default=None
                The API key for accessing the model.

            vector_db_api_key : str, default=None
                The API key for accessing the vector database.

            batch_size : int, default=500
                The batch size to use for embedding.

            max_len : int, default=None
                The maximum length for embedding.

            use_gpu : bool, default=True
                Whether to use GPU for embedding.

            Returns
            -------
            embeddings : dict or None
                The created embeddings dict, or None if no embeddings could be created.
        """

        embeddings = None
        my_model = None

        # step 1 - load selected model from ModelCatalog - will pass 'loaded' model to the EmbeddingHandler

        # check if instantiated model and tokenizer -> load as HuggingFace model
        if model:
            if from_hf:
                logger.info("update: loading hf model")
                my_model = ModelCatalog().load_hf_embedding_model(model, tokenizer)
                batch_size = 50

            if from_sentence_transformer:
                logger.info("update: loading sentence transformer model")
                if not embedding_model_name:
                    raise ImportingSentenceTransformerRequiresModelNameException

                my_model = ModelCatalog().load_sentence_transformer_model(model,embedding_model_name)
        else:
            # if no model explicitly passed, then look up in the model catalog
            if embedding_model_name:
                my_model = ModelCatalog().load_model(selected_model=embedding_model_name, api_key=model_api_key)

        if not my_model:
            logger.error("error: install_new_embedding - can not identify a selected model")
            return -1

        # new - insert - handle no vector_db passed
        if not vector_db:
            vector_db = LLMWareConfig().get_config("vector_db")
        # end - new insert

        if vector_db not in LLMWareConfig().get_supported_vector_db():
            raise UnsupportedEmbeddingDatabaseException(vector_db)

        if my_model and max_len:
            my_model.max_len = max_len

        # step 2 - pass loaded embedding model to EmbeddingHandler, which will route to the appropriate resource
        embeddings = EmbeddingHandler(self).create_new_embedding(vector_db, my_model, batch_size=batch_size)

        if not embeddings:
            logger.warning("warning: no embeddings created")

        return embeddings

    def delete_library(self, library_name=None, confirm_delete=False, account_name="llmware"):

        """ Deletes all artifacts of a library 
        
            Parameters
            ----------
            library_name : str, default=None
                The name of the library to delete. If not provided, defaults to None.

            confirm_delete : bool, default=False
                Confirmation flag to proceed with deletion. Must be set to True to delete the library.

            Returns
            -------
            success_code : int
                Returns 1 if the deletion was successful, or -1 if an error occurred.
        
        """

        if library_name:
            self.library_name = library_name

            #   loads the library specific path information if required
            self.load_library(library_name,account_name=account_name)

        success_code = 1

        try:
            if confirm_delete:

                # 1st - remove the blocks - drop the collection in database
                CollectionWriter(self.library_name, account_name=self.account_name).destroy_collection(confirm_destroy=True)

                # 2nd - Eliminate the local file structure
                file_path = self.library_main_path
                shutil.rmtree(file_path)

                # 3rd - remove record in LibraryCatalog
                LibraryCatalog(self).delete_library_card(self.library_name)

                logger.info("update:  deleted all library file artifacts + folders")

        except:
            logger.exception("Error destroying library")
            success_code = -1

        return success_code

    def update_block (self, doc_id, block_id, key, new_value):
        """Convenience method to update the record of a specific block - identified by doc_ID and block_ID
        in text collection database.
        
            Parameters
            ----------
            doc_id : int
                The ID of the document containing the block to update.

            block_id : int
                The ID of the block to update.

            key : str
                The key in the block record to update.

            new_value : str
                The new value to set for the specified key.

            Returns
            -------
            completed : bool
                True if the block was successfully updated, False otherwise.
        """

        completed = (CollectionWriter(self.library_name, account_name=self.account_name).
                     update_block(doc_id, block_id,key,new_value,self.default_keys))

        return completed

    def add_website (self, url, get_links=True, max_links=5):
        """Main method to ingest a website into a library.
        
            Parameters
            ----------
            url : str
                The URL of the website to ingest.

            get_links : bool, default=True
                Whether to follow and ingest links found on the website.

            max_links : int, default=5
                The maximum number of links to follow and ingest.

            Returns
            -------
            self : Library
                The updated ``Library`` object after ingesting the website.
        """

        Parser(library=self).parse_website(url,get_links=get_links,max_links=max_links)
        CollectionWriter(self.library_name, account_name=self.account_name).build_text_index()

        return self

    def add_wiki(self, topic_list,target_results=10):
        """Main method to add a wikipedia article to a library - enter a list of topics.
        
            Parameters
            ----------
            topic_list : list of str
                A list of topics to search for on Wikipedia.

            target_results : int, default=10
                The target number of results to retrieve for each topic.

            Returns
            -------
            self : Library
                The updated ``Library`` object after adding the Wikipedia articles.
        """

        Parser(library=self).parse_wiki(topic_list,target_results=target_results)
        CollectionWriter(self.library_name, account_name=self.account_name).build_text_index()

        return self

    def add_dialogs(self, input_folder=None):
        """Main method to add an AWS dialog transcript into a library.
        
            Parameters
            ----------
            input_folder : str, default=None
                The path to the folder containing the dialog transcripts. If not provided, defaults to None.

            Returns
            -------
            self : Library
                The updated ``Library`` object after adding the dialog transcripts.
        """

        if not input_folder:
            input_folder = LLMWareConfig.get_input_path()

        output = Parser(library=self).parse_dialog(input_folder)

        return self

    def add_image(self, input_folder=None):
        """Main method to add image and scanned OCR content into a library.
        
            Parameters
            ----------
            input_folder : str, default=None
                The path to the folder containing the images. If not provided, defaults to None

            Returns
            -------
            self : Library
                The updated ``Library`` object after adding the image and OCR content.
        """

        if not input_folder:
            input_folder = LLMWareConfig.get_input_path()

        output = Parser(library=self).parse_image(input_folder)

        return self

    def add_pdf_by_ocr(self, input_folder=None):
        """Alternative method to ingest PDFs that are scanned, or can not be otherwise parsed.
        
            Parameters
            ----------
            input_folder : str, default=None
                The path to the folder containing the PDFs. If not provided, defaults to None

            Returns
            -------
            self : Library
                The updated ``Library`` object after adding the PDFs through OCR.
        """

        if not input_folder:
            input_folder = LLMWareConfig.get_input_path()

        output = Parser(library=self).parse_pdf_by_ocr_images(input_folder)

        return self

    def add_pdf(self, input_folder=None):
        """Convenience method to directly add PDFs only - note, in most cases, 'add_files' is the better option.
        
            Parameters
            ----------
            input_folder : str, default=None
                The path to the folder containing the PDFs. If not provided, defaults to None

            Returns
            -------
            self : Library
                The updated ``Library`` object after adding the PDFs.
        """

        if not input_folder:
            input_folder = LLMWareConfig.get_input_path()

        output = Parser(library=self).parse_pdf(input_folder)

        return self

    def add_office(self, input_folder=None):
        """Convenience method to directly add PDFs only -  note, in most cases, 'add_files' is the better option.
        
            Parameters
            ----------
            input_folder : str, default=None
                The path to the folder containing the Office documents. If not provided, defaults to None.

            Returns
            -------
            self : Library
                The updated ``Library`` object after adding the Office documents.
        """

        if not input_folder:
            input_folder = LLMWareConfig.get_input_path()

        output = Parser(library=self).parse_office(input_folder)

        return self

    def get_all_library_cards(self, account_name='llmware'):
        """Get all library cards for all libraries on account.
        
            Parameters
            ----------
            account_name : str, default='llmware'
                The name of the account for which to retrieve all library cards.

            Returns
            -------
            library_cards : list of dict
                A list of all library card dictionaries for the specified account.
        """

        library_cards = LibraryCatalog(account_name=account_name).all_library_cards()
        return library_cards

    def delete_installed_embedding(self, embedding_model_name, vector_db, vector_db_api_key=None):
        """Deletes an installed embedding on specific combination of vector_db + embedding_model_name.
        
            Parameters
            ----------
            embedding_model_name : str
                The name of the embedding model to delete.

            vector_db : str
                The name of the vector database from which to delete the embedding.

            vector_db_api_key : str, default=None
                The API key for accessing the vector database. If not provided, defaults to None

            Returns
            -------
            int
                Returns 1 if the embedding was successfully deleted.
        """

        # insert safety check - confirm that this is valid combination with installed embedding
        lib_card = LibraryCatalog(self).get_library_card(self.library_name)
        embedding_list = lib_card["embedding"]
        found_match = False
        embedding_dims = 0

        for entries in embedding_list:
            if entries["embedding_model"] == embedding_model_name and entries["embedding_db"] == vector_db:
                found_match = True
                embedding_dims = entries["embedding_dims"]

                logger.info(f"update: library - delete_installed_embedding request - found matching"
                            f"embedding record - {entries}")
                break

        if found_match:
            EmbeddingHandler(self).delete_index(vector_db,embedding_model_name, embedding_dims)
        else:
            # update exception
            raise LibraryNotFoundException(embedding_model_name, vector_db)

        return 1

    def run_ocr_on_images(self, add_to_library=False,chunk_size=400,min_size=10, realtime_progress=True):
        """Convenience method in Library class to pass Library to Parser to run OCR on all of the images
        found in the Library, and OCR-extracted text from the images directly into the Library as additional
        blocks. 
        
            Parameters
            ----------
            add_to_library : bool, default=False
                Whether to add the OCR-extracted text directly into the Library as additional blocks.

            chunk_size : int, default=400
                The size of text chunks to create during OCR processing.

            min_size : int, default=10
                The minimum size of text chunks to consider during OCR processing.

            realtime_progress : bool, default=True
                Whether to display real-time progress during OCR processing.

            Returns
            -------
            output : int
                Returns 1 if running the OCR on the images was successful.
        """

        output = Parser(library=self).ocr_images_in_library(add_to_library=add_to_library,
                                                            chunk_size=chunk_size,min_size=min_size,
                                                            realtime_progress=realtime_progress)

        return output


class LibraryCatalog:
    """Implements the management of tracking details for libraries via the library card, which is stored
    in the `library` table of the text collection database. It is used by the ``Library`` class.

    ``LibraryCatalog`` is responsible for managing tracking details. This includes creating,
    reading, updating, and deleting library cards. The library card is stored in the table library
    of the chosen text collection database. In most cases, ``LibraryCatalog`` does not need to be directly
    invoked, instead it is used indirectly through the methods of ``Library``.

    Parameters
    ----------
    library : Library, default=None
        The library with which the ``LibraryCatalog`` interacts.

    library_path : str or pathlib.Path object, default=None
        The path to the llmware directory. If set, then the default from ``LLMWareconfig`` is used.

    account_name : str, default='llmware'
        Name of the account.

    Returns
    -------
    library_catalog : LibraryCatalog
        A new ``LibraryCatalog`` object.
    """
    def __init__(self, library=None, library_path=None, account_name="llmware"):

        self.library = library
        if library:
            self.library_name = library.library_name
            self.account_name = library.account_name
        else:
            self.library_name = None
            self.account_name = account_name

        self.schema = LLMWareTableSchema().get_library_card_schema()

        # if table does not exist, then create
        if CollectionWriter("library",account_name=self.account_name).check_if_table_build_required():
            CollectionWriter("library", account_name=self.account_name).create_table("library", self.schema)

        # check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):
            LLMWareConfig.setup_llmware_workspace()

        if not library_path:
            self.library_path = LLMWareConfig.get_llmware_path()
        else:
            self.library_path = library_path

    def get_library_card (self, library_name, account_name="llmware"):

        """ Gets the selected library card for the selected library_name """

        # note: will return either library_card {} or None

        db_record = CollectionRetrieval("library", account_name=account_name).lookup("library_name", library_name)

        if isinstance(db_record, list):
            if len(db_record) > 0:
                db_record = db_record[0]

        library_card = db_record

        return library_card

    def all_library_cards(self):
        all_library_cards_cursor = CollectionRetrieval("library",
                                                       account_name=self.account_name).get_whole_collection()

        """ Gets all library cards """

        all_library_cards = all_library_cards_cursor.pull_all()

        return all_library_cards

    def create_new_library_card(self, new_library_card):

        """ Creates new library card entry """

        new_lib_name = new_library_card["library_name"]

        logger.debug(f"update: LibraryCatalog - create_new_library_card - {new_lib_name} - "
                     f"{new_library_card}")

        CollectionWriter("library", account_name=self.account_name).write_new_record(new_library_card)

        # test to pull card here
        # lib_card = self.get_library_card(new_lib_name)
        # end - test get card

        return 0

    def update_library_card(self, library_name, update_dict, account_name="llmware", delete_record=False):

        """ Updates library card entry """

        lib_card = self.get_library_card(library_name, account_name=account_name)

        updater = CollectionWriter("library",
                                   account_name=self.account_name).update_library_card(library_name,
                                                                                       update_dict,
                                                                                       lib_card,
                                                                                       delete_record=delete_record)

        return 1

    def delete_library_card(self, library_name=None, account_name="llmware"):

        """ Deletes library card """

        if not library_name:
            library_name = self.library_name

        if account_name != "llmware":
            self.account_name = account_name

        f = {"library_name": library_name}

        # self.library_card_collection.delete_one(f)
        CollectionWriter("library", account_name=self.account_name).delete_record_by_key("library_name", library_name)

        return 1

    def get_and_increment_doc_id (self, library_name, account_name="llmware"):

        """ Gets and increments unique doc id counter for library """

        if account_name != "llmware":
           self.account_name = account_name

        cw = CollectionWriter("library", account_name=self.account_name)
        unique_doc_id = cw.get_and_increment_doc_id(library_name)

        return unique_doc_id

    def set_incremental_docs_blocks_images(self, added_docs=0, added_blocks=0, added_images=0, added_pages=0,
                                           added_tables=0):

        """ Updates library card with incremental counters after parsing """

        # updates counting parameters at end of parsing
        cw = CollectionWriter("library", account_name=self.account_name)

        cw.set_incremental_docs_blocks_images(self.library_name,added_docs=added_docs,added_blocks=added_blocks,
                                              added_images=added_images, added_pages=added_pages,
                                              added_tables=added_tables)
        return 0

    def bulk_update_graph_status(self):

        """ Updates graph status on library card """

        update_dict = {"graph_status": "true"}
        self.update_library_card(self.library_name,update_dict, account_name=self.account_name )

        return 0
