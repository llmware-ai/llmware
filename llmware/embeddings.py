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

"""The embeddings module implements the supported vector databases.

The common abstraction for all supported vector databases is the EmbeddingHandler class, which supports
creating a new embedding, as well as searching and deleting the vector index. The module also implements the
_EmbeddingUtils class, which provides a set of functions used by all vector database classes.
"""

import os
import logging
import numpy as np
import re
import time
import uuid
import itertools
from importlib import util
import importlib

from llmware.configs import LLMWareConfig, MongoConfig, MilvusConfig, PostgresConfig, RedisConfig, \
    PineconeConfig, QdrantConfig, Neo4jConfig, LanceDBConfig, ChromaDBConfig, VectorDBRegistry
from llmware.exceptions import (UnsupportedEmbeddingDatabaseException, EmbeddingModelNotFoundException,
                                DependencyNotInstalledException, LLMWareException)
from llmware.resources import CollectionRetrieval, CollectionWriter
from llmware.status import Status
from llmware.util import Utilities

""" By default, no vector db drivers are loaded into global program space unless and until they are invoked.  Within 
each embedding class handler, there is a check if GLOBAL_{VECTOR_DB}_IMPORT is False, and if so, then the module 
is loaded, and the GLOBAL_{VECTOR_DB}_IMPORT is set to True.  """

pymilvus = None
GLOBAL_PYMILVUS_IMPORT = False

chromadb = None
GLOBAL_CHROMADB_IMPORT = False

lancedb = None
GLOBAL_LANCEDB_IMPORT = False

faiss = None
GLOBAL_FAISS_IMPORT = False

neo4j = None
GLOBAL_NEO4J_IMPORT = False

qdrant_client = None
GLOBAL_QDRANT_IMPORT = False

pinecone = None
GLOBAL_PINECONE_IMPORT = False

redis = None
GLOBAL_REDIS_IMPORT = False

#   pgvector requires import of both pgvector and psycopg
pgvector = None
GLOBAL_PGVECTOR_IMPORT = False

psycopg = None
GLOBAL_PSYCOPG_IMPORT = False

#   used in mongo-atlas
pymongo = None
GLOBAL_PYMONGO_IMPORT = False

logger = logging.getLogger(__name__)
log_level = LLMWareConfig().get_logging_level_by_module("llmware.embeddings")
logger.setLevel(level=log_level)


class EmbeddingHandler:

    """Provides an interface to all supported vector databases, which is used by the ``Library`` class.

    ``EmbeddingHandler`` is responsible for embedding-related interactions between a library and a vector
    store. This includes creating, reading, updating, and deleting (CRUD) embeddings. The ``EmbeddingHandler``,
    in addition, synchronizes the vector store with the text collection database, this includes incremental
    updates to the embeddings. Finally, it also allows one library to have multiple embeddings.

    Parameters
    ----------
    library : Library
        The library with which the ``EmbeddingHandler`` interacts.

    Returns
    -------
    embedding_handler : EmbeddingHandler
        A new ``EmbeddingHandler`` object.
    """

    def __init__(self, library):

        self.supported_embedding_dbs = VectorDBRegistry().get_vector_db_list()

        self.library = library
   
    def create_new_embedding(self, embedding_db, model, doc_ids=None, batch_size=500):

        """ Creates new embedding - routes to correct vector db and loads the model and text collection """

        embedding_class = self._load_embedding_db(embedding_db, model=model)
        embedding_status = embedding_class.create_new_embedding(doc_ids, batch_size)

        if embedding_status:
            if "embeddings_created" in embedding_status:
                if embedding_status["embeddings_created"] > 0:
                    # only update if non-zero embeddings created
                    if "embedded_blocks" in embedding_status:
                        embedded_blocks = embedding_status["embedded_blocks"]
                    else:
                        embedded_blocks = -1
                        logger.warning("update: embedding_handler - unable to determine if embeddings have "
                                        "been properly counted and captured.   Please check if databases connected.")

                    self.library.update_embedding_status("yes", model.model_name, embedding_db,
                                                         embedded_blocks=embedded_blocks,
                                                         embedding_dims=embedding_status["embedding_dims"],
                                                         time_stamp=embedding_status["time_stamp"])

        return embedding_status
   
    def search_index(self, query_vector, embedding_db, model, sample_count=10):

        """ Main entry point to vector search query """

        # Need to normalize the query_vector.
        # Sometimes it comes in as [[1.1,2.1,3.1]] (from Transformers) and sometimes as [1.1,2.1,3.1]
        # We'll make sure it's the latter and then each Embedding Class will deal with it how it needs to

        if len(query_vector) == 1:
            query_vector = query_vector[0]

        embedding_class = self._load_embedding_db(embedding_db, model=model)
        return embedding_class.search_index(query_vector,sample_count=sample_count)

    def delete_index(self, embedding_db, model_name, embedding_dims):

        """ Deletes vector embedding - note:  does not delete the underlying text collection """

        embedding_class = self._load_embedding_db(embedding_db, model_name=model_name,
                                                  embedding_dims=embedding_dims)
        embedding_class.delete_index()
        self.library.update_embedding_status("delete", model_name, embedding_db,
                                             embedded_blocks=0, delete_record=True)

        return 0

    def _load_embedding_db(self, embedding_db, model=None, model_name=None, embedding_dims=None):

        """ Looks up and loads the selected vector database """

        if not embedding_db in self.supported_embedding_dbs:
            raise UnsupportedEmbeddingDatabaseException(embedding_db)

        vdb = self.supported_embedding_dbs[embedding_db]

        #   dynamically load the module/class for the specific embedding handler
        vdb_module = vdb["module"]
        vdb_class = vdb["class"]
        vdb_module = importlib.import_module(vdb_module)

        if hasattr(vdb_module, vdb_class):
            model_class = getattr(vdb_module, vdb_class)

            return model_class(self.library, model=model, model_name=model_name,embedding_dims=embedding_dims)

        else:
            raise LLMWareException(message=f"Exception: could not find class implementation for {embedding_db}, which "
                                           f"is expected at: {vdb_module} - {vdb_class}.")

    def generate_index_name(self, account_name, library_name, model_name, max_component_length=19):

        """ Creates a unique name for the vector index that concats library_name + model_name + account_name """

        index_name = account_name

        # Remove non-alphanumerics from the remaining components and if still longer than the max, remove middle chars
        for s in [library_name, model_name]:
            s = re.sub(r'\W+', '', s)
            if len(s) > max_component_length:
                excess_length = len(s) - max_component_length
                left_length = (len(s) - excess_length) // 2
                right_start = left_length + excess_length
                index_name += s[:left_length] + s[right_start:]

        # Return the lowercase name:
        return index_name.lower()


class _EmbeddingUtils:

    """Provides functions to vector stores, such as creating names for the text collection database as well
    as creating names for vector such, and creating a summary of an embedding process.

    ``_EmbeddingUTils`` provides utilities used by all vector stores, especially in interaction and
    synchronization with the underlying text collection database. In short, it has functions for
    creating names, the text index, the embedding flag, the block curser, and the embedding summary.

    Parameters
    ----------
    library_name : str, default=None
        Name of the library.

    model_name : str, default=None
        Name of the model.

    account_name : str, default=None
        Name of the account.

    db_name : str, default=None
        Name of the vector store.

    embedding_dims : int, default=None
        Dimension of the embedding.

    Returns
    -------
    embedding_utils : _EmbeddingUtils
        A new ``_EmbeddingUtils`` object.
    """

    def __init__(self, library_name=None, model_name=None, account_name=None,db_name=None,
                 embedding_dims=None):

        self.library_name = library_name
        self.account_name = account_name
        self.model_name = model_name
        self.db_name = db_name
        self.embedding_dims = embedding_dims
        self.collection_key= None
        self.collection_name= None

    def create_safe_collection_name(self):

        """ Creates concatenated safe name for collection """

        converted_library_name = re.sub(r"[-@_.\/ ]", "", self.library_name).lower()
        if len(converted_library_name) > 18:
            converted_library_name = converted_library_name[0:18]

        converted_model_name = re.sub(r"[-@_.\/ ]", "", self.model_name).lower()
        if len(converted_model_name) > 18:
            # chops off the start of the model name if longer than 18 chars
            starter = len(converted_model_name) - 18
            converted_model_name = converted_model_name[starter:]

        converted_account_name = re.sub(r"[-@_.\/ ]", "", self.account_name).lower()
        if len(converted_model_name) > 7:
            converted_account_name = converted_account_name[0:7]

        # create collection name here - based on account + library + model_name
        self.collection_name = f"{converted_account_name}_{converted_library_name}_{converted_model_name}"

        return self.collection_name

    def create_db_specific_key(self):

        """ Creates db_specific key """

        # will leave "-" and "_" in file path, but remove "@" and " "
        model_safe_path = re.sub(r"[@ ]", "", self.model_name).lower()
        self.collection_key = f"embedding_{self.db_name}_" + model_safe_path

        return self.collection_key

    def get_blocks_cursor(self, doc_ids = None):

        """ Retrieves a cursor from the text collection database that will define the scope of text chunks
            to be embedded """

        if not self.collection_key:
            self.create_db_specific_key()

        cr = CollectionRetrieval(self.library_name, account_name=self.account_name)
        num_of_blocks, all_blocks_cursor = cr.embedding_job_cursor(self.collection_key,doc_id=doc_ids)

        return all_blocks_cursor, num_of_blocks

    def generate_embedding_summary(self, embeddings_created):

        """ Common summary dictionary at end of embedding job """

        if not self.collection_key:
            self.create_db_specific_key()

        cr = CollectionRetrieval(self.library_name,account_name=self.account_name)
        embedded_blocks = cr.count_embedded_blocks(self.collection_key)

        embedding_summary = {"embeddings_created": embeddings_created,
                             "embedded_blocks": embedded_blocks,
                             "embedding_dims": self.embedding_dims,
                             "time_stamp": Utilities().get_current_time_now()}

        return embedding_summary

    def update_text_index(self, block_ids, current_index):

        """ Update main text collection db """

        for block_id in block_ids:

            cw = CollectionWriter(self.library_name, account_name=self.account_name)
            cw.add_new_embedding_flag(block_id,self.collection_key,current_index)

            current_index += 1

        return current_index

    def lookup_text_index(self, _id, key="_id"):

        """Returns a single block entry from text index collection with lookup by _id - returns a list, not a cursor"""

        cr = CollectionRetrieval(self.library_name, account_name=self.account_name)
        block_cursor = cr.lookup(key, _id)

        return block_cursor

    def lookup_embedding_flag(self, key, value):

        """ Used to look up an embedding flag in text collection index """

        # used specifically by FAISS index - which uses the embedding flag value as lookup
        cr = CollectionRetrieval(self.library_name, account_name=self.account_name)
        block_cursor = cr.embedding_key_lookup(key,value)

        return block_cursor

    def unset_text_index(self):

        """Removes embedding key flag for library, e.g., 'unsets' a group of blocks in text index """

        cw = CollectionWriter(self.library_name, account_name=self.account_name)
        cw.unset_embedding_flag(self.collection_key)

        return 0


