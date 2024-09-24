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

"""The resources module implements the text index databases that are used as the foundation for creating a
Library in LLMWare, and a wide range of supporting methods, including text query retrieval, library card
 management, tracking of embedding progress and status, and the ability to create custom tables.  The text index
 is used as the 'master' source of aggregating and access unstructured information that has been parsed and
 organized into Library collections.

Currently, llmware supports MongoDB, Postgres, and SQLite as text index databases, and supports the use of both
Postgres and SQLIte for creation of custom (SQL) tables.

"""

import platform
import os
import ast
import json
import csv
import uuid
import re
from datetime import datetime
import random
import logging
import sys

try:
    from pymongo import MongoClient, ReturnDocument
    from bson import ObjectId
    import pymongo
    from pymongo.errors import ConnectionFailure
except ImportError:
    pass

try:
    import boto3
    from botocore import UNSIGNED
    from botocore.config import Config
    from botocore.exceptions import ClientError
except ImportError:
    pass

from llmware.configs import LLMWareConfig, PostgresConfig, LLMWareTableSchema, SQLiteConfig, AWSS3Config

from llmware.exceptions import LLMWareException, UnsupportedCollectionDatabaseException, InvalidNameException

# new imports
try:
    import sqlite3
except ImportError:
    pass

try:
    import psycopg
except ImportError:
    pass

logger = logging.getLogger(__name__)
logger.setLevel(level=LLMWareConfig().get_logging_level_by_module(__name__))


class CollectionRetrieval:

    """CollectionRetrieval is primary class abstraction to handle all queries to underlying Text Index Database.
    All calling functions should use CollectionRetrieval, which will, in turn, route to the correct DB resource """

    def __init__(self, library_name, account_name="llmware",db_name=None,custom_table=False, custom_schema=False):

        self.library_name = library_name
        self.account_name = account_name

        self.supported_collection_db = LLMWareConfig().get_supported_collection_db()

        #   allow direct pass of db name
        if db_name:
            self.active_db = db_name
        else:
            self.active_db = LLMWareConfig().get_active_db()

        self._retriever = None

        if self.active_db in self.supported_collection_db:

            if self.active_db == "mongo":
                self._retriever = MongoRetrieval(self.library_name, account_name=account_name,
                                                 custom_table=custom_table, custom_schema=custom_schema)

            if self.active_db == "postgres":
                self._retriever = PGRetrieval(self.library_name, account_name=account_name,
                                              custom_table=custom_table, custom_schema=custom_schema)

            if self.active_db == "sqlite":
                self._retriever = SQLiteRetrieval(self.library_name, account_name=account_name,
                                                  custom_table=custom_table, custom_schema=custom_schema)

        else:
            raise UnsupportedCollectionDatabaseException(self.active_db)

    def test_connection(self):
        """Pings database and confirms valid connection"""
        return self._retriever.test_connection()

    def safe_name(self, input_name):
        """ Checks if collection name valid for db resource """
        return self._retriever.safe_name(input_name)

    def lookup(self, key,value):
        """lookup returns a list of dictionary entries - generally a list of 1 entry for 'lookup'"""
        return self._retriever.lookup(key,value)

    def embedding_key_lookup(self, key, value):
        return self._retriever.embedding_key_lookup(key,value)

    def get_whole_collection(self):
        """Retrieves whole collection, e.g., filter {} or SELECT * FROM {table}- will return a Cursor object"""
        return self._retriever.get_whole_collection()

    def basic_query(self, query):
        """Simple text query passed to the text index"""
        return self._retriever.basic_query(query)

    def filter_by_key(self, key, value):
        """Filter_by_key accepts a key string, corresponding to a column in the DB, and matches to a value"""
        return self._retriever.filter_by_key(key, value)

    def text_search_with_key_low_high_range(self, query, key, low, high, key_value_dict=None):
        """Text search with a key, such as page or document number, and matches entries in a range of 'low' to 'high'"""
        return self._retriever.text_search_with_key_low_high_range(query, key, low, high, key_value_dict=key_value_dict)

    def text_search_with_key_value_range(self, query, key, value_range_list, key_value_dict=None):
        """Text search with added filter of confirming that a key is in the selected value_range list
        with option for any number of further constraints passed as optional key_value_dict"""
        return self._retriever.text_search_with_key_value_range(query, key, value_range_list,
                                                                key_value_dict=key_value_dict)

    def text_search_with_key_value_dict_filter(self, query, key_value_dict):
        """Text search with with {key:value} filter added"""
        return self._retriever.text_search_with_key_value_dict_filter(query, key_value_dict)

    def get_distinct_list(self, key):
        """Returns distinct list of elements in collection by key"""
        return self._retriever.get_distinct_list(key)

    def filter_by_key_dict(self, key_dict):
        """Filters by key dictionary"""
        return self._retriever.filter_by_key_dict(key_dict)

    def filter_by_key_value_range(self, key, value_range):
        """Filters by key value range"""
        return self._retriever.filter_by_key_value_range(key, value_range)

    def filter_by_key_ne_value(self, key, value):
        """Filters by key not equal to selected value"""
        return self._retriever.filter_by_key_ne_value(key, value)

    def count_documents(self, filter_dict):
        """Counts entries returned by filter dict"""
        return self._retriever.count_documents(filter_dict)

    def close(self):
        """Close underlying DB connection - handled by underlying DB resource"""
        return self._retriever.close()

    #   2 specific reads for embedding
    def embedding_job_cursor(self, new_embedding_key, doc_id=None):
        """Handles end-to-end retrieval of text blocks selected for embedding & returns cursor"""
        return self._retriever.embedding_job_cursor(new_embedding_key,doc_id=doc_id)

    def count_embedded_blocks(self, embedding_key):
        """Counts the number of blocks to be created for an embedding job"""
        return self._retriever.count_embedded_blocks(embedding_key)

    def direct_custom_query(self, query_filter):
        """Applies the custom query directly to the DB and returns the results"""
        return self._retriever.direct_custom_query(query_filter)

    def list_all_tables(self):
        """Get list of all collections on the database"""
        return self._retriever.list_all_tables()

    def get_schema(self, table_name):
        """Return schema for selected table"""
        return self._retriever.get_schema(table_name)


class CollectionWriter:

    """CollectionWriter is the main class abstraction for writing, editing, and deleting new elements to the
    underlying text collection index - calling functions should use CollectionWriter, which will route and manage
    the connection to the underlying DB resource"""

    def __init__(self, library_name, account_name="llmware", db_name=None, custom_table=False, custom_schema=None):

        self.library_name = library_name
        self.account_name = account_name

        self.supported_collection_db = LLMWareConfig().get_supported_collection_db()

        if db_name:
            self.active_db = db_name
        else:
            self.active_db = LLMWareConfig().get_active_db()

        self._writer = None

        if self.active_db in self.supported_collection_db:

            if self.active_db == "mongo":
                self._writer = MongoWriter(self.library_name, account_name=self.account_name, custom_table=custom_table,
                                           custom_schema=custom_schema)

            if self.active_db == "postgres":
                self._writer = PGWriter(self.library_name, account_name=self.account_name, custom_table=custom_table,
                                        custom_schema=custom_schema)

            if self.active_db == "sqlite":
                self._writer = SQLiteWriter(self.library_name, account_name=self.account_name, custom_table=custom_table,
                                            custom_schema=custom_schema)

        else:
            raise UnsupportedCollectionDatabaseException(self.active_db)

    def build_text_index(self):
        """Builds text index using db-specific methods"""
        self._writer.build_text_index()
        return 1

    def check_if_table_build_required(self):
        """Checks if table build required- returns True if table build required, e.g., no table found
        and building table schema is required by the DB resource"""

        build_table = self._writer.check_if_table_build_required()

        return build_table

    def create_table(self, table_name, schema):
        """Creates table"""
        return self._writer.create_table(table_name, schema)

    def write_new_record(self, new_record):
        """Inserts new record to the DB resource - unpacks and validates the new_record dict, if required """
        return self._writer.write_new_record(new_record)

    def write_new_parsing_record(self, new_record):
        """Inserts new parsing record to the DB resource """
        return self._writer.write_new_parsing_record(new_record)

    def destroy_collection(self, confirm_destroy=False):
        """Drops the collection associated with the library"""
        return self._writer.destroy_collection(confirm_destroy=confirm_destroy)

    #TODO: may be able to remove - called only by Library.update_block
    def update_block(self, doc_id, block_id, key, new_value, default_keys):
        """Updates specific row, based on doc_id and block_id"""
        return self._writer.update_block(doc_id, block_id, key, new_value, default_keys)

    def update_one_record(self, filter_dict, key, new_value):
        """Updates one record selected by filter_dict"""
        return self._writer.update_one_record(filter_dict, key, new_value)

    #TODO:  may be able to remove - not called
    """
    def update_many_records(self, filter_dict, key, new_value):
        # Updates multiple records selected by filter_dict
        return self._writer.update_many_records(filter_dict, key, new_value)

    def update_many_records_custom(self, filter_dict, update_dict):
        # Updates many records custom using update_dict
        return self._writer.update_many_records_custom(filter_dict, update_dict)
    """

    def replace_record(self, filter_dict, new_entry):
        """Deletes and replaces selected record"""
        return self._writer.replace_record(filter_dict, new_entry)

    def delete_record_by_key(self, key, value):
        """Deletes single record by key and matching value"""
        return self._writer.delete_record_by_key(key, value)

    def update_library_card(self, library_name, update_dict, lib_card, delete_record=False):

        """Special update method to handle library card updates"""

        return self._writer.update_library_card(library_name, update_dict, lib_card, delete_record=delete_record)

    def get_and_increment_doc_id(self, library_name):

        """Gets and increments doc_id"""

        return self._writer.get_and_increment_doc_id(library_name)

    def set_incremental_docs_blocks_images(self, library_name, added_docs=0, added_blocks=0, added_images=0,
                                           added_pages=0, added_tables=0):

        """Updates counts on library card"""

        return self._writer.set_incremental_docs_blocks_images(library_name, added_docs=added_docs,
                                                               added_blocks=added_blocks,
                                                               added_images=added_images, added_pages=added_pages,
                                                               added_tables=added_tables)

    def add_new_embedding_flag(self, _id, embedding_key, value):
        """Updates JSON column of one record by adding new key:value"""
        return self._writer.add_new_embedding_flag(_id, embedding_key,value)

    def unset_embedding_flag(self, embedding_key):
        return self._writer.unset_embedding_flag(embedding_key)

    def close(self):
        """Close connection to underlying DB resource"""
        return self._writer.close()


class MongoWriter:

    """MongoWriter is main class abstraction for writes, edits and deletes to a Mongo text index collection"""

    def __init__(self, library_name, account_name="llmware", custom_table=False, custom_schema=None):

        self.library_name = library_name
        self.account_name = account_name
        self.uri_string = LLMWareConfig.get_db_uri_string()

        # initiate connection to Mongo resource
        self.collection = _MongoConnect().connect(db_name=account_name, collection_name=library_name)

        self.custom_table = custom_table
        self.custom_schema = custom_schema

    def build_text_index(self):
        """Builds Mongo text search index"""
        self.collection.create_index([("text_search", "text")])
        return True

    def check_if_table_build_required(self):
        """Always returns False, since no table build steps required for Mongo no-sql DB"""
        return False

    def create_table(self, table_name, schema):
        """No table creation steps required in Mongo DB"""
        return True

    def write_new_record(self, new_record):
        """Inserts one new record in Mongo collection"""

        if "_id" in new_record:
            new_record.update({"_id": ObjectId(new_record["_id"])})

        registry_id = self.collection.insert_one(new_record).inserted_id

        return 1

    def write_new_parsing_record(self, new_record):
        """ Writes new parsing record into Mongo DB """
        return self.write_new_record(new_record)

    def destroy_collection(self, confirm_destroy=False):

        """Drops collection for library"""
        if confirm_destroy:
            self.collection.drop()
            return 1

        logger.warning("update: library not destroyed - need to set confirm_destroy = True")
        return 0

    def update_block (self, doc_id, block_id, key, new_value, default_keys):

        """Selects specific (doc_id, block_id) and updates with {key:new_value}"""

        completed = False

        f = {"$and": [{"block_ID": block_id}, {"doc_ID": doc_id}]}

        if key in default_keys:
            new_values = {"$set": {key: new_value}}
            self.collection.update_one(f,new_values)
            completed = True

        return completed

    def update_one_record(self, filter_dict, key,new_value):

        """Updates one record selected by filter_dict, with {key:new_value}"""

        if "_id" in filter_dict:
            filter_dict.update({"_id": ObjectId(filter_dict["_id"])})

        new_values = {"$set": {key:new_value}}
        self.collection.update_one(filter_dict, new_values)
        return 0

    """
    def update_many_records(self, filter_dict, key, new_value):

        # Updates many records selected by filter_dict, with {key:new_value}

        if "_id" in filter_dict:
            filter_dict.update({"_id": ObjectId(filter_dict["_id"])})

        new_values = {"$set": {key :new_value}}
        self.collection.update_many(filter_dict, new_values)
        return 0
    """
    """
    def update_many_records_custom(self, filter_dict, update_dict):

        # Updates many records using custom filter dict and potentially multiple updates

        if "_id" in filter_dict:
            filter_dict.update({"_id": ObjectId(filter_dict["_id"])})

        self.collection.update_many(filter_dict, update_dict)
        return 0
    """

    def replace_record(self, filter_dict, new_entry):

        """Replaces record in MongoDB collection"""

        if "_id" in filter_dict:
            filter_dict.update({"_id": ObjectId(filter_dict["_id"])})

        self.collection.replace_one(filter_dict, new_entry, upsert=True)

        return 1

    def delete_record_by_key(self,key,value):

        """Deletes record by key matching value"""

        if key == "_id":
            value = ObjectId(value)

        self.collection.delete_one({key:value})

        return 1

    def update_library_card(self, library_name, update_dict,lib_card, delete_record=False):

        """Updates library card in Mongo Library Catalog"""

        f = {"library_name": library_name}
        new_values = {"$set": update_dict}

        embedding_list = lib_card["embedding"]

        #   standard collection update for all except embedding
        if "embedding" not in update_dict:
            self.collection.update_one(f,new_values)

        else:
            # special flag to identify where to 'merge' and update an existing embedding record
            merged_embedding_update = False
            inserted_list = []

            if len(embedding_list) > 0:
                # if the last row is a "no" embedding, then remove it
                if embedding_list[-1]["embedding_status"] == "no":
                    del embedding_list[-1]

                for emb_records in embedding_list:

                    if emb_records["embedding_model"] == update_dict["embedding"]["embedding_model"] and \
                            emb_records["embedding_db"] == update_dict["embedding"]["embedding_db"]:

                        if not delete_record:
                            inserted_list.append(update_dict["embedding"])
                        else:
                            pass

                        merged_embedding_update = True

                        # catch potential error

                        if not delete_record:
                            if "embedded_blocks" in emb_records and "embedded_blocks" in update_dict["embedding"]:

                                if emb_records["embedded_blocks"] > update_dict["embedding"]["embedded_blocks"]:

                                    logger.warning(f"warning: may be issue with embedding - mis-alignment in "
                                                   f"embedding block count - "
                                                   f"{emb_records['embedded_blocks']} > "
                                                   f"{update_dict['embedding']['embedded_blocks']}")

                    else:
                        inserted_list.append(emb_records)

            if not merged_embedding_update:
                embedding_list.append(update_dict["embedding"])
                embedding_update_dict = {"embedding": embedding_list}
            else:
                embedding_update_dict = {"embedding": inserted_list}

            self.collection.update_one(f, {"$set": embedding_update_dict})

        return 1

    def get_and_increment_doc_id(self, library_name):

        """method called at the start of parsing each new doc -> each parser gets a new doc_id"""

        library_counts = self.collection.find_one_and_update(
            {"library_name": library_name},
            {"$inc": {"unique_doc_id": 1}},
            return_document=ReturnDocument.AFTER
        )

        unique_doc_id = library_counts.get("unique_doc_id",-1)

        return unique_doc_id

    def set_incremental_docs_blocks_images(self, library_name, added_docs=0, added_blocks=0, added_images=0,
                                           added_pages=0, added_tables=0):

        """updates counting parameters at end of parsing"""

        self.collection.update_one(
            {"library_name": library_name},
            {"$inc": {"documents": added_docs, "blocks": added_blocks, "images": added_images, "pages": added_pages,
                      "tables": added_tables
        }})

        return 0

    def add_new_embedding_flag(self,_id,  embedding_key, value):

        filter_dict = {"_id": _id}
        self.update_one_record (filter_dict, embedding_key, value)

        return 0

    def unset_embedding_flag(self, embedding_key):

        update = {"$unset": {embedding_key: ""}}
        self.collection.update_many({}, update)

        return 0

    def close(self):
        """Closes MongoDB connection"""
        # self.collection.close()
        return 0


