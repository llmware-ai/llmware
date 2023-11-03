
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


from bson.int64 import Int64

from pymongo import ReturnDocument
from pymongo import MongoClient
import pymongo
from bson.objectid import ObjectId
import sys
import bson.json_util as json_util
import boto3
from botocore import UNSIGNED
from botocore.config import Config
from werkzeug.utils import secure_filename
import shutil
from botocore.exceptions import ClientError
import os
import json
import csv
import uuid
import re
from datetime import datetime
import random
import logging
from pymongo.errors import ConnectionFailure

from llmware.configs import LLMWareConfig
from llmware.exceptions import LibraryNotFoundException, UnsupportedCollectionDatabaseException


class DBManager:

    class __DBManager:

        def __init__(self):

            self.collection_db_path = LLMWareConfig.get_config("collection_db_uri")

            # default client is Mongo currently
            self.client = MongoClient(self.collection_db_path, unicode_decode_error_handler='ignore')
            #self.client.admin.authenticate(username, password)

    __instance = None

    def __init__(self):

        if not DBManager.__instance:
            DBManager.__instance = DBManager.__DBManager()

    def __getattr__(self, item):
        return getattr(self.__instance, item)


def check_db_uri(timeout_secs=5):

    uri_string = LLMWareConfig.get_config("collection_db_uri")

    # default client is Mongo currently
    client = MongoClient(uri_string, unicode_decode_error_handler='ignore')

    # self.client.admin.authenticate(username, password)

    try:
        # catch if mongo not available
        with pymongo.timeout(timeout_secs):
            client.admin.command('ping')
            logging.info("update: confirmed - Collection DB available at uri string - %s ", uri_string)
            db_status = True

    except ConnectionFailure:
        logging.warning("warning:  Collection DB not found at uri string in LLMWareConfig - %s - check "
                        "connection and/or reset LLMWareConfig 'collection_db_uri' to point to the correct uri.",
                        uri_string)

        db_status = False

    return db_status


class CollectionWriter:

    def __init__(self, collection):
        self.collection = collection

    # write - this is where new blocks get added to the library collection
    def write_new_record(self, new_record):
        registry_id = self.collection.insert_one(new_record).inserted_id
        return 1

    # note:  this will delete the entire collection
    def destroy_collection(self, confirm_destroy=False):

        if confirm_destroy:
            self.collection.drop()
            return 1

        logging.warning("update: library not destroyed - need to set confirm_destroy = True")
        return 0

    # write/update specific record
    def update_block (self, doc_id, block_id, key, new_value, default_keys):

        # for specific (doc_id, block_id) identified, update {key:new_value}
        completed = False

        f = {"$and": [{"block_ID": block_id}, {"doc_ID": doc_id}]}

        if key in default_keys:
            new_values = {"$set": {key: new_value}}
            self.collection.update_one(f,new_values)
            completed = True

        return completed

    def update_one_record(self, filter_dict, key,new_value):
        new_values = {"$set": {key:new_value}}
        self.collection.update_one(filter_dict, new_values)
        return 0

    def update_many_records(self, filter_dict, key, new_value):
        new_values = {"$set": {key:new_value}}
        self.collection.update_many(filter_dict, new_values)
        return 0
    
    def update_many_records_custom(self, filter_dict, update_dict):
        self.collection.update_many(filter_dict, update_dict)
        return 0