class EmbeddingMilvus:

    """
    ``EmbeddingMilvus`` implements the interface to the ``Milvus`` vector store. It is used by the
    ``EmbeddingHandler``.

    Parameters
    ----------
    library : object
        A ``Library`` object.

    model : object
        A model object. See :mod:`models` for available models.

    model_name : str, default=None
        Name of the model.

    embedding_dims : int, default=None
        Dimension of the embedding.

    Returns
    -------
    embedding_milvus : EmbeddingMilvus
        A new ``EmbeddingMilvus`` object.
    """

    def __init__(self, library, model=None, model_name=None, embedding_dims=None):

        self.library = library
        self.library_name = library.library_name
        self.account_name = library.account_name
        self.milvus_alias = "default"

        self.use_milvus_lite = MilvusConfig().get_config("lite")

        #   confirm that pymilvus installed

        global GLOBAL_PYMILVUS_IMPORT
        if not GLOBAL_PYMILVUS_IMPORT:
            if util.find_spec("pymilvus"):

                try:
                    global pymilvus
                    pymilvus = importlib.import_module("pymilvus")
                    GLOBAL_PYMILVUS_IMPORT = True
                except:
                    raise LLMWareException(message="Exception: could not load pymilvus module.")

            else:
                raise LLMWareException(message="Exception: need to import pymilvus to use this class.")

        # end dynamic import here

        # look up model card
        if not model and not model_name:
            raise EmbeddingModelNotFoundException("no-model-or-model-name-provided")

        self.model=model
        self.model_name=model_name
        self.embedding_dims = embedding_dims

        # if model passed (not None), then use model name
        if self.model:
            self.model_name = self.model.model_name
            self.embedding_dims = self.model.embedding_dims

        self.utils = _EmbeddingUtils(library_name=self.library_name,
                                     model_name=self.model_name,
                                     account_name=self.account_name,
                                     db_name="milvus",
                                     embedding_dims=self.embedding_dims)

        self.collection_name = self.utils.create_safe_collection_name()
        self.collection_key = self.utils.create_db_specific_key()

        if self.use_milvus_lite:

            logger.info(f"update: EmbeddingHandler - Milvus - selecting 'lite' version.  If you intend to use "
                        f"a server-based version of Milvus, please set: MilvusConfig().set_config('lite', False).")

            lite_path = MilvusConfig().get_config("lite_folder_path")
            lite_db_name = MilvusConfig().get_config("lite_name")

            self.collection = pymilvus.MilvusClient(os.path.join(lite_path, lite_db_name))

            #   check if collection_name found in list of collections - load, if exists, else create new
            if self.collection_name in self.collection.list_collections():
                self.collection.load_collection(self.collection_name)
            else:
                schema = self.collection.create_schema(
                    auto_id=False,
                    enable_dynamic_field=True,
                )

                # add fields to schema
                schema.add_field(field_name="block_mongo_id", datatype=pymilvus.DataType.VARCHAR, is_primary=True,
                                 max_length=30, auto_id=False)
                schema.add_field(field_name="block_doc_id", datatype=pymilvus.DataType.INT64)
                schema.add_field(field_name="embedding_vector", datatype=pymilvus.DataType.FLOAT_VECTOR, dim=self.embedding_dims)

                index_params = self.collection.prepare_index_params()

                # add index
                index_params.add_index(
                    field_name="embedding_vector",
                    metric_type="L2",
                )

                self.collection.create_collection(collection_name=self.collection_name,
                                                  dimension=self.embedding_dims,
                                                  schema=schema,
                                                  index_params=index_params)

        else:

            #   connect to Milvus server

            logger.info(f"update: EmbeddingHandler - Milvus - connecting to Milvus server instance.  To use "
                        f"Milvus 'lite', set MilvusConfig().set_config('lite', True).")

            pymilvus.connections.connect(self.milvus_alias,
                                host=MilvusConfig.get_config("host"),
                                port=MilvusConfig.get_config("port"),
                                db_name=MilvusConfig.get_config("db_name"))

            if not pymilvus.utility.has_collection(self.collection_name):
                fields = [
                    pymilvus.FieldSchema(name="block_mongo_id",
                                         dtype=pymilvus.DataType.VARCHAR, is_primary=True, max_length=30,auto_id=False),
                    pymilvus.FieldSchema(name="block_doc_id", dtype=pymilvus.DataType.INT64),
                    pymilvus.FieldSchema(name="embedding_vector", dtype=pymilvus.DataType.FLOAT_VECTOR,
                                         dim=self.embedding_dims)
                ]

                collection = pymilvus.Collection(self.collection_name, pymilvus.CollectionSchema(fields))
                index_params = {
                    "metric_type": "L2",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 1024}
                }
                collection.create_index("embedding_vector", index_params)

            self.collection = pymilvus.Collection(self.collection_name)

    def create_new_embedding(self, doc_ids = None, batch_size=500):

        """ Create new embedding """

        all_blocks_cursor, num_of_blocks = self.utils.get_blocks_cursor(doc_ids=doc_ids)

        # Initialize a new status
        status = Status(self.account_name)
        status.new_embedding_status(self.library_name, self.model_name, num_of_blocks)

        embeddings_created = 0
        current_index = 0
        finished = False

        while not finished:

            block_ids, doc_ids, sentences = [], [], []

            # Build the next batch
            for i in range(batch_size):

                block = all_blocks_cursor.pull_one()

                if not block:
                    finished = True
                    break

                text_search = block["text_search"].strip()
                if not text_search or len(text_search) < 1:
                    continue

                # data model
                block_ids.append(str(block["_id"]))
                doc_ids.append(int(block["doc_ID"]))
                sentences.append(text_search)

            if len(sentences) > 0:

                # Process the batch
                vectors = self.model.embedding(sentences)
                data = [block_ids, doc_ids, vectors]

                if self.use_milvus_lite:

                    d=[]
                    for i, vec in enumerate(vectors):
                        new_row = {"block_mongo_id": block_ids[i], "block_doc_id": doc_ids[i], "embedding_vector": vec}
                        d.append(new_row)

                    self.collection.insert(data=d, collection_name=self.collection_name)

                else:
                    self.collection.insert(data)

                current_index = self.utils.update_text_index(block_ids,current_index)

                embeddings_created += len(sentences)

                status.increment_embedding_status(self.library_name, self.model_name, len(sentences))

                # will add configuration options to show/display
                logger.info(f"update: embedding_handler - Milvus - Embeddings Created: {embeddings_created} of {num_of_blocks}")

        if not self.use_milvus_lite:
            self.collection.flush()

        embedding_summary = self.utils.generate_embedding_summary(embeddings_created)

        logger.info(f"update: EmbeddingHandler - Milvus - embedding_summary - {embedding_summary}")

        return embedding_summary

    def search_index(self, query_embedding_vector, sample_count=10):

        if not self.use_milvus_lite:
            self.collection.load()

            search_params = {
                "field_name": "embedding_vector",
                "metric_type": "L2",
                "params": {"nprobe": 10}
            }

            # TODO: add optional / configurable partitions

            result = self.collection.search(
                data=[query_embedding_vector],
                anns_field="embedding_vector",
                param=search_params,
                limit=sample_count,
                output_fields=["block_mongo_id"]
            )

        else:

            search_params = {
                "field_name": "embedding_vector",
                "metric_type": "L2",
                # "params": {"nprobe": 10}
            }

            result = self.collection.search(collection_name=self.collection_name,
                data=[query_embedding_vector],
                anns_field="embedding_vector",
                search_params=search_params,
                limit=sample_count,
                output_fields=["block_mongo_id"]
            )

        block_list = []
        for hits in result:
            for hit in hits:

                if self.use_milvus_lite:

                    try:
                        # alt: _id = int(hit["entity"]["block_mongo_id"])
                        _id = hit["entity"]["block_mongo_id"]
                    except:
                        logger.warning(f"update: EmbeddingHandler - Milvus - search - unexpected - "
                                       f"could not convert to number - {hit}")
                        _id = -1
                else:
                    _id = hit.entity.get('block_mongo_id')

                block_result_list = self.utils.lookup_text_index(_id)

                for block in block_result_list:

                    if self.use_milvus_lite:
                        distance = hit["distance"]
                    else:
                        distance = hit.distance

                    block_list.append((block, distance))

                """
                try:
                    block = block_cursor.next()
                    block_list.append((block, hit.distance))
                except StopIteration:
                    # The cursor is empty (no blocks found)
                    continue 
                """

        return block_list
   
    def delete_index(self):

        if not self.use_milvus_lite:

            collection = pymilvus.Collection(self.collection_name)
            collection.release()
            pymilvus.utility.drop_collection(self.collection_name)
            pymilvus.connections.disconnect(self.milvus_alias)

        else:
            # delete
            res = self.collection.delete(collection_name=self.collection_name)

        # Synchronize and remove embedding flag from collection db
        self.utils.unset_text_index()

        return 1