class MongoRetrieval:

    """MongoRetrieval is primary class abstraction to handle queries to Mongo text collection"""

    def __init__(self, library_name, account_name="llmware", custom_table=False, custom_schema=None):

        self.library_name = library_name
        self.account_name = account_name
        self.uri_string = LLMWareConfig.get_db_uri_string()

        # establish connection at construction of retrieval object
        self.collection = _MongoConnect().connect(self.account_name,collection_name=self.library_name)

        self.reserved_tables = ["status", "library", "parser_events"]
        self.text_retrieval = False

        if library_name not in self.reserved_tables:
            self.text_retrieval = True

        self.custom_table = custom_table
        if custom_table:
            self.text_retrieval = False

    def safe_name(self, input_name):

        """ Mongo is flexible on collection names - for now, only filter is reserved collection names"""

        if input_name not in self.reserved_tables:
            output_name = input_name
        else:
            raise InvalidNameException(input_name)

        return output_name

    def test_connection(self,timeout_secs=5):

        """Tests and confirms if connected to MongoDB"""

        client = MongoClient(self.uri_string, unicode_decode_error_handler='ignore')

        # self.client.admin.authenticate(username, password)

        try:
            # catch if mongo not available
            with pymongo.timeout(timeout_secs):
                client.admin.command('ping')
                logger.info(f"update: mongo connected - collection db available at uri string - "
                            f"{self.uri_string}")
                db_status = True

        except ConnectionFailure:
            logger.warning(f"warning:  collection db not found at uri string in LLMWareConfig - "
                           f"{self.uri_string} - check connection and/or reset LLMWareConfig 'collection_db_uri' "
                           f"to point to the correct uri.")

            db_status = False

        return db_status

    def unpack(self, entry):

        """Unpack converts array row output to dictionary using schema, e.g., Identity function for MongoDB """

        output = entry

        if isinstance(entry, list):
            if len(entry) > 0:
                if isinstance(entry[0], dict):
                    output = entry[0]

        return output

    def lookup(self, key, value):

        """Returns list of dictionary entries representing results"""

        # special handling for reserved id in Mongo
        if key == "_id":

            try:
                value = ObjectId(value)
            except:
                logger.debug(f"update: mongo lookup - could not find _id into ObjectID - {value}")
                value = value

        target = list(self.collection.find({key:value}))

        return target

    def embedding_key_lookup(self, key, value):
        return self.lookup(key,value)

    def get_whole_collection(self):

        """Retrieves whole collection in Mongo- will return as a Cursor object"""

        # update: removing no_cursor_timeout=True
        # setting timeout to 30 minutes = 1,800,000 milliseconds
        all_output = self.collection.find({}).max_time_ms(1800000)

        cursor = DBCursor(all_output,self, "mongo")

        return cursor

    def basic_query(self, query):

        """Basic text index query in MongoDB"""

        match_results_cursor = self.collection.find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}).sort([('score', {'$meta': 'textScore'})]).allow_disk_use(True)

        return match_results_cursor

    def filter_by_key(self, key, value):

        """Returns a cursor of entries in which key matches value"""

        match_results_cursor = list(self.collection.find({key:value}))
        return match_results_cursor

    def text_search_with_key_low_high_range(self, query, key, low, high, key_value_dict=None):

        """Accepts key with low & high value + optional key_value_dict with additional parameters"""

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

        """Text search with additional constraint of key in provided value_range list"""

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

        """Text search with additional key_value filter dictionary applied"""

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

        """Returns distinct list of items by key"""
        # not using distinct operation
        # distinct can break due to the number of entries in the library
        # to prevent this from happen we use a aggregate which does not produce a document but a cursor
        # we loop the cursor and so we overcome the distinct operation 16mb document cap

        group = self.collection.aggregate([{ "$group": {"_id": f'${key}',}}])

        distinct_list = []
        for entry in group:
            distinct_list.append(entry['_id'])

        return distinct_list

    def filter_by_key_dict (self, key_dict):

        """Filters collection by key-value dictionary"""

        f = {}
        d = []
        for key, value in key_dict.items():
            d.append({key :value})

        # if one key-value pair, then simple filter
        if len(d) == 1: f = d[0]

        # if multiple key-value pairs, then insert list with "$and"
        if len(d) >= 2: f= {"$and":d}

        results = list(self.collection.find(f))

        return results

    def filter_by_key_value_range(self, key, value_range):

        """Filter by key matching value_range list, e.g., {"doc_ID": [1,2,3,4,5]}"""

        results = list(self.collection.find({key: {"$in": value_range}}))
        return results

    def filter_by_key_ne_value(self, key, value):

        """Filter by key not equal to specific value"""

        f = {key: {"$ne":value}}
        output = list(self.collection.find(f))
        return output

    def count_documents(self, filter_dict):

        """Count documents that match filter conditions"""

        num_of_blocks = self.collection.count_documents(filter_dict)
        return num_of_blocks

    def embedding_job_cursor(self, new_embedding_key,doc_id=None):

        """Handles end-to-end retrieval of text blocks selected for embedding - returns Cursor"""

        if doc_id:
            filter_dict = {"doc_ID":{"$in": doc_id}}
            num_of_blocks = self.count_documents(filter_dict)
            all_blocks_cursor = self.collection.find(filter_dict)

        else:
            filter_dict = {new_embedding_key: {"$exists": False}}
            num_of_blocks = self.count_documents(filter_dict)
            all_blocks_cursor = self.collection.find(filter_dict)

        cursor = DBCursor(all_blocks_cursor,self, "mongo")

        return num_of_blocks, cursor

    def count_embedded_blocks(self, embedding_key):

        """Counts number of text blocks to be embedded in current embedding job scope"""

        filter_dict = {embedding_key: {"$exists": True}}
        embedded_blocks = self.count_documents(filter_dict)

        return embedded_blocks

    def close(self):
        """Closing MongoDB connection not required - no action taken"""
        # self.collection.close()
        return 0

    def direct_custom_query(self, query_filter):

        """Applies the custom query directly to the DB and returns the results"""

        # will force exhausting cursor iterable into list - designed for relatively small in-memory retrievals
        results = list(self.collection.find(query_filter))

        return results

    def list_all_tables(self):

        """Get list of all collections on the database"""
        # self.mongo_client = MongoDBManager().client[db_name][collection_name]

        results = list(MongoDBManager().client[self.account_name].list_collection_names())

        return results

    def get_schema(self, table_name):

        """ No schema in Mongo collections so returns empty value """

        table_schema = {}

        return table_schema


class PGRetrieval:

    """PGRetrieval is main class to handle interactions with Postgres DB for queries and retrieval -
    Embedding connections through PGVector are handled separately through EmbeddingPGVector class"""

    def __init__(self, library_name, account_name="llmware", custom_table=False, custom_schema=None):

        self.account_name = account_name
        self.library_name = library_name

        self.conn = _PGConnect().connect()

        self.reserved_tables = ["status", "library", "parser_events"]
        self.text_retrieval = False

        if library_name == "status":
            self.schema = LLMWareTableSchema().get_status_schema()
        elif library_name == "library":
            self.schema = LLMWareTableSchema().get_library_card_schema()
        elif library_name == "parser_events":
            self.schema = LLMWareTableSchema().get_parser_table_schema()
        else:
            self.schema = LLMWareTableSchema().get_block_schema()

        if library_name not in self.reserved_tables:
            self.text_retrieval = True

        self.custom_table=custom_table
        if custom_table:
            self.text_retrieval = False

            if custom_schema:
                self.schema = custom_schema

    def test_connection(self):

        """Test connection to Postgres database"""
        test = True

        try:
            # try to open and close connection
            test_connection = _PGConnect().connect()
            test_connection.close()
        except:
            # if error, then catch and fail test
            test = False

        return test

    def safe_name(self, input_name):

        """ Table names in Postgres must consist of alpha, numbers and _ -> does not permit '-' """

        if input_name not in self.reserved_tables:
            output_name = re.sub("-","_", input_name)
        else:
            raise InvalidNameException(input_name)

        return output_name

    def unpack(self, results_cursor):

        """Iterate through rows of results_cursor and builds dictionary output rows using schema"""

        output = []

        for row in results_cursor:

            counter = 0
            new_dict = {}

            for key, value in self.schema.items():

                if key != "PRIMARY KEY":
                    if counter < len(row):
                        if key == "text_block":
                            key = "text"
                        if key == "table_block":
                            key = "table"
                        new_dict.update({key: row[counter]})
                        counter += 1
                    else:
                        logger.warning(f"update: pg_retriever - outputs not matching - {counter}")

            output.append(new_dict)

        return output

    def unpack_search_result(self, results_cursor):

        """Iterate through rows of results_cursor and builds dictionary output rows using schema"""

        output = []

        for row in results_cursor:

            counter = 0
            new_dict = {}
            new_dict.update({"score": row[0]})
            counter += 1

            for key, value in self.schema.items():

                if key != "PRIMARY KEY":
                    if counter < len(row):
                        if key == "text_block":
                            key = "text"
                        if key == "table_block":
                            key = "table"
                        new_dict.update({key: row[counter]})
                        counter += 1
                    else:
                        logger.warning (f"update: pg_retriever - outputs not matching - {counter}")

            output.append(new_dict)

        return output

    def lookup(self, key, value):

        """Lookup returns entry with key (column) with matching value - returns as unpacked dict entry"""

        output = {}

        sql_query = f"SELECT * FROM {self.library_name} WHERE {key} = '{value}';"
        results = list(self.conn.cursor().execute(sql_query))

        if results:
            if len(results) >= 1:
                output = self.unpack(results)

        self.conn.close()

        return output

    def embedding_key_lookup(self, key, value):

        # lookup in json dictionary - special sql command
        output = []
        value = str(value)

        sql_query= f"SELECT * FROM {self.library_name} WHERE embedding_flags->>'{key}' = '{value}'"

        results = list(self.conn.cursor().execute(sql_query))

        if results:
            if len(results) >= 1:
                output = self.unpack(results)

        self.conn.close()

        return output

    def get_whole_collection(self):

        """Returns whole collection - as a Cursor object"""

        sql_command = f"SELECT * FROM {self.library_name}"
        results = self.conn.cursor().execute(sql_command)

        cursor = DBCursor(results,self, "postgres")

        # self.conn.close()

        return cursor

    def _prep_query(self, query):

        """ Simple query text preparation - will add more options over time """

        pg_strings = {"AND": " & ", "OR": " | "}

        exact_match = False
        # check if wrapped in quotes
        if query.startswith('"') and query.endswith('"'):
            exact_match = True

        # remove punctuation and split into tokens by whitespace
        q_clean = re.sub(r"[^\w\s]", "", query)
        q_toks = q_clean.split(" ")

        q_string = ""
        for tok in q_toks:
            q_string += tok
            if exact_match:
                # q_string += " & "
                q_string += pg_strings["AND"]
            else:
                # q_string += " | "
                q_string += pg_strings["OR"]

        if q_string.endswith(pg_strings["AND"]):
            q_string = q_string[: -len(pg_strings["AND"])]

        if q_string.endswith(pg_strings["OR"]):
            # if q_string.endswith(" & ") or q_string.endswith(" | "):
            q_string = q_string[:-len(pg_strings["OR"])]

        return q_string

    def basic_query(self, query):

        """Basic Postgres tsquery text query"""

        search_string = self._prep_query(query)

        sql_query = f"SELECT ts_rank_cd (ts, to_tsquery('english', '{search_string}')) as rank, * " \
                    f"FROM {self.library_name} " \
                    f"WHERE ts @@ to_tsquery('english', '{search_string}') " \
                    f"ORDER BY rank DESC LIMIT 100 ;"

        results = self.conn.cursor().execute(sql_query)

        output_results = self.unpack_search_result(results)

        self.conn.close()

        return output_results

    def filter_by_key(self, key, value):

        """SELECT ... WHERE {key} = '{value}'"""

        output = [{}]

        sql_query = f"SELECT * FROM {self.library_name} WHERE {key} = '{value}';"
        results = self.conn.cursor().execute(sql_query)

        if results:
            output = self.unpack(results)

        self.conn.close()

        return output

    def text_search_with_key_low_high_range(self, query, key, low, high, key_value_dict=None):

        """Text search with additional constraint of matching column with value in specified range"""

        search_string = self._prep_query(query)

        sql_query = f"SELECT ts_rank_cd (ts, to_tsquery('english', '{search_string}')) as rank, * " \
                    f"FROM {self.library_name} " \
                    f"WHERE ts @@ to_tsquery('english', '{search_string}') " \
                    f"AND {key} BETWEEN {low} AND {high}"

        if key_value_dict:
            for key, value in key_value_dict.items():
                sql_query += f" AND {key} = {value}"

        sql_query += " ORDER by rank"
        sql_query += ";"

        results = self.conn.cursor().execute(sql_query)

        output_results = self.unpack_search_result(results)

        self.conn.close()

        return output_results

    def text_search_with_key_value_range(self, query, key, value_range_list, key_value_dict=None):

        """Text search with additional constraint(s) of keys matching values in value_range list and
            optional key_value_dict"""

        search_string = self._prep_query(query)

        ia_str = "("
        for v in value_range_list:
            if isinstance(v, int):
                ia_str += str(v)
            else:
                ia_str += "'" + v + "'"
            ia_str += ", "
        if ia_str.endswith(", "):
            ia_str = ia_str[:-2]
        ia_str += ")"

        # ia_str = "(1)"

        sql_query = f"SELECT ts_rank_cd (ts, to_tsquery('english', '{search_string}')) as rank, * " \
                    f"FROM {self.library_name} " \
                    f"WHERE ts @@ to_tsquery('english', '{search_string}') " \
                    f"AND {key} IN {ia_str}"

        if key_value_dict:
            for key, value in key_value_dict.items():
                sql_query += f" AND {key} = {value}"

        sql_query += " ORDER BY rank"
        sql_query += ";"

        results = self.conn.cursor().execute(sql_query)

        output_results = self.unpack_search_result(results)

        self.conn.close()

        return output_results

    def text_search_with_key_value_dict_filter(self, query, key_value_dict):

        """Text search with additional "AND" constraints of key value dict with key = value"""

        search_string = self._prep_query(query)

        sql_query = f"SELECT ts_rank_cd (ts, to_tsquery('english', '{search_string}')) as rank, * " \
                    f"FROM {self.library_name} " \
                    f"WHERE ts @@ to_tsquery('english', {search_string})"

        if key_value_dict:
            for key, value in key_value_dict.items():

                if isinstance(value,list):

                    # need to check this
                    value_range = str(value)
                    value_range = value_range.replace("[", "(")
                    value_range = value_range.replace("]", ")")

                    sql_query += f" AND {key} IN {value_range}"
                else:
                    sql_query += f" AND {key} = '{value}'"

        sql_query += " ORDER BY rank"
        sql_query += ";"

        results = self.conn.cursor().execute(sql_query)
        output_results = self.unpack_search_result(results)

        self.conn.close()

        return output_results

    def get_distinct_list(self, key):

        """Returns distinct list by col (key)"""

        sql_query = f"SELECT DISTINCT {key} FROM {self.library_name};"
        results = self.conn.cursor().execute(sql_query)

        output = []
        for res in results:
            if res:
                if len(res) > 0:
                    output.append(res[0])

        self.conn.close()

        return output

    def filter_by_key_dict (self, key_dict):

        """Returns rows selected by where conditions set forth in key-value dictionary"""

        sql_query = f"SELECT * FROM {self.library_name}"

        conditions_clause = " WHERE"
        for key, value in key_dict.items():

            #   handles passing a filter with 'mongo' style $in key range
            if isinstance(value,dict):
                if "$in" in value:
                    value = value["$in"]

                    logger.debug(f"update: Postgres - filter_by_key_dict - value - {value}")

                    if isinstance(value,list):
                        v_str = "("
                        for entry in value:
                            v_str += str(entry) + ","
                        if v_str.endswith(","):
                            v_str = v_str[:-1]
                        v_str += ")"
                        conditions_clause += f" {key} IN {v_str} AND "
            else:

                conditions_clause += f" {key} = '{value}' AND "

        if conditions_clause.endswith(' AND '):
            conditions_clause = conditions_clause[:-5]
        if len(conditions_clause) > len(" WHERE"):
            sql_query += conditions_clause + ";"

        results = self.conn.cursor().execute(sql_query)

        output = self.unpack(results)

        self.conn.close()

        return output

    def filter_by_key_value_range(self, key, value_range):

        """Filter by key in value range, e.g., {"doc_ID": [1,2,3,4,5]}"""

        value_range_str = "("
        for v in value_range:
            value_range_str += "'" + str(v) + "'" + ", "
        if value_range_str.endswith(", "):
            value_range_str = value_range_str[:-2]
        value_range_str += ")"

        sql_query = f"SELECT * from {self.library_name} WHERE {key} IN {value_range_str};"

        results = self.conn.cursor().execute(sql_query)

        output = self.unpack(results)

        self.conn.close()

        return output

    def filter_by_key_ne_value(self, key, value):

        """Filter by col (key) not equal to specified value"""

        sql_query = f"SELECT * from {self.library_name} WHERE NOT {key} = {value};"

        results = self.conn.cursor().execute(sql_query)

        output = self.unpack(results)

        self.conn.close()

        return output

    def embedding_job_cursor(self, new_embedding_key, doc_id=None):

        """Handles end-to-end retrieval of text blocks selected for embedding job - returns Cursor"""

        if doc_id:

            # pull selected documents for embedding
            insert_array = ()
            insert_array += (tuple(doc_id),)

            sql_query = f"SELECT COUNT(*) FROM {self.library_name} WHERE doc_ID IN %s;"
            count_result = list(self.conn.cursor().execute(sql_query, insert_array))
            count = count_result[0]

            sql_query = f"SELECT * FROM {self.library_name} WHERE doc_ID IN %s;"
            results = self.conn.cursor().execute(sql_query, insert_array)

        else:

            # first get the total count of blocks 'un-embedded' with this key in the collection
            sql_query = f"SELECT COUNT(*) FROM {self.library_name} WHERE embedding_flags->>'{new_embedding_key}' " \
                        f"is NULL;"

            count_result = list(self.conn.cursor().execute(sql_query))
            count = count_result[0]

            sql_query = f"SELECT * FROM {self.library_name} WHERE embedding_flags->>'{new_embedding_key}' is NULL;"
            results = self.conn.cursor().execute(sql_query)

        cursor = DBCursor(results,self,"postgres")

        return count[0], cursor

    def count_embedded_blocks(self, embedding_key):

        """Counts the total number of blocks to be embedded in current job scope"""

        # send error code by default if can not count from db directly
        embedded_blocks = -1

        sql_query = f"SELECT COUNT(*) FROM {self.library_name} WHERE embedding_flags->>'{embedding_key}' is NOT NULL;"
        results = list(self.conn.cursor().execute(sql_query))

        if len(results) > 0:
            embedded_blocks = results[0]

            if not isinstance(embedded_blocks, int):
                if len(embedded_blocks) > 0:
                    embedded_blocks = embedded_blocks[0]

        self.conn.close()

        return embedded_blocks

    def count_documents(self, filter_dict):

        """Count documents that match filter conditions"""
        conditions_clause = ""

        if filter_dict:

            for key, value in filter_dict.items():
                conditions_clause += f"{key} = {value} AND "

            if conditions_clause.endswith(" AND "):
                conditions_clause = conditions_clause[:-5]

        if conditions_clause:
            sql_query = f"SELECT COUNT(*) FROM {self.library_name} WHERE {conditions_clause};"
        else:
            sql_query = f"SELECT COUNT(*) FROM {self.library_name};"

        results = list(self.conn.cursor().execute(sql_query))

        output = results[0]

        self.conn.close()

        return output

    def close(self):

        """Closes Postgres connection"""

        self.conn.close()
        return 0

    def direct_custom_query(self, query_filter):

        """Applies the custom query directly to the DB and returns the results"""
        results = list(self.conn.cursor().execute(str(query_filter)))
        # output = self.unpack(results)
        self.conn.close()
        return results

    def list_all_tables(self):

        """Get list of all tables on the database"""

        sql_query = f"SELECT * FROM pg_tables;"

        list_of_tables = list(self.conn.cursor().execute(sql_query))

        self.conn.close()

        return list_of_tables

    def get_schema(self, table_name):

        sql_query = (f"SELECT ordinal_position, column_name, data_type "
                     f"FROM information_schema.columns "
                     f"WHERE table_schema = 'public' "
                     f"AND table_name = '{table_name}';")

        # sql_query = f"SELECT * FROM pg_tables WHERE tablename = '{table_name}';"
        table_results = list(self.conn.cursor().execute(sql_query))
        self.conn.close()

        # unpack into a dictionary from list
        table_results_sorted = sorted(table_results, key=lambda x:x[0], reverse=False)
        schema_dict = {}
        for i, entry in enumerate(table_results_sorted):
            if len(entry) >= 3 and (entry[0]==i+1):
                if entry[1] not in schema_dict:
                    schema_dict.update({entry[1]:entry[2]})

        return schema_dict


