
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


import os
import faiss
import logging
import numpy as np
import re
import time

from bson import ObjectId
from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection
from pymongo import MongoClient

from llmware.configs import LLMWareConfig
from llmware.exceptions import UnsupportedEmbeddingDatabaseException
from llmware.resources import CollectionRetrieval, CollectionWriter
from llmware.status import Status
from llmware.util import Utilities

class EmbeddingHandler:

    # An EmbeddingHandler is used for all embedding-related interactions with a library
    # It provides a common set of methods that wrap the specific embedding classes.

    def __init__(self, library):
        
        self.supported_embedding_dbs = ["milvus", "faiss", "pinecone", "mongo_atlas"]
        self.library = library
   
    # Create a new embedding. 
    def create_new_embedding(self, embedding_db, model, doc_ids=None, batch_size=500):

        embedding_class = self._load_embedding_db(embedding_db, model)
        embedding_status = embedding_class.create_new_embedding(doc_ids, batch_size)

        if embedding_status:
            self.library.update_embedding_status("yes", model.model_name, embedding_db)

        return embedding_status
   
    # Search the vector space
    def search_index(self, query_vector, embedding_db, model, sample_count=10):
        # Need to normalize the query_vector.  Sometimes it comes in as [[1.1,2.1,3.1]] (from Transformers) and sometimes as [1.1,2.1,3.1]
        # We'll make sure it's the latter and then each Embedding Class will deal with it how it needs to
        if len(query_vector) == 1:
            query_vector = query_vector[0]

        embedding_class = self._load_embedding_db(embedding_db, model)
        return embedding_class.search_index(query_vector,sample_count=sample_count)

    # Delete a specific index (for a given model)
    def delete_index(self, embedding_db, model):

        embedding_class = self._load_embedding_db(embedding_db, model)
        embedding_class.delete_embedding()
        self.library.update_embedding_status(None, None, None)

    # Delete all embeddings for the given library across all embedding dbs
    def delete_all_indexes(self):
        EmbeddingMilvus(self.library).delete_all_indexes()
        EmbeddingFAISS(self.library).delete_all_indexes()
        try:
            EmbeddingPinecone(self.library).delete_all_indexes()
        except ImportError:
            logging.info("Not deleting any pinecone indexes due to pinecone module not being present")
    
    # Load the appropriate embedding class and update the class variables
    def _load_embedding_db(self, embedding_db, model):

        if not embedding_db in self.supported_embedding_dbs:
            raise UnsupportedEmbeddingDatabaseException(embedding_db)
         
        if embedding_db == "milvus": 
            return EmbeddingMilvus(self.library, model)

        if embedding_db == "faiss": 
            return EmbeddingFAISS(self.library, model)

        if embedding_db == "pinecone": 
            return EmbeddingPinecone(self.library, model)

        if embedding_db == "mongo_atlas": 
            return EmbeddingMongoAtlas(self.library, model)

    def generate_index_name(self, account_name, library_name, model_name, max_component_length=19):

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