class CollectionRetrieval:

    def __init__(self, collection):
        self.collection = collection

    def get_whole_collection(self):
        all_output = list(self.collection.find({},no_cursor_timeout=True))
        return all_output

    def basic_query(self, query):
        match_results_cursor = self.collection.find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}).sort([('score', {'$meta': 'textScore'})]).allow_disk_use(True)

        return match_results_cursor

    def filter_by_key(self, key, value):
        match_results_cursor = self.collection.find({key:value})
        return match_results_cursor

    def text_search_with_key_low_high_range(self, query, key, low, high, key_value_dict=None):

        # accepts key with low & high value + optional key_value_dict with additional parameters
        d = []
        f = {}

        text_search = {"$text": {"$search": query}}
        d.append(text_search)
        key_value_range = {key: {"$gte": low, "$lte": high}}
        d.append(key_value_range)

        if key_value_dict:
            for key, value in key_value_dict.items():
                d.append({key: value})

        # if one key-value pair, then simple filter
        if len(d) == 1: f = d[0]

        # if multiple key-value pairs, then insert list with "$and"
        if len(d) >= 2:
            f = {"$and": d}

        results = list(self.collection.find(f,
                                            {"score": {"$meta": "textScore"}}).
                       sort([('score', {'$meta': 'textScore'})]).allow_disk_use(True))

        return results

    def text_search_with_key_value_range(self, query, key, value_range_list, key_value_dict=None):

        f = {}
        text_search = {"$text": {"$search": query}}

        d = [text_search]
        range_filter = {key: {"$in": value_range_list}}
        d.append(range_filter)

        if key_value_dict:
            for key, value in key_value_dict.items():
                d.append({key: value})

        # if one key-value pair, then simple filter
        if len(d) == 1: f = d[0]

        # if multiple key-value pairs, then insert list with "$and"
        if len(d) >= 2:
            f = {"$and": d}

        results = list(self.collection.find(f,
                                            {"score": {"$meta": "textScore"}}).
                       sort([('score', {'$meta': 'textScore'})]).allow_disk_use(True))

        return results

    def text_search_with_key_value_dict_filter(self, query, key_value_dict):

        f = {}
        text_search = {"$text": {"$search": query}}
        d = [text_search]
        for key, value in key_value_dict.items():

            if isinstance(value, list):
                # if value is a list, then interpret as "$in"
                range_filter = {key: {"$in": value}}
                d.append(range_filter)
            else:
                # if value is not a list, then look for exact match
                d.append({key: value})

        # if one key-value pair, then simple filter
        if len(d) == 1: f = d[0]

        # if multiple key-value pairs, then insert list with "$and"
        if len(d) >= 2:
            f = {"$and": d}

        results = list(self.collection.find(f,
                                            {"score": {"$meta": "textScore"}}).
                       sort([('score', {'$meta': 'textScore'})]).allow_disk_use(True))

        return results

    def get_distinct_list(self, key):
        distinct_list = list(self.collection.distinct(key))
        return distinct_list

    def filter_by_key_dict (self, key_dict):

        f = {}
        d = []
        for key, value in key_dict.items():
            d.append({key:value})

        # if one key-value pair, then simple filter
        if len(d) == 1: f = d[0]

        # if multiple key-value pairs, then insert list with "$and"
        if len(d) >= 2:
            f= {"$and":d}

        results = list(self.collection.find(f))

        return results

    def filter_by_key_value_range(self, key, value_range):
        # e.g., {"doc_ID": [1,2,3,4,5]}
        results = list(self.collection.find({key: {"$in": value_range}}))
        return results

    def filter_by_key_ne_value(self, key, value):
        f = {key: {"$ne":value}}
        output = list(self.collection.find(f))
        return output

    def custom_filter(self, custom_filter):
        results = list(self.collection.find(custom_filter))
        return results

    def get_cursor_by_block(self, doc_id, block_id, selected_page):

        block_cursor = self.collection.find_one({"$and": [
            {"doc_ID": int(doc_id)},
            {"block_ID": {"$gt": block_id}},
            {"content_type": {"$ne": "image"}},
            {"master_index": {"$in": [selected_page, selected_page + 1]}}]})

        return block_cursor