class PGWriter:

    """PGWriter is main class abstraction to handle writing, indexing, modifying and deleting records in
    Postgres tables"""

    def __init__(self, library_name, account_name="llmware", custom_table=False, custom_schema=None):

        self.library_name = library_name
        self.account_name = account_name

        self.conn = _PGConnect().connect()

        #   simple lookup of schema by supported table type

        if library_name == "status":
            self.schema = LLMWareTableSchema().get_status_schema()

        elif library_name == "library":
            self.schema = LLMWareTableSchema().get_library_card_schema()

        elif library_name == "parser_events":
            self.schema = LLMWareTableSchema().get_parser_table_schema()

        else:
            # default is to assign as a 'block' text collection schema
            self.schema = LLMWareTableSchema().get_block_schema()

        self.reserved_tables = ["status", "library", "parser_events"]
        self.text_retrieval = False

        if library_name not in self.reserved_tables:
            self.text_retrieval = True

        self.custom_table = custom_table

        if custom_table:
            self.text_retrieval = False
            if custom_schema:
                self.schema = custom_schema

    def _add_search_column(self, search_col="ts"):

        """Creates ts_vector search column = ts to enable text_search on Postgres DB"""

        sql_add_ts_col = f"ALTER TABLE {self.library_name} ADD COLUMN {search_col} tsvector " \
                         f"GENERATED ALWAYS AS(to_tsvector('english', text_search)) STORED;"

        self.conn.execute(sql_add_ts_col)

        self.conn.commit()

        return 0

    def build_text_index(self):

        """Creates GIN index on new search column to enable text index search on Postgres DB"""

        sql_text_index_create = f"CREATE INDEX IF NOT EXISTS ts_idx ON {self.library_name} USING GIN(ts);"

        self.conn.execute(sql_text_index_create)
        self.conn.commit()
        self.conn.close()

        return 1

    def check_if_table_build_required(self):

        """Check if table already exists"""

        build_table = True
        table_name = self.library_name

        sql_query = f"SELECT * FROM pg_tables WHERE tablename = '{table_name}';"

        test_result = list(self.conn.cursor().execute(sql_query))

        if len(test_result) > 0:
            if table_name in test_result[0]:
                build_table = False

        # self.conn.close()

        return build_table

    def _build_sql_from_schema (self, table_name, schema):

        """Utility function to build sql from a schema dictionary"""

        table_create = f"CREATE TABLE IF NOT EXISTS {table_name} ("

        for key, value in schema.items():
            table_create += key + " " + value + ", "

        if table_create.endswith(", "):
            table_create = table_create[:-2]

        table_create += ");"

        return table_create

    def create_table(self, table_name, schema, add_search_column=True):

        """ Creates table with selected name and schema"""

        #   only add search index to library blocks collection using self.library_name

        if table_name in ["status", "library", "parser_events"] or self.custom_table:
            add_search_column = False
        else:
            add_search_column = True

        table_create = self._build_sql_from_schema(table_name, schema)

        self.conn.execute(table_create)

        if add_search_column:
            self._add_search_column()

        self.conn.commit()

        # close connection at end of update
        self.conn.close()

        return 1

    def write_new_record(self, new_record):

        """Writes new record - primary for creating new library card and status update"""

        keys_list = "("
        output_values = "("

        for keys, values in new_record.items():

            keys_list += keys + ", "

            new_entry = str(new_record[keys])
            new_entry = new_entry.replace("'", '"')

            output_values += "'" + new_entry + "'" + ", "

        if keys_list.endswith(", "):
            keys_list = keys_list[:-2]

        if output_values.endswith(", "):
            output_values = output_values[:-2]

        keys_list += ")"
        output_values += ")"

        sql_instruction = f"INSERT INTO {self.library_name} {keys_list} VALUES {output_values};"

        results = self.conn.cursor().execute(sql_instruction)

        self.conn.commit()

        self.conn.close()

        return 1

    def write_new_parsing_record(self, rec):

        """ Writes new parsing record dictionary into Postgres """

        sql_string = f"INSERT INTO {self.library_name}"
        sql_string += " (block_ID, doc_ID, content_type, file_type, master_index, master_index2, " \
                      "coords_x, coords_y, coords_cx, coords_cy, author_or_speaker, added_to_collection, " \
                      "file_source, table_block, modified_date, created_date, creator_tool, external_files, " \
                      "text_block, header_text, text_search, user_tags, special_field1, special_field2, " \
                      "special_field3, graph_status, dialog, embedding_flags) "

        sql_string += " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " \
                      "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

        # now unpack the new_record into parameters
        insert_arr = (rec["block_ID"], rec["doc_ID"],rec["content_type"], rec["file_type"], rec["master_index"],
                      rec["master_index2"], rec["coords_x"], rec["coords_y"], rec["coords_cx"], rec["coords_cy"],
                      rec["author_or_speaker"], rec["added_to_collection"], rec["file_source"], rec["table"],
                      rec["modified_date"], rec["created_date"], rec["creator_tool"], rec["external_files"],
                      rec["text"], rec["header_text"], rec["text_search"], rec["user_tags"],
                      rec["special_field1"], rec["special_field2"], rec["special_field3"], rec["graph_status"],
                      rec["dialog"], str(rec["embedding_flags"]))

        # note: sets embedding_flag value (last parameter) to "{}" = str({})

        results = self.conn.cursor().execute(sql_string,insert_arr)

        self.conn.commit()

        self.conn.close()

        return True

    def destroy_collection(self, confirm_destroy=False):

        """Drops table from database"""

        if confirm_destroy:

            sql_instruction = f"DROP TABLE {self.library_name};"

            #   returns TRUE if table does not exist & FALSE if table exists
            table_does_not_exist = self.check_if_table_build_required()

            #   if FALSE ... drop the table
            if not table_does_not_exist:
                results = self.conn.cursor().execute(sql_instruction)
                self.conn.commit()
                self.conn.close()
                return 1
            else:
                logger.warning(f"update: PGWriter - request to drop table not executed because table "
                               f"could not be found in the database.")
                return -1

        logger.warning("update: library not destroyed - need to set confirm_destroy = True")

        # self.conn.commit()
        self.conn.close()

        return 0

    def update_block (self, doc_id, block_id, key, new_value, default_keys):

        """Lookup block by doc_id & block_id and update with specific key and new value"""

        completed = False

        if key in default_keys:

            sql_instruction = f"UPDATE {self.library_name} "\
                              f"SET {key} = {new_value} " \
                              f"WHERE doc_ID = {doc_id} AND block_ID = {block_id};"

            completed = True
            results = self.conn.cursor().execute(sql_instruction)

            self.conn.commit()

        self.conn.close()

        return completed

    def update_one_record(self, filter_dict, key, new_value):

        """Updates one record"""

        conditions_clause = ""
        for k, v in filter_dict.items():
            conditions_clause += f"{k} = '{v}' AND"

        if conditions_clause.endswith(" AND"):
            conditions_clause = conditions_clause[:-4]

        if conditions_clause:
            sql_instruction = f"UPDATE {self.library_name} " \
                              f"SET {key} = '{new_value}' " \
                              f"WHERE {conditions_clause};"

            results = self.conn.cursor().execute(sql_instruction)
            self.conn.commit()

        self.conn.close()

        return 0

    def replace_record(self, filter_dict, new_entry):

        """Check if existing record with the same key - if so, delete, then create new"""

        new_values = "("
        for keys, values in new_entry.items():
            new_values += "'" + str(values) + "', "
        if new_values.endswith(", "):
            new_values = new_values[:-2]
        new_values += ")"

        conditions_clause = ""
        for keys, values in filter_dict.items():
            conditions_clause += f"{keys} = '{values}' AND"
        if conditions_clause.endswith(" AND"):
            conditions_clause = conditions_clause[:-4]

        sql_check = f"SELECT * FROM {self.library_name} WHERE {conditions_clause};"

        exists = list(self.conn.cursor().execute(sql_check))

        if exists:
            # need to delete, then replace with new record

            sql_delete = f"DELETE FROM {self.library_name} WHERE {conditions_clause};"
            self.conn.cursor().execute(sql_delete)

        sql_new_insert = f"INSERT INTO {self.library_name} VALUES {new_values};"

        self.conn.cursor().execute(sql_new_insert)
        self.conn.commit()

        self.conn.close()

        return 0

    def delete_record_by_key(self,key,value):

        """Deletes record found by matching key = value"""

        sql_command = f"DELETE FROM {self.library_name} WHERE {key} = '{value}';"
        self.conn.execute(sql_command)
        self.conn.commit()
        self.conn.close()
        return 0

    def update_library_card(self, library_name, update_dict, lib_card, delete_record=False):

        """Updates library card"""

        conditions_clause = f"library_name = '{library_name}'"

        update_embedding_record = False
        insert_array = ()

        update_clause = ""
        for key, new_value in update_dict.items():

            if key != "embedding":

                if isinstance(new_value, int):
                    # update_clause += f"{key} = {new_value}, "
                    update_clause += f"{key} = %s"
                    insert_array += (new_value,)
                else:
                    # update_clause += f"{key} = '{new_value}', "
                    update_clause += f"{key} = %s"
                    insert_array += (new_value,)
            else:
                # will update in second step
                current_emb_record = lib_card["embedding"]
                embedding_update = self._update_embedding_record_handler(current_emb_record, new_value,
                                                                         delete_record=delete_record)
                embedding_update = json.dumps(embedding_update)
                # embedding_update = str(embedding_update).replace("'", '"')
                # update_clause += f"{key} = '{embedding_update}', "
                update_clause += f"{key} = %s, "
                insert_array += (embedding_update,)

        if update_clause.endswith(", "):
            update_clause = update_clause[:-2]

        sql_instruction = f"UPDATE {self.library_name} " \
                          f"SET {update_clause} " \
                          f"WHERE {conditions_clause};"

        self.conn.cursor().execute(sql_instruction, insert_array)
        self.conn.commit()

        self.conn.close()

        return 1

    def _update_embedding_record_handler(self, embedding_list, new_value,delete_record=False):

        """Internal helper method to integrate embedding update into array of dicts- which
            is inserted as JSON directly in Postgres"""

        # special flag to identify where to 'merge' and update an existing embedding record
        merged_embedding_update = False
        inserted_list = []

        if len(embedding_list) > 0:
            # if the last row is a "no" embedding, then remove it
            if embedding_list[-1]["embedding_status"] == "no":
                del embedding_list[-1]

            for emb_records in embedding_list:

                if emb_records["embedding_model"] == new_value["embedding_model"] and \
                        emb_records["embedding_db"] == new_value["embedding_db"]:

                    if not delete_record:
                        inserted_list.append(new_value)
                    else:
                        pass

                    merged_embedding_update = True

                    # catch potential error

                    if not delete_record:
                        if "embedded_blocks" in emb_records and "embedded_blocks" in new_value:

                            if emb_records["embedded_blocks"] > new_value["embedded_blocks"]:

                                logger.warning(f"warning: may be issue with embedding - mis-alignment in "
                                                f"embedding block count - "
                                               f"{emb_records['embedded_blocks']} > {new_value['embedded_blocks']}")

                else:
                    inserted_list.append(emb_records)

        if not merged_embedding_update:
            embedding_list.append(new_value)

            output = embedding_list
        else:
            output = inserted_list

        return output

    def get_and_increment_doc_id (self, library_name):

        """Gets and increments unique doc ID"""

        val_out = -1

        val_array = (str(library_name),)

        sql_instruction = f"UPDATE library " \
                          f"SET unique_doc_id = unique_doc_id + 1 " \
                          f"WHERE library_name = %s " \
                          f"RETURNING unique_doc_id"

        result = self.conn.cursor().execute(sql_instruction, val_array)

        output = list(result)
        if len(output) > 0:
            val = output[0]
            if len(val) > 0:
                val_out = val[0]

        self.conn.commit()
        self.conn.close()

        return val_out

    def set_incremental_docs_blocks_images(self, library_name, added_docs=0, added_blocks=0, added_images=0,
                                           added_pages=0, added_tables=0):

        """Updates library card after update of new parsing jobs"""

        conditions_clause = f"library_name = '{library_name}'"

        set_clause = f"documents = documents + {added_docs}, " \
                     f"blocks = blocks + {added_blocks}, " \
                     f"images = images + {added_images}, " \
                     f"pages = pages + {added_pages}, " \
                     f"tables = tables + {added_tables}"

        sql_instruction = f"UPDATE {self.library_name} SET {set_clause} WHERE {conditions_clause};"

        results = self.conn.cursor().execute(sql_instruction)

        self.conn.commit()

        self.conn.close()

        return 0

    def add_new_embedding_flag(self, _id, embedding_key, value):

        insert_array = ()

        insert_json = f'X"{embedding_key}": "{value}"Y'
        insert_json = insert_json.replace("X", "{")
        insert_json = insert_json.replace("Y", "}")
        insert_json = "'" + insert_json + "'"
        insert_json += "::jsonb"

        json_dict = json.dumps({embedding_key:value})
        insert_array += (json_dict,)

        sql_command = f"UPDATE {self.library_name} " \
                      f"SET embedding_flags = coalesce(embedding_flags, 'XY') || %s WHERE _id = {_id}"
        sql_command = sql_command.replace("X","{")
        sql_command = sql_command.replace("Y","}")

        self.conn.cursor().execute(sql_command, insert_array)
        self.conn.commit()
        self.conn.close()

        return 0

    def unset_embedding_flag(self, embedding_key):

        """To complete deletion of an embedding, remove the json embedding_key from the text collection"""

        sql_instruction = f"UPDATE {self.library_name} " \
                          f"SET embedding_flags = embedding_flags - {embedding_key}" \
                          f"WHERE embedding_flags->>{embedding_key} IS NOT NULL"

        self.conn.cursor().execute(sql_instruction)
        self.conn.commit()
        self.conn.close()

        return 0

    def close(self):
        """Closes Postgres connection"""
        self.conn.close()
        return 0