class EmbeddingMilvus:

    def __init__(self, library, model):

        self.library = library
        self.milvus_alias = "default"

        # Connect to milvus
        connections.connect(self.milvus_alias,
                            host=LLMWareConfig.get_config("milvus_host"),
                            port=LLMWareConfig.get_config("milvus_port"))
        
        # look up model card
        self.model = model
        self.model_name = self.model.model_name

        #   milvus - 255 chars - letters, numbers and "_" OK -> does not accept "-" or " " in collection name
        #   removes a few common non-alpha characters - we can expand the regex to be wider
        #   caps at 43 chars + two '_'s in collection name - conforms with Pinecone char size
        #   puts in lower case - conforms with Pinecone requirement

        converted_library_name = re.sub("[-@_.\/ ]", "", self.library.library_name).lower()
        if len(converted_library_name) > 18:
            converted_library_name = converted_library_name[0:18]

        converted_model_name = re.sub("[-@_.\/ ]", "", self.model_name).lower()
        if len(converted_model_name) > 18:
            # chops off the start of the model name if longer than 18 chars
            starter = len(converted_model_name) - 18
            converted_model_name = converted_model_name[starter:]

        converted_account_name = re.sub("[-@_.\/ ]","", self.library.account_name).lower()
        if len(converted_model_name) > 7:
            converted_account_name = converted_account_name[0:7]

        # get collection name here
        self.collection_name = f"{converted_account_name}_{converted_library_name}_{converted_model_name}"

        # If the Collection doesn't already exist, create it
        if not utility.has_collection(self.collection_name):
            fields = [
                FieldSchema(name="block_mongo_id", dtype=DataType.VARCHAR, is_primary=True, max_length=30,auto_id=False),
                FieldSchema(name="block_doc_id", dtype=DataType.INT64),
                FieldSchema(name="embedding_vector", dtype=DataType.FLOAT_VECTOR, dim=self.model.embedding_dims)
            ]

            collection = Collection(self.collection_name, CollectionSchema(fields))
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            collection.create_index("embedding_vector", index_params)

        self.collection = Collection(self.collection_name)

        # will leave "-" and "_" in file path, but remove "@" and " "
        model_safe_path = re.sub("[@ ]", "", self.model_name).lower()
        self.mongo_key = "embedding_milvus_" + model_safe_path

    def __del__(self):
        connections.disconnect("default")

    def create_new_embedding(self, doc_ids = None, batch_size=500):

        if doc_ids:
            num_of_blocks = self.library.collection.count_documents({"doc_ID": {"$in": doc_ids}})
            all_blocks_cursor = CollectionRetrieval(self.library.collection).filter_by_key_value_range("doc_ID", doc_ids)
        else:
            num_of_blocks = self.library.collection.count_documents({self.mongo_key: {"$exists": False }})
            all_blocks_cursor = CollectionRetrieval\
                (self.library.collection).custom_filter({self.mongo_key: {"$exists": False }})
        
        # Initialize a new status
        status = Status(self.library.account_name)
        status.new_embedding_status(self.library.library_name, self.model_name, num_of_blocks)

        embeddings_created = 0
        current_index = 0
        finished = False

        all_blocks_iter = iter(all_blocks_cursor)
        while not finished:
            block_ids, doc_ids, sentences = [], [], []
            # Build the next batch
            for i in range(batch_size):
                block = next(all_blocks_iter, None)
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
                self.collection.insert(data)

                # Update mongo
                for block_id in block_ids:
                    self.library.collection.update_one({"_id": ObjectId(block_id)}, {"$set": {self.mongo_key:
                                                                                              current_index}})
                    current_index += 1
            
                embeddings_created += len(sentences)

                status.increment_embedding_status(self.library.library_name, self.model_name, len(sentences))
                #print (f"Embeddings Created: {embeddings_created} of {num_of_blocks}")
        
        self.collection.flush()
        embedding_summary = {"embeddings_created": embeddings_created}

        return embedding_summary

    def search_index(self, query_embedding_vector, sample_count=10):

        self.collection.load()

        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10}
        }
        result = self.collection.search(
            data=[query_embedding_vector],
            anns_field="embedding_vector",
            param=search_params,
            limit=sample_count,
            output_fields=["block_mongo_id"]
        )

        block_list = []
        for hits in result:
            for hit in hits:
                _id = hit.entity.get('block_mongo_id') 
                block_cursor = CollectionRetrieval(self.library.collection).filter_by_key("_id", ObjectId(_id))
                try:
                    block = block_cursor.next()
                    block_list.append((block, hit.distance))
                except StopIteration:
                    # The cursor is empty (no blocks found)
                    continue 
        return block_list
   
    def delete_embedding(self):
        collection = Collection(self.collection_name)
        collection.release()
        utility.drop_collection(self.collection_name)
        connections.disconnect(self.milvus_alias)

        # Delete mongo fields
        block_cursor = CollectionWriter(self.library.collection).update_many_records_custom({}, {
            "$unset": {self.mongo_key: ""}})

    def convert_to_underscores(self, input_string):
        return input_string.replace("-", "_").replace(" ", "_")