class CloudBucketManager:

    def __init__(self):
        # placeholder - no state / config required currently
        self.start = 0

    # used in Setup() to get sample test documents
    def pull_file_from_public_s3(self, object_key, local_file, bucket_name):

        # return list of successfully downloaded files
        downloaded_files = []

        try:
            # Ensure the local file's folder exists
            os.makedirs(os.path.dirname(local_file), exist_ok=True)

            s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
            s3.Bucket(bucket_name).download_file(object_key, local_file)
            downloaded_files.append(object_key)

        except ClientError as e:
            logging.error(e)

        return downloaded_files

    def create_local_model_repo(self, access_key=None,secret_key=None):

        # list of models retrieved from cloud repo
        models_retrieved = []

        # check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):
            # if not explicitly set up by user, then create folder directory structure
            LLMWareConfig.setup_llmware_workspace()

        # confirm that local model repo path has been created
        local_model_repo_path = LLMWareConfig.get_model_repo_path()
        if not os.path.exists(local_model_repo_path):
            os.mkdir(local_model_repo_path)

        aws_repo_bucket = LLMWareConfig.get_config("llmware_public_models_bucket")

        # if specific model_list passed, then only retrieve models on the list

        bucket = boto3.resource('s3', aws_access_key_id=access_key,
                                aws_secret_access_key=secret_key).Bucket(aws_repo_bucket)

        files = bucket.objects.all()

        s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

        # bucket = s3.Bucket(bucket_name)
        # files = bucket.objects.all()

        for file in files:

            name_parts = file.key.split(os.sep)

            # confirm that file.key is correctly structure as [0] model name, and [1] model component
            if len(name_parts) == 2:

                logging.info("update: identified models in model_repo: %s ", name_parts)

                if name_parts[0] and name_parts[1]:

                    model_folder = os.path.join(local_model_repo_path,name_parts[0])

                    if not os.path.exists(model_folder):
                        os.mkdir(model_folder)
                        models_retrieved.append(name_parts[0])

                    logging.info("update: downloading file from s3 bucket - %s - %s ", name_parts[1], file.key)

                    s3.download_file(aws_repo_bucket, file.key, os.path.join(model_folder,name_parts[1]))

        logging.info("update: created local model repository - # of models - %s - model list - %s ",
                     len(models_retrieved), models_retrieved)

        return models_retrieved

    def pull_single_model_from_llmware_public_repo(self, model_name=None):

        # if no model name selected, then get all
        bucket_name = LLMWareConfig().get_config("llmware_public_models_bucket")

        # check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):
            # if not explicitly set up by user, then create folder directory structure
            LLMWareConfig().setup_llmware_workspace()

        model_path_local = LLMWareConfig.get_model_repo_path()
        
        if not os.path.exists(model_path_local):
            os.makedirs(model_path_local)

        #   assumes that files in model folder are something like:
        #   "pytorch_model.bin" | "config.json" | "tokenizer.json"

        bucket = boto3.resource('s3', config=Config(signature_version=UNSIGNED)).Bucket(bucket_name)

        files = bucket.objects.all()

        for file in files:

            if file.key.startswith(model_name):

                #   found component of model in repo, so go ahead and create local model folder, if needed
                local_model_folder = os.path.join(model_path_local, model_name)
                if not os.path.exists(local_model_folder):
                    os.mkdir(local_model_folder)

                #   simple model_repo structure - each model is a separate folder
                #   each model is a 'flat list' of files, so safe to split on ("/") to get key name
                if not file.key.endswith(os.sep):
                    local_file_path = os.path.join(local_model_folder,file.key.split(os.sep)[-1])
                    bucket.download_file(file.key, local_file_path)

        logging.info("update: successfully downloaded model - %s -  from aws s3 bucket for future access",
                     model_name)

        return files

    #   called in Library as convenience method to connect to user S3 bucket and download into library path
    def connect_to_user_s3_bucket (self, aws_access_key, aws_secret_key,
                                   user_bucket_name, local_download_path, max_files=1000):

        files_copied = []

        accepted_file_formats = ["pptx", "xlsx", "docx", "pdf", "txt", "csv", "html", "jsonl",
                                 "jpg", "jpeg", "png", "wav", "zip"]

        try:
            s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

            bucket = s3.Bucket(user_bucket_name)
            files = bucket.objects.all()

            for file in files:
                f = secure_filename(file.key)
                file_type = f.split(".")[-1].lower()
                if file_type in accepted_file_formats:
                    s3.download_file(user_bucket_name, file.key, local_download_path + f)
                    files_copied.append(f)
                    if len(files_copied) > max_files:
                        break

        except:
            logging.error("error: could not connect to s3 bucket - % ", user_bucket_name)

            return files_copied

        return files_copied


class LibraryCollection:

    def __init__(self, library=None):

        self.library = library

        if library:
            self.library_name = library.library_name
            self.account_name = library.account_name
        else:
            self.library_name = None
            self.account_name = "llmware"      # default, if no account name specified

    def create_library_collection(self, library_name=None, account_name="llmware"):

        collection = None
        if not library_name:
            library_name = self.library_name

        logging.info("update: LibraryCollection().create_library_collection - %s - %s - %s",
                     library_name, self.account_name, LLMWareConfig.get_config("collection_db"))

        if LLMWareConfig().get_config("collection_db") == "mongo":

            if check_db_uri(timeout_secs=5):

                collection = DBManager().client[self.account_name][library_name]
                logging.info("update: creating library collection with Mongo - %s ",
                             LLMWareConfig.get_config("collection_db_uri"))

            else:
                logging.error("error: tried unsuccessfully to connect to Mongo - %s ",
                              LLMWareConfig.get_config("collection_db_uri"))

        else:
            raise UnsupportedCollectionDatabaseException(LLMWareConfig.get_config("collection_db"))

        return collection

    def get_library_collection(self, library_name, account_name="llmware"):

        if LLMWareConfig.get_config("collection_db") == "mongo":

            if check_db_uri(timeout_secs=5):
                collection = DBManager().client[account_name][library_name]
                logging.info("update: creating library collection with Mongo - %s ",
                             LLMWareConfig.get_config("collection_db_uri"))

            else:
                logging.error("error: tried unsuccessfully to connect to Mongo - %s - "
                              "please check connection and reset LLMWare Config collection db settings"
                              "if needed to point to correction uri.", LLMWareConfig.get_config("collection_db_uri"))

                collection = None

            return collection
        else:
            raise UnsupportedCollectionDatabaseException(LLMWareConfig.get_config("collection_db"))

    def get_library_card_collection(self, account_name="llmware"):

        if LLMWareConfig.get_config("collection_db") == "mongo":

            if check_db_uri(timeout_secs=5):
                collection = DBManager().client[account_name].library
                logging.info("update: creating library collection with Mongo - %s ",
                             LLMWareConfig.get_config("collection_db_uri"))
            else:
                logging.error("error: tried unsuccessfully to connect to Mongo - %s ",
                              LLMWareConfig.get_config("collection_db_uri"))
                collection = None

            return collection

        else:
            raise UnsupportedCollectionDatabaseException(LLMWareConfig.get_config("collection_db"))

    def create_index(self, library_name=None):

        if not library_name:
            library_name = self.library_name

        if LLMWareConfig.get_config("collection_db") == "mongo":
            self.library.collection.create_index([("text_search", "text")])
        else:
            raise UnsupportedCollectionDatabaseException(LLMWareConfig.get_config("collection_db"))

        return 0