class EmbeddingFAISS:

    """Implements the vector database FAISS.

    ``EmbeddingFAISS`` implements the interface to the ``FAISS`` vector database. It is used by the
    ``EmbeddingHandler``.

    Parameters
    ----------
    library : object
        A ``Library`` object.

    model : object
        A model object. See :mod:`models` for available models.

    model_name : str, default=None
        Name of the model.

    embedding_dims : int, default=None
        Dimension of the embedding.

    Returns
    -------
    embedding_faiss : EmbeddingFAISS
        A new ``EmbeddingFAISS`` object.
    """

    def __init__(self, library, model=None, model_name=None, embedding_dims=None):

        global GLOBAL_FAISS_IMPORT
        if not GLOBAL_FAISS_IMPORT:
            if util.find_spec("faiss"):

                try:
                    global faiss
                    faiss = importlib.import_module("faiss")
                    GLOBAL_FAISS_IMPORT = True
                except:
                    raise LLMWareException(message="Exception: could not load faiss module.")

            else:
                raise LLMWareException(message="Exception: need to import faiss to use this class.")

        # end dynamic import here

        self.library = library
        self.library_name = library.library_name
        self.account_name = library.account_name
        self.index = None

        # look up model card
        if not model and not model_name:
            raise EmbeddingModelNotFoundException("no-model-or-model-name-provided")

        self.model=model
        self.model_name=model_name
        self.embedding_dims=embedding_dims

        # if model passed (not None), then use model name and embedding dims
        if self.model:
            self.model_name = self.model.model_name
            self.embedding_dims = self.model.embedding_dims

        # embedding file name here
        self.utils = _EmbeddingUtils(library_name=self.library_name,
                                     model_name=self.model_name,
                                     account_name=self.account_name,
                                     db_name="faiss",
                                     embedding_dims=self.embedding_dims)

        self.collection_name = self.utils.create_safe_collection_name()
        self.collection_key = self.utils.create_db_specific_key()

        # will leave "-" and "_" in file path, but remove "@" and " "
        model_safe_path = re.sub(r"[@\/. ]", "", self.model_name).lower()
        self.embedding_file_path = os.path.join(self.library.embedding_path, model_safe_path, "embedding_file_faiss")

    def create_new_embedding(self, doc_ids=None, batch_size=100):

        """ Load or create index """

        if not self.index:
            if os.path.exists(self.embedding_file_path):

                #   faiss is optional dependency
                #   note: there may be an edge case where this faiss command would fail even with
                #   library installed, but we throw dependency not installed error as most likely cause

                try:
                    self.index = faiss.read_index(self.embedding_file_path)
                except:
                    raise DependencyNotInstalledException("faiss-cpu")
            else:
                try:
                    self.index = faiss.IndexFlatL2(self.embedding_dims)
                except:
                    raise DependencyNotInstalledException("faiss-cpu")

        # get cursor for text collection with blocks requiring embedding
        all_blocks_cursor, num_of_blocks = self.utils.get_blocks_cursor(doc_ids=doc_ids)

        # Initialize a new status
        status = Status(self.account_name)
        status.new_embedding_status(self.library_name, self.model_name, num_of_blocks)

        embeddings_created = 0
        finished = False

        while not finished:

            block_ids, sentences = [], []
            current_index = self.index.ntotal

            # Build the next batch
            for i in range(batch_size):

                block = all_blocks_cursor.pull_one()

                if not block:
                    finished = True
                    break

                text_search = block["text_search"].strip()

                if not text_search or len(text_search) < 1:
                    continue
                block_ids.append(str(block["_id"]))

                sentences.append(text_search)
            
            if len(sentences) > 0:
                # Process the batch
                vectors = self.model.embedding(sentences)
                self.index.add(np.array(vectors))

                current_index = self.utils.update_text_index(block_ids,current_index)

                embeddings_created += len(sentences)
                status.increment_embedding_status(self.library.library_name, self.model_name, len(sentences))

                # will add options to display/hide
                logger.info(f"update: embedding_handler - FAISS - Embeddings Created: {embeddings_created} of {num_of_blocks}")
        
        # Ensure any existing file is removed before saving
        if os.path.exists(self.embedding_file_path):
            os.remove(self.embedding_file_path)
        os.makedirs(os.path.dirname(self.embedding_file_path), exist_ok=True)
        faiss.write_index(self.index, self.embedding_file_path)

        embedding_summary = self.utils.generate_embedding_summary(embeddings_created)

        logger.info(f"update: EmbeddingHandler - FAISS - embedding_summary - {embedding_summary}")

        return embedding_summary

    def search_index (self, query_embedding_vector, sample_count=10):

        """ Search FAISS index """

        if not self.index:
            self.index = faiss.read_index(self.embedding_file_path)

        distance_list, index_list = self.index.search(np.array([query_embedding_vector]), sample_count)

        block_list = []
        for i, index in enumerate(index_list[0]):

            index_int = int(index.item())

            #   FAISS is unique in that it requires a 'reverse lookup' to match the FAISS index in the
            #   text collection

            block_result_list = self.utils.lookup_embedding_flag(self.collection_key,index_int)

            # block_result_list = self.utils.lookup_text_index(index_int, key=self.collection_key)

            for block in block_result_list:
                block_list.append((block, distance_list[0][i]))

        return block_list

    def delete_index(self):

        """ Delete FAISS index """

        if os.path.exists(self.embedding_file_path):
            os.remove(self.embedding_file_path)

            # remove emb key - 'unset' the blocks in the text collection
            self.utils.unset_text_index()

        return 1


class EmbeddingLanceDB:

    """Implements the vector database LanceDB.

    ``EmbeddingLanceDB`` implements the interface to the ``LanceDB`` vector database. It is used by the
    ``EmbeddingHandler``.

    Parameters
    ----------
    library : object
        A ``Library`` object.

    model : object
        A model object. See :mod:`models` for available models.

    model_name : str, default=None
        Name of the model.

    embedding_dims : int, default=None
        Dimension of the embedding.

    Returns
    -------
    embedding_lancedb : EmbeddingLanceDB
        A new ``EmbeddingLanceDB`` object.
    """

    def __init__(self, library, model=None, model_name=None, embedding_dims=None):

        #   confirm that lancedb installed

        global GLOBAL_LANCEDB_IMPORT
        if not GLOBAL_LANCEDB_IMPORT:
            if util.find_spec("lancedb"):

                try:
                    global lancedb
                    lancedb = importlib.import_module("lancedb")
                    GLOBAL_LANCEDB_IMPORT = True
                except:
                    raise LLMWareException(message="Exception: could not load lancedb module.")

            else:
                raise LLMWareException(message="Exception: need to import lancedb to use this class.")

        # end dynamic import here

        self.uri = LanceDBConfig().get_config("uri")
        self.library = library
        self.library_name = self.library.library_name
        self.account_name = self.library.account_name

        # look up model card
        if not model and not model_name:
            raise EmbeddingModelNotFoundException("no-model-or-model-name-provided")

        self.model = model
        self.model_name = model_name
        self.embedding_dims = embedding_dims

        # if model passed (not None), then use model name
        if self.model:
            self.model_name = self.model.model_name
            self.embedding_dims = model.embedding_dims

        # initialize LanceDB
        self.index = None

        # initiate connection to LanceDB locally
        try:
            self.db = lancedb.connect(self.uri)
        except:
            raise ImportError(
                "Exception - could not connect to LanceDB - please check:"
                "1.  LanceDB python package is installed, e.g,. 'pip install lancedb', and"
                "2.  The uri is properly set.")

        self.utils = _EmbeddingUtils(library_name=self.library_name,
                                 model_name=self.model_name,
                                 account_name=self.account_name,
                                 db_name="lancedb",
                                 embedding_dims=self.embedding_dims)

        self.collection_name = self.utils.create_safe_collection_name()
        self.collection_key = self.utils.create_db_specific_key()

        if self.collection_name not in self.db.table_names():
            self.index = self._init_table(self.collection_name)

            # you don't need to create an index with lanceDB up to million vectors is efficiently supported with peak performance,
            # Creating an index will accelerate the search process and it needs to be done once table has some vectors already.

        # connect to table
        self.index = self.db.open_table(self.collection_name)

    def _init_table(self,table_name):

            try:
                import pyarrow as pa
            except:
                raise DependencyNotInstalledException("pyarrow")

            schema = pa.schema([
                            pa.field("vector", pa.list_(pa.float32(), int(self.embedding_dims))),
                            pa.field("id", pa.string()),
                        ])
            tbl = self.db.create_table(table_name, schema=schema, mode="overwrite")
            return tbl

    def create_new_embedding(self, doc_ids = None, batch_size=500):

            all_blocks_cursor, num_of_blocks = self.utils.get_blocks_cursor(doc_ids=doc_ids)

            # Initialize a new status
            status = Status(self.library.account_name)
            status.new_embedding_status(self.library.library_name, self.model_name, num_of_blocks)

            embeddings_created = 0

            # starting current_index @ 0
            current_index = 0

            finished = False

            while not finished:
                block_ids, doc_ids, sentences = [], [], []
                # Build the next batch
                for i in range(batch_size):
                    block = all_blocks_cursor.pull_one()

                    if not block:
                        finished = True
                        break
                    text_search = block["text_search"].strip()
                    if not text_search or len(text_search) < 1:
                        continue
                    block_ids.append(str(block["_id"]))
                    doc_ids.append(int(block["doc_ID"]))
                    sentences.append(text_search)
                
                if len(sentences) > 0:
                    # Process the batch
                    vectors = self.model.embedding(sentences)

                    # expects records as tuples - (batch of _ids, batch of vectors, batch of dict metadata)
                    # records = zip(block_ids, vectors) #, doc_ids)
                    # upsert to lanceDB
                    try  :
                        vectors_ingest = [{ 'id' : block_id,'vector': vector.tolist()} for block_id,vector in zip(block_ids,vectors)]
                        self.index.add(vectors_ingest)
                    except Exception as e :
                        raise LLMWareException(message=f"Exception: LanceDB - {e} - {self.index} - schema - "
                                                       f"{self.index.schema}")

                    current_index = self.utils.update_text_index(block_ids,current_index)

                    embeddings_created += len(sentences)
                    status.increment_embedding_status(self.library.library_name, self.model_name, len(sentences))

                    # will add options to configure to show/hide
                    logger.info (f"update: embedding_handler - Lancedb - Embeddings Created: "
                                  f"{embeddings_created} of {num_of_blocks}")

            embedding_summary = self.utils.generate_embedding_summary(embeddings_created)

            logger.info(f"update: EmbeddingHandler - Lancedb - embedding_summary - {embedding_summary}")

            return embedding_summary
    
    def search_index(self, query_embedding_vector, sample_count=10):
        try:
            result = self.index.search(query=query_embedding_vector.tolist())\
                .select(["id", "vector"])\
                .limit(sample_count).to_pandas()

            block_list = []

            for (_, id, vec, score) in result.itertuples(name=None):
                _id = id
                block_result_list = self.utils.lookup_text_index(_id)

                for block in block_result_list:
                    block_list.append((block, score))

        except Exception as e:
            raise LLMWareException(message=f"Exception: LanceDB - {e}")

        return block_list

    def delete_index(self):

        self.db.drop_table(self.collection_name)

        # remove emb key - 'unset' the blocks in the text collection
        self.utils.unset_text_index()

        return 1