class EmbeddingFAISS:

    def __init__(self, library, model=None):

        self.library = library
        self.index = None
        
        self.model = model
        self.model_name = model.model_name
        if not self.model_name:
            self.model_name = model.__class__.__name__
            
        self.embedding_dims = self.model.embedding_dims

        # embedding file name here

        # will leave "-" and "_" in file path, but remove "@" and " "
        model_safe_path = re.sub("[@\/. ]", "", self.model_name).lower()

        self.embedding_file_path = os.path.join(self.library.embedding_path, model_safe_path, "embedding_file_faiss")
        self.mongo_key = "embedding_faiss_" + model_safe_path

    def create_new_embedding(self, doc_ids=None, batch_size=100):

        # Load or create index
        if not self.index:
            if os.path.exists(self.embedding_file_path):
                self.index = faiss.read_index(self.embedding_file_path)
            else: 
                self.index = faiss.IndexFlatL2(self.embedding_dims)

        if doc_ids:
            num_of_blocks = self.library.collection.count_documents({"doc_ID": {"$in": doc_ids}})
            all_blocks_cursor = CollectionRetrieval(self.library.collection).filter_by_key_value_range("doc_ID", doc_ids)
        else:
            num_of_blocks = self.library.collection.count_documents({self.mongo_key: {"$exists": False }})
            all_blocks_cursor = CollectionRetrieval(self.library.collection).\
                custom_filter({self.mongo_key: { "$exists": False }})

        # Initialize a new status
        status = Status(self.library.account_name)
        status.new_embedding_status(self.library.library_name, self.model_name, num_of_blocks)

        embeddings_created = 0
        finished = False

        # batch_size = 50

        all_blocks_iter = iter(all_blocks_cursor)
        while not finished:

            block_ids, sentences = [], []
            current_index = self.index.ntotal
            # Build the next batch
            for i in range(batch_size):

                block = next(all_blocks_iter, None)

                # print("update: faiss iteration thru collection - ", i)

                if not block:
                    finished = True
                    break

                text_search = block["text_search"].strip()

                # print("update: text_search - ", text_search)

                if not text_search or len(text_search) < 1:
                    continue
                block_ids.append(str(block["_id"]))
                sentences.append(text_search)
            
            if len(sentences) > 0:
                # Process the batch
                vectors = self.model.embedding(sentences)
                self.index.add(np.array(vectors))

                # Update mongo
                for block_id in block_ids:
                    self.library.collection.update_one({"_id": ObjectId(block_id)}, {"$set": {self.mongo_key: current_index}}) 
                    current_index += 1          

                embeddings_created += len(sentences)
                status.increment_embedding_status(self.library.library_name, self.model_name, len(sentences))
                #print (f"Embeddings Created: {embeddings_created} of {num_of_blocks}")
        
        # Ensure any existing file is removed before saving
        if os.path.exists(self.embedding_file_path):
            os.remove(self.embedding_file_path)
        os.makedirs(os.path.dirname(self.embedding_file_path), exist_ok=True)
        faiss.write_index(self.index, self.embedding_file_path)

        embedding_summary = {"embeddings_created": embeddings_created}  
        return embedding_summary

    def search_index (self, query_embedding_vector, sample_count=10):

        if not self.index:
            self.index = faiss.read_index(self.embedding_file_path)

        distance_list, index_list = self.index.search(np.array([query_embedding_vector]), sample_count)

        block_list = []
        for i, index in enumerate(index_list[0]):
            index_int = int(index.item())
            block_cursor = CollectionRetrieval(self.library.collection).filter_by_key(self.mongo_key, index_int)
            try:
                block = block_cursor.next()
                block_list.append((block, distance_list[0][i]))
            except StopIteration:
                # The cursor is empty (no blocks found)
                continue    
        return block_list

    def delete_embedding(self):
        if os.path.exists(self.embedding_file_path):
            os.remove(self.embedding_file_path)

            # Delete mongo fields
            block_cursor = CollectionWriter(self.library.collection).update_many_records_custom({}, {
                "$unset": {self.mongo_key: ""}})