class LibraryCatalog:

    def __init__(self, library=None, library_path=None, account_name="llmware"):

        self.library = library
        if library:
            self.library_name = library.library_name
            self.account_name = library.account_name
        else:
            self.library_name = None
            self.account_name = account_name

        self.library_card_collection = LibraryCollection().get_library_card_collection(self.account_name)

        # check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):
            LLMWareConfig.setup_llmware_workspace()

        if not library_path:
            self.library_path = LLMWareConfig.get_llmware_path()
        else:
            self.library_path = library_path

    def get_library_card (self, library_name, account_name="llmware"):

        # return either library_card {} or None

        if account_name != "llmware":
            # dynamically change to point to selected account_name - else points to default
            # self.library_card_collection = DBManager().client[account_name].library
            self.library_card_collection = LibraryCollection().get_library_card_collection(account_name=account_name)

        db_record = list(self.library_card_collection.find({"library_name": library_name}))

        if len(db_record) == 1:
            library_card = db_record[0]
        else:
            library_card = None

        return library_card

    def all_library_cards(self):
        all_library_cards = list(self.library_card_collection.find({}))
        return all_library_cards

    def create_new_library_card(self, new_library_card):
        registry_id = self.library_card_collection.insert_one(new_library_card).inserted_id
        return 0

    def update_library_card(self, library_name, update_dict, account_name="llmware"):

        f = {"library_name": library_name}
        new_values = {"$set": update_dict}

        if account_name != "llmware":
            self.library_card_collection = LibraryCollection().get_library_card_collection(account_name=account_name)

        #   standard collection update for all except embedding
        if "embedding" not in update_dict:
            self.library_card_collection.update_one(f,new_values)

        else:
            #   special handling for "embedding" attribute

            lib_card = self.get_library_card(library_name)
            embedding_list = lib_card["embedding"]

            if len(embedding_list) > 0:
                # if the last row is a "no" embedding, then remove it
                if embedding_list[-1]["embedding_status"] == "no":
                    del embedding_list[-1]

            embedding_list.append(update_dict["embedding"])
            embedding_update_dict = {"embedding": embedding_list}
            self.library_card_collection.update_one(f, {"$set": embedding_update_dict})

        return 1

    def delete_library_card(self, library_name=None, account_name="llmware"):

        if not library_name:
            library_name = self.library_name

        f = {"library_name": library_name}

        if account_name != "llmware":
            self.library_card_collection = LibraryCollection().get_library_card_collection(account_name=account_name)

        self.library_card_collection.delete_one(f)

        return 1

    def get_and_increment_doc_id (self, library_name, account_name="llmware"):

        # controller for setting the library_collection and pointer to the DB Collection library

        if account_name != "llmware":
            self.library_card_collection = LibraryCollection().get_library_card_collection(account_name=account_name)

        # method called at the start of parsing each new doc -> each parser gets a new doc_id
        library_counts = self.library_card_collection.find_one_and_update(
            {"library_name": self.library_name},
            {"$inc": {"unique_doc_id": 1}},
            return_document=ReturnDocument.AFTER
        )

        unique_doc_id = library_counts.get("unique_doc_id",-1)

        return unique_doc_id

    def set_incremental_docs_blocks_images(self, added_docs=0, added_blocks=0, added_images=0, added_pages=0,
                                           added_tables=0):

        # updates counting parameters at end of parsing

        self.library_card_collection.update_one(
            {"library_name": self.library_name},
            {"$inc": {"documents": added_docs, "blocks": added_blocks, "images": added_images, "pages": added_pages,
                      "tables": added_tables
        }})

        return 0

    def bulk_update_graph_status(self):

        update_dict = {"graph_status": "true"}
        self.update_library_card(self.library_name,update_dict)

        return 0