class EmbeddingPinecone:

    """Implements the vector database Pinecone.

    ``EmbeddingPinecone`` implements the interface to the ``Pinecone`` vector database. It is used by the
    ``EmbeddingHandler``.

    Parameters
    ----------
    library : object
        A ``Library`` object.

    model : object
        A model object. See :mod:`models` for available models.

    model_name : str, default=None
        Name of the model.

    embedding_dims : int, default=None
        Dimension of the embedding.

    Returns
    -------
    embedding_pinecone : EmbeddingPinecone
        A new ``EmbeddingPinecone`` object.
    """

    def __init__(self, library, model=None, model_name=None, embedding_dims=None):

        self.api_key = PineconeConfig().get_config("pinecone_api_key")
        self.cloud = PineconeConfig().get_config("pinecone_cloud")
        self.region = PineconeConfig().get_config("pinecone_region")

        self.library = library
        self.library_name = self.library.library_name
        self.account_name = self.library.account_name

        # look up model card
        if not model and not model_name:
            raise EmbeddingModelNotFoundException("no-model-or-model-name-provided")

        self.model = model
        self.model_name = model_name
        self.embedding_dims = embedding_dims

        # if model passed (not None), then use model name
        if self.model:
            self.model_name = self.model.model_name
            self.embedding_dims = model.embedding_dims

        # initialize pinecone
        self.index = None

        global GLOBAL_PINECONE_IMPORT
        if not GLOBAL_PINECONE_IMPORT:
            if util.find_spec("pinecone"):

                try:
                    global pinecone
                    pinecone = importlib.import_module("pinecone")
                    GLOBAL_PINECONE_IMPORT = True
                except:
                    raise LLMWareException(message="Exception: could not load pinecone module.")

            else:
                raise LLMWareException(message="Exception: need to import pinecone to use this class.")

        # initiate connection to Pinecone
        try:
            pinecone_client = pinecone.Pinecone(api_key=self.api_key)
        except:
            raise ImportError(
                "Exception - could not connect to Pinecone - please check:"
                "1.  Pinecone python package is installed, e.g,. 'pip install pinecone-client', and"
                "2.  The api key and environment is properly set.")

        # check index name - pinecone - 45 chars - numbers, letters and "-" ok - no "_" and all lowercase

        self.utils = _EmbeddingUtils(library_name=self.library_name,
                                     model_name=self.model_name,
                                     account_name=self.account_name,
                                     db_name="pinecone",
                                     embedding_dims=self.embedding_dims)

        collection_name = self.utils.create_safe_collection_name()
        self.collection_name = collection_name.replace('_', '-')

        self.collection_key = self.utils.create_db_specific_key()

        pinecone_indexes = [pincone_index['name'] for pincone_index in pinecone_client.list_indexes()]
        if self.collection_name not in pinecone_indexes:
            pinecone_client.create_index(
                name=self.collection_name,
                dimension=self.embedding_dims,
                metric="euclidean",
                spec=pinecone.ServerlessSpec(
                    cloud=self.cloud,
                    region=self.region))

            pinecone_client.describe_index(self.collection_name) # Waits for index to be created
            # describe_index_stats()  # Returns: {'dimension': 8, 'index_fullness': 0.0, 'namespaces': {'': {'vector_count': 5}}}

        # connect to index
        self.index = pinecone_client.Index(self.collection_name)

    def create_new_embedding(self, doc_ids = None, batch_size=100):

        def chunks(iterable, batch_size=100):
            """A helper function to break an iterable into chunks of size batch_size."""
            it = iter(iterable)
            chunk = tuple(itertools.islice(it, batch_size))
            while chunk:
                yield chunk
                chunk = tuple(itertools.islice(it, batch_size))

        all_blocks_cursor, num_of_blocks = self.utils.get_blocks_cursor(doc_ids=doc_ids)

        # Initialize a new status
        status = Status(self.library.account_name)
        status.new_embedding_status(self.library.library_name, self.model_name, num_of_blocks)

        embeddings_created = 0

        # starting current_index @ 0
        current_index = 0

        finished = False

        while not finished:
            block_ids, doc_ids, sentences = [], [], []
            # Build the next batch
            for i in range(batch_size):

                block = all_blocks_cursor.pull_one()

                if not block:
                    finished = True
                    break
                text_search = block["text_search"].strip()
                if not text_search or len(text_search) < 1:
                    continue
                block_ids.append(str(block["_id"]))
                doc_ids.append(int(block["doc_ID"]))
                sentences.append(text_search)
            
            if len(sentences) > 0:
                # Process the batch
                vectors = self.model.embedding(sentences)

                # expects records as tuples - (batch of _ids, batch of vectors, batch of dict metadata)
                records = zip(block_ids, vectors) #, doc_ids)
                # upsert to Pinecone

                # Upsert data with 100 vectors per upsert request
                for records_chunk in chunks(records, batch_size=100):
                    self.index.upsert(vectors=records_chunk)

                current_index = self.utils.update_text_index(block_ids,current_index)

                embeddings_created += len(sentences)
                status.increment_embedding_status(self.library.library_name, self.model_name, len(sentences))

                # will add options to configure to show/hide
                logger.info (f"update: embedding_handler - Pinecone - Embeddings Created: "
                             f"{embeddings_created} of {num_of_blocks}")

        embedding_summary = self.utils.generate_embedding_summary(embeddings_created)

        logger.info(f"update: EmbeddingHandler - Pinecone - embedding_summary - {embedding_summary}")

        return embedding_summary

    def search_index(self, query_embedding_vector, sample_count=10):

        result = self.index.query(vector=query_embedding_vector, top_k=sample_count,include_values=True)
       
        block_list = []
        for match in result["matches"]:
            _id = match["id"]

            block_result_list = self.utils.lookup_text_index(_id)

            for block in block_result_list:
                block_list.append((block, match["score"]))

        return block_list

    def delete_index(self, index_name):

        pinecone.delete_index(index_name)

        # remove emb key - 'unset' the blocks in the text collection
        self.utils.unset_text_index()

        return 1