class SQLiteRetrieval:

    """SQLiteRetrieval is main class abstraction to handle queries and retrievals from a SQLite DB running locally"""

    def __init__(self, library_name, account_name="llmware", custom_table=False, custom_schema=None):

        self.library_name = library_name
        self.account_name = account_name

        self.conn = _SQLiteConnect().connect(library_name)

        self.conn.text_factory = lambda b: b.decode(errors='ignore')

        self.reserved_tables = ["status", "library", "parser_events"]
        self.text_retrieval = False

        if library_name == "status":
            self.schema = LLMWareTableSchema().get_status_schema()

        elif library_name == "library":
            self.schema = LLMWareTableSchema().get_library_card_schema()

        elif library_name == "parser_events":
            self.schema = LLMWareTableSchema().get_parser_table_schema()

        else:
            self.schema = LLMWareTableSchema().get_block_schema()

        if library_name not in self.reserved_tables:
            self.text_retrieval = True

        self.custom_table = custom_table
        if custom_table:
            self.text_retrieval = False

            if custom_schema:
                self.schema = custom_schema

    def test_connection(self):

        """SQLite test connection always returns True - runs in file system"""

        return True

    def safe_name(self, input_name):

        """ Conforming table name rules in Sqlite to Postgres """

        if input_name not in self.reserved_tables:
            output_name = re.sub("-", "_", input_name)
        else:
            raise InvalidNameException(input_name)

        return output_name

    def unpack(self, results_cursor):

        """Iterate through rows of results_cursor and builds dictionary output rows using schema"""

        output = []

        for row in results_cursor:

            counter = 0
            new_dict = {}

            # assumes rowid included
            new_dict.update({"_id": row[0]})
            counter += 1

            for key, value in self.schema.items():

                if key not in ["_id","PRIMARY KEY"]:

                    if counter < len(row):

                        output_value = row[counter]

                        if key == "text_block":
                            key = "text"

                        if key == "table_block":
                            key = "table"

                        if key == "embedding":
                            output_value = ast.literal_eval(output_value)

                        new_dict.update({key: output_value})
                        counter += 1

                    else:
                        logger.warning(f"update: sqlite_retriever - outputs not matching -{counter}")

            output.append(new_dict)

        return output

    def unpack_search_result(self, results_cursor):

        """Iterate through rows of results_cursor and builds dictionary output rows using schema"""

        # assumes prepending of score + rowid

        output = []

        for row in results_cursor:

            counter = 0
            new_dict = {}
            new_dict.update({"score": row[0]})
            counter += 1
            new_dict.update({"_id": row[1]})
            counter += 1

            for key, value in self.schema.items():

                if key not in ["_id", "PRIMARY KEY"]:

                    if counter < len(row):

                        if key == "text_block":
                            key = "text"

                        if key == "table_block":
                            key = "table"

                        new_dict.update({key: row[counter]})
                        counter += 1

                    else:
                        logger.warning(f"update: sqlite_retriever - outputs not matching - {counter}")

            output.append(new_dict)

        return output

    def lookup(self, key, value):

        """Lookup of col (key) matching to value - returns unpacked dictionary result"""

        output = {}

        if key == "_id":
            key = "rowid"

        sql_query = f"SELECT rowid, * FROM {self.library_name} WHERE {key} = '{value}';"

        results = list(self.conn.cursor().execute(sql_query))

        if results:
            if len(results) >= 1:
                output = self.unpack(results)

        self.conn.close()

        return output

    def embedding_key_lookup(self, key, value):

        output = {}

        value = str(value)

        # lookup embedding_flag = value and value in special_field1
        sql_command = (f"SELECT rowid, * FROM {self.library_name} WHERE embedding_flags = '{key}' AND "
                       f"special_field1 = '{value}'")

        results = list(self.conn.cursor().execute(sql_command))

        if len(results) > 0:
            output = self.unpack(results)

        return output

    def get_whole_collection(self):

        """Returns whole collection - as a Cursor object"""

        sql_command = f"SELECT rowid, * FROM {self.library_name}"
        results = self.conn.cursor().execute(sql_command)

        cursor = DBCursor(results,self, "sqlite")

        return cursor

    def _prep_query(self, query):

        """ Basic preparation of text search query for SQLite - will evolve over time. """

        sqlite_strings = {"AND": " AND ", "OR": " OR "}

        exact_match = False
        # check if wrapped in quotes
        if query.startswith('"') and query.endswith('"'):
            exact_match = True

        # remove punctuation and split into tokens by whitespace
        q_clean = re.sub(r"[^\w\s]", "", query)
        q_toks = q_clean.split(" ")

        q_string = ""
        for tok in q_toks:
            q_string += tok
            if exact_match:
                # q_string += " & "
                q_string += sqlite_strings["AND"]
            else:
                # q_string += " | "
                q_string += sqlite_strings["OR"]

        if q_string.endswith(sqlite_strings["AND"]):
            q_string = q_string[:-len(sqlite_strings["AND"])]

        if q_string.endswith(sqlite_strings["OR"]):
            q_string = q_string[:-len(sqlite_strings["OR"])]

        return q_string

    def basic_query(self, query):

        """Basic text query on SQLite using FTS5 index"""

        query_str = self._prep_query(query)

        sql_query = f"SELECT rank, rowid, * FROM {self.library_name} " \
                    f"WHERE text_search MATCH '{query_str}' ORDER BY rank"

        results = self.conn.cursor().execute(sql_query)

        output = self.unpack_search_result(results)

        self.conn.close()

        return output

    def filter_by_key(self, key, value):

        """Returns rows in which col (key) = value"""

        # used for getting library card
        sql_query = f"SELECT rowid, * FROM {self.library_name} WHERE {key} = '{value}';"
        results = self.conn.cursor().execute(sql_query)

        output = self.unpack(results)

        self.conn.close()

        return output

    def text_search_with_key_low_high_range(self, query, key, low, high, key_value_dict=None):

        """Text search with additional filter of col (key) in low to high value range specified"""

        query_str = self._prep_query(query)

        sql_query = f"SELECT rank, rowid, * FROM {self.library_name} WHERE text_search MATCH '{query_str}' " \
                    f"AND {key} BETWEEN {low} AND {high}"

        if key_value_dict:
            for key, value in key_value_dict.items():
                sql_query += f" AND {key} = {value}"

        sql_query += " ORDER BY rank"
        sql_query += ";"

        results = self.conn.cursor().execute(sql_query)

        output = self.unpack_search_result(results)

        self.conn.close()

        return output

    def text_search_with_key_value_range(self, query, key, value_range_list, key_value_dict=None):

        """Text search with additional filter of key in value_range list with optional further key=value pairs
        in key_value_dict"""

        query_str = self._prep_query(query)

        # insert_array = (tuple(value_range_list),)
        # insert_array = tuple(value_range_list)
        # ia_str = str("(1)")
        # insert_array = value_range_list
        # insert_array = [1,]

        ia_str = "("
        for v in value_range_list:
            if isinstance(v, int):
                ia_str += str(v)
            else:
                ia_str += "'" + v + "'"
            ia_str += ", "
        if ia_str.endswith(", "):
            ia_str = ia_str[:-2]
        ia_str += ")"

        sql_query = f"SELECT rank, rowid, * FROM {self.library_name} WHERE text_search MATCH '{query_str}' " \
                    f"AND {key} IN {ia_str}"

        if key_value_dict:
            for key, value in key_value_dict.items():
                sql_query += f" AND {key} = '{value}'"

        sql_query += " ORDER BY rank"

        sql_query += ";"

        results = self.conn.cursor().execute(sql_query)
        output = self.unpack_search_result(results)

        self.conn.close()

        return output

    def text_search_with_key_value_dict_filter(self, query, key_value_dict):

        """Text search with additional 'AND' filter of key=value for all keys in key_value_dict"""

        query_str = self._prep_query(query)

        sql_query = f"SELECT rank, rowid, * FROM {self.library_name} WHERE text_search MATCH '{query_str}' "

        insert_array = ()

        if key_value_dict:
            for key, value in key_value_dict.items():

                if isinstance(value,list):

                    sql_query += f" AND ("

                    for items in value:
                        if isinstance(value,str):
                            sql_query += f" {key} = '{items}' OR "
                        else:
                            sql_query += f" {key} = {items} OR "

                    if sql_query.endswith("OR "):
                        sql_query = sql_query[:-3]
                    sql_query += ")"

                else:
                    if isinstance(value,str):
                        sql_query += f" AND {key} = '{value}'"
                    else:
                        sql_query += f" AND {key} = {value}"

        sql_query += " ORDER BY rank"
        sql_query += ";"

        results = self.conn.cursor().execute(sql_query, insert_array)
        output = self.unpack_search_result(results)

        self.conn.close()

        return output

    def get_distinct_list(self, key):

        """Gets distinct elements from list for selected col (key)"""

        sql_query = f"SELECT DISTINCT {key} FROM {self.library_name};"
        results = self.conn.cursor().execute(sql_query)

        output = []
        for res in results:
            if res:
                if len(res) > 0:
                    output.append(res[0])

        self.conn.close()

        return output

    def filter_by_key_dict (self, key_dict):

        """Filters and returns elements where key=value as specified by the key_dict"""

        sql_query = f"SELECT rowid, * FROM {self.library_name}"

        conditions_clause = " WHERE"
        for key, value in key_dict.items():

            #   handles passing a filter with 'mongo' style $in key range
            if isinstance(value,dict):
                if "$in" in value:
                    value = value["$in"]

                    logger.debug(f"update: SQLite - filter_by_key_dict - value - {value}")

                    if isinstance(value,list):
                        v_str = "("
                        for entry in value:
                            v_str += str(entry) + ","
                        if v_str.endswith(","):
                            v_str = v_str[:-1]
                        v_str += ")"
                        conditions_clause += f" {key} IN {v_str} AND "
            else:
                if isinstance(value, int):
                    conditions_clause += f" {key} = {value} AND "
                else:
                    conditions_clause += f" {key} = '{value}' AND "

            # conditions_clause += f" {key} = {value} AND "

        if conditions_clause.endswith(" AND "):
            conditions_clause = conditions_clause[:-5]

        if len(conditions_clause) > len(" WHERE"):
            sql_query += conditions_clause + ";"

        results = self.conn.cursor().execute(sql_query)

        output = self.unpack(results)

        self.conn.close()

        return output

    def filter_by_key_value_range(self, key, value_range):

        """Filter by key in value range, e.g., {"doc_ID": [1,2,3,4,5]}"""

        value_range_str = "("

        for v in value_range:
            value_range_str += "'" + str(v) + "'" + ", "

        if value_range_str.endswith(", "):
            value_range_str = value_range_str[:-2]

        value_range_str += ")"

        sql_query = f"SELECT rowid, * from {self.library_name} WHERE {key} IN {value_range_str};"

        results = self.conn.cursor().execute(sql_query)

        output = self.unpack(results)

        self.conn.close()

        return output

    def filter_by_key_ne_value(self, key, value):

        """Filters where key not equal to value"""

        sql_query = f"SELECT rowid, * from {self.library_name} WHERE NOT {key} = {value};"

        results = self.conn.cursor().execute(sql_query)

        output = self.unpack(results)

        self.conn.close()

        return output

    def embedding_job_cursor(self, new_embedding_key, doc_id=None):

        """Handles end-to-end retrieval of text blocks to be embedded - returns Cursor"""

        if doc_id:
            # pull selected documents for embedding
            insert_array = ()
            insert_array += (tuple(doc_id),)
            sql_query = f"SELECT COUNT(*) FROM {self.library_name} WHERE doc_ID IN %s;"
            results = list(self.conn.cursor().execute(sql_query, insert_array))
            count = results[0]

            sql_query = f"SELECT rowid, * FROM {self.library_name} WHERE doc_ID IN %s;"
            results = self.conn.cursor().execute(sql_query, insert_array)

        else:

            # Note: for SQLite - only designed for single embedding, not multiple embeddings on each block

            # first get the total count of blocks 'un-embedded' with this key in the collection
            sql_query = f"SELECT COUNT(*) FROM {self.library_name} WHERE embedding_flags IS NULL OR " \
                        f"embedding_flags != '{new_embedding_key}';"

            results = list(self.conn.cursor().execute(sql_query))
            count = results[0]

            sql_query = f"SELECT rowid, * FROM {self.library_name} WHERE embedding_flags IS NULL OR " \
                        f"embedding_flags != '{new_embedding_key}';"

            results = self.conn.cursor().execute(sql_query)

        results = list(results)

        cursor = DBCursor(results, self, "sqlite")

        return count[0], cursor

    def count_embedded_blocks(self, embedding_key):

        """Count all blocks to be embedded in current job scope"""

        sql_query = f"SELECT COUNT(*) FROM {self.library_name} WHERE embedding_flags = '{embedding_key}';"

        results = list(self.conn.cursor().execute(sql_query))

        embedded_blocks = results[0]

        self.conn.close()

        return embedded_blocks[0]

    def count_documents(self, filter_dict):

        """Count documents that match filter conditions"""

        conditions_clause = ""

        if filter_dict:

            for key, value in filter_dict.items():
                conditions_clause += f"{key} = '{value}' AND "

            if conditions_clause.endswith(" AND "):
                conditions_clause = conditions_clause[:-5]

        if conditions_clause:
            sql_query = f"SELECT COUNT(*) FROM {self.library_name} WHERE {conditions_clause};"
        else:
            sql_query = f"SELECT COUNT(*) FROM {self.library_name};"

        results = list(self.conn.cursor().execute(sql_query))

        output = results[0]

        self.conn.close()

        return output

    def close(self):
        """Closes SQLite connection"""
        self.conn.close()
        return 0

    def direct_custom_query(self, query_filter):
        """Applies the custom query directly to the DB and returns the results"""
        results = list(self.conn.cursor().execute(str(query_filter)))
        # output = self.unpack(results)
        self.conn.close()
        return results

    def list_all_tables(self):

        """Get list of all tables on the database"""

        sql_query = f"SELECT * FROM sqlite_master WHERE type = 'table';"

        results = self.conn.cursor().execute(sql_query)

        list_of_tables = list(self.conn.cursor().execute(sql_query))

        self.conn.close()

        return list_of_tables

    def get_schema(self, table_name):

        """ Lookup of table_schema for an input table_name - outputs 'create table schema string' that can
        be used directly as context in a text2sql inference """

        table_schema = ""
        schema_dict = {}
        primary_key = ""

        sql_query = f"SELECT * FROM sqlite_master WHERE type = 'table' AND name = '{table_name}';"

        table_schema_row = self.conn.cursor().execute(sql_query)
        table_schema_row = list(table_schema_row)

        if len(table_schema_row) > 0:

            #   in [0][4] is the original sql command to create the table,
            #   e.g., 'CREATE TABLE {table_name} (key1 datatype1, key2 datatype2, key3 datatype3, ...)'
            table_schema = table_schema_row[0][4]

            #   split to look only at the string portion inside ( )
            ts_split = table_schema.split("(")[-1]
            ts_split = ts_split.split(")")[0]

            #   split by ',' to get the individual chunks with key datatype
            ts_chunks = ts_split.split(",")

            for chunk in ts_chunks:

                found_primary_key = False

                if chunk.strip():

                    if chunk.strip().endswith("PRIMARY KEY"):
                        found_primary_key = True
                        chunk = chunk.strip()[:-len("PRIMARY KEY")]

                    #   remove any leading/trailing spaces and split by space
                    kv = chunk.strip().split(" ")

                    #   if well formed should be only two values - excluding PRIMARY KEY !
                    if len(kv) == 2:
                        schema_dict.update({kv[0]:kv[1]})

                    if found_primary_key:
                        primary_key = kv[0]

            if primary_key:
                schema_dict.update({"PRIMARY KEY": primary_key})

        return schema_dict