class ParserState:

    def __init__(self, parsing_output=None, parse_job_id=None):

        self.parse_job_id = parse_job_id
        self.parsing_output = parsing_output
        self.parser_job_output_base_name = "parser_job_"
        self.parser_output_format = ".jsonl"
        self.parser_output_fp = LLMWareConfig.get_parser_path()

        # check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):

            # if not explicitly set up by user, then create folder directory structure
            LLMWareConfig.setup_llmware_workspace()

    def get_parser_state_fn_from_id(self, parser_job_id):

        fn = self.parser_job_output_base_name + str(parser_job_id) + self.parser_output_format
        return fn

    def get_parser_id_from_parser_state_fn(self, fn):

        core_fn = fn.split(".")[0]
        id = core_fn.split("_")[-1]
        return id

    def lookup_by_parser_job_id(self, parser_id):

        parser_output = self.lookup_by_parse_job_id(parser_id)
        return parser_output

    def save_parser_output(self, parser_job_id, parser_output):

        fn = self.get_parser_state_fn_from_id(parser_job_id)
        fp = os.path.join(self.parser_output_fp, fn)

        outfile = open(fp, "w")

        for entry_dict in parser_output:
            jsonl_row = json.dumps(entry_dict)
            outfile.write(jsonl_row)
            outfile.write("\n")

        outfile.close()

        return fn

    def issue_new_parse_job_id(self, custom_id=None, mode="uuid"):

        # issue new parse_job_id

        if custom_id:
            self.parse_job_id = custom_id
        else:
            if mode == "time_stamp":
                self.parse_job_id = StateResourceUtil().get_current_time_now()
            elif mode == "uuid":
                self.parse_job_id = str(StateResourceUtil().get_uuid())
            elif mode == "random_number":
                self.parse_job_id = str(random.randint(1000000, 9999999))

        return self.parse_job_id

    def lookup_by_parse_job_id (self, prompt_id):

        output = []

        fn = self.get_parser_state_fn_from_id(prompt_id)
        fp = os.path.join(self.parser_output_fp, fn)

        try:
            my_file = open(fp, 'r', encoding='utf-8')
            for lines in my_file:
                new_row = json.loads(lines)
                output.append(new_row)

        except:
            logging.info("warning: ParserState - could not find previous parse job record - %s ", prompt_id)
            output = []

        return output