class EmbeddingMongoAtlas:
    """Implements the use of MongoDB Atlas as a vector database.

    ``EmbeddingMongoAtlas`` implements the interface to ``MongoDB Atlas``. It is used by the
    ``EmbeddingHandler``.

    Parameters
    ----------
    library : object
        A ``Library`` object.

    model : object
        A model object. See :mod:`models` for available models.

    model_name : str, default=None
        Name of the model.

    embedding_dims : int, default=None
        Dimension of the embedding.

    Returns
    -------
    embedding_mongoatlas : EmbeddingMongoAtlas
        A new ``EmbeddingMongoAtlas`` object.
    """

    def __init__(self, library, model=None, model_name=None, embedding_dims=None):
        
        # Use a specified Mongo Atlas connection string if supplied.
        # Otherwise fallback to the the Mongo DB connection string 
        # self.connection_uri = os.environ.get("MONGO_ATLAS_CONNECTION_URI", MongoConfig.get_config("collection_db_uri"))

        self.connection_uri = MongoConfig().get_config("atlas_db_uri")

        self.library = library
        self.library_name = self.library.library_name
        self.account_name = self.library.account_name

        # look up model card
        self.model_name = model.model_name
        self.model = model
        self.embedding_dims = embedding_dims

        # look up model card
        if not model and not model_name:
            raise EmbeddingModelNotFoundException("no-model-or-model-name-provided")

        # if model passed (not None), then use model name
        if self.model:
            self.model_name = self.model.model_name
            self.embedding_dims = model.embedding_dims

        self.utils = _EmbeddingUtils(library_name=self.library_name,
                                     model_name=self.model_name,
                                     account_name=self.account_name,
                                     db_name="mongoatlas",
                                     embedding_dims=self.embedding_dims)

        self.collection_name = self.utils.create_safe_collection_name()
        self.collection_key = self.utils.create_db_specific_key()

        # Connect and create a MongoClient
        #   confirm that pymongo installed

        global GLOBAL_PYMONGO_IMPORT
        if not GLOBAL_PYMONGO_IMPORT:
            if util.find_spec("pymongo"):

                try:
                    global pymongo
                    pymongo = importlib.import_module("pymongo")
                    GLOBAL_PYMONGO_IMPORT = True
                except:
                    raise LLMWareException(message="Exception: could not load pymongo module.")

            else:
                raise LLMWareException(message="Exception: need to import pymongo to use this class.")

        # end dynamic import here
        # alt: from pymongo import MongoClient

        self.mongo_client = pymongo.MongoClient(self.connection_uri)

        # Make sure the Database exists by creating a dummy metadata collection
        self.embedding_db_name = "llmware_embeddings"
        self.embedding_db = self.mongo_client["llmware_embeddings"]
        if self.embedding_db_name not in self.mongo_client.list_database_names():
            self.embedding_db["metadata"].insert_one({"created": Utilities().get_current_time_now()})

        # Connect to collection and create it if it doesn't exist by creating a dummy doc
        self.embedding_collection = self.embedding_db[self.collection_name]
        if self.collection_name not in self.embedding_db.list_collection_names():
            self.embedding_collection.insert_one({"created": Utilities().get_current_time_now()})
        
        # If the collection does not have a search index (e.g if it's new), create one
        if len (list(self.embedding_collection.list_search_indexes())) < 1:
            model = { 
                        'name': self.collection_name,
                        'definition': {
                            'mappings': {
                                'dynamic': True, 
                                'fields': {
                                    'eVector': {
                                        'type': 'knnVector', 
                                        'dimensions': self.embedding_dims, 
                                        'similarity': 'euclidean'
                                    },
                                }
                            }
                        }
                    }

            self.embedding_collection.create_search_index(model)

    def create_new_embedding(self, doc_ids = None, batch_size=500):

        all_blocks_cursor, num_of_blocks = self.utils.get_blocks_cursor(doc_ids=doc_ids)

        # Initialize a new status
        status = Status(self.library.account_name)
        status.new_embedding_status(self.library.library_name, self.model_name, num_of_blocks)

        embeddings_created = 0

        # starting current_index @ 0
        current_index = 0

        finished = False

        last_block_id = ""

        while not finished:

            block_ids, doc_ids, sentences = [], [], []
            # Build the next batch

            for i in range(batch_size):

                block = all_blocks_cursor.pull_one()

                if not block:
                    finished = True
                    break
                text_search = block["text_search"].strip()
                if not text_search or len(text_search) < 1:
                    continue
                block_ids.append(str(block["_id"]))
                doc_ids.append(int(block["doc_ID"]))
                sentences.append(text_search)
            
            if len(sentences) > 0:
                # Process the batch
                vectors = self.model.embedding(sentences).tolist()

                docs_to_insert = []
                for i, vector in enumerate(vectors):
                    doc = {
                        "id": str(block_ids[i]),
                        "doc_ID": str(doc_ids[i]),
                        "eVector": vector
                    }
                    docs_to_insert.append(doc)

                insert_result = self.embedding_collection.insert_many(docs_to_insert)

                current_index = self.utils.update_text_index(block_ids,current_index)

                embeddings_created += len(sentences)
                status.increment_embedding_status(self.library.library_name, self.model_name, len(sentences))

                # will add configuration options to hide/show
                logger.info(f"update: embedding_handler - Mongo Atlas - Embeddings Created: "
                            f"{embeddings_created} of {num_of_blocks}")

                last_block_id = block_ids[-1]

        if embeddings_created > 0:

            logger.info(f"Embedding(Mongo Atlas): Waiting for {self.embedding_db_name}.{self.collection_name} "
                        f"to be ready for vector search...")

            start_time = time.time()
            self.wait_for_search_index(last_block_id, start_time)
            wait_time = time.time() - start_time

            logger.info(f"Embedding(Mongo Atlas): {self.embedding_db_name}.{self.collection_name} "
                        f"ready ({wait_time: .2f} seconds)")

        embedding_summary = self.utils.generate_embedding_summary(embeddings_created)

        logger.info(f"update: EmbeddingHandler - Mongo Atlas - embedding_summary - {embedding_summary}")

        return embedding_summary
    
    def wait_for_search_index(self, last_block_id, start_time):

        """ After doc insertion, we want to make sure the index is ready before proceeding ... """

        # if wait longer than 5 mins, then time out and just return
        if time.time() > start_time + (5 * 60):
            return

        # Get the atlas search index
        the_index = self.embedding_collection.list_search_indexes().next()
        
        # If the index doesn't have status="READY" or queryable=True, wait
        if the_index["status"] != "READY" or not the_index["queryable"]:
            time.sleep(3)
            return self.wait_for_search_index(last_block_id, start_time)

        # If we can't find the last block yet in the search index, wait
        search_query = {
            "$search": {
                "index": self.collection_name,
                "text": {
                    "query": str(last_block_id),
                    "path": "id"  # The field in your documents you're matching against
                }
            }
        }
        results = self.embedding_collection.aggregate([search_query])
        if not results.alive:
            time.sleep(1)
            return self.wait_for_search_index(last_block_id, start_time)

    def search_index(self, query_embedding_vector, sample_count=10):

        search_results = self.embedding_collection.aggregate([
            {
                "$vectorSearch": {
                    "index": self.collection_name,
                    "path": "eVector",
                    "queryVector": query_embedding_vector.tolist(),
                    "numCandidates": sample_count * 10, # Following recommendation here: https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-stage/
                    "limit": sample_count
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "doc_ID": 1,
                    "score": { "$meta": "vectorSearchScore" }
                }
            }
        ])

        block_list = []
        for search_result in search_results:
            _id = search_result["id"]

            block_result_list = self.utils.lookup_text_index(_id)

            for block in block_result_list:
                distance = 1 - search_result["score"]   # Atlas returns a score from 0 to 1.0
                block_list.append((block, distance))

        return block_list

    def delete_index(self, index_name):

        self.embedding_db.drop_collection(index_name)

        # remove emb key - 'unset' the blocks in the text collection
        self.utils.unset_text_index()

        return 1


class EmbeddingRedis:

    """Implements the use of Redis as a vector database.

    ``EmbeddingRedis`` implements the interface to ``Redis``. It is used by the
    ``EmbeddingHandler``.

    Parameters
    ----------
    library : object
        A ``Library`` object.

    model : object
        A model object. See :mod:`models` for available models.

    model_name : str, default=None
        Name of the model.

    embedding_dims : int, default=None
        Dimension of the embedding.

    Returns
    -------
    embedding_redis : EmbeddingRedis
        A new ``EmbeddingRedis`` object.
    """

    def __init__(self, library, model=None, model_name=None, embedding_dims=None):

        self.library = library
        self.library_name = library.library_name
        self.account_name = library.account_name

        # Connect to redis - use "localhost" & 6379 by default
        redis_host = RedisConfig().get_config("host")
        redis_port = RedisConfig().get_config("port")

        #   confirm that redis installed

        global GLOBAL_REDIS_IMPORT
        if not GLOBAL_REDIS_IMPORT:
            if util.find_spec("redis"):

                try:
                    global redis
                    redis= importlib.import_module("redis")
                    GLOBAL_REDIS_IMPORT = True
                except:
                    raise LLMWareException(message="Exception: could not load redis module.")

            else:
                raise LLMWareException(message="Exception: need to import redis to use this class.")

        # end dynamic import here

        self.r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

        # look up model card
        self.model = model
        self.model_name = model_name
        self.embedding_dims = embedding_dims

        if self.model:
            self.model_name = self.model.model_name
            self.embedding_dims = self.model.embedding_dims

        self.utils = _EmbeddingUtils(library_name=self.library_name,
                                     model_name=self.model_name,
                                     account_name=self.account_name,
                                     db_name="redis",
                                     embedding_dims=self.embedding_dims)

        self.collection_name = self.utils.create_safe_collection_name()
        self.collection_key = self.utils.create_db_specific_key()

        self.DOC_PREFIX = self.collection_name  # key prefix used for the index

        try:
            # check to see if index exists
            self.r.ft(self.collection_name).info()
            logger.info("update: embedding_handler - Redis - index already exists - %s", self.collection_name)

        except:

            from redis.commands.search import field
            # schema
            schema = (
                field.NumericField("id"),
                field.TextField("text"),
                field.TextField("block_mongo_id"),
                field.NumericField("block_id"),
                field.NumericField("block_doc_id"),
                field.VectorField("vector",                 # Vector Field Name
                            "FLAT", {     #  Vector Index Type: FLAT or HNSW
                                "TYPE": "FLOAT32",          #  FLOAT32 or FLOAT64
                                "DIM": self.embedding_dims,
                                "DISTANCE_METRIC": "L2",     #  "COSINE" alternative
                            }
                            ),
            )

            # index Definition
            from redis.commands.search.indexDefinition import IndexDefinition, IndexType
            definition = IndexDefinition(prefix=[self.DOC_PREFIX],
                                         index_type=IndexType.HASH)

            # create Index
            self.r.ft(self.collection_name).create_index(fields=schema, definition=definition)

            logger.info("update: embedding_handler - Redis - creating new index - %s ", self.collection_name)

    def create_new_embedding(self, doc_ids=None, batch_size=500):

        all_blocks_cursor, num_of_blocks = self.utils.get_blocks_cursor(doc_ids=doc_ids)

        # Initialize a new status
        status = Status(self.library.account_name)
        status.new_embedding_status(self.library.library_name, self.model_name, num_of_blocks)

        embeddings_created = 0
        current_index = 0
        finished = False

        obj_batch = []

        while not finished:

            block_ids, doc_ids, sentences = [], [], []

            # Build the next batch
            for i in range(batch_size):

                block = all_blocks_cursor.pull_one()

                if not block:
                    finished = True
                    break

                text_search = block["text_search"].strip()
                if not text_search or len(text_search) < 1:
                    continue

                block_ids.append(str(block["_id"]))
                doc_ids.append(int(block["doc_ID"]))
                sentences.append(text_search)

                obj = {"block_mongo_id": str(block["_id"]),
                       "block_doc_id": int(block["doc_ID"]),
                       "block_id": int(block["block_ID"]),
                       "text": text_search
                       }

                obj_batch.append(obj)

            if len(sentences) > 0:

                # Process the batch
                vectors = self.model.embedding(sentences)

                pipe = self.r.pipeline()

                for i, embedding in enumerate(vectors):

                    redis_dict = obj_batch[i]

                    embedding = np.array(embedding)
                    redis_dict.update({"vector": embedding.astype(np.float32).tobytes()})
                    key_name = f"{self.DOC_PREFIX}:{redis_dict['block_mongo_id']}"

                    pipe.hset(key_name, mapping=redis_dict)

                res = pipe.execute()
                obj_batch = []

                current_index = self.utils.update_text_index(block_ids,current_index)

                embeddings_created += len(sentences)

                status.increment_embedding_status(self.library.library_name, self.model_name, len(sentences))

                # will add configuration options to show/display
                logger.info(f"update: embedding_handler - Redis - Embeddings Created: "
                             f"{embeddings_created} of {num_of_blocks}")

        embedding_summary = self.utils.generate_embedding_summary(embeddings_created)

        logger.info(f"update: EmbeddingHandler - Redis - embedding_summary - {embedding_summary}")

        return embedding_summary

    def search_index(self, query_embedding_vector, sample_count=10):

        query_embedding_vector = np.array(query_embedding_vector)

        query = (
            redis.commands.search.query.Query(f"*=>[KNN {sample_count} @vector $vec as score]")
            .sort_by("score")
            .return_fields("score", "block_mongo_id", "block_doc_id", "block_id","text")
            .paging(0, sample_count)
            .dialect(2)
        )

        query_params = {
            "vec": query_embedding_vector.astype(np.float32).tobytes()
        }

        results = self.r.ft(self.collection_name).search(query, query_params).docs

        block_list = []
        for j, res in enumerate(results):

            _id = str(res["block_mongo_id"])
            score = float(res["score"])

            block_result_list = self.utils.lookup_text_index(_id)

            for block in block_result_list:
                block_list.append((block, score))

        return block_list

    def delete_index(self):

        # delete index
        self.r.ft(self.collection_name).dropindex(delete_documents=True)

        # remove emb key - 'unset' the blocks in the text collection
        self.utils.unset_text_index()

        return 0