class SQLiteWriter:

    """SQLiteWriter is the main class abstraction to handle writes, indexes, edits and deletes on SQLite DB"""

    def __init__(self, library_name, account_name="llmware", custom_table=False, custom_schema=None):

        self.library_name = library_name
        self.account_name = account_name

        self.conn = _SQLiteConnect().connect(library_name)

        if library_name == "status":
            self.schema = LLMWareTableSchema().get_status_schema()

        elif library_name == "library":
            self.schema = LLMWareTableSchema().get_library_card_schema()

        elif library_name == "parser_events":
            self.schema = LLMWareTableSchema().get_parser_table_schema()

        else:
            self.schema = LLMWareTableSchema().get_block_schema()

        self.reserved_tables = ["status", "library", "parser_events"]
        self.text_retrieval = False

        if library_name not in self.reserved_tables:
            self.text_retrieval = True

        self.custom_table = custom_table

        if custom_table:
            self.text_retrieval = False
            if custom_schema:
                self.schema = custom_schema

    def build_text_index(self, index_col="text_search"):

        """No separate text index created on SQLite - created in Virtual Table at time of set up"""

        return True

    def check_if_table_build_required(self):

        """Checks if table exists, and if not, responds True that build is required"""

        sql_query = f"SELECT * FROM sqlite_master " \
                    f"WHERE type = 'table' AND name = '{self.library_name}';"

        results = self.conn.cursor().execute(sql_query)

        if len(list(results)) > 0:
            table_build = False
        else:
            table_build = True

        return table_build

    def _build_sql_virtual_table_from_schema (self, table_name, schema):

        table_create = f"CREATE VIRTUAL TABLE IF NOT EXISTS {table_name} USING fts5("

        for key, value in schema.items():

            if key not in ["_id", "PRIMARY KEY"]:
                table_create += key + ", "

        if table_create.endswith(", "):
            table_create = table_create[:-2]

        table_create += ");"

        return table_create

    def _build_sql_from_schema (self, table_name, schema):

        """Builds SQL table create string from schema dictionary"""

        table_create = f"CREATE TABLE IF NOT EXISTS {table_name} ("

        for key, value in schema.items():

            # replace jsonb with json for sqlite
            if value == "jsonb":
                value = "json"

            table_create += key + " " + value + ", "

        if table_create.endswith(", "):
            table_create = table_create[:-2]

        table_create += ");"

        return table_create

    def create_table(self, table_name, schema, add_search_column=True):

        """Builds SQL table"""

        if table_name not in ["library", "status", "parsing_events"] and not self.custom_table:

            # used for creating library text search index
            table_create = self._build_sql_virtual_table_from_schema(table_name, schema)

        else:
            # status, library, parser_events + any other structured table
            table_create = self._build_sql_from_schema(table_name, schema)

        self.conn.execute(table_create)
        self.conn.commit()

        # close connection at end of update
        self.conn.close()

        return 1

    def write_new_record(self, new_record):

        """Writes new record - primary for creating new library card and status update"""

        keys_list = "("
        output_values = "("

        for keys, values in new_record.items():
            keys_list += keys + ", "

            new_entry = str(new_record[keys])
            new_entry = new_entry.replace("'", '"')

            output_values += "'" + new_entry + "'" + ", "

        if keys_list.endswith(", "):
            keys_list = keys_list[:-2]

        if output_values.endswith(", "):
            output_values = output_values[:-2]

        keys_list += ")"
        output_values += ")"

        sql_instruction = f"INSERT INTO {self.library_name} {keys_list} VALUES {output_values};"

        results = self.conn.cursor().execute(sql_instruction)

        self.conn.commit()

        self.conn.close()

        return 1

    def write_new_parsing_record(self, rec):

        """ Writes new parsing record dictionary into SQLite """

        sql_string = f"INSERT INTO {self.library_name}"
        sql_string += " (block_ID, doc_ID, content_type, file_type, master_index, master_index2, " \
                      "coords_x, coords_y, coords_cx, coords_cy, author_or_speaker, added_to_collection, " \
                      "file_source, table_block, modified_date, created_date, creator_tool, external_files, " \
                      "text_block, header_text, text_search, user_tags, special_field1, special_field2, " \
                      "special_field3, graph_status, dialog, embedding_flags) "
        sql_string += " VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, " \
                      "$19, $20, $21, $22, $23, $24, $25, $26, $27, $28);"

        # now unpack the new_record into parameters
        insert_arr = (rec["block_ID"], rec["doc_ID"],rec["content_type"], rec["file_type"], rec["master_index"],
                      rec["master_index2"], rec["coords_x"], rec["coords_y"], rec["coords_cx"], rec["coords_cy"],
                      rec["author_or_speaker"], rec["added_to_collection"], rec["file_source"], rec["table"],
                      rec["modified_date"], rec["created_date"], rec["creator_tool"], rec["external_files"],
                      rec["text"], rec["header_text"], rec["text_search"], rec["user_tags"],
                      rec["special_field1"], rec["special_field2"], rec["special_field3"], rec["graph_status"],
                      rec["dialog"], "")

        # note: sets embedding flag - parameter $28 to "" by default

        results = self.conn.cursor().execute(sql_string,insert_arr)

        self.conn.commit()

        self.conn.close()

        return True

    def destroy_collection(self, confirm_destroy=False):

        """Drops table"""

        if confirm_destroy:

            sql_instruction = f"DROP TABLE {self.library_name};"

            #   returns TRUE if table does not exist & FALSE if table exists
            table_does_not_exist = self.check_if_table_build_required()

            #   if FALSE ... drop the table
            if not table_does_not_exist:
                results = self.conn.cursor().execute(sql_instruction)
                self.conn.commit()
                self.conn.close()
                return 1
            else:
                logger.warning(f"update: SQLiteWriter - request to drop table not executed because table "
                               f"could not be found in the database.")
                return -1

        logger.warning("update: library not destroyed - need to set confirm_destroy = True")
        self.conn.close()

        return 0

    def update_block (self, doc_id, block_id, key, new_value, default_keys):

        """Updates block by specified (doc_id, block_id) pair"""

        completed = False

        if key in default_keys:

            sql_instruction = f"UPDATE {self.library_name} "\
                              f"SET {key} = {new_value} " \
                              f"WHERE doc_ID = {doc_id} AND block_ID = {block_id};"

            completed = True
            results = self.conn.cursor().execute(sql_instruction)

        self.conn.close()

        return completed

    def update_one_record(self, filter_dict, key, new_value):

        """Updates one record"""

        conditions_clause = ""
        for k, v in filter_dict.items():
            conditions_clause += f"{k} = '{v}' AND"

        if conditions_clause.endswith(" AND"):
            conditions_clause = conditions_clause[:-4]

        if conditions_clause:
            sql_instruction = f"UPDATE {self.library_name} " \
                              f"SET {key} = '{new_value}' " \
                              f"WHERE {conditions_clause};"

            results = self.conn.cursor().execute(sql_instruction)
            self.conn.commit()

        self.conn.close()

        return 0

    def replace_record(self, filter_dict, new_entry):

        """Check if existing record with the same key - if so, delete, then create new"""

        new_values = "("
        for keys, values in new_entry.items():

            if keys not in ["_id"]:
                new_values += "'" + str(values) + "', "

        if new_values.endswith(", "):
            new_values = new_values[:-2]
        new_values += ")"

        conditions_clause = ""
        for keys, values in filter_dict.items():
            conditions_clause += f"{keys} = '{values}' AND"
        if conditions_clause.endswith(" AND"):
            conditions_clause = conditions_clause[:-4]

        sql_check = f"SELECT * FROM {self.library_name} WHERE {conditions_clause};"

        exists = list(self.conn.cursor().execute(sql_check))

        if exists:
            # need to delete, then replace with new record
            sql_delete = f"DELETE FROM {self.library_name} WHERE {conditions_clause};"
            self.conn.cursor().execute(sql_delete)

        sql_new_insert = f"INSERT INTO {self.library_name} VALUES {new_values};"

        self.conn.cursor().execute(sql_new_insert)
        self.conn.commit()

        self.conn.close()

        return 0

    def delete_record_by_key(self, key, value):

        """Deletes record by matching key = value"""

        sql_command = f"DELETE FROM {self.library_name} WHERE {key} = '{value}';"
        self.conn.execute(sql_command)
        self.conn.commit()
        self.conn.close()
        return 0

    def update_library_card(self, library_name, update_dict, lib_card, delete_record=False):

        """Updates library card"""

        conditions_clause = f"library_name = '{library_name}'"
        update_clause = ""

        for key, new_value in update_dict.items():

            if key != "embedding":

                if isinstance(new_value, int):
                    update_clause += f"{key} = {new_value}, "
                else:
                    update_clause += f"{key} = '{new_value}', "
            else:
                # will update in second step
                current_emb_record = lib_card["embedding"]
                embedding_update = self._update_embedding_record_handler(current_emb_record, new_value,
                                                                         delete_record=delete_record)
                # from pg- start
                embedding_update=str(embedding_update)
                embedding_update=embedding_update.replace("'", '"')
                update_clause += f"{key} = '{embedding_update}', "
                # from pg- end

        if update_clause.endswith(", "):
            update_clause = update_clause[:-2]

        sql_instruction = f"UPDATE {self.library_name} " \
                          f"SET {update_clause} " \
                          f"WHERE {conditions_clause};"

        self.conn.cursor().execute(sql_instruction)
        self.conn.commit()

        self.conn.close()

        return 1

    def _update_embedding_record_handler(self, embedding_list, new_value, delete_record=False):

        """Internal helper method to integrate embedding update into array of dicts- which
            is inserted as JSON directly in Postgres"""

        # special flag to identify where to 'merge' and update an existing embedding record
        merged_embedding_update = False
        inserted_list = []

        if len(embedding_list) > 0:
            # if the last row is a "no" embedding, then remove it
            if embedding_list[-1]["embedding_status"] == "no":
                del embedding_list[-1]

            for emb_records in embedding_list:

                if emb_records["embedding_model"] == new_value["embedding_model"] and \
                        emb_records["embedding_db"] == new_value["embedding_db"]:

                    if not delete_record:
                        inserted_list.append(new_value)
                    else:
                        pass

                    merged_embedding_update = True

                    # catch potential error

                    if not delete_record:
                        if "embedded_blocks" in emb_records and "embedded_blocks" in new_value:

                            if emb_records["embedded_blocks"] > new_value["embedded_blocks"]:
                                logger.warning(f"warning: may be issue with embedding - mis-alignment in "
                                               f"embedding block count - {emb_records['embedded_blocks']} > "
                                               f"{new_value['embedded_blocks']}")

                else:
                    inserted_list.append(emb_records)

        if not merged_embedding_update:
            embedding_list.append(new_value)

            output = embedding_list
        else:
            output = inserted_list

        return output

    def get_and_increment_doc_id(self, library_name):

        """Gets and increments unique doc ID"""

        val_out = -1

        val_array = (str(library_name),)

        sql_instruction = f"UPDATE library " \
                          f"SET unique_doc_id = unique_doc_id + 1 " \
                          f"WHERE library_name = '{library_name}' " \
                          f"RETURNING unique_doc_id"

        result = self.conn.cursor().execute(sql_instruction)

        output = list(result)
        if len(output) > 0:
            val = output[0]
            if len(val) > 0:
                val_out = val[0]

        self.conn.commit()
        self.conn.close()

        return val_out

    def set_incremental_docs_blocks_images(self, library_name, added_docs=0, added_blocks=0, added_images=0,
                                           added_pages=0, added_tables=0):

        """Increments key counters on library card post parsing"""

        conditions_clause = f"library_name = '{library_name}'"

        set_clause = f"documents = documents + {added_docs}, " \
                     f"blocks = blocks + {added_blocks}, " \
                     f"images = images + {added_images}, " \
                     f"pages = pages + {added_pages}, " \
                     f"tables = tables + {added_tables}"

        sql_instruction = f"UPDATE {self.library_name} SET {set_clause} WHERE {conditions_clause};"

        results = self.conn.cursor().execute(sql_instruction)

        self.conn.commit()

        self.conn.close()

        return 0

    def add_new_embedding_flag(self, _id, embedding_key, value):

        """SQLite implementation saves new embedding flag in column and replaces any previous values"""

        # the embedding key name is saved in embedding_flags, and the index is saved in special_field1

        insert_array = ()

        insert_array += (embedding_key,)
        value=str(value)

        sql_command = f"UPDATE {self.library_name} " \
                      f"SET embedding_flags = '{embedding_key}', special_field1 = '{value}' " \
                      f"WHERE rowid = {_id}"

        self.conn.cursor().execute(sql_command)
        self.conn.commit()

        self.conn.close()

        return 0

    def unset_embedding_flag(self, embedding_key):

        """To complete deletion of an embedding, remove the json embedding_key from the text collection"""

        sql_instruction = f"UPDATE {self.library_name} " \
                          f"SET embedding_flags = ''" \
                          f"WHERE embedding_flags = '{embedding_key}';"

        self.conn.cursor().execute(sql_instruction)
        self.conn.commit()
        self.conn.close()

        return 0

    def close(self):
        """Closes SQLite connection"""
        self.conn.close()
        return 0