class PromptState:

    def __init__(self, prompt=None):

        self.prompt = prompt
        self.prompt_state_base_name = "prompt_"
        self.prompt_state_format = ".jsonl"

        # check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):

            # if not explicitly set up by user, then create folder directory structure
            LLMWareConfig.setup_llmware_workspace()

        self.prompt_path = LLMWareConfig.get_prompt_path()
        self.output_path = LLMWareConfig.get_prompt_path()

        # prompt state written to files
        self.prompt_collection = None
        self.write_to_db = False

    def get_prompt_state_fn_from_id(self, prompt_id):
        fn = self.prompt_state_base_name + str(prompt_id) + self.prompt_state_format
        return fn

    def get_prompt_id_from_prompt_state_fn(self, fn):
        core_fn = fn.split(".")[0]
        id = core_fn.split("_")[-1]
        return id

    def lookup_by_prompt_id(self, prompt_id):
        ai_trx_list = self.lookup_by_prompt_id_from_file(prompt_id)
        return ai_trx_list

    def register_interaction(self, ai_dict):

        # by default, add to the interaction_history in memory
        self.prompt.interaction_history.append(ai_dict)

        return ai_dict

    def initiate_new_state_session(self, prompt_id=None):

        if not prompt_id:
            prompt_id = self.issue_new_prompt_id()

        # reset key trackers
        self.prompt.llm_history = []
        self.prompt.prompt_id = prompt_id
        return prompt_id

    def issue_new_prompt_id(self, custom_id=None, mode="uuid"):

        # issue new prompt_id
        if custom_id:
            self.prompt.prompt_id = custom_id
        else:
            if mode == "time_stamp":
                self.prompt.prompt_id = StateResourceUtil().get_current_time_now()
            elif mode == "uuid":
                self.prompt.prompt_id = str(StateResourceUtil().get_uuid())
            elif mode == "random_number":
                self.prompt.prompt_id = str(random.randint(1000000, 9999999))

        return self.prompt.prompt_id

    def load_state(self, prompt_id, prompt_path=None,clear_current_state=True):

        output = None

        if not prompt_path:
            prompt_path = self.prompt_path

        fn = self.get_prompt_state_fn_from_id(prompt_id)
        fp = os.path.join(prompt_path, fn)

        try:
            if clear_current_state:
                self.prompt.interaction_history = []

            my_file = open(fp, 'r', encoding='utf-8')
            for lines in my_file:
                new_row = json.loads(lines)
                self.prompt.interaction_history.append(new_row)
                self.prompt.prompt_id = prompt_id
                output = self.prompt.interaction_history

        except:
            logging.info("update: PromptState - could not find previous prompt interaction state- %s ", prompt_id)
            output = None

        return output

    def lookup_by_prompt_id_from_file(self, prompt_id):

        output = []

        fn = self.get_prompt_state_fn_from_id(prompt_id)
        fp = os.path.join(self.prompt_path, fn)

        try:
            my_file = open(fp, 'r', encoding='utf-8')
            for lines in my_file:
                new_row = json.loads(lines)
                output.append(new_row)
        except:
            logging.info("warning: PromptState - could not find previous prompt interaction state- %s ", prompt_id)
            output = []

        return output

    def full_history(self):
        ai_trx_list = self.full_history_from_file()
        return ai_trx_list

    def full_history_from_file(self):

        output= []

        all_prompts = os.listdir(self.prompt_path)

        for i, files in enumerate(all_prompts):

            #   will iterate through all files in the prompt path that start with the expected
            #   prompt base name

            if files.startswith(self.prompt_state_base_name):
                prompt_id = self.get_prompt_id_from_prompt_state_fn(files)
                records = self.lookup_by_prompt_id(prompt_id)
                output += records

        return output

    def lookup_prompt_with_filter(self, filter_dict):

        # default - return []
        output = []

        # may want to add safety check that filter_dict is dict
        all_prompt_records = self.full_history_from_file()

        for i, prompt in enumerate(all_prompt_records):
            match = -1
            for keys, values in filter_dict.items():

                # must match every key in the filter dict
                if keys in prompt:
                    if values == prompt[keys]:
                        match = 1
                    else:
                        match = -1
                        break
                else:
                    # if key not in record, then not a match
                    match = -1
                    break

            if match == 1:
                output.append(prompt)

        return output

    def update_records(self, prompt_id, filter_dict, update_dict):

        updated_prompt_records = []
        matching_record = {}
        prompt_records = self.lookup_by_prompt_id(prompt_id)
        for record in prompt_records:
            match = -1
            for keys, values in filter_dict.items():
                if keys in record:
                    if record[keys] == values:
                        match = 1
                    else:
                        match = -1
                        break
                else:
                    match = -1
                    break

            if match == -1:
                updated_prompt_records.append(record)
            else:
                # found matching record
                matching_record = record

                # update records according to update_dict
                updated_record = {}
                for key, value in matching_record.items():
                    for update_key, update_value in update_dict.items():
                        if key == update_key:
                            updated_record.update({key: update_value})
                        else:
                            updated_record.update({key:value})

                updated_prompt_records.append(updated_record)

        self.save_custom_state(prompt_id, updated_prompt_records)

        return 0

    def save_custom_state(self, prompt_id, custom_history, prompt_path=None):

        if not prompt_path:
            prompt_path = LLMWareConfig.get_prompt_path()

        fn = self.get_prompt_state_fn_from_id(prompt_id)
        fp = os.path.join(prompt_path, fn)

        outfile = open(fp, "w")

        for entry_dict in custom_history:
            jsonl_row = json.dumps(entry_dict)
            outfile.write(jsonl_row)
            outfile.write("\n")

        outfile.close()

        return fp

    def save_state(self, prompt_id, prompt_path=None):

        if not prompt_path:
            prompt_path = LLMWareConfig.get_prompt_path()

        fn = self.get_prompt_state_fn_from_id(prompt_id)
        fp = os.path.join(prompt_path, fn)

        outfile = open(fp, "w")

        for entry_dict in self.prompt.interaction_history:
            jsonl_row = json.dumps(entry_dict)
            outfile.write(jsonl_row)
            outfile.write("\n")

        outfile.close()

        return fp

    def available_states(self, prompt_path=None):

        available_states = []

        if not prompt_path:
            prompt_path = self.prompt_path

        for x in os.listdir(prompt_path):
            if x.startswith(self.prompt_state_base_name):
                prompt_id = self.get_prompt_id_from_prompt_state_fn(x)
                new_entry = {"prompt_id": prompt_id, "prompt_fn": x}
                available_states.append(new_entry)

        logging.info("update: PromptState - available states - ", available_states)

        return available_states

    def generate_interaction_report(self, prompt_id_list, output_path=None, report_name=None):

        # prepares a csv report that can be extracted to a spreadsheet

        if not output_path:
            output_path = self.output_path

        if not report_name:
            report_name = "interaction_report_" + str(StateResourceUtil().get_current_time_now()) + ".csv"

        result_count = 0

        report_fp = os.path.join(output_path,report_name)

        with open(report_fp, 'w', newline='') as csvfile:
            c = csv.writer(csvfile, dialect='excel', doublequote=False, delimiter=',', escapechar=']')

            header_row = ["Prompt_ID", "Prompt", "LLM_Response", "Instruction", "Evidence", "Model", "Time-Stamp"]
            c.writerow(header_row)

            for i, prompt_id in enumerate(prompt_id_list):

                fn = self.get_prompt_state_fn_from_id(prompt_id)
                fp = os.path.join(self.prompt_path, fn)

                my_file = open(fp, 'r', encoding='utf-8')
                for lines in my_file:
                    new_row = json.loads(lines)

                    # create new csv row

                    csv_row = [prompt_id,
                               new_row["prompt"],
                               new_row["llm_response"],
                               new_row["instruction"],
                               new_row["evidence"],
                               new_row["model"],
                               new_row["time_stamp"]
                               ]

                    c.writerow(csv_row)
                    result_count += 1

        csvfile.close()

        output_response = {"report_name": report_name, "report_fp": report_fp, "results": result_count}

        return output_response

    def generate_interaction_report_current_state(self, output_path=None, report_name=None):

        # prepares a csv report that can be extracted to a spreadsheet

        if not output_path:
            output_path = self.output_path

        if not report_name:
            report_name = "interaction_report_" + str(StateResourceUtil().get_current_time_now()) + ".csv"

        result_count = 0

        report_fp = os.path.join(output_path,report_name)

        with open(report_fp, 'w', newline='') as csvfile:
            c = csv.writer(csvfile, dialect='excel', doublequote=False, delimiter=',', escapechar=']')

            header_row = ["Prompt_ID", "Prompt", "LLM_Response", "Instruction", "Evidence", "Model", "Time-Stamp"]
            c.writerow(header_row)

            for i, new_row in enumerate(self.prompt.interaction_history):

                # create new csv row

                csv_row = [self.prompt.prompt_id,
                           new_row["prompt"],
                           new_row["llm_response"],
                           new_row["instruction"],
                           new_row["evidence"],
                           new_row["model"],
                           new_row["time_stamp"]
                           ]

                c.writerow(csv_row)
                result_count += 1

        csvfile.close()

        output_response = {"report_name": report_name, "report_fp": report_fp, "results": result_count}

        return output_response