class EmbeddingQdrant:

    """Implements the Qdrant vector database.

    ``EmbeddingQdrant`` implements the interface to ``Qdrant``. It is used by the
    ``EmbeddingHandler``.

    Parameters
    ----------
    library : object
        A ``Library`` object.

    model : object
        A model object. See :mod:`models` for available models.

    model_name : str, default=None
        Name of the model.

    embedding_dims : int, default=None
        Dimension of the embedding.

    Returns
    -------
    embedding_qdrant : EmbeddingQdrant
        A new ``EmbeddingQdrant`` object.
    """

    def __init__(self, library, model=None, model_name=None, embedding_dims=None):

        self.library = library
        self.library_name = library.library_name
        self.account_name = library.account_name

        #   confirm that qdrant installed

        global GLOBAL_QDRANT_IMPORT
        if not GLOBAL_QDRANT_IMPORT:
            if util.find_spec("qdrant_client"):

                try:
                    global qdrant_client
                    qdrant_client = importlib.import_module("qdrant_client")
                    GLOBAL_QDRANT_IMPORT = True
                except:
                    raise LLMWareException(message="Exception: could not load qdrant_client module.")

            else:
                raise LLMWareException(message="Exception: need to import qdrant_client to use this class.")

        # end dynamic import here

        self.qclient = qdrant_client.QdrantClient(**QdrantConfig.get_config())

        # look up model card
        self.model = model
        self.model_name = model_name
        self.embedding_dims = embedding_dims

        if self.model:
            self.model_name = self.model.model_name
            self.embedding_dims = self.model.embedding_dims

        self.utils = _EmbeddingUtils(library_name=self.library_name,
                                     model_name=self.model_name,
                                     account_name=self.account_name,
                                     db_name="qdrant",
                                     embedding_dims=self.embedding_dims)

        self.collection_name = self.utils.create_safe_collection_name()
        self.collection_key = self.utils.create_db_specific_key()

        # check if collection already exists, or if needs to be created

        collections = self.qclient.get_collections()
        collection_exists = False

        for i, cols in enumerate(collections.collections):
            if cols.name == self.collection_name:
                collection_exists = True
                break

        if not collection_exists:

            self.collection = (
                self.qclient.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qdrant_client.http.models.VectorParams(size=self.embedding_dims,
                                                                          distance=qdrant_client.http.models.Distance.DOT), ))

            logger.info("update: embedding_handler - QDRANT - creating new collection - %s",
                         self.collection_name)

        else:
            # if collection already exists, then 'get' collection
            self.collection = self.qclient.get_collection(self.collection_name)

    def create_new_embedding(self, doc_ids=None, batch_size=500):

        all_blocks_cursor, num_of_blocks = self.utils.get_blocks_cursor(doc_ids=doc_ids)

        # Initialize a new status
        status = Status(self.library.account_name)
        status.new_embedding_status(self.library.library_name, self.model_name, num_of_blocks)

        embeddings_created = 0
        current_index = 0
        finished = False

        points_batch = []

        while not finished:

            block_ids, doc_ids, sentences = [], [], []

            # Build the next batch
            for i in range(batch_size):

                block = all_blocks_cursor.pull_one()

                if not block:
                    finished = True
                    break

                text_search = block["text_search"].strip()
                if not text_search or len(text_search) < 1:
                    continue

                block_ids.append(str(block["_id"]))
                doc_ids.append(int(block["doc_ID"]))
                sentences.append(text_search)

            if len(sentences) > 0:

                # Process the batch
                vectors = self.model.embedding(sentences)

                for i, embedding in enumerate(vectors):

                    point_id = str(uuid.uuid4())
                    ps = qdrant_client.http.models.PointStruct(id=point_id, vector=embedding,
                                                               payload={"block_doc_id": doc_ids[i],
                                                                        "sentences": sentences[i],
                                                                        "block_mongo_id": block_ids[i]})

                    points_batch.append(ps)

                #   upsert a batch of points
                self.qclient.upsert(collection_name=self.collection_name, wait=True, points=points_batch)

                points_batch = []

                current_index = self.utils.update_text_index(block_ids,current_index)

                embeddings_created += len(sentences)

                status.increment_embedding_status(self.library.library_name, self.model_name, len(sentences))

                # will add configuration options to show/display
                logger.info(f"update: embedding_handler - Qdrant - Embeddings Created: "
                            f"{embeddings_created} of {num_of_blocks}")

        embedding_summary = self.utils.generate_embedding_summary(embeddings_created)

        logger.info(f"update: EmbeddingHandler - Qdrant - embedding_summary - {embedding_summary}")

        return embedding_summary

    def search_index(self, query_embedding_vector, sample_count=10):

        search_results = self.qclient.search(collection_name=self.collection_name,
                                             query_vector=query_embedding_vector, limit=sample_count)

        block_list = []
        for j, res in enumerate(search_results):

            _id = res.payload["block_mongo_id"]

            block_result_list = self.utils.lookup_text_index(_id)

            for block in block_result_list:
                block_list.append((block, res.score))

        return block_list

    def delete_index(self):

        # delete index - need to add
        self.qclient.delete_collection(collection_name=f"{self.collection_name}")

        # remove emb key - 'unset' the blocks in the text collection
        self.utils.unset_text_index()

        return 0