class _PGConnect:

    """_PGConnect returns a Postgres DB connection"""

    def __init__(self):

        #   Connect to postgres
        self.postgres_host = None
        self.postgres_port = None
        self.postgres_db_name = None
        self.postgres_user_name = None
        self.postgres_full_schema = None
        self.postgres_pw = None

        self.conn = None

    def connect(self, db_name=None, collection_name=None):

        """Connect to Postgres DB - using config data in PostgresConfig"""

        self.postgres_host = PostgresConfig().get_config("host")
        self.postgres_port = PostgresConfig().get_config("port")
        self.postgres_user_name = PostgresConfig().get_config("user_name")
        self.postgres_pw = PostgresConfig().get_config("pw")

        #   postgres will use the configured db name
        # if db_name: self.postgres_db_name = db_name

        self.postgres_db_name = PostgresConfig().get_config("db_name")

        self.conn = psycopg.connect(host=self.postgres_host, port=self.postgres_port, dbname=self.postgres_db_name,
                                    user=self.postgres_user_name, password=self.postgres_pw)

        return self.conn


class _SQLiteConnect:

    """_SQLiteConnect returns a connection to a SQLite DB running locally"""

    def __init__(self):
        self.conn = None

        #   check for llmware path & create if not already set up, e.g., "first time use"
        if not os.path.exists(LLMWareConfig.get_llmware_path()):
            LLMWareConfig.setup_llmware_workspace()
            logger.info("_SQliteConnect - Setting up LLMWare Workspace.")

    def connect(self, db_name=None, collection_name=None):

        """Connect to SQLite DB - using configuration parameters in SQLiteConfig"""

        # db_file = os.path.join(SQLiteConfig.get_db_fp(), "sqlite_llmware.db")
        db_file = SQLiteConfig.get_uri_string()

        self.conn = sqlite3.connect(db_file)

        return self.conn


class _MongoConnect:

    """_MongoConnect returns a connection to a Mongo collection"""

    def __init__(self):

        # self.collection_db_path = LLMWareConfig.get_config("collection_db_uri")
        self.collection_db_path = LLMWareConfig.get_db_uri_string()
        # self.client = MongoClient(self.collection_db_path, unicode_decode_error_handler='ignore')
        self.mongo_client = None
        self.timeout_secs = 5

    def connect(self, db_name=None,collection_name=None):

        """Connect to Mongo DB collection"""

        self.mongo_client = MongoDBManager().client[db_name][collection_name]
        return self.mongo_client


class MongoDBManager:

    """This is internal class - recommended as best practice by Mongo to manage connection threads"""

    class __MongoDBManager:

        def __init__(self):

            # self.collection_db_path = LLMWareConfig.get_config("collection_db_uri")
            self.collection_db_path = LLMWareConfig.get_db_uri_string()

            # default client is Mongo currently
            self.client = MongoClient(self.collection_db_path, unicode_decode_error_handler='ignore')
            # self.client.admin.authenticate(username, password)

    __instance = None

    def __init__(self):

        if not MongoDBManager.__instance:
            MongoDBManager.__instance = MongoDBManager.__MongoDBManager()

    def __getattr__(self, item):
        return getattr(self.__instance, item)


class DBCursor:

    """Wrapper class around database cursors to handle specific cursor management across DBs"""

    def __init__(self, cursor, collection_retriever, db_name, close_when_exhausted=True, return_dict=True, schema=None):

        self.cursor = iter(cursor)
        self.collection_retriever = collection_retriever
        self.db_name = db_name
        self.close_when_exhausted = close_when_exhausted
        self.return_dict = return_dict
        self.schema = schema

    def pull_one(self):

        """Calls next on the iterable cursor to pull one new row off the cursor and return to calling function"""

        try:
            new_row = next(self.cursor)

        except StopIteration:
            # The cursor is empty (no blocks found)
            new_row = None
            if self.close_when_exhausted:
                self.collection_retriever.close()

        if new_row and self.return_dict and not isinstance(new_row,dict):
            return self.collection_retriever.unpack([new_row])[0]

        return new_row

    def pull_all(self):

        """Exhausts remaining cursor and returns to calling function"""

        output = []

        while True:

            new_entry = self.pull_one()

            if not new_entry:
                break
            else:
                output.append(new_entry)

        """   
        for entries in self.cursor:

            if self.return_dict and not isinstance(entries,dict):
                output.append(self.collection_retriever.unpack(entries))
            else:
                output.append(entries)
        """

        return output