class QueryState:

    def __init__(self, query=None, query_id=None):

        if query:
            self.query = query
            self.query_id = query.query_id

        if query_id:
            self.query_id = query_id
            self.query = None

        self.query_state_base_name = "query_"
        self.query_state_format = ".jsonl"

        self.query_path = LLMWareConfig.get_query_path()
        self.output_path = LLMWareConfig.get_query_path()

        # check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):

            # if not explicitly set up by user, then create folder directory structure
            LLMWareConfig.setup_llmware_workspace()

    def get_query_state_fn_from_id(self, prompt_id):
        fn = self.query_state_base_name + str(prompt_id) + self.query_state_format
        return fn

    def get_query_id_from_prompt_state_fn(self, fn):
        core_fn = fn.split(".")[0]
        id = core_fn.split("_")[-1]
        return id

    def initiate_new_state_session(self, query_id=None):

        if not query_id:
            query_id = self.issue_new_query_id()

        # reset key trackers
        self.query.query_history = []
        self.query.results = []
        self.query.doc_id_list = []
        self.query.doc_fn_list = []

        self.query_id = query_id

        return query_id

    def issue_new_query_id(self, custom_id=None, mode="uuid"):

        # issue new query_id
        if not custom_id:

            if mode == "time_stamp":
                custom_id = StateResourceUtil().get_current_time_now()
            elif mode == "uuid":
                custom_id = StateResourceUtil().get_uuid()
            elif mode == "random_number":
                custom_id = str(random.randint(1000000, 9999999))

        return custom_id

    def available_states(self):

        available_states = []

        for x in os.listdir(self.query_path):
            if x.startswith(self.query_state_base_name):
                query_id = self.get_query_id_from_prompt_state_fn(x)
                new_entry = {"query_id": query_id, "query_fn": x}
                available_states.append(new_entry)

        logging.info("update: QueryState - available saved query states - ", available_states)

        return available_states

    def load_state (self, query_id):

        output = []
        doc_id_list = []
        doc_fn_list = []
        query_history = []

        fn = self.get_query_state_fn_from_id(query_id)
        fp = os.path.join(self.query_path, fn)

        try:
            my_file = open(fp, 'r', encoding='utf-8')
            for lines in my_file:
                new_row = json.loads(lines)
                output.append(new_row)

                if "doc_ID" in new_row:
                    if new_row["doc_ID"] not in doc_id_list:
                        doc_id_list.append(new_row["doc_ID"])

                if "file_source" in new_row:
                    if new_row["file_source"] not in doc_fn_list:
                        doc_fn_list.append(new_row["file_source"])

                if "query" in new_row:
                    if new_row["query"] not in query_history:
                        query_history.append(new_row["query"])

        except:
            logging.info("warning: QueryState - could not find previous query state- %s ", query_id)
            output = []

        self.query.results = output
        self.query.doc_id_list = doc_id_list
        self.query.doc_fn_list = doc_fn_list
        self.query.query_history = query_history

        return self

    def save_state(self, query_id=None):

        if not query_id:
            query_id = self.query.query_id

        fn = self.get_query_state_fn_from_id(query_id)
        fp = os.path.join(self.query_path, fn)

        outfile = open(fp, "w")

        for entry_dict in self.query.results:
            jsonl_row = json.dumps(entry_dict)
            outfile.write(jsonl_row)
            outfile.write("\n")

        outfile.close()

        return fn

    def generate_query_report_current_state(self, report_name=None):

        # prepares a csv report that can be extracted to a spreadsheet

        if not self.query:
            logging.error("error: QueryState - report generation - must load a current query")
            return -1

        query_name = ""
        for entries in self.query.query_history:
            query_name += re.sub(" ", "_", entries) + "-"

        if len(query_name) > 100:
            query_name = query_name[0:100]
        if query_name.endswith("-"):
            query_name = query_name[:-1]

        if not report_name:
            report_name = "query_report_" + query_name + ".csv"

        report_out = []
        col_headers = ["Query", "File_Source", "Doc_ID", "Block_ID", "Page", "Text"]

        report_out.append(col_headers)

        for j, results in enumerate(self.query.results):

            query = ""
            if "query" in results:
                query = results["query"]

            file_source = ""
            if "file_source" in results:
                file_source = results["file_source"]

            doc_id = "NA"
            if "doc_ID" in results:
                doc_id = results["doc_ID"]

            block_id = "NA"
            if "block_ID" in results:
                block_id = results["block_ID"]

            page_num = "NA"
            if "page_num" in results:
                page_num = results["page_num"]

            text = ""
            if "text" in results:
                text = re.sub("[,\"]"," ", results["text"])

            new_row = [query, file_source, doc_id, block_id, page_num, text]

            report_out.append(new_row)

        fp = os.path.join(self.query_path, report_name)

        StateResourceUtil().file_save(report_out, self.output_path, report_name)

        return report_name


class StateResourceUtil:

    def __init__(self):
        self.do_nothing = 0     # placeholder - may add attributes in the future

    def get_uuid(self):
        # uses unique id creator from uuid library
        return uuid.uuid4()

    @staticmethod
    def get_current_time_now (time_str="%a %b %e %H:%M:%S %Y"):
        time_stamp = datetime.now().strftime(time_str)
        return time_stamp

    @staticmethod
    def file_save (cfile, file_path, file_name):

        max_csv_size = 20000
        csv.field_size_limit(max_csv_size)

        out_file = file_path + file_name
        with open(out_file, 'w', newline='') as csvfile:
            c = csv.writer(csvfile, dialect='excel', doublequote=False, delimiter=',', escapechar= ']')
            # c.writerow(first_row)
            for z in range(0 ,len(cfile)):
                # intercept a line too large here
                if sys.getsizeof(cfile[z]) < max_csv_size:
                    c.writerow(cfile[z])
                else:
                    logging.error("error:  CSV ERROR:   Row exceeds MAX SIZE: %s %s", sys.getsizeof(cfile[z])
                                  ,cfile[z])

        csvfile.close()

        return 0