class EmbeddingPinecone:

    def __init__(self, library, model=None):

        # Try to import pinecone
        try:
            import pinecone
        except ImportError:
            raise ImportError (
                "Could not import the pinecone Python package. " 
                "Please install it with 'pip install pinecone-client'"
            )
        
        self.api_key = os.environ.get("USER_MANAGED_PINECONE_API_KEY")
        self.environment = os.environ.get("USER_MANAGED_PINECONE_ENVIRONMENT")

        self.library = library

        # look up model card
        self.model_name = model.model_name
        self.model = model
        self.embedding_dims = model.embedding_dims

        # initialize pinecone
        self.index = None

        # initiate connection to Pinecone
        pinecone.init(api_key=self.api_key, environment=self.environment)

        # check index name - pinecone - 45 chars - numbers, letters and "-" ok - no "_" and all lowercase

        converted_library_name = re.sub("[-@_.\/ ]", "", self.library.library_name).lower()
        if len(converted_library_name) > 18:
            converted_library_name = converted_library_name[0:18]

        converted_model_name = re.sub("[-@_.\/ ]", "", self.model_name).lower()
        if len(converted_model_name) > 18:
            # chops off the start of the model name if longer than 18 chars
            starter = len(converted_model_name) - 18
            converted_model_name = converted_model_name[starter:]
            # converted_model_name = converted_model_name[0:18]

        converted_account_name = re.sub("[-@_.\/ ]", "", self.library.account_name).lower()
        if len(converted_model_name) > 7:
            converted_account_name = converted_account_name[0:7]

        # converted_library_name =  self.convert_to_hyphens(self.library.library_name)
        # converted_model_name = self.convert_to_hyphens(self.model_name)

        # build new name here
        self.index_name = f"{converted_account_name}-{converted_library_name}-{converted_model_name}"

        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(self.index_name, dimension=self.embedding_dims, metric="euclidean")
            pinecone.describe_index(self.index_name) # Waits for index to be created
            # describe_index_stats()  # Returns: {'dimension': 8, 'index_fullness': 0.0, 'namespaces': {'': {'vector_count': 5}}}

        # connect to index
        self.index = pinecone.Index(self.index_name)

        # will leave "-" and "_" in file path, but remove "@" and " "
        model_safe_path = re.sub("[@ ]", "", self.model_name).lower()
        self.mongo_key = "embedding_pinecone_" + model_safe_path

    def create_new_embedding(self, doc_ids = None, batch_size=500):

        if doc_ids:
            num_of_blocks = self.library.collection.count_documents({"doc_ID": {"$in": doc_ids}})
            all_blocks_cursor = CollectionRetrieval(self.library.collection).filter_by_key_value_range("doc_ID", doc_ids)
        else:
            num_of_blocks = self.library.collection.count_documents({self.mongo_key: {"$exists": False }})
            all_blocks_cursor = CollectionRetrieval(self.library.collection).\
                custom_filter({self.mongo_key: { "$exists": False }})

        # Initialize a new status
        status = Status(self.library.account_name)
        status.new_embedding_status(self.library.library_name, self.model_name, num_of_blocks)

        embeddings_created = 0

        # starting current_index @ 0
        current_index = 0

        finished = False

        all_blocks_iter = iter(all_blocks_cursor)
        while not finished:
            block_ids, doc_ids, sentences = [], [], []
            # Build the next batch
            for i in range(batch_size):
                block = next(all_blocks_iter, None)
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

                # expects records as tuples - (batch of _ids, batch of vectors, batch of dict metadata)
                records = zip(block_ids, vectors) #, doc_ids)
                # upsert to Pinecone
                self.index.upsert(vectors=records)

                # Update mongo
                for block_id in block_ids:
                    self.library.collection.update_one({"_id": ObjectId(block_id)},
                                                       {"$set": {self.mongo_key: current_index}})
                    current_index += 1

                embeddings_created += len(sentences)
                status.increment_embedding_status(self.library.library_name, self.model_name, len(sentences))
                #print (f"Embeddings Created: {embeddings_created} of {num_of_blocks}")

        embedding_summary = {"embeddings_created": embeddings_created}  
        return embedding_summary

    def search_index(self, query_embedding_vector, sample_count=10):

        result = self.index.query(vector=query_embedding_vector.tolist(), top_k=sample_count,include_values=True)
       
        block_list = []
        for match in result["matches"]:
            _id = match["id"]
            block_cursor = CollectionRetrieval(self.library.collection).filter_by_key("_id", ObjectId(_id))
            try:
                block = block_cursor.next()
                distance = match["score"]
                block_list.append((block, distance))
            except StopIteration:
                # The cursor is empty (no blocks found)
                continue 

        return block_list

    def delete_index(self, index_name):
        pinecone.delete_index(index_name)

        # Delete mongo fields
        block_cursor = CollectionWriter(self.library.collection).update_many_records_custom({}, {
            "$unset": {self.mongo_key: ""}})

    def delete_all_indexes(self):
        placeholder_no_action_taken_currently = 0

    def convert_to_hyphens(self, input_string):
        return input_string.replace("_", "-").replace(" ", "-").lower()


