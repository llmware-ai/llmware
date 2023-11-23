
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


from werkzeug.utils import secure_filename
import shutil
import os
import json
import logging

from llmware.configs import LLMWareConfig
from llmware.util import Utilities, Graph
from llmware.parsers import Parser
from llmware.models import ModelCatalog
from llmware.resources import LibraryCatalog, LibraryCollection, CollectionRetrieval, CollectionWriter, \
    CloudBucketManager, check_db_uri
from llmware.embeddings import EmbeddingHandler
from llmware.exceptions import LibraryNotFoundException, SetUpLLMWareWorkspaceException, \
    CollectionDatabaseNotFoundException, ImportingSentenceTransformerRequiresModelNameException


class Library:

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
                             "table", "external_files", "text", "header_text", "text_search",
                             "user_tags", "special_field1", "special_field2", "special_field3","graph_status","dialog"]

        # default library card elements
        self.default_library_card = ["library_name", "embedding_status", "embedding_model", "embedding_db",
                                     "knowledge_graph", "unique_doc_id", "documents", "blocks", "images", "pages",
                                     "tables"]

        self.block_size_target_characters = 400

        # attributes used in parsing workflow
        self.doc_ID = 0
        self.block_ID = 0

        # db settings
        self.collection = None

        # check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):

            # if not explicitly set up by user, then create folder directory structure
            LLMWareConfig.setup_llmware_workspace()

        # check if collection datastore is connected
        if not check_db_uri(timeout_secs=3):
            raise CollectionDatabaseNotFoundException(LLMWareConfig.get_config("collection_db_uri"))

    # explicit constructor to create a new library
    def create_new_library(self, library_name, account_name="llmware"):

        # note: default behavior - if library with same name already exists, then it loads existing library

        self.library_name = library_name
        self.account_name = account_name

        # apply safety check to library_name path
        library_name = secure_filename(library_name)

        library_exists = self.check_if_library_exists(library_name,account_name)

        if library_exists:
            # do not create
            logging.info("update: library already exists - returning library - %s - %s ", library_name, account_name)
            return self.load_library(library_name, account_name)

        # allow 'dynamic' creation of a new account path
        account_path = os.path.join(LLMWareConfig.get_library_path(), account_name)
        if not os.path.exists(account_path):
            os.makedirs(account_path,exist_ok=True)

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

                             "embedding": [{"embedding_status": "no", "embedding_model": "none", "embedding_db": "none"}],

                             # knowledge graph
                             "knowledge_graph": "no",

                             # doc trackers
                             "unique_doc_id": 0, "documents": 0, "blocks": 0, "images": 0, "pages": 0, "tables": 0,

                             # *** NEW ***
                             "account_name": self.account_name
                             }

        # LibraryCatalog will register the new library card
        new_library_card = LibraryCatalog(self).create_new_library_card(new_library_entry)

        # assumes DB Connection for saving .collection
        self.collection = LibraryCollection(self).create_library_collection()

        # *** change *** - update collection text index in collection after adding documents
        LibraryCollection(self).create_index()

        return self

    def load_library(self, library_name, account_name="llmware"):

        # first check that library exists
        # *** INSERT CHANGE HERE - need to pass account name ***
        library_exists = self.check_if_library_exists(library_name, account_name=account_name)
        # *** END - CHANGE ***

        if not library_exists:
            logging.error("error: library/account not found - %s - %s ", library_name, account_name)
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

        # assumes DB Connection for saving collection
        self.collection = LibraryCollection(self).create_library_collection()

        # *** change *** - update collection text index in collection after adding documents
        LibraryCollection(self).create_index()

        return self

    def get_library_card(self, library_name=None, account_name="llmware"):

        # *** INSERT CHANGE HERE - better handling of optional parameters ***

        library_card = None

        if library_name:
            lib_lookup_name = library_name
            acct_lookup_name = account_name
        else:
            lib_lookup_name = self.library_name
            acct_lookup_name = self.account_name

        # if library_name: self.library_name = library_name
        # if account_name: self.account_name = account_name

        if lib_lookup_name and acct_lookup_name:
            library_card= LibraryCatalog().get_library_card(lib_lookup_name, account_name=acct_lookup_name)

        # *** END - INSERT CHANGE ***

        if not library_card:
            logging.warning("warning:  error retrieving library card - not found - %s - %s ", library_name, account_name)

        return library_card

    def check_if_library_exists(self, library_name, account_name="llmware"):

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

    def update_embedding_status (self, status_message, embedding_model, embedding_db):

        # sets three parameters for embedding -
        #   "embedding_status", e.g., is embedding completed for library
        #   "embedding_model", e.g., what is the embedding model used to create the embedding
        #   "embedding_db":, e.g., Milvus, FAISS, Pinecone

        #   special handling for updating "embedding" in update_library_card
        #   -- will append this new embedding dict to the end of the embedding list

        update_dict = {"embedding": {"embedding_status": status_message,
                                     "embedding_model": embedding_model,
                                     "embedding_db": embedding_db}}

        updater = LibraryCatalog(self).update_library_card(self.library_name, update_dict)

        return True

    def get_embedding_status (self):

        library_card = LibraryCatalog(self).get_library_card(self.library_name, account_name=self.account_name)

        if not library_card:

            logging.error("error: library/account not found - %s - %s ", self.library_name, self.account_name)
            raise LibraryNotFoundException(self.library_name, self.account_name)

        # embedding record will be a list of {"embedding_status" | "embedding_model" | "embedding_db"}
        logging.info("update: library_card - %s ", library_card)

        if "embedding" in library_card:
            embedding_record = library_card["embedding"]
        else:
            logging.warning("warning: could not identify embedding record in library card - %s ", library_card)
            embedding_record = None

        """
        embedding_record = {"embedding_status": library_card["embedding_status"],
                            "embedding_model": library_card["embedding_model"],
                            "embedding_db": library_card["embedding_db"]}
        """

        return embedding_record

    def get_knowledge_graph_status (self):

        library_card = LibraryCatalog(self).get_library_card(self.library_name, self.account_name)

        if not library_card:
            logging.error("error: library/account not found - %s - %s ", self.library_name, self.account_name)
            raise LibraryNotFoundException(self.library_name, self.account_name)

        status_message = library_card["knowledge_graph"]

        return status_message

    def set_knowledge_graph_status (self, status_message):

        update_dict = {"knowledge_graph": status_message}
        updater = LibraryCatalog(self).update_library_card(self.library_name,update_dict)

        return True

    def get_and_increment_doc_id(self):
        unique_doc_id = LibraryCatalog(self).get_and_increment_doc_id(self.library_name)
        return unique_doc_id

    def set_incremental_docs_blocks_images(self, added_docs=0, added_blocks=0, added_images=0, added_pages=0,
                                           added_tables=0):

        # updates counting parameters at end of parsing
        updater = LibraryCatalog(self).set_incremental_docs_blocks_images(added_docs=added_docs,
                                                                          added_blocks=added_blocks,
                                                                          added_images=added_images,
                                                                          added_pages=added_pages,
                                                                          added_tables=added_tables)

        return True

    # Helper method to support adding a single file to a library
    def add_file(self, file_path):
        # Ensure the input path exists
        os.makedirs(LLMWareConfig.get_input_path(), exist_ok=True)
        
        file_name = os.path.basename(file_path)
        target_path = os.path.join(LLMWareConfig.get_input_path(), file_name)

        shutil.copyfile(file_path,target_path)
        self.add_files()

    # main method for adding file - pass local filepath and appropriate parsers will be called
    def add_files (self, input_folder_path=None):

        if not input_folder_path:
            input_folder_path = LLMWareConfig.get_input_path()

        # get overall counters at start of process
        lib_counters_before = self.get_library_card()

        logging.info("update: lib_counters_before - %s ", lib_counters_before)

        parsing_results = Parser(library=self).ingest(input_folder_path,dupe_check=True)

        logging.info("update: parsing results - %s ", parsing_results)

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
            logging.error("error: unexpected - could not identify the library_card correctly")

        logging.info("update: output_results - %s ", output_results)

        # update collection text index in collection after adding documents
        LibraryCollection(self).create_index()

        return output_results

    def export_library_to_txt_file(self, output_fp=None, output_fn=None, include_text=True, include_tables=True,
                                   include_images=False):

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

        results = CollectionRetrieval(self.collection).filter_by_key_value_range("content_type",filter_list)

        file_location = os.path.join(output_fp, output_fn + ".txt")
        output_file = open(file_location, "w")
        text_field = "text_search"
        for elements in results:
            new_entry = elements[text_field].strip() + "\n"
            output_file.write(new_entry)

        output_file.close()

        return file_location

    def export_library_to_jsonl_file(self, output_fp, output_fn, include_text=True, include_tables=True,
                                     include_images=False, dict_keys=None):

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

        results = CollectionRetrieval(self.collection).filter_by_key_value_range("content_type", filter_list)

        file_location = os.path.join(output_fp, output_fn + ".jsonl")
        output_file = open(file_location, "w")

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

        # pull files into local cache for processing
        files_copied = CloudBucketManager().connect_to_user_s3_bucket (aws_access_key, aws_secret_key,
                                                                       bucket_name, LLMWareConfig.get_input_path())

        return files_copied

    def generate_knowledge_graph(self):
        kg = Graph(library=self).build_graph()
        self.set_knowledge_graph_status("yes")
        return 0

    def install_new_embedding (self, embedding_model_name=None, vector_db="milvus",
                               from_hf= False, from_sentence_transformer=False, model=None, tokenizer=None, model_api_key=None,
                               vector_db_api_key=None, batch_size=500):

        embeddings = None
        my_model = None

        # step 1 - load selected model from ModelCatalog - will pass 'loaded' model to the EmbeddingHandler

        # check if instantiated model and tokenizer -> load as HuggingFace model
        if model:
            if from_hf:
                logging.info("update: loading hf model")
                my_model = ModelCatalog().load_hf_embedding_model(model, tokenizer)
                batch_size = 50

            if from_sentence_transformer:
                logging.info("update: loading sentence transformer model")
                if not embedding_model_name:
                    raise ImportingSentenceTransformerRequiresModelNameException

                my_model = ModelCatalog().load_sentence_transformer_model(model,embedding_model_name)
        else:
            # if no model explicitly passed, then look up in the model catalog
            if embedding_model_name:
                my_model = ModelCatalog().load_model(selected_model=embedding_model_name, api_key=model_api_key)

        if not my_model:
            logging.error("error: install_new_embedding - can not identify a selected model")
            return -1

        # step 2 - pass loaded embedding model to EmbeddingHandler, which will route to the appropriate resource
        embeddings = EmbeddingHandler(self).create_new_embedding(vector_db, my_model, batch_size=batch_size)

        if not embeddings:
            logging.warning("warning: no embeddings created")

        return embeddings

    def delete_library(self, library_name=None, confirm_delete=False):

        # remove all artifacts from library to wipe the slate clean

        if library_name:
            self.library_name = library_name

        success_code = 1

        try:
            if confirm_delete:

                # 1st - remove the blocks - drop the collection in database
                CollectionWriter(self.collection).destroy_collection(confirm_destroy=True)

                # 2nd - Eliminate the local file structure
                file_path = self.library_main_path
                shutil.rmtree(file_path)

                # 3rd - remove record in LibraryCatalog
                LibraryCatalog(self).delete_library_card(self.library_name)

                logging.info("update:  deleted all library file artifacts + folders")

        except:
            logging.exception("Error destroying library")
            success_code = -1

        return success_code

    def update_block (self, doc_id, block_id, key, new_value):
        completed = CollectionWriter(self.collection).update_block(doc_id, block_id,key,new_value,self.default_keys)
        return completed

    def add_website (self, url, get_links=True, max_links=5):

        Parser(library=self).parse_website(url,get_links=get_links,max_links=max_links)
        LibraryCollection(self).create_index(self.library_name)

        return self

    def add_wiki(self, topic_list,target_results=10):
        Parser(library=self).parse_wiki(topic_list,target_results=target_results)
        LibraryCollection(self).create_index(self.library_name)
        return self

    def add_dialogs(self, input_folder=None):
        if not input_folder:
            input_folder = LLMWareConfig.get_input_path()

        output = Parser(library=self).parse_dialog(input_folder)

        return self

    def add_image(self, input_folder=None):
        if not input_folder:
            input_folder = LLMWareConfig.get_input_path()

        output = Parser(library=self).parse_image(input_folder)

        return self

    def add_pdf_by_ocr(self, input_folder=None):

        if not input_folder:
            input_folder = LLMWareConfig.get_input_path()

        output = Parser(library=self).parse_pdf_by_ocr_images(input_folder)

        return self

    def add_pdf(self, input_folder=None):

        if not input_folder:
            input_folder = LLMWareConfig.get_input_path()

        output = Parser(library=self).parse_pdf(input_folder)

        return self

    def add_office(self, input_folder=None):

        if not input_folder:
            input_folder = LLMWareConfig.get_input_path()

        output = Parser(library=self).parse_office(input_folder)

        return self

    def get_all_library_cards(self, account_name='llmware'):
        library_cards = LibraryCatalog(account_name=account_name).all_library_cards()
        return library_cards