class EmbeddingPGVector:

    """Implements the interface to the PGVector vector database.

    ``EmbeddingPGVector`` implements the interface to ``PGVector``. It is used by the
    ``EmbeddingHandler``.

    Parameters
    ----------
    library : object
        A ``Library`` object.

    model : object
        A model object. See :mod:`models` for available models.

    model_name : str, default=None
        Name of the model.

    embedding_dims : int, default=None
        Dimension of the embedding.

    Returns
    -------
    embedding_pgvector : EmbeddingPGVector
        A new ``EmbeddingPGVector`` object.
    """

    def __init__(self, library, model=None, model_name=None, embedding_dims=None, full_schema=False):

        self.library = library
        self.library_name = library.library_name
        self.account_name = library.account_name

        #   look up model card
        self.model = model
        self.model_name = model_name
        self.embedding_dims = embedding_dims

        if self.model:
            self.model_name = self.model.model_name
            self.embedding_dims = self.model.embedding_dims

        self.utils = _EmbeddingUtils(library_name=self.library_name,
                                     model_name=self.model_name,
                                     account_name=self.account_name,
                                     db_name="pg_vector",
                                     embedding_dims=self.embedding_dims)

        self.collection_name = self.utils.create_safe_collection_name()
        self.collection_key = self.utils.create_db_specific_key()

        #   Connect to postgres
        postgres_host = PostgresConfig().get_config("host")
        postgres_port = PostgresConfig().get_config("port")
        postgres_db_name = PostgresConfig().get_config("db_name")
        postgres_user_name = PostgresConfig().get_config("user_name")
        postgres_pw = PostgresConfig().get_config("pw")
        postgres_schema = PostgresConfig().get_config("pgvector_schema")

        # default schema captures only minimum required for tracking vectors
        if postgres_schema == "vector_only":
            self.full_schema = False
        else:
            self.full_schema = True

        #   determines whether to use 'skinny' schema or 'full' schema
        #   --note:  in future releases, we will be building out more support for Postgres

        #   first check for core postgres driver, and load if not present
        global GLOBAL_PSYCOPG_IMPORT
        if not GLOBAL_PSYCOPG_IMPORT:
            if util.find_spec("psycopg"):

                try:
                    global psycopg
                    psycopg = importlib.import_module("psycopg")
                    GLOBAL_PSYCOPG_IMPORT = True
                except:
                    raise LLMWareException(message="Exception: could not load psycopg module.")

            else:
                raise LLMWareException(message="Exception: need to import psycopg to use this class.")

        #   second check for pg_vector specific driver and load if not present
        global GLOBAL_PGVECTOR_IMPORT
        if not GLOBAL_PGVECTOR_IMPORT:
            if util.find_spec("pgvector"):

                try:
                    global pgvector
                    pgvector = importlib.import_module("pgvector")
                    GLOBAL_PGVECTOR_IMPORT = True
                except:
                    raise LLMWareException(message="Exception: could not load pgvector module.")

            else:
                raise LLMWareException(message="Exception: need to import neo4j to use this class.")

        #   note: for initial connection, need to confirm that the database exists
        self.conn = psycopg.connect(host=postgres_host, port=postgres_port, dbname=postgres_db_name,
                                    user=postgres_user_name, password=postgres_pw)

        # register vector extension
        self.conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
        from pgvector.psycopg import register_vector
        register_vector(self.conn)

        if not self.full_schema:

            table_create = (f"CREATE TABLE IF NOT EXISTS {self.collection_name} "
                            f"(id bigserial PRIMARY KEY, "
                            f"text text, "
                            f"embedding vector({self.embedding_dims}), "
                            f"block_mongo_id text, "
                            f"block_doc_id integer);")
        else:

            # full schema is a replica of the Mongo parsing output key structure

            table_create = (f"CREATE TABLE IF NOT EXISTS {self.collection_name} "
                            f"(id bigserial PRIMARY KEY, "
                            f"embedding vector({self.embedding_dims}),"
                            f"block_mongo_id text, "
                            f"block_doc_id integer,"
                            f"block_ID integer, "
                            f"doc_ID integer, "
                            f"content_type text, "
                            f"file_type text, "
                            f"master_index integer, "
                            f"master_index2 integer, "
                            f"coords_x integer, "
                            f"coords_y integer, "
                            f"coords_cx integer, "
                            f"coords_cy integer, "
                            f"author_or_speaker text, "
                            f"modified_date text, "
                            f"created_date text, "
                            f"creator_tool text,"
                            f"added_to_collection text,"
                            f"table_block text,"
                            f"text text,"
                            f"external_files text,"
                            f"file_source text,"
                            f"header_text text,"
                            f"text_search text,"
                            f"user_tags text,"
                            f"special_field1 text,"
                            f"special_field2 text,"
                            f"special_field3 text,"
                            f"graph_status text,"
                            f"embedding_flags json,"
                            f"dialog text);")

        # execute the creation of the table, if needed
        self.conn.execute(table_create)
        self.conn.commit()

    def create_new_embedding(self, doc_ids=None, batch_size=500):

        all_blocks_cursor, num_of_blocks = self.utils.get_blocks_cursor(doc_ids=doc_ids)

        # Initialize a new status
        status = Status(self.library.account_name)
        status.new_embedding_status(self.library.library_name, self.model_name, num_of_blocks)

        embeddings_created = 0
        current_index = 0
        finished = False

        obj_batch = []

        while not finished:

            block_ids, doc_ids, sentences = [], [], []

            # Build the next batch
            for i in range(batch_size):

                block = all_blocks_cursor.pull_one()

                if not block:
                    finished = True
                    break

                text_search = block["text_search"].strip()
                if not text_search or len(text_search) < 1:
                    continue
                block_ids.append(str(block["_id"]))
                doc_ids.append(int(block["doc_ID"]))
                sentences.append(text_search)

                if not self.full_schema:

                    obj = {"block_mongo_id": str(block["_id"]),
                           "block_doc_id": int(block["doc_ID"]),
                           "text": text_search}
                else:
                    obj = {}
                    for keys in block:
                        if keys == "_id":
                           value = str(block["_id"])
                           obj.update({"block_mongo_id": value})
                        else:
                            value = block[keys]
                        obj.update({keys:value})
                    obj.update({"block_doc_id": int(block["doc_ID"])})

                obj_batch.append(obj)

            if len(sentences) > 0:

                # Process the batch
                vectors = self.model.embedding(sentences)

                for i, embedding in enumerate(vectors):

                    if not self.full_schema:

                        insert_command=(f"INSERT INTO {self.collection_name} (text, embedding, block_mongo_id,"
                                        f"block_doc_id) VALUES (%s, %s, %s, %s)")

                        insert_array=(obj_batch[i]["text"], embedding,
                                      obj_batch[i]["block_mongo_id"], obj_batch[i]["block_doc_id"],)

                    else:

                        insert_command=(f"INSERT INTO {self.collection_name} "
                                        f"(embedding, block_mongo_id, block_doc_id,"
                                        f"block_ID, doc_ID, content_type, file_type, master_index,"
                                        f"master_index2, coords_x, coords_y,coords_cx, coords_cy,"
                                        f"author_or_speaker, modified_date, created_date, creator_tool,"
                                        f"added_to_collection, table_block, text, external_files,file_source,"
                                        f"header_text, text_search, user_tags, special_field1, special_field2,"
                                        f"special_field3, graph_status, dialog) "
                                        f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
                                        f"%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
                                        f"%s, %s, %s, %s)")

                        insert_array=(embedding, obj_batch[i]["block_mongo_id"],
                                      obj_batch[i]["block_doc_id"], obj_batch[i]["block_ID"],
                                      obj_batch[i]["doc_ID"], obj_batch[i]["content_type"],
                                      obj_batch[i]["file_type"], obj_batch[i]["master_index"],
                                      obj_batch[i]["master_index2"], obj_batch[i]["coords_x"],
                                      obj_batch[i]["coords_y"], obj_batch[i]["coords_cx"],
                                      obj_batch[i]["coords_cy"], obj_batch[i]["author_or_speaker"],
                                      obj_batch[i]["modified_date"], obj_batch[i]["created_date"],
                                      obj_batch[i]["creator_tool"], obj_batch[i]["added_to_collection"],
                                      obj_batch[i]["table"], obj_batch[i]["text"], obj_batch[i]["external_files"],
                                      obj_batch[i]["file_source"], obj_batch[i]["header_text"],
                                      obj_batch[i]["text_search"], obj_batch[i]["user_tags"],
                                      obj_batch[i]["special_field1"], obj_batch[i]["special_field2"], obj_batch[i]["special_field3"],
                                      obj_batch[i]["graph_status"], obj_batch[i]["dialog"])

                    self.conn.execute(insert_command, insert_array)

                self.conn.commit()

                obj_batch = []

                current_index = self.utils.update_text_index(block_ids,current_index)

                embeddings_created += len(sentences)

                status.increment_embedding_status(self.library.library_name, self.model_name, len(sentences))

                # will add configuration options to show/display
                logger.info(f"update: embedding_handler - PGVector - Embeddings Created: "
                             f"{embeddings_created} of {num_of_blocks}")

        embedding_summary = self.utils.generate_embedding_summary(embeddings_created)
        embedded_blocks = embedding_summary["embedded_blocks"]

        logger.info(f"update: EmbeddingHandler - PG_Vector - embedding_summary - {embedding_summary}")

        # safety check on output
        if not isinstance(embedded_blocks, int):
            if len(embedded_blocks) > 0:
                embedded_blocks = embedded_blocks[0]
            else:
                embedded_blocks = embeddings_created

        # create index
        lists = max(embedded_blocks // 1000, 10)

        create_index_command = (f"CREATE INDEX ON {self.collection_name} "
                                f"USING ivfflat(embedding vector_l2_ops) WITH(lists={lists});")

        self.conn.execute(create_index_command)
        self.conn.commit()

        # TODO - add options to create text index and options to query directly against PG

        # Closing the connection
        self.conn.close()

        return embedding_summary

    def search_index(self, query_embedding_vector, sample_count=10):

        #   note: converting to np.array is 'safety' for postgres vector type
        query_embedding_vector = np.array(query_embedding_vector)

        q = (f"SELECT id, block_mongo_id, embedding <-> %s AS distance, text "
             f"FROM {self.collection_name} ORDER BY distance LIMIT %s")

        """
        # alt - look to generalize the query
        q = (f"SELECT embedding <-> %s AS distance, * FROM {self.collection_name} ORDER BY "
             f"distance LIMIT %s")
        """

        cursor = self.conn.cursor()
        results = cursor.execute(q, (query_embedding_vector,sample_count))

        block_list = []
        for j, res in enumerate(results):

            pg_id = res[0]
            _id = res[1]
            distance = res[2]
            text = res[3]

            block_result_list = self.utils.lookup_text_index(_id)

            for block in block_result_list:
                block_list.append((block, distance))

        # Closing the connection
        self.conn.close()

        return block_list

    def delete_index(self, collection_name=None):

        # delete index - drop table
        if collection_name:
            self.collection_name = collection_name

        drop_command = f'''DROP TABLE {self.collection_name} '''

        # Executing the query
        cursor = self.conn.cursor()
        cursor.execute(drop_command)

        logger.info("update: embedding_handler - PG Vector - table dropped - %s", self.collection_name)

        # Commit your changes in the database
        self.conn.commit()

        # Closing the connection
        self.conn.close()

        # remove emb key - 'unset' the blocks in the text collection
        self.utils.unset_text_index()

        return 0


class EmbeddingNeo4j:

    """Implements the interface to Neo4j as a vector database.

    ``EmbeddingNeo4j`` implements the interface to ``Neo4j``. It is used by the
    ``EmbeddingHandler``.

    Parameters
    ----------
    library : object
        A ``Library`` object.

    model : object
        A model object. See :mod:`models` for available models.

    model_name : str, default=None
        Name of the model.

    embedding_dims : int, default=None
        Dimension of the embedding.

    Returns
    -------
    embedding_Neo4j : EmbeddingNeo4j
        A new ``EmbeddingNeo4j`` object.
    """

    def __init__(self, library, model=None, model_name=None, embedding_dims=None):

        # look up model card
        if not model and not model_name:
            raise EmbeddingModelNotFoundException("no-model-or-model-name-provided")

        self.library = library
        self.library_name = library.library_name
        self.model = model
        self.model_name = model_name
        self.embedding_dims = embedding_dims
        self.account_name = library.account_name

        # if model passed (not None), then use model name
        if self.model:
            self.model_name = self.model.model_name
            self.embedding_dims = model.embedding_dims

        # user and password names are taken from environmen variables
        # Names for user and password are taken from the link below
        # https://neo4j.com/docs/operations-manual/current/tools/neo4j-admin/upload-to-aura/#_options
        uri = Neo4jConfig.get_config('uri')
        user = Neo4jConfig.get_config('user')
        password = Neo4jConfig.get_config('password')
        database = Neo4jConfig.get_config('database')

        global GLOBAL_NEO4J_IMPORT
        if not GLOBAL_NEO4J_IMPORT:
            if util.find_spec("neo4j"):

                try:
                    global neo4j
                    neo4j = importlib.import_module("neo4j")
                    GLOBAL_NEO4J_IMPORT = True
                except:
                    raise LLMWareException(message="Exception: could not load neo4j module.")

            else:
                raise LLMWareException(message="Exception: need to import neo4j to use this class.")

        # end dynamic import here

        # Connect to Neo4J and verify connection.
        # Code taken from the code below
        # https://github.com/langchain-ai/langchain/blob/master/libs/community/langchain_community/vectorstores/neo4j_vector.py#L165C9-L177C14
        try:
            self.driver = neo4j.GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
        except neo4j.exceptions.ServiceUnavailable:
            raise ValueError(
                "Could not connect to Neo4j database. "
                "Please ensure that the url is correct and that Neo4j is up and running.")
        except neo4j.exceptions.AuthError:
            raise ValueError(
                "Could not connect to Neo4j database. "
                "Please ensure that the username and password are correct.")
        except Exception as err:
            # We raise here any other exception that happened.
            # This is useful for debugging when some other error occurs.
            raise 

        # Make sure that the Neo4j version supports vector indexing.
        neo4j_version = self._query('call dbms.components() '
                                    'yield name, versions, edition '
                                    'unwind versions as version '
                                    'return version')[0]['version']

        neo4j_version = tuple(map(int, neo4j_version.split('.')))

        target_version = (5, 11, 0)
        if neo4j_version < target_version:
            raise ValueError('Vector indexing requires a Neo4j version >= 5.11.0')

        # If the index does not exist, then we create the vector search index.
        neo4j_indexes = self._query('SHOW INDEXES yield name')
        neo4j_indexes = [neo4j_index['name'] for neo4j_index in neo4j_indexes]
        if 'vectorIndex' not in neo4j_indexes:
            self._query(
                query='CALL '
                      'db.index.vector.createNodeIndex('
                          '$indexName, '
                          '$label, '
                          '$propertyKey, '
                          'toInteger($vectorDimension), '
                          '"euclidean"'
                      ')',
                parameters={
                        'indexName': 'vectorIndex',
                        'label': 'Chunk',
                        'propertyKey': 'embedding',
                        'vectorDimension': int(self.model.embedding_dims)
                })


        self.utils = _EmbeddingUtils(library_name=self.library_name,
                                     model_name=self.model_name,
                                     account_name=self.account_name,
                                     db_name="neo4j",
                                     embedding_dims=self.embedding_dims)

    def create_new_embedding(self, doc_ids=None, batch_size=500):
        
        all_blocks_cursor, num_of_blocks = self.utils.get_blocks_cursor(doc_ids=doc_ids)

        # Initialize a new status
        status = Status(self.library.account_name)
        status.new_embedding_status(self.library.library_name, self.model_name, num_of_blocks)

        embeddings_created = 0
        current_index = 0
        finished = False

        while not finished:
            block_ids, doc_ids, sentences = [], [], []

            # Build the next batch
            for i in range(batch_size):
                block = all_blocks_cursor.pull_one()
                if not block:
                    finished = True
                    break

                text_search = block["text_search"].strip()
                if not text_search or len(text_search) < 1:
                    continue

                block_ids.append(str(block["_id"]))
                doc_ids.append(int(block["doc_ID"]))
                sentences.append(text_search)

            if len(sentences) > 0:
                # Process the batch
                vectors = self.model.embedding(sentences)
                data = [block_ids, doc_ids, vectors]

                # Insert into Neo4J
                insert_query = (
                    "UNWIND $data AS row "
                    "CALL "
                    "{ " 
                    "WITH row "
                    "MERGE (c:Chunk {id: row.doc_id, block_id: row.block_id}) "
                    "WITH c, row "
                    "CALL db.create.setVectorProperty(c, 'embedding', row.embedding) "
                    "YIELD node "
                    "SET c.sentence = row.sentence "
                    "} "
                    f"IN TRANSACTIONS OF {batch_size} ROWS"
                )

                parameters = {
                    "data": [
                        {"block_id": block_id, "doc_id": doc_id, "sentence": sentences, "embedding": vector}
                        for block_id, doc_id, sentence, vector in zip(
                            block_ids, doc_ids, sentences, vectors
                        )
                    ]
                }

                self._query(query=insert_query, parameters=parameters)

                current_index = self.utils.update_text_index(block_ids, current_index)

                # Update statistics
                embeddings_created += len(sentences)
                status.increment_embedding_status(self.library.library_name, self.model_name, len(sentences))

                logger.info(f"update: embedding_handler - Neo4j - Embeddings Created: "
                             f"{embeddings_created} of {num_of_blocks}")

        embedding_summary = self.utils.generate_embedding_summary(embeddings_created)
        logger.info(f'update: EmbeddingHandler - Neo4j - embedding_summary - {embedding_summary}')

        return embedding_summary

    def search_index(self, query_embedding_vector, sample_count=10):
        block_list = []

        search_query = 'CALL db.index.vector.queryNodes("vectorIndex" , $sample_count, $query_embedding_vector) '\
                       'YIELD node, score '

        parameters = {'sample_count': sample_count, 'query_embedding_vector': query_embedding_vector}

        results = self._query(query=search_query, parameters=parameters)

        for result in results:
            block_id = result['node']['block_id']
            block_result_list = self.utils.lookup_text_index(block_id)

            for block in block_result_list:
                block_list.append((block, result["score"]))

        return block_list

    def delete_index(self, index_name):

        try:
            self._query(f"DROP INDEX $index_name", {'index_name': index_name})
        except neo4j.DatabaseError: # Index did not exist yet
            pass

        self.utils.unset_text_index()

    def _query(self, query, parameters=None):

        # alt: from neo4j.exceptions import CypherSyntaxError

        parameters = parameters or {}

        with self.driver.session(database='neo4j') as session:
            try:
                data = session.run(query, parameters)
                return [d.data() for d in data]
            except neo4j.exceptions.CypherSyntaxError as e:
                raise ValueError(f'Cypher Statement is not valid\n{e}')


class EmbeddingChromaDB:

    """Implements the interface to the ChromaDB vector database.

    ``EmbeddingChromaDB`` implements the interface to ``ChromaDB``. It is used by the
    ``EmbeddingHandler``.

    Parameters
    ----------
    library : object
        A ``Library`` object.

    model : object
        A model object. See :mod:`models` for available models.

    model_name : str, default=None
        Name of the model.

    embedding_dims : int, default=None
        Dimension of the embedding.

    Returns
    -------
    embedding_chromadb : EmbeddingChromaDB
        A new ``EmbeddingPGVector`` object.
    """

    def __init__(self, library, model=None, model_name=None, embedding_dims=None):

        #
        #   General llmware set up code
        #
        #   confirm that pymilvus installed

        global GLOBAL_CHROMADB_IMPORT
        if not GLOBAL_CHROMADB_IMPORT:
            if util.find_spec("chromadb"):

                try:
                    global chromadb
                    chromadb = importlib.import_module("chromadb")
                    GLOBAL_CHROMADB_IMPORT = True
                except:
                    raise LLMWareException(message="Exception: could not load chromadb module.")

            else:
                raise LLMWareException(message="Exception: need to import chromadb to use this class.")

        # end dynamic import here

        # look up model card
        if not model and not model_name:
            raise EmbeddingModelNotFoundException("no-model-or-model-name-provided")

        self.library = library
        self.library_name = library.library_name
        self.model = model
        self.model_name = model_name
        self.embedding_dims = embedding_dims
        self.account_name = library.account_name

        # if model passed (not None), then use model name
        if self.model:
            self.model_name = self.model.model_name
            self.embedding_dims = model.embedding_dims

        #
        # ChromaDB instantiation
        #

        # Get environment variables to decide which client to use.
        persistent_path = ChromaDBConfig.get_config('persistent_path')
        host = ChromaDBConfig.get_config('host')

        # Instantiate client.
        if not util.find_spec("chromadb"):
            raise DependencyNotInstalledException("pip3 install chromadb")

        if host is None and persistent_path is None:
            self.client = chromadb.EphemeralClient()

        if persistent_path is not None:
            self.client = chromadb.PersistentClient(path=persistent_path)

        if host is not None:
            self.client = chromadb.HttpClient(host=host,
                                              port=ChromaDBConfig.get_config('port'),
                                              ssl=ChromaDBConfig.get_config('ssl'),
                                              headers=ChromaDBConfig.get_config('headers'))

        #   ChromaDB Collection maps to the LLMWare library
        collection_name = self.library_name

        # If the collection already exists, it is returned.
        self._collection = self.client.create_collection(name=collection_name, get_or_create=True)

        #
        # Embedding utils
        #

        self.utils = _EmbeddingUtils(library_name=self.library_name,
                                     model_name=self.model_name,
                                     account_name=self.account_name,
                                     db_name="chromadb",
                                     embedding_dims=self.embedding_dims)

    def create_new_embedding(self, doc_ids=None, batch_size=500):

        all_blocks_cursor, num_of_blocks = self.utils.get_blocks_cursor(doc_ids=doc_ids)

        # Initialize a new status
        status = Status(self.library.account_name)
        status.new_embedding_status(self.library.library_name, self.model_name, num_of_blocks)

        embeddings_created = 0
        current_index = 0
        finished = False

        while not finished:
            block_ids, doc_ids, sentences = [], [], []

            # Build the next batch
            for i in range(batch_size):
                block = all_blocks_cursor.pull_one()
                if not block:
                    finished = True
                    break

                text_search = block["text_search"].strip()
                if not text_search or len(text_search) < 1:
                    continue

                block_ids.append(str(block["_id"]))
                doc_ids.append(int(block["doc_ID"]))
                sentences.append(text_search)

            if len(sentences) > 0:
                # Process the batch
                vectors = self.model.embedding(sentences)

                # Insert into ChromaDB
                ids = [f'{doc_id}-{block_id}' for doc_id, block_id in zip(doc_ids, block_ids)]
                metadatas = [{'doc_id': doc_id, 'block_id': block_id, 'sentence': sentence}
                             for doc_id, block_id, sentence in zip(doc_ids, block_ids, sentences)]

                self._collection.add(ids=ids,
                                     documents=doc_ids,
                                     embeddings=vectors,
                                     metadatas=metadatas)

                current_index = self.utils.update_text_index(block_ids, current_index)

                # Update statistics
                embeddings_created += len(sentences)
                status.increment_embedding_status(self.library.library_name, self.model_name, len(sentences))

                logger.info(f"update: embedding_handler - ChromaDB - Embeddings Created: "
                             f"{embeddings_created} of {num_of_blocks}")

        embedding_summary = self.utils.generate_embedding_summary(embeddings_created)
        logger.info(f'update: EmbeddingHandler - ChromaDB - embedding_summary - {embedding_summary}')

        return embedding_summary

    def search_index(self, query_embedding_vector, sample_count=10):

        block_list = []

        # add one dimension because chroma expects two dimensions - a list of lists
        query_embedding_vector = query_embedding_vector.reshape(1, -1)

        results = self._collection.query(query_embeddings=query_embedding_vector, n_results=sample_count)

        for idx_result, _ in enumerate(results['ids'][0]):
            block_id = results['metadatas'][0][idx_result]['block_id']
            block_result_list = self.utils.lookup_text_index(block_id)

            for block in block_result_list:
                block_list.append((block, results['distances'][0][idx_result]))

        return block_list

    def delete_index(self):

        self.client.delete_collection(self._collection.name)
        self.utils.unset_text_index()