class CustomTable:

    """ CustomTable resource that can be implemented on a LLMWare collection database using consistent set of methods
    and utilities.   Intended for creation of supporting tables and leveraging structured and semi-structured
    information in conjunction with LLM-based workflows and for easier integration of supporting tables in
    larger projects. """

    def __init__(self, db=None, table_name=None, schema=None, library_name=None, account_name="llmware",
                 auto_correct_schema_errors=True,auto_correct_postpend="_d"):

        #   check for llmware path & create if not already set up, e.g., "first time use"
        if not os.path.exists(LLMWareConfig.get_llmware_path()):
            LLMWareConfig.setup_llmware_workspace()
            logger.info("CustomTable - Setting up LLMWare Workspace.")

        if not db:
            self.db = LLMWareConfig().get_active_db()
        else:
            if db in LLMWareConfig().get_supported_collection_db():
                self.db = db

        self.reserved_tables = ["status", "library", "parser_events"]

        #   this list will be improved over time to include common reserved col names
        self.reserved_col_names = ["table","text"]

        if table_name not in self.reserved_tables:
            self.table_name = table_name
        else:
            logger.warning(
                f"error: proposed custom table name - {table_name} - is a reserved table name and can not be used.  "
                f"self.table_name is being set to None, and will need to be set to a different name before using.")

            self.table_name = None

        self.schema = schema
        self.library_name = library_name
        self.account_name = account_name
        self.db_connection = None

        #   if schema column name is in reserved list, then will add the value of schema_postpend to end of string
        self.auto_correct_schema_errors = auto_correct_schema_errors
        self.postpend = auto_correct_postpend

        #   attributes used when loading a custom csv or json/jsonl to populate a table
        self.rows = None
        self.col_numbers = []
        self.col_names = []
        self.column_map = {}
        self.sql_create_table = None

        #   check if table_name already registered in LLMWareTableSchema
        if table_name in LLMWareTableSchema().get_custom_tables() and not self.schema:

            self.schema = LLMWareTableSchema().get_custom_schema()[table_name]

        #   check if table already created in DB, and if not, create table
        if table_name and self.schema:

            if self.db != "mongo":
                self.build_table()

        #   confirm that table name and schema are registered in LLMWareTableSchema for easy future access
        if self.table_name and self.schema:
            LLMWareTableSchema().register_custom_schema(self.table_name, self.schema, replace=False)

    def build_table(self, table_name=None, schema=None):

        """ Method to explicitly build a new table with the table_name and schema passed.  This is not needed if
        both table_name and schema are passed in the constructor when instantiating the CustomTable. """

        if table_name:
            self.table_name = table_name

        if schema:
            self.schema = schema

        completed = False

        if self.table_name and self.schema:

            #   runs a quick check to identify common schema errors
            #   if auto_correct == True, then will attempt to remediate
            confirmation = self._check_and_remediate_schema()

            if confirmation:

                conn = self.get_connection(table_name=self.table_name, type="write")
                if conn.check_if_table_build_required():
                    conn.create_table(self.table_name, self.schema)
                conn.close()

                completed = True

            else:
                logger.warning(f"warning: could not successfully remediate schema - there is an issue with the "
                               f"current schema - please review and adjust.")
                complete = False

        else:
            logger.warning(f"warning: could not build_table since missing either table name, schema or both - "
                            f"table_name = {self.table_name} - schema = {self.schema}")
            completed = False

        return completed

    def _check_and_remediate_schema(self, schema=None):

        """ Internal method used in table build process to check that namespace of proposed schema do not conflict
        with any reserved terms or have other potential issues.  If auto_correct_schema_errors == True, then
        it will attempt to fix the schema and self.rows on the fly by identifying reserved keywords, and
        adding the designated 'postpend' value to the term, e.g., "_d"

        If auto_correct_schema_errors == False, and there are schema errors, then confirmation returned will be False.

        """

        if schema:
            self.schema = schema

        confirmation = True

        updated_schema = {}
        remediated_keys = []

        for k, v in self.schema.items():
            if k in self.reserved_col_names:
                logger.warning(f"warning: schema column name - {k} - in reserved column names list - will need to "
                               f"change before creating table.")
                updated_schema.update({k+self.postpend: v})
                remediated_keys.append(k)
                confirmation = False
            else:
                updated_schema.update({k:v})

        if not confirmation:
            if self.auto_correct_schema_errors:

                # remediated problematic names
                self.schema = updated_schema

                # change keys in self.rows
                updated_rows = []
                for x in range(0,len(self.rows)):
                    new_row = {}
                    for k,v in self.rows[x].items():
                        if k in self.reserved_col_names:
                            new_row.update({k+self.postpend: v})
                        else:
                            new_row.update({k:v})
                    updated_rows.append(new_row)

                self.rows = updated_rows
                confirmation = True

        return confirmation

    def get_connection(self, table_name=None, type="read"):

        """ Convenience method that gets a connection to the selected database with two connection types -
        'read' and 'write'. """

        if table_name:
            self.table_name = table_name

        if type == "read":
            self.db_connection = CollectionRetrieval(self.table_name, account_name=self.account_name,
                                                     db_name=self.db, custom_table=True, custom_schema=self.schema)

        if type == "write":
            self.db_connection = CollectionWriter(self.table_name, account_name=self.account_name,
                                                  db_name=self.db, custom_table=True, custom_schema=self.schema)

        if type not in ["read", "write"]:
            raise LLMWareException(message=f"Exception: not recognized connection type {type}")

        return self.db_connection

    def close_connection(self):

        """ Used by each method that opens a connection to explicitly close the connection at the end of the
        processing. """

        self.db_connection.close()
        return True

    def _get_best_guess_value_type(self, v):

        """ Simple utility function to check the value of a 'test row' element and use as the basis for an automated
        data type determination.  This can be replaced/supplemented with more sophisticated checks, or the data
        type can be explicitly passed as a more robust alternative. """

        # all data elements will be set to either: "text" | "float" | "integer"

        dt = "text"

        try:
            #  if whole number, then store in DB as 'integer'
            vt = int(v)
            dt = "integer"
            if self.db == "postgres":
                # for safety, pick the largest int data type
                dt = "bigint"

            # if there is a 0 value, then use float to be safe
            if vt == 0:
                dt = "float"

        except:
            try:
                #   if element can be converted to a python 'float', then store in DB as 'float'
                #   may evaluate if 'decimal' or 'numeric' is better default choice
                vt = float(v)
                dt = "float"
            except:
                # if can not convert to a python number, then store in DB as 'text'
                dt = "text"

        return dt

    def test_and_remediate_schema(self, samples=10, auto_remediate=True):

        """ Applies a larger test of the schema against the data held in CustomTable .rows attribute - will
        test the number of samples passed as an optional parameter.

        If auto_remediate == True (default), then it will automatically update the data type used in the schema to
        the 'safest' among the types found in the sample set. """

        updated_schema = {}

        for key, data_type in self.schema.items():

            if len(self.rows) < samples:
                samples = len(self.rows)

            samples_dt_list = []

            for x in range(0,samples):

                if key not in self.rows[x]:
                    logger.warning(f"warning:  CustomTable - test_and_remediate_schema - unexpected error - "
                                   f"key not found in row - {x} - {key} - {self.rows[x]}")
                else:
                    check_value = self.rows[x][key]
                    samples_dt_list.append(self._get_best_guess_value_type(check_value))

            #   simple decision tree - will add more options over time
            if "text" in samples_dt_list or data_type=="text":
                dt = "text"
            elif "float" in samples_dt_list or data_type=="float":
                dt = "float"
            elif "integer" in samples_dt_list or "bigint" in samples_dt_list and data_type in ["integer", "bigint"]:
                dt = "integer"
                if self.db == "postgres":
                    dt = "bigint"
            else:
                # when in doubt, assign 'text' as safest choice
                dt = "text"

            updated_schema.update({key: dt})

        if auto_remediate:
            self.schema = updated_schema

        return updated_schema

    def load_json(self, fp, fn, selected_keys=None, data_type_map=None, schema=None):

        """ Import JSON/JSONL file - build schema and 'rows' to be processed and loaded to DB.  Assumes that
        JSON/JSONL file is a well-formed 'pseudo-DB' with each entry consisting of elements with the same
        dictionary keys.

        -- If an optional list of selected_keys is passed, then it will be used to filter the elements
        found in the table, and only 'keys' in the 'selected_keys' list will be added to the schema.

        --If an optional (dictionary) key_data_type_map is passed, e.g., {"account_ID": "decimal"}, then the
         data type passed will be used in the database schema.   If no explicit data type provided, then
         it will use 'best guess' to determine a safe type.

         -- Assumes that entire file can be read in memory. This is intended for
        small tables and rapid prototyping - and not as a general purpose DB loading utility. """

        f = open(os.path.join(fp, fn), "r", encoding='utf-8-sig', errors='ignore')

        if fn.endswith(".json"):
            json_rows = json.load(f)

        elif fn.endswith(".jsonl"):
            json_rows = []
            for entries in f:
                row = json.loads(entries)
                json_rows.append(row)
        else:
            raise LLMWareException(message=f"Exception: File Type - {fn} - not supported - please use a .json or "
                                           f".jsonl file with this method.")

        #   get to list of rows, with each comprising a dictionary of keys
        if len(json_rows) == 0:
            raise LLMWareException(message="Exception: length of json rows == 0 - no content found suitable "
                                           "for DB ingestion.")

        #   assume that json_rows will be a list of dictionaries as default case
        if isinstance(json_rows, list):
            first_row = json_rows[0]
        else:
            # exception case - if inserting only 'one' row into DB with a small JSON file
            first_row = json_rows

        self.rows = []
        skipped_rows = []

        if not schema:

            # if no schema provided, then derive from data structure implicitly

            schema = {}

            for keys, values in first_row.items():

                add_key = True
                if selected_keys:
                    if keys not in selected_keys:
                        add_key = False

                if add_key:

                    dt = "text"
                    if data_type_map:
                        if keys in data_type_map:
                            dt = data_type_map[keys]
                        else:
                            dt = self._get_best_guess_value_type(values)
                    else:
                        dt = self._get_best_guess_value_type(values)

                    schema.update({keys:dt})

        #   assigns both the updated schema and rows to the attributes of the CustomTable
        self.schema = schema

        column_size = len(self.schema.items())

        # iterate thru all rows (and extract keys matching to schema from each row)
        for x in range(0,len(json_rows)):

            new_row = {}

            for k, v in json_rows[x].items():

                if k in self.schema:
                    new_row.update({k:v})

            if len(new_row.items()) != column_size:
                logger.warning(f"warning: on line - {x} - extracted elements - {len(new_row.items())} - does "
                               f"not map to the target column size - {column_size} - skipping row - {new_row}.")
                skipped_rows.append([x, json_rows[x]])

            else:
                self.rows.append(new_row)

        output = {"rows": len(self.rows), "columns": column_size, "schema": self.schema,
                  "skipped_rows": skipped_rows}

        return output

    @staticmethod
    def file_load (in_path, delimiter=",",encoding='utf-8-sig',errors='ignore'):

        """ Utility function provided inline - mirrors function in Utility class - basic configurable
        csv file loading with optional parameters to set delimiter (e.g., ',' '\t', etc.) and encoding.

        Returns a python list of lists in which each element corresponds to a 'row' of the spreadsheet, and is in turn,
        a list of each of the individual 'cells' of the csv. """

        record_file = open(in_path, encoding=encoding,errors=errors)
        c = csv.reader(record_file, dialect='excel', doublequote=False, delimiter=delimiter)
        output = []
        for lines in c:
            output.append(lines)
        record_file.close()

        return output

    def validate_json(self, fp, fn, key_list=None):

        """ Provides an assessment and validation of a json/jsonl file and readiness for insertion into a
        database.   Optional key_list can be passed to confirm validation of a specified (minimum) set of
        keys present in every row of the file.

        If no key_list provided, then the keys in the first row of the
        file will be used as the basis for all future rows.

        Output is a dictionary with analysis of rows, columns, keys, and any nonconforming rows.

        *** This method is intended to be used prior to loading a JSON/JSONL file into a CustomTable to assess
        readiness and any additional preparation steps. *** """

        f = open(os.path.join(fp, fn), "r", encoding='utf-8-sig', errors='ignore')

        if fn.endswith(".json"):
            json_rows = json.load(f)

        elif fn.endswith(".jsonl"):
            json_rows = []
            for entries in f:
                row = json.loads(entries)
                json_rows.append(row)
        else:
            raise LLMWareException(message=f"Exception: File Type - {fn} - not supported - please use a .json or "
                                           f".jsonl file with this method.")

        col_count_tracker = {}
        noted_list = []
        total_rows = len(json_rows)
        all_keys_present_in_row = 0

        if key_list:
            keys = key_list
        else:
            keys= []

        for x in range(0,total_rows):

            # if no key_list provided, then use the first row to identify the expected keys
            if x == 0 and not key_list:
                for k,v in json_rows[x].items():
                    if k not in keys:
                        keys.append(k)

            if x >= 0:
                all_keys_found = True
                for key in keys:
                    if key not in json_rows[x]:
                        noted_list.append([x,key, json_rows[x]])
                        all_keys_found = False
                if all_keys_found:
                    all_keys_present_in_row += 1

            row_elements = len(json_rows[x].items())
            if row_elements in col_count_tracker:
                col_count_tracker[row_elements] += 1
            else:
                col_count_tracker.update({row_elements: 1})

        most_common_column = max(col_count_tracker, key=col_count_tracker.get)
        match_percent = col_count_tracker[most_common_column] / total_rows

        if len(col_count_tracker.items()) > 1:
            logger.warning(f"warning: found more than one length - {col_count_tracker}")

            for x in range(0,total_rows):
                row_elements = len(json_rows[x].items())
                if row_elements != most_common_column:
                    noted_list.append([x,row_elements, json_rows[x]])

        output = {"rows": total_rows,
                  "columns": most_common_column,
                  "rows_with_all_keys_present": all_keys_present_in_row,
                  "conforming_rows_percent": match_percent,
                  "column_analysis": col_count_tracker,
                  "keys": keys,
                  "nonconforming_rows": noted_list}

        return output

    def validate_csv(self, fp, fn, delimiter=',', encoding='utf-8-sig'):

        """ Provides an assessment and validation of a csv file and readiness for insertion into a
        database.

        Output is a dictionary with analysis of rows, columns, and any nonconforming rows.

        *** This method is intended to be used prior to loading a CSV file into a CustomTable to assess
        readiness and any additional preparation steps. *** """

        #   load csv
        in_path = os.path.join(fp,fn)
        output = self.file_load(in_path,delimiter=delimiter,encoding=encoding,errors='ignore')

        col_count_tracker = {}
        noted_list = []
        total_rows = len(output)

        for x in range(0,total_rows):
            row_elements = len(output[x])
            if row_elements in col_count_tracker:
                col_count_tracker[row_elements] += 1
            else:
                col_count_tracker.update({row_elements: 1})

        most_common_column = max(col_count_tracker, key=col_count_tracker.get)
        match_percent = col_count_tracker[most_common_column] / total_rows

        if len(col_count_tracker.items()) > 1:
            logger.warning(f"warning: CustomTable - validate_csv - in reviewing the rows of the CSV - "
                           f"found more than one column length - {col_count_tracker}")

            for x in range(0,total_rows):
                row_elements = len(output[x])
                if row_elements != most_common_column:
                    noted_list.append([x,row_elements, output[x]])

        output = {"rows": total_rows,
                  "columns": most_common_column,
                  "conforming_rows_percent": match_percent,
                  "column_frequency_analysis": col_count_tracker,
                  "nonconforming_rows": noted_list}

        return output

    def load_csv(self, fp, fn, column_names=None, required_column_count=None, column_mapping_dict=None,
                 data_type_map=None, header_row=True, delimiter=',', encoding='utf-8-sig'):

        """ Import CSV file and extract schema and 'rows' to be loaded into DB. Assumes that CSV is a well-formed
        'pseudo-DB' with common set of elements in each row, and a first row that can be used to derive the
        column names.

        -- if optional column_names is passed, then these names will be used instead of the first row of the
        spreadsheet to derive names, with assumption that the column_names are in sequential order, and map 1:1 with
        rows in the CSV.

        -- if an optional column_mapping_dict is passed, then this will be used to extract the key elements from the
        CSV rows according to the mapping, e.g.,

                column_mapping_dict = {"column1": 0, "column3": 2, "column5":4}

        This will extract 3 columns with the keys - "column1", "column3" and "column5" and will assign the values
        in the 0th, 2nd, and 4th slots of each CSV row.

        -- if optional header_row is True, then the first row will be interpreted as a header row.  If False,
        then it will be interpreted as part of the dataset. """

        #   load csv
        in_path = os.path.join(fp,fn)
        output = self.file_load(in_path,delimiter=delimiter,encoding=encoding,errors='ignore')

        if (len(output) < 2 and header_row) or (len(output) < 1 and not header_row):
            raise LLMWareException(message=f"Exception: not sufficient content found in the CSV to load "
                                           f"into DB table - found {len(output)} rows")

        schema = {}
        column_map = {}
        self.rows = []
        skipped_rows = []

        if column_mapping_dict:
            column_map = column_mapping_dict

        else:
            #   get column names
            if column_names:

                # will take this and map in sequential order
                column_map = {}
                for i, name in enumerate(column_names):
                    column_map.update({name:i})

            else:
                # will try to derive from the header row
                if not header_row:
                    raise LLMWareException(message="Exception: can not determine the column names of the "
                                                   "spreadsheet - no 'column_names' passed, and there is no "
                                                   "header_row to use in the csv.  To try to derive from the "
                                                   "CSV first row, set header_row = True.")
                else:

                    hrow = output[0]

                    for i, entry in enumerate(hrow):
                        header_entry = re.sub("[\xfe\xff]", "", entry)
                        header_entry = re.sub(" ", "_", header_entry)
                        column_map.update({header_entry:i})

        #   review the first content row to confirm matching number of entries and test data type

        column_size = len(column_map.items())

        if header_row:
            test_row = output[1]
        else:
            test_row = output[0]

        # basic minimal check
        if len(test_row) != column_size and not column_mapping_dict:
            raise LLMWareException(message=f"Exception: Number of elements in first row of data - {len(test_row)} - "
                                           f"does not match the number of column names in the column mapping - "
                                           f"{column_size}.")

        if required_column_count:
            if len(test_row) != required_column_count:
                raise LLMWareException(message=f"Exception: Number of elements in first row of data - {len(test_row)} - "
                                       f"does not match the number specified in required_column_count parameter - "
                                       f"{required_column_count}.")

        column_map_inverted = {v: k for k, v in column_map.items()}

        for i, entry in enumerate(test_row):

            if i in column_map_inverted:

                if data_type_map:

                    if column_map_inverted[i] in data_type_map:
                        dt = data_type_map[column_map_inverted[i]]
                    elif i in data_type_map:
                        dt = data_type_map[i]
                    else:
                        dt = self._get_best_guess_value_type(test_row[i])
                else:
                    dt = self._get_best_guess_value_type(test_row[i])

                schema.update({column_map_inverted[i]:dt})

        self.schema = schema

        if header_row:
            starter = 1
        else:
            starter = 0

        # iterate thru all rows (excluding header_row, if any)
        for x in range(starter,len(output)):

            new_row = {}

            if (len(output[x]) != column_size and not column_mapping_dict) or (required_column_count and
                                                                               len(output[x] != required_column_count)):
                logger.warning(f"warning: line - {x} - has {len(output[x])} elements, and does not match the "
                               f"number of columns in the schema - {column_size} - or specified in "
                               f"required_column_count - {required_column_count} -  for safety, this row is being "
                               f"skipped.")
                skipped_rows.append([x,output[x]])

            else:
                for i, entry in enumerate(output[x]):

                    if i in column_map_inverted:

                        # handle missing or null values
                        if not entry:
                            entry = "0"
                        new_row.update({column_map_inverted[i]: entry})

                if len(new_row.items()) != column_size:
                    logger.warning(f"warning: on line - {x} - extracted elements - {len(new_row.items())} - does "
                                    f"not map to the target column size - {column_size} - skipping row.")
                else:
                    self.rows.append(new_row)

        output = {"rows": len(self.rows), "columns": column_size, "schema": self.schema,
                  "skipped_rows": []}

        return output

    def sql_table_create_string(self,table_name=None,schema=None):

        """ Builds a 'CREATE SQL TABLE' schema string that can be used directly as context in a Text2SQL model.
        Optional parameters to pass a table_name and schema - if none provided, then it will pull from the
        existing CustomTable parameters.

        Returns 'CREATE SQL TABLE' string as output. """

        if schema:
            self.schema= schema

        if table_name:
            self.table_name = table_name

        sql_create_table = ""

        if not schema:

            try:
                self.get_schema(self.table_name)
            except:
                raise LLMWareException(message=f"Exception: could not locate schema for selected "
                                               f"table - {self.table_name}")

        if self.schema and self.table_name:

            keys_list = "("

            sql_create_table = f"CREATE TABLE {self.table_name} ("

            for key, data_types in self.schema.items():

                if key != "PRIMARY KEY":

                    keys_list += key + ", "
                    sql_create_table += key + " " + data_types + ", "

            if sql_create_table.endswith(", "):
                sql_create_table = sql_create_table[:-2]

            sql_create_table += " )"

            if keys_list.endswith(", "):
                keys_list = keys_list[:-2]

            keys_list += " )"

        self.sql_create_table = sql_create_table

        return sql_create_table

    def insert_rows(self, table_name=None, rows=None, schema=None):

        """ Designed for rapid prototyping - by default, intended to be called after a preliminary step of
        'load_csv' or 'load_json' file, which will package up the schema and save the rows, e.g.,

            ct = CustomTable(table_name='my_test_table', db_name='sqlite')
            analysis = ct.validate_csv('/path/to/csv', 'file.csv')
            ct.load_csv('/path/to/csv', 'file.csv')
            ct.insert_rows()

            If table_name and schema not previously passed/created, then these parameters should be passed in
        calling this method.

            This method will insert the rows, held/packaged in self.rows, into the table."""

        if table_name:
            self.table_name = table_name

        if rows:
            self.rows = rows

        if schema:
            self.schema = schema

        rows_completed = 0

        if self.build_table():

            for i in range(0, len(self.rows)):

                if i >= 100 and i % 100 == 0:

                    logger.info(f"update: CustomTable - insert_rows - status - rows loaded - "
                                f"{i} - out of {len(self.rows)}")

                try:
                    self.write_new_record(self.rows[i])
                except:
                    logger.warning(f"warning: write transaction not successful - skipping row - "
                                   f"{i} - {self.rows[i]}")

                rows_completed += 1

        else:
            raise LLMWareException(message=f"Exception: unable to confirm build_table - table_name - "
                                           f"{self.table_name} - schema - {self.schema}")

        return rows_completed

    def get_schema(self, table_name=None):

        """ Returns the schema for the table_name provided.  If no table_name provided, then it will pull from
        self.table_name """

        if table_name:
            self.table_name = table_name

        conn = self.get_connection(type="read")
        schema = conn.get_schema(self.table_name)
        conn.close()

        self.schema = schema
        return schema

    def list_all_tables(self):

        """ Returns a list of all of the tables on the selected database. """

        conn = self.get_connection(type="read")
        all_tables = conn.list_all_tables()
        conn.close()

        return all_tables

    def write_new_record(self, new_record, table_name=None):

        """ Writes a single new record to the database in the table provided, either directly (optional), or in
        self.table_name. """

        if table_name:
            self.table_name = table_name

        conn = self.get_connection(type="write")
        response = conn.write_new_record(new_record)
        self.close_connection()

        return response

    def lookup(self, key, value, table_name=None):

        """ Core lookup method takes a 'key' and 'value' as input, and performs a lookup on the target DB and table
        and returns the corresponding full row as a python dictionary with keys corresponding to the schema. """

        if table_name:
            self.table = table_name

        conn = self.get_connection(type="read")
        response = conn.lookup(key, value)

        return response

    def custom_lookup(self, custom_filter):

        """ Input is a custom filter which will be applied directly to the database.

        For MongoDB, this should be a filter dictionary, following standard Mongo query structures.

        For Postgres and SQLite, this should be a SQL string - which will be passed directly to the DB
        without modification or safety checks. """

        # pass filter/params directly to resource
        conn = self.get_connection(type="read")

        try:
            response = conn.direct_custom_query(custom_filter)
        except:
            logger.warning(f"warning: query was not successful - {str(custom_filter)} - and generated an error "
                           f"when attempting to run on table - {self.table_name} - database - {self.db}. ")
            response = []

        return response

    def get_all(self, table_name=None, return_cursor=False):

        """ Returns all rows from the DB table as a list of python dictionaries, corresponding to the schema -
        assumed to be able to fit in memory.   This method should not be used for extremely large tables
        where a cursor/iterator should be used. """

        if table_name:
            self.table_name = table_name

        conn = self.get_connection(type="read")
        response_cursor = conn.get_whole_collection()

        #   in most cases, it is more convenient to exhaust the cursor and pull the whole set of results into
        #   memory.
        #   TODO:  implement cursor option - see DBCursor class for more details.

        if not return_cursor:
            output = response_cursor.pull_all()
        else:
            output = response_cursor.pull_all()

        conn.close()

        return output

    def get_distinct_list(self, key, table_name=None):

        """ Returns the distinct elements for a selected key in the database table. """

        if table_name:
            self.table_name = table_name

        conn = self.get_connection(type="read")
        response = conn.get_distinct_list(key)
        conn.close()

        return response

    def count_documents(self, filter_dict):

        conn = self.get_connection(type="read")
        count = conn.count_documents(filter_dict)
        conn.close()

        return count

    def delete_record(self, key, value, table_name=None):

        """ Deletes a selected record(s) with matching key:value in selected table. """

        if table_name:
            self.table_name = table_name

        conn = self.get_connection(type="write")
        d = conn.delete_record_by_key(key, value)

        conn.close()

        return 0

    def update_record(self, filter_dict, key, new_value):

        """ Updates a selected record(s) identified with filter_dict {any_key:any_value}, and then sets the new_value
        of the attribute value for key in that record. """

        conn = self.get_connection(type="write")
        confirmation = conn.update_one_record(filter_dict, key, new_value)
        conn.close()

        return 0

    def delete_table(self, table_name=None, confirm=False):

        """ Deletes a selected table in the database - note: the optional 'confirm' parameter must be set to
        True explicitly as a safety check. """

        if table_name:
            self.table_name = table_name

        conn = self.get_connection(type="write")
        confirmation = conn.destroy_collection(confirm_destroy=confirm)

        conn.close()

        return 0