class EmbeddingMongoAtlas:

    def __init__(self, library, model=None):
        
        # Use a specified Mongo Atlas connection string if supplied.
        # Otherwise fallback to the the Mongo DB connection string 
        self.connection_uri = os.environ.get("MONGO_ATLAS_CONNECTION_URI",
                                             LLMWareConfig.get_config("collection_db_uri"))

        self.library = library

        # look up model card
        self.model_name = model.model_name
        self.model = model
        self.embedding_dims = model.embedding_dims

        # Create a "safe" index name
        converted_library_name = re.sub("[-@_.\/ ]", "", self.library.library_name).lower()
        if len(converted_library_name) > 18:
            converted_library_name = converted_library_name[0:18]

        converted_model_name = re.sub("[-@_.\/ ]", "", self.model_name).lower()
        if len(converted_model_name) > 18:
            # chops off the start of the model name if longer than 18 chars
            starter = len(converted_model_name) - 18
            converted_model_name = converted_model_name[starter:]
            # converted_model_name = converted_model_name[0:18]

        converted_account_name = re.sub("[-@_.\/ ]", "", self.library.account_name).lower()
        if len(converted_model_name) > 7:
            converted_account_name = converted_account_name[0:7]

        # build new name here
        self.index_name = f"{converted_account_name}-{converted_library_name}-{converted_model_name}"

        # Connect and create a MongoClient
        self.mongo_client = MongoClient(self.connection_uri)

        # Make sure the Database exists by creating a dummy metadata collection
        self.embedding_db_name = "llmware_embeddings"
        self.embedding_db = self.mongo_client["llmware_embeddings"]
        if self.embedding_db_name not in self.mongo_client.list_database_names():
            self.embedding_db["metadata"].insert_one({"created": Utilities().get_current_time_now()})

        # Connect to collection and create it if it doesn't exist by creating a dummy doc
        self.embedding_collection = self.embedding_db[self.index_name]
        if self.index_name not in self.embedding_db.list_collection_names():
            self.embedding_collection.insert_one({"created": Utilities().get_current_time_now()})
        
        # If the collection does not have a search index (e.g if it's new), create one
        if len (list(self.embedding_collection.list_search_indexes())) < 1:
            model = { 
                        'name': self.index_name, 
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

        # will leave "-" and "_" in file path, but remove "@" and " "
        model_safe_path = re.sub("[@ ]", "", self.model_name).lower()
        self.mongo_key = "embedding_mongoatlas_" + model_safe_path

    def create_new_embedding(self, doc_ids = None, batch_size=500):

        if doc_ids:
            num_of_blocks = self.library.collection.count_documents({"doc_ID": {"$in": doc_ids}})
            all_blocks_cursor = CollectionRetrieval(self.library.collection).filter_by_key_value_range("doc_ID", doc_ids)
        else:
            num_of_blocks = self.library.collection.count_documents({self.mongo_key: {"$exists": False }})
            all_blocks_cursor = CollectionRetrieval(self.library.collection).\
                custom_filter({self.mongo_key: { "$exists": False }})
       
        # Initialize a new status
        status = Status(self.library.account_name)
        status.new_embedding_status(self.library.library_name, self.model_name, num_of_blocks)

        embeddings_created = 0

        # starting current_index @ 0
        current_index = 0

        finished = False

        all_blocks_iter = iter(all_blocks_cursor)
        last_block_id = ""
        while not finished:
            block_ids, doc_ids, sentences = [], [], []
            # Build the next batch
            for i in range(batch_size):
                block = next(all_blocks_iter, None)
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

                # Update mongo
                for block_id in block_ids:
                    self.library.collection.update_one({"_id": ObjectId(block_id)},
                                                       {"$set": {self.mongo_key: current_index}})
                    current_index += 1

                embeddings_created += len(sentences)
                status.increment_embedding_status(self.library.library_name, self.model_name, len(sentences))
                #print (f"Embeddings Created: {embeddings_created} of {num_of_blocks}")
                last_block_id = block_ids[-1]

        if embeddings_created > 0:
            print(f"Embedding(Mongo Atlas): Waiting for {self.embedding_db_name}.{self.index_name} to be ready for vector search...")
            start_time = time.time()
            self.wait_for_search_index(last_block_id, start_time)
            wait_time = time.time() - start_time
            print(f"Embedding(Mongo Atlas): {self.embedding_db_name}.{self.index_name} ready ({wait_time: .2f} seconds)")

        embedding_summary = {"embeddings_created": embeddings_created}  

        return embedding_summary
    
    # After doc insertion we want to make sure the index is ready before proceeding
    def wait_for_search_index(self, last_block_id, start_time):
        # If we've been waiting for 5 mins, then time out and just return
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
                "index": self.index_name,
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
                    "index": self.index_name,
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
            block_cursor = CollectionRetrieval(self.library.collection).filter_by_key("_id", ObjectId(_id))
            try:
                block = block_cursor.next()
                distance = 1 - search_result["score"] # Atlas returns a score from 0 to 1.0
                block_list.append((block, distance))
            except StopIteration:
                # The cursor is empty (no blocks found)
                continue 

        return block_list

    def delete_index(self, index_name):
        self.embedding_db.drop_collection(index_name)
     
        # Delete mongo fields
        block_cursor = CollectionWriter(self.library.collection).update_many_records_custom({}, {
            "$unset": {self.mongo_key: ""}})

    def delete_all_indexes(self):
        placeholder_no_action_taken_currently = 0

    def convert_to_hyphens(self, input_string):
        return input_string.replace("_", "-").replace(" ", "-").lower()