class CloudBucketManager:

    """Main class for handling basic operations with Cloud Buckets - specifically for AWS S3"""

    def __init__(self):
        # placeholder - no state / config required currently
        self.s3_access_key = AWSS3Config().get_config("access_key")
        self.s3_secret_key = AWSS3Config().get_config("secret_key")

    # used in Setup() to get sample test documents
    def pull_file_from_public_s3(self, object_key, local_file, bucket_name):

        """Pulls selected file from public S3 bucket - used by Setup to get sample files"""

        # return list of successfully downloaded files
        downloaded_files = []

        try:
            # Ensure the local file's folder exists
            os.makedirs(os.path.dirname(local_file), exist_ok=True)

            s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
            s3.Bucket(bucket_name).download_file(object_key, local_file)
            downloaded_files.append(object_key)

        except ClientError as e:
            logger.error(e)

        return downloaded_files

    def create_local_model_repo(self, access_key=None,secret_key=None):

        """Pulls down and caches models from public llmware public S3 repo """

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

                logger.info(f"update: identified models in model_repo: {name_parts}")

                if name_parts[0] and name_parts[1]:

                    model_folder = os.path.join(local_model_repo_path,name_parts[0])

                    if not os.path.exists(model_folder):
                        os.mkdir(model_folder)
                        models_retrieved.append(name_parts[0])

                    logger.info(f"update: downloading file from s3 bucket - "
                                f"{name_parts[1]} - {file.key}")

                    s3.download_file(aws_repo_bucket, file.key, os.path.join(model_folder,name_parts[1]))

        logger.info(f"update: created local model repository - {len(models_retrieved)} models retrieved - "
                    f" model list - {models_retrieved}")

        return models_retrieved

    def pull_single_model_from_llmware_public_repo(self, model_name=None):

        """Pulls selected model from llmware public S3 repo to local model repo"""

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
                if not file.key.endswith('/'):
                    local_file_path = os.path.join(local_model_folder,file.key.split('/')[-1])
                    bucket.download_file(file.key, local_file_path)

        logger.info(f"update: successfully downloaded model - {model_name} - "
                    f"from aws s3 bucket for future access")

        return files

    #   called in Library as convenience method to connect to user S3 bucket and download into library path
    def connect_to_user_s3_bucket (self, aws_access_key, aws_secret_key,
                                   user_bucket_name, local_download_path, max_files=1000):

        """Connects to user S3 bucket"""

        files_copied = []

        accepted_file_formats = ["pptx", "xlsx", "docx", "pdf", "txt", "csv", "html", "jsonl",
                                 "jpg", "jpeg", "png", "wav", "zip"]

        try:
            s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

            bucket = boto3.resource('s3', aws_access_key_id=aws_access_key,
                                    aws_secret_access_key=aws_secret_key).Bucket(user_bucket_name)

            files = bucket.objects.all()

            for file in files:

                # strip os.sep from file name
                safe_file_name = str(file.key)
                if safe_file_name.startswith(os.sep):
                    safe_file_name = safe_file_name[1:]

                f = safe_file_name.replace(os.sep, "_")
                f = f.replace(" ", "_")

                file_type = f.split(".")[-1].lower()
                if file_type in accepted_file_formats:
                    s3.download_file(user_bucket_name, file.key, local_download_path + f)
                    files_copied.append(f)
                    if len(files_copied) > max_files:
                        break

        except:
            logger.error(f"error: could not connect to s3 bucket - {user_bucket_name}")

            return files_copied

        return files_copied

    def upload_file(self,file_name, bucket, object_name=None, aws_secret_key=None, aws_access_key=None):

        """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        # Upload the file
        s3_client = boto3.client('s3',aws_access_key_id=aws_access_key,aws_secret_access_key=aws_secret_key)
        try:
            response = s3_client.upload_file(file_name, bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def fetch_model_from_bucket(self, model_name=None, bucket_name=None, save_path=None):

        """Pulls selected model from llmware public S3 repo to local model repo"""

        # if no model name selected, then get all
        if not bucket_name:
            bucket_name = LLMWareConfig().get_config("llmware_public_models_bucket")

        # check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):
            # if not explicitly set up by user, then create folder directory structure
            LLMWareConfig().setup_llmware_workspace()

        if not save_path:
            save_path = LLMWareConfig.get_model_repo_path()

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        #   assumes that files in model folder are something like:
        #   "pytorch_model.bin" | "config.json" | "tokenizer.json"

        bucket = boto3.resource('s3', config=Config(signature_version=UNSIGNED)).Bucket(bucket_name)

        files = bucket.objects.all()

        for file in files:

            if file.key.startswith(model_name):

                #   found component of model in repo, so go ahead and create local model folder, if needed
                local_model_folder = os.path.join(save_path, model_name)
                if not os.path.exists(local_model_folder):
                    os.mkdir(local_model_folder)

                #   simple model_repo structure - each model is a separate folder
                #   each model is a 'flat list' of files, so safe to split on ("/") to get key name
                if not file.key.endswith('/'):
                    local_file_path = os.path.join(local_model_folder, file.key.split('/')[-1])
                    bucket.download_file(file.key, local_file_path)

        logger.info(f"update: successfully downloaded model - {model_name} - "
                    f"from aws s3 bucket for future access")

        return files


class ParserState:

    """ ParserState is the main class abstraction to manage and persist Parser State """

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

        """ Generates the state filename from parser_job_id """

        fn = self.parser_job_output_base_name + str(parser_job_id) + self.parser_output_format
        return fn

    def get_parser_id_from_parser_state_fn(self, fn):

        """ Returns the parser id extracted from the parser state filename """

        core_fn = fn.split(".")[0]
        id = core_fn.split("_")[-1]
        return id

    def lookup_by_parser_job_id(self, parser_id):

        """ Look up the parser job id"""

        parser_output = self.lookup_by_parse_job_id(parser_id)
        return parser_output

    def save_parser_output(self, parser_job_id, parser_output):

        """ Saves the parser output to jsonl file in parser history """

        fn = self.get_parser_state_fn_from_id(parser_job_id)
        fp = os.path.join(self.parser_output_fp, fn)

        outfile = open(fp, "w", encoding='utf-8')

        for entry_dict in parser_output:
            jsonl_row = json.dumps(entry_dict)
            outfile.write(jsonl_row)
            outfile.write("\n")

        outfile.close()

        return fn

    def issue_new_parse_job_id(self, custom_id=None, mode="uuid"):

        """ Issues new parse_job_id """

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

        """ Lookup by parse_job_id """

        output = []

        fn = self.get_parser_state_fn_from_id(prompt_id)
        fp = os.path.join(self.parser_output_fp, fn)

        try:
            my_file = open(fp, 'r', encoding='utf-8')
            for lines in my_file:
                new_row = json.loads(lines)
                output.append(new_row)

        except:
            logger.warning(f"update: ParserState - could not find previous parse job record - {prompt_id}")
            output = []

        return output


class PromptState:

    """ PromptState is the main class abstraction that handles persisting and lookup of Prompt interactions"""

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

        # edge case - if llmware main path exists, but prompt path not created or deleted
        if not os.path.exists(self.prompt_path):
            os.mkdir(self.prompt_path)
            os.chmod(self.prompt_path, 0o777)

        # prompt state written to files
        self.prompt_collection = None
        self.write_to_db = False

    def get_prompt_state_fn_from_id(self, prompt_id):

        """Generates the prompt state filename from prompt_id """
        fn = self.prompt_state_base_name + str(prompt_id) + self.prompt_state_format
        return fn

    def get_prompt_id_from_prompt_state_fn(self, fn):

        """ Gets the prompt id extracted from prompt state filename """

        core_fn = fn.split(".")[0]
        id = core_fn.split("_")[-1]
        return id

    def lookup_by_prompt_id(self, prompt_id):

        """ Lookup by prompt id to retrieve a persisted prompt interaction """

        ai_trx_list = self.lookup_by_prompt_id_from_file(prompt_id)
        return ai_trx_list

    def register_interaction(self, ai_dict):

        """ Registers a new prompt interaction into the interaction history in memory """

        # by default, add to the interaction_history in memory
        self.prompt.interaction_history.append(ai_dict)

        return ai_dict

    def initiate_new_state_session(self, prompt_id=None):

        """ Starts a new state session for an indefinite set of prompt interactions """

        if not prompt_id:
            prompt_id = self.issue_new_prompt_id()

        # reset key trackers
        self.prompt.llm_history = []
        self.prompt.prompt_id = prompt_id
        return prompt_id

    def issue_new_prompt_id(self, custom_id=None, mode="uuid"):

        """ Issues a new prompt id """

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

        """ Loads a saved prompt interaction history from disk """

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
            logger.warning(f"update: PromptState - could not find previous prompt interaction state- {prompt_id}")
            output = None

        return output

    def lookup_by_prompt_id_from_file(self, prompt_id):

        """ Lookup prompt id from file """

        output = []

        fn = self.get_prompt_state_fn_from_id(prompt_id)
        fp = os.path.join(self.prompt_path, fn)

        try:
            my_file = open(fp, 'r', encoding='utf-8')
            for lines in my_file:
                new_row = json.loads(lines)
                output.append(new_row)
        except:
            logger.warning(f"warning: PromptState - could not find previous prompt interaction state- {prompt_id}")
            output = []

        return output

    def full_history(self):

        """ Returns the full prompt history from disk """

        ai_trx_list = self.full_history_from_file()
        return ai_trx_list

    def full_history_from_file(self):

        """ Returns the full prompt history from disk """

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

        """ Enables lookup of prompt history with filter """

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

        """ Enables update of a prompt interaction history from file """

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

        """ Saves state """

        if not prompt_path:
            prompt_path = LLMWareConfig.get_prompt_path()

        fn = self.get_prompt_state_fn_from_id(prompt_id)
        fp = os.path.join(prompt_path, fn)

        outfile = open(fp, "w", encoding='utf-8')

        for entry_dict in custom_history:
            jsonl_row = json.dumps(entry_dict)
            outfile.write(jsonl_row)
            outfile.write("\n")

        outfile.close()

        return fp

    def save_state(self, prompt_id, prompt_path=None):

        """ Saves state """

        if not prompt_path:
            prompt_path = LLMWareConfig.get_prompt_path()

        fn = self.get_prompt_state_fn_from_id(prompt_id)
        fp = os.path.join(prompt_path, fn)

        outfile = open(fp, "w", encoding='utf-8')

        for entry_dict in self.prompt.interaction_history:
            jsonl_row = json.dumps(entry_dict)
            outfile.write(jsonl_row)
            outfile.write("\n")

        outfile.close()

        return fp

    def available_states(self, prompt_path=None):

        """ Lists available prompt interaction history states """

        available_states = []

        if not prompt_path:
            prompt_path = self.prompt_path

        for x in os.listdir(prompt_path):
            if x.startswith(self.prompt_state_base_name):
                prompt_id = self.get_prompt_id_from_prompt_state_fn(x)
                new_entry = {"prompt_id": prompt_id, "prompt_fn": x}
                available_states.append(new_entry)

        logger.info(f"update: PromptState - available states - {available_states}")

        return available_states

    def generate_interaction_report(self, prompt_id_list, output_path=None, report_name=None):

        """ Prepares a csv report that can be extracted to a spreadsheet """

        if not output_path:
            output_path = self.output_path

        if not report_name:
            report_name = "interaction_report_" + str(StateResourceUtil().get_current_time_now()) + ".csv"

        result_count = 0

        report_fp = os.path.join(output_path,report_name)

        with open(report_fp, 'w', encoding='utf-8', newline='') as csvfile:
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
                    # strip symbols that can disrupt csv output
                    evidence_clean = re.sub(r"[,\"\'\n\r\u2018\u2019\u201c\u201d]"," ", new_row['evidence'])
                    response_clean = re.sub(r"[,\"\'\n\r\u2018\u2019\u201c\u201d]", " ", new_row['llm_response'])

                    csv_row = [prompt_id,
                               new_row["prompt"],
                               response_clean,
                               new_row["instruction"],
                               evidence_clean,
                               new_row["model"],
                               new_row["time_stamp"]
                               ]

                    c.writerow(csv_row)
                    result_count += 1

        csvfile.close()

        output_response = {"report_name": report_name, "report_fp": report_fp, "results": result_count}

        return output_response

    def generate_interaction_report_current_state(self, output_path=None, report_name=None):

        """ Prepares a csv report that can be extracted to a spreadsheet """

        if not output_path:
            output_path = self.output_path

        if not report_name:
            report_name = "interaction_report_" + str(StateResourceUtil().get_current_time_now()) + ".csv"

        result_count = 0

        report_fp = os.path.join(output_path,report_name)

        with open(report_fp, 'w', encoding='utf-8', newline='') as csvfile:
            c = csv.writer(csvfile, dialect='excel', doublequote=False, delimiter=',', escapechar=']')

            header_row = ["Prompt_ID", "Prompt", "LLM_Response", "Instruction", "Evidence", "Model", "Time-Stamp"]
            c.writerow(header_row)

            for i, new_row in enumerate(self.prompt.interaction_history):

                # create new csv row
                # strip symbols that can disrupt csv output
                evidence_clean = re.sub(r"[,\"\'\n\r\u2018\u2019\u201c\u201d]", " ", new_row['evidence'])
                response_clean = re.sub(r"[,\"\'\n\r\u2018\u2019\u201c\u201d]", " ", new_row['llm_response'])

                csv_row = [self.prompt.prompt_id,
                           new_row["prompt"],
                           response_clean,
                           new_row["instruction"],
                           evidence_clean,
                           new_row["model"],
                           new_row["time_stamp"]
                           ]

                c.writerow(csv_row)
                result_count += 1

        csvfile.close()

        output_response = {"report_name": report_name, "report_fp": report_fp, "results": result_count}

        return output_response


class QueryState:

    """ QueryState is the main class abstraction to manage persistence of Queries """

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

        #   check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):

            # if not explicitly set up by user, then create folder directory structure
            LLMWareConfig.setup_llmware_workspace()

        #   if llmware main path exists, but query_path not created or deleted
        if not os.path.exists(self.query_path):
            os.mkdir(self.query_path)
            os.chmod(self.query_path, 0o777)

    def get_query_state_fn_from_id(self, prompt_id):

        """ Generates query state filename from query id  """

        fn = self.query_state_base_name + str(prompt_id) + self.query_state_format
        return fn

    def get_query_id_from_prompt_state_fn(self, fn):

        """ Extracts the query id from the filename """

        core_fn = fn.split(".")[0]
        id = core_fn.split("_")[-1]
        return id

    def initiate_new_state_session(self, query_id=None):

        """ Starts a new state session in memory - tracks all query results and metadata in session """

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

        """ Issue new query_id """

        if not custom_id:

            if mode == "time_stamp":
                custom_id = StateResourceUtil().get_current_time_now()
            elif mode == "uuid":
                custom_id = StateResourceUtil().get_uuid()
            elif mode == "random_number":
                custom_id = str(random.randint(1000000, 9999999))

        return custom_id

    def available_states(self):

        """ Gets all available saved query states on file """

        available_states = []

        for x in os.listdir(self.query_path):
            if x.startswith(self.query_state_base_name):
                query_id = self.get_query_id_from_prompt_state_fn(x)
                new_entry = {"query_id": query_id, "query_fn": x}
                available_states.append(new_entry)

        logger.info(f"update: QueryState - available saved query states - {available_states}")

        return available_states

    def load_state (self, query_id):

        """ Loads query state from file """

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
            logger.warning(f"update: QueryState - could not find previous query state- {query_id}")
            output = []

        self.query.results = output
        self.query.doc_id_list = doc_id_list
        self.query.doc_fn_list = doc_fn_list
        self.query.query_history = query_history

        return self

    def save_state(self, query_id=None):

        """ Saves query state to jsonl file in query state history """

        if not query_id:
            query_id = self.query.query_id

        fn = self.get_query_state_fn_from_id(query_id)
        fp = os.path.join(self.query_path, fn)

        outfile = open(fp, "w", encoding='utf-8')

        for entry_dict in self.query.results:
            jsonl_row = json.dumps(entry_dict)
            outfile.write(jsonl_row)
            outfile.write("\n")

        outfile.close()

        return fn

    def generate_query_report_current_state(self, report_name=None):

        """ Prepares a csv report that can be extracted to a spreadsheet """

        if not self.query:
            logger.error("error: QueryState - report generation - must load a current query")
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
                text = re.sub(r"[,\"]"," ", results["text"])

            new_row = [query, file_source, doc_id, block_id, page_num, text]

            report_out.append(new_row)

        fp = os.path.join(self.query_path, report_name)

        StateResourceUtil().file_save(report_out, self.output_path, report_name)

        return report_name


class StateResourceUtil:

    """ Utility methods for the State Resource classes """

    def __init__(self):
        self.do_nothing = 0     # placeholder - may add attributes in the future

    def get_uuid(self):
        """ Uses unique id creator from uuid library """
        return uuid.uuid4()

    @staticmethod
    def get_current_time_now (time_str="%a %b %e %H:%M:%S %Y"):
        """ Gets current time """

        #   if time stamp used in filename, needs to be Windows compliant
        if platform.system() == "Windows":
            time_str = "%Y-%m-%d_%H%M%S"
    
        return datetime.now().strftime(time_str)

    @staticmethod
    def file_save (cfile, file_path, file_name):

        """ Saves list/array to csv file to disk """

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
                    logger.error(f"error:  CSV ERROR:   Row exceeds MAX SIZE: "
                                 f"{sys.getsizeof(cfile[z])} - {cfile[z]}")

        csvfile.close()

        return 0
