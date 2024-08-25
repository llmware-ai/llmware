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

"""The retrieval module implements the Query class.  The Query class provides a high-level interface for executing
a variety of queries on a Library collection, whether instantiated on Mongo, Postgres, or SQLite.

The Query class includes both text retrieval strategies, which operate directly as queries on the text collection
database, as well as vector embedding semantic retrieval strategies, which require the use of o vector DB and that the
embeddings were previously created for the Library.  There are also a number of convenience methods that provide
'hybrid' strategies combining elements of semantic and text querying."""


import logging
import os
from collections import Counter
from datetime import datetime

try:
    from bson.objectid import ObjectId
except:
    pass

from llmware.configs import LLMWareConfig
from llmware.embeddings import EmbeddingHandler
from llmware.resources import CollectionRetrieval, QueryState
from llmware.util import Utilities, CorpTokenizer
from llmware.models import ModelCatalog
from llmware.exceptions import LibraryObjectNotFoundException,UnsupportedEmbeddingDatabaseException,\
    ImportingSentenceTransformerRequiresModelNameException, EmbeddingModelNotFoundException

logger = logging.getLogger(__name__)


class Query:

    """Implements the query capabilities against a ``Library` object`.

    Query is responsible for executing queries against an indexed library. The library can be semantic, text, custom,
    or hybrid. A query object requires a library object as input, which will be the source of the query.

    Parameters
    ----------
    library : Library object
        A ``library`` object.

    embedding_model : object, default=None
        An ``embedding_model`` object.

    tokenizer : object, default=None

    vector_db_api_key : str, default=None
        The API key for the vector store.

    query_id : int, default=None
        The identifier for a query. This is used when a query state has to be loaded.

    from_hf : bool, default=False
        Sets whether the embedding model should be loaded from hugging face.

    from_sentence_transformer: bool, default=False
        Sets whether the embedding model should be loaded from ``LLMWareSemanticModel``.

    embedding_model_name : str, default=None
        The name of the embedding model. This has to be set if ``from_sentence_transformer=True``.

    save_history : bool, default=True
        Sets whether the history of queries should be saved.

    query_mode : str, default=None
        Sets the query mode that should be used. It has to be either 'text', 'semantic', or 'hybrid'.

    vector_db : str, default=None
        The name of the vector store to be queried against. If it is not set, then this is determined by the
        given ``embedding_model``.


    Examples
    ----------
    >>> from llmware.library import Library
    >>> from llmware.retrieval import Query
    >>> library = Library().create_new_library('lib_semantic_query')
    >>> library.add_website(url='https://en.wikipedia.org/wiki/Austria', get_links=False)
    >>> library.install_new_embedding(embedding_model_name="industry-bert-sec", vector_db="milvus", batch_size=500)
    >>> query = Query(library=library)
    >>> results = query.semantic_query(query='the capital of austria is', result_count=3)
    >>> len(results)
    3
    >>> results[0].keys()
    dict_keys(['query', '_id', 'text', 'doc_ID', 'block_ID', 'page_num', 'content_type',
               'author_or_speaker', 'special_field1', 'file_source', 'added_to_collection',
               'table', 'coords_x', 'coords_y', 'coords_cx', 'coords_cy', 'external_files',
               'score', 'similarity', 'distance', 'matches', 'account_name', 'library_name'])
    >>> results[0]['query']
    'the capital of austria is'
    >>> results[0]['text']
    'Austria is a parliamentary representative democracy with a popularly elected president as head of '
    'state and a chancellor as head of government and chief executive. Major cities include Vienna , Graz, '
    'Linz , Salzburg , and Innsbruck . Austria has the 17th highest nominal GDP per capita with high '
    'standards of living; it was ranked 25th in the world for its Human Development Index in 2021. '
    >>> results[2]['text']
    "Austrian Parliament Building Vienna The Parliament of Austria is located in Vienna , the country's capital "
    "and most populous city. Austria became a federal , representative democratic republic through the "
    "Federal Constitutional Law of 1920. The political system of the Second Republic with its nine federal "
    "states is based on the constitution of 1920, amended in 1929, which was re-enacted on 1 May 1945. [108] "
    """

    def __init__(self, library, embedding_model=None, tokenizer=None, vector_db_api_key=None,
                 query_id=None, from_hf=False, from_sentence_transformer=False,embedding_model_name=None,
                 save_history=True, query_mode=None, vector_db=None, model_api_key=None):

        # load user profile & instantiate core library assets linked to profile

        self.library = library

        if library:
            self.library_name = library.library_name
            self.account_name = library.account_name
        else:
            # throw error if library object does not have library_name and account_name attributes
            raise LibraryObjectNotFoundException(library)

        # explicitly pass name of embedding model, if multiple embeddings on library
        self.embedding_model_name = embedding_model_name

        # added option to pass embedding_model and tokenizer
        self.user_passed_model = embedding_model
        self.user_passed_tokenizer = tokenizer
        self.from_hf = from_hf
        self.from_sentence_transformer = from_sentence_transformer

        # edge case - if a user tries to load a sentence_transformer model but does not pass a model name
        if from_sentence_transformer and not embedding_model_name:
            raise ImportingSentenceTransformerRequiresModelNameException

        # load default configs
        # embedding initialization parameters
        self.query_embedding = None
        self.embedding_model = None
        self.embedding_db = None
        self.embeddings = None
        self.model_api_key = model_api_key

        if self.library:
            self.embeddings = EmbeddingHandler(self.library)

        self.semantic_distance_threshold = 1000  # basic shut off at such a high level

        # keys that will be included in query results

        # full list
        self.query_result_standard_keys = ["_id", "text", "doc_ID", "block_ID","page_num","content_type",
                                           "author_or_speaker", "special_field1", "file_source","added_to_collection",
                                           "table", "coords_x", "coords_y", "coords_cx", "coords_cy", "external_files",
                                           "score", "similarity", "distance", "matches"]

        # short_list
        self.query_result_short_keys = ["text", "file_source", "page_num", "score", "distance","matches"]

        # minimum_list
        self.query_result_min_required_keys = ["text", "file_source", "page_num"]

        # default - set at 'full list'
        self.query_result_return_keys = self.query_result_standard_keys

        # default is semantic if embedding in place
        embedding_record = self.library.get_embedding_status()

        matched_lib_model = False

        if embedding_model_name:
            for emb in embedding_record:

                logger.info(f"update: Query - embedding record lookup - {embedding_model_name} - {emb}")

                if emb["embedding_model"] == embedding_model_name:

                    # if no vector_db name passed, then select based only on embedding_model
                    if not vector_db:
                        if emb["embedding_status"] == "yes":
                            self.embedding_db = emb["embedding_db"]
                            self.search_mode = "semantic"
                            matched_lib_model = True
                            break
                    else:
                        # confirm match of pair - embedding_model + vector_db
                        if emb["embedding_db"] == vector_db:
                            if emb["embedding_status"] == "yes":
                                self.embedding_db = emb["embedding_db"]
                                self.search_mode = "semantic"
                                matched_lib_model = True
                                break

        else:
            if len(embedding_record) > 0:

                if not vector_db:
                    last_emb_record = embedding_record[-1]
                    if last_emb_record["embedding_status"] == "yes":
                        self.embedding_db = last_emb_record["embedding_db"]
                        self.search_mode = "semantic"
                        self.embedding_model_name = last_emb_record["embedding_model"]
                        matched_lib_model = True
                else:
                    # look for match to passed vector_db and take most recent embedding
                    embedding_record.reverse()
                    for embs in embedding_record:
                        if embs["embedding_db"] == vector_db:
                            if embs["embedding_status"] == "yes":
                                self.embedding_db = vector_db
                                self.search_mode = "semantic"
                                self.embedding_model_name = embs["embedding_model"]
                                matched_lib_model = True
                                break

        if matched_lib_model:

            logger.info(f"update: Query - found matches in embedding record - "
                        f"{self.embedding_db} - {self.embedding_model_name}")

            if not self.embedding_model:
                self.load_embedding_model()

        else:
            self.search_mode = "text"

        # passed for accessing api_based vector db
        self.vector_db_api_key = vector_db_api_key

        # if query_id passed, then load that state
        if query_id:
            self.query_id = query_id
            self.load_query_state(query_id)
        else:
            self.query_id = QueryState().issue_new_query_id()

        self.result_text_chunk_size = self.library.block_size_target_characters

        # state variables
        self.results = []
        self.query_history = []
        self.doc_id_list = []
        self.doc_fn_list = []

        self.save_history = save_history

        if query_mode:
            self.search_mode = query_mode

        #   confirm that 'query_history' path exists
        query_history_path = LLMWareConfig().get_query_path()
        if not os.path.exists(query_history_path):
            os.mkdir(query_history_path)
            os.chmod(query_history_path, 0o777)

    def load_embedding_model(self):

        """ Loads the embedding model pulled from the embedding_record of the library. """

        # skip if already instantiated self.embedding_model

        if not self.embedding_model:

            if self.user_passed_model:

                if self.from_hf:
                    self.embedding_model = ModelCatalog().load_hf_embedding_model(self.user_passed_model,
                                                                                  self.user_passed_tokenizer)
                if self.from_sentence_transformer:
                    self.embedding_model = ModelCatalog().load_sentence_transformer_model(self.user_passed_model,
                                                                                          self.embedding_model_name)

            else:
                if ModelCatalog().lookup_model_card(self.embedding_model_name):
                    self.embedding_model = ModelCatalog().load_model(selected_model=self.embedding_model_name,
                                                                     api_key=self.model_api_key)
                else:
                    logger.info(f"update: Query - selected embedding model could not be found - "
                                f"{self.embedding_model_name}")

        return self

    def get_output_keys(self):

        """ Returns list of keys that will be provided in each query_result. """

        return self.query_result_return_keys

    def set_output_keys(self, result_key_list):

        """ Sets the list of keys that will be returned in each query_result. """

        # set the output keys
        validated_list = []
        for key in result_key_list:
            if key in self.library.default_keys:
                validated_list.append(key)

        # minimum required list
        for rk in self.query_result_min_required_keys:
            if rk not in validated_list:
                validated_list.append(rk)
                logger.info(f"warning: Query - adding required keys useful in downstream processing - {rk}")

        # setting updated query_return_keys that is used in packaging query results
        self.query_result_return_keys = validated_list

        return validated_list

    def start_query_session(self, query_id=None):

        """ Initiates a query session and will capture potentially multiple related queries in single state. """

        if query_id:
            self.query_id = query_id

        if self.query_id:
            QueryState(self).load_state(self.query_id)
        else:
            query_id = QueryState(self).initiate_new_state_session()

        return query_id

    def register_query (self, retrieval_dict):

        """ Registers a query to the query state. """

        # qr_dict = ["query", "results", "doc_ID", "file_source"]

        # add query results as new "column" in query state
        self.results += retrieval_dict["results"]

        if retrieval_dict["query"] not in self.query_history:
            self.query_history.append(retrieval_dict["query"])

        for doc_id in retrieval_dict["doc_ID"]:
            if doc_id not in self.doc_id_list:
                self.doc_id_list.append(doc_id)

        for doc_fn in retrieval_dict["file_source"]:
            if doc_fn not in self.doc_fn_list:
                self.doc_fn_list.append(doc_fn)

        # QueryState(self).save_state(self.query_id)

        return self

    def load_query_state(self, query_id):

        """ Loads a query state of a previous query by query_id """

        state = QueryState(self).load_state(query_id)
        return self

    def save_query_state(self):

        """ Saves the current query state. """

        QueryState(self).save_state()
        return self

    def clear_query_state(self):

        """ Resets the query state. """

        # need to reset state variables
        QueryState(self).initiate_new_state_session()
        return self

    def dump_current_query_state(self):

        """ Dumps the current query_state to a query_state_dict. """

        query_state_dict = {"query_id": self.query_id,
                            "query_history": self.query_history,
                            "results": self.results,
                            "doc_ID": self.doc_id_list,
                            "file_source": self.doc_fn_list
                            }

        return query_state_dict

    def query(self, query, query_type="text", result_count=20, results_only=True):

        """ Main method for executing a basic query - expects query as input, and optional parameters for
        query_type, result_count and whether results_only.  Output is a set of query results, which is a list of
        dictionaries, with each dictionary representing a single matching retrieval from the collection. """

        output_result = {"results": [], "doc_ID": [], "file_source": []}

        if query_type not in ["text", "semantic"]:
            logger.error("error: Query().query expects a query type of either 'text' or 'semantic'")
            return output_result

        if query_type == "text":
            output_result = self.text_query(query,result_count=result_count,results_only=results_only)

        if query_type == "semantic":

            #   check that embedding model is available, and if not, flip to text search

            if not self.embedding_model:
                self.load_embedding_model()

            if self.search_mode == "text" or not self.embedding_model:
                output_result = self.text_query(query, result_count=result_count,results_only=results_only)
            else:
                output_result = self.semantic_query(query, result_count=result_count,results_only=results_only)

        return output_result

    def text_query (self, query, exact_mode=False, result_count=20, exhaust_full_cursor=False, results_only=True):

        """ Execute a basic text query. """

        # prepare query if exact match required
        if exact_mode:
            query = self.exact_query_prep(query)

        # query the text collection
        cursor = CollectionRetrieval(self.library_name,account_name=self.account_name).basic_query(query)

        # package results, with correct sample counts and output keys requested
        results_dict = self._cursor_to_qr(query, cursor,result_count=result_count,exhaust_full_cursor=
                                          exhaust_full_cursor)

        if results_only:
            return results_dict["results"]

        return results_dict

    def text_query_with_document_filter(self, query, doc_filter, result_count=20, exhaust_full_cursor=False,
                                        results_only=True, exact_mode=False):

        """ Execute a text query with a document filter applied. """

        # prepare query if exact match required
        if exact_mode:
            query = self.exact_query_prep(query)

        key = None
        value_range = []

        if "doc_ID" in doc_filter:
            key = "doc_ID"
            value_range = doc_filter["doc_ID"]

        elif "file_source" in doc_filter:
            key = "file_source"
            value_range = doc_filter["file_source"]

        else:
            logger.warning("warning: Query - expected to receive document filter with keys of 'doc_ID' or "
                           "'file_source' - as a safe fall-back - will run the requested query without a filter.")

        if key:
            cursor = CollectionRetrieval(self.library_name, account_name=self.account_name). \
                    text_search_with_key_value_range(query, key, value_range)
        else:
            # as fallback, if no key found, then run query without filter
            cursor = CollectionRetrieval(self.library_name, account_name=self.account_name).basic_query(query)

        result_dict = self._cursor_to_qr(query, cursor, result_count=result_count,
                                         exhaust_full_cursor=exhaust_full_cursor)

        if results_only:
            return result_dict["results"]

        return result_dict

    def text_query_by_content_type (self, query, content_type,results_only=True):

        """ Execute a text query with additional constraint of content type, e.g., 'image', 'table', or 'text' """

        filter_dict = {"content_type": content_type}
        retrieval_dict = self.text_query_with_custom_filter(query,filter_dict,results_only=True)
        return retrieval_dict

    def image_query(self, query, results_only=True):

        """ Execute a query with content_type == 'image'. """

        filter_dict = {"content_type": "image"}
        retrieval_dict = self.text_query_with_custom_filter(query, filter_dict,results_only=True)
        return retrieval_dict

    def table_query(self, query, export_tables_to_csv=False, results_only=True):

        """ Execute a query with content_type == 'table'. """

        filter_dict = {"content_type": "table"}
        retrieval_dict = self.text_query_with_custom_filter(query, filter_dict,results_only=True)

        # output and write tables to csv files
        if export_tables_to_csv:
            for i, entry in enumerate(retrieval_dict["results"]):
                f = self.export_one_table_to_csv(entry,output_fp=LLMWareConfig.get_query_path(),
                                                 output_fn="table_{}.csv".format(i))

                logger.warning(f"update: csv created - {LLMWareConfig.get_query_path()}- {f}")

        return retrieval_dict

    def text_search_by_page (self, query, page_num=1, results_only=True):

        """ Execute a text search with page number constraint provided as page_num parameter. """

        key = "master_index"  # parsing uses "master_index" across multiple input sources, interpret as "page_num"

        if not isinstance(page_num, list):
            page_num = [page_num]

        cursor_results = CollectionRetrieval(self.library_name, account_name=self.account_name).\
            text_search_with_key_value_range(query, key, page_num)

        retrieval_dict = self._cursor_to_qr(query, cursor_results)

        if results_only:
            return retrieval_dict["results"]

        return retrieval_dict

    def text_query_by_author_or_speaker(self, query, author_or_speaker, results_only=True):

        """ Execute a text query with specific author_or_speaker constraint. """

        filter_dict = {"author_or_speaker": author_or_speaker}
        retrieval_dict = self.text_query_with_custom_filter(query,filter_dict,results_only=results_only)
        return retrieval_dict

    def text_query_with_custom_filter (self, query, filter_dict, result_count=20,
                                       exhaust_full_cursor=False, results_only=True):

        """ Execute a text query with additional custom filter dictionary. """

        # filter_dict is a dict with indefinite number of key:value pairs - each key will be interpreted
        #   as "$and" in the query, requiring a match against all of the key:values in the filter_dict

        # validate filter dict
        validated_filter_dict = {}
        for key, values in filter_dict.items():
            for valid_keys in self.library.default_keys:
                if key in valid_keys:
                    validated_filter_dict.update({key:values})

        if validated_filter_dict:
            cursor = CollectionRetrieval(self.library_name, account_name=self.account_name).\
                text_search_with_key_value_dict_filter(query,validated_filter_dict)

        else:
            logger.error("error: Query text_query_with_custom_filter - keys in filter_dict are not"
                         "recognized as part of the library.collection default_keys list.")

            return -1

        result_dict = self._cursor_to_qr_with_secondary_filter(query, cursor,filter_dict,
                                                               result_count=result_count,
                                                               exhaust_full_cursor=exhaust_full_cursor)

        if results_only:
            return result_dict["results"]

        return result_dict

    def _cursor_to_qr_with_secondary_filter(self, query, cursor_results, filter_dict,
                                            result_count=20, exhaust_full_cursor=False):

        """ Internal helper method to package query results from cursor. """

        qr = []
        counter = 0
        doc_id_list = []
        doc_fn_list = []

        for raw_qr in cursor_results:

            # update to locate match and add to result
            matches_found = self.locate_query_match(query, raw_qr["text"])
            raw_qr.update({"matches": matches_found})
            raw_qr.update({"page_num": raw_qr["master_index"]})

            raw_qr.update({"_id": str(raw_qr["_id"])})

            if "score" not in raw_qr:
                raw_qr.update({"score": 0.0})

            if "similarity" not in raw_qr:
                raw_qr.update({"similarity": 0.0})

            if "distance" not in raw_qr:
                raw_qr.update({"distance": 0.0})

            # apply secondary filter dict
            match = -1
            for key, value in filter_dict.items():
                if key in raw_qr:
                    # support case in which filter_dict is a list, e.g., doc_id = {5,9,13}
                    if raw_qr[key] == value or (isinstance(value,list) and raw_qr[key] in value):
                        match = 1
                    else:
                        match = -1
                        break

            if match == 1:

                # output target keys
                output_dict = {}
                output_dict.update({"query": query})

                for key in self.query_result_return_keys:
                    if key not in raw_qr:
                        logger.warning(f"warning: Query() - selected output key not found in result - {key}")
                    else:
                        output_dict.update({key: raw_qr[key]})

                output_dict.update({"account_name": self.account_name})
                output_dict.update({"library_name": self.library_name})

                qr.append(output_dict)

                if raw_qr["doc_ID"] not in doc_id_list:
                    doc_id_list.append(raw_qr["doc_ID"])
                    doc_fn_list.append(raw_qr["file_source"])

                counter += 1

                # will exhaust full cursor if .exhaust_full_cursor = True
                if counter >= result_count and not exhaust_full_cursor:
                    break

        qr_dict = {"query": query, "results": qr, "doc_ID": doc_id_list, "file_source": doc_fn_list}

        if self.save_history:
            self.register_query(qr_dict)

        return qr_dict

    def _cursor_to_qr (self, query, cursor_results, result_count=20, exhaust_full_cursor=False):

        """ Internal helper method to package query results from cursor. """

        qr = []
        counter = 0
        doc_id_list = []
        doc_fn_list = []

        for raw_qr in cursor_results:

            # update to locate match and add to result
            matches_found = self.locate_query_match(query, raw_qr["text"])
            raw_qr.update({"matches": matches_found})
            raw_qr.update({"page_num": raw_qr["master_index"]})

            raw_qr.update({"_id": str(raw_qr["_id"])})

            if "score" not in raw_qr:
                raw_qr.update({"score": 0.0})

            if "similarity" not in raw_qr:
                raw_qr.update({"similarity": 0.0})

            if "distance" not in raw_qr:
                raw_qr.update({"distance": 0.0})

            # output target keys
            output_dict = {}
            output_dict.update({"query": query})

            for key in self.query_result_return_keys:
                if key not in raw_qr:
                    logger.warning(f"warning: Query() - selected output key not found in result - {key}")
                else:
                    output_dict.update({key: raw_qr[key]})

            output_dict.update({"account_name": self.account_name})
            output_dict.update({"library_name": self.library_name})

            qr.append(output_dict)

            if raw_qr["doc_ID"] not in doc_id_list:
                doc_id_list.append(raw_qr["doc_ID"])
                doc_fn_list.append(raw_qr["file_source"])

            counter += 1

            # will exhaust full cursor if .exhaust_full_cursor = True
            if counter >= result_count and not exhaust_full_cursor:
                break

        qr_dict = {"query": query,"results": qr, "doc_ID": doc_id_list, "file_source": doc_fn_list}

        if self.save_history:
            self.register_query(qr_dict)

        return qr_dict

    def semantic_query(self, query, result_count=20, embedding_distance_threshold=None, custom_filter=None, results_only=True):

        """ Main method to execute a semantic query - only required parameter is the query. """

        if not embedding_distance_threshold:
            embedding_distance_threshold = self.semantic_distance_threshold

        self.load_embedding_model()

        # confirm that embedding model exists, or catch and raise error
        if self.embedding_model:
            self.query_embedding = self.embedding_model.embedding(query)
        else:
            raise EmbeddingModelNotFoundException(self.library_name)

        if self.embedding_db and self.embedding_model:

            semantic_block_results = self.embeddings.search_index(self.query_embedding,
                                                                  embedding_db=self.embedding_db,
                                                                  model=self.embedding_model,
                                                                  sample_count=result_count)

        else:
            logger.error(f"error: Query - embedding record does not indicate embedding db - "
                         f"{self.embedding_db} and/or embedding model - {self.embedding_model}")

            raise UnsupportedEmbeddingDatabaseException(self.embedding_db)

        qr_raw = []

        # Collecting semantic results
        for i, blocks in enumerate(semantic_block_results):
            if blocks[1] < embedding_distance_threshold:
                block_data = blocks[0]
                block_data["distance"] = blocks[1]
                block_data["semantic"] = "semantic"
                block_data["score"] = 0.0
                qr_raw.append(block_data)

        # Applying custom filter if provided
        if custom_filter:
            qr_raw = self.apply_custom_filter(qr_raw, custom_filter)

        # Processing results
        results_dict = self._cursor_to_qr(query, qr_raw, result_count=result_count)

        return results_dict["results"] if results_only else results_dict

    def apply_custom_filter(self, results, custom_filter):

        """ Apply custom filter to a set of results. """

        filtered_results = []
        for result in results:
            if all(result.get(key) == value for key, value in custom_filter.items()):
                filtered_results.append(result)
        return filtered_results

    def semantic_query_with_document_filter(self, query, filter_dict, embedding_distance_threshold=None,
                                            result_count=100, results_only=True):

        """ Execute semantic query with secondary constraint of document filter. """

        #   checks for filter to offer option to do semantic query in specific doc, page or content range
        if not embedding_distance_threshold:
            embedding_distance_threshold = self.semantic_distance_threshold

        #   note:  by default, retrieves a much larger set of results to try to account for filter

        th = self.semantic_distance_threshold

        # confirm that embedding model exists, or catch and raise error
        if self.embedding_model:
            self.query_embedding = self.embedding_model.embedding(query)
        else:
            raise EmbeddingModelNotFoundException(self.library_name)

        if self.embedding_db and self.embedding_model:
            semantic_block_results = self.embeddings.search_index(self.query_embedding,
                                                                  embedding_db=self.embedding_db,
                                                                  model=self.embedding_model,
                                                                  sample_count=result_count)

        else:
            logger.error(f"error: Query - embedding record does not indicate embedding db- {self.embedding_db} "
                         f"and/or an embedding_model - {self.embedding_model}")

            raise UnsupportedEmbeddingDatabaseException(self.embedding_db)

        qr_raw = []

        # may need to conform the output structure of semantic_block_results
        for i, blocks in enumerate(semantic_block_results):
            # assume that each block has at least two components:  [0] core mongo block, and [1] distance metric
            if blocks[1] < embedding_distance_threshold:

                blocks[0].update({"distance": blocks[1]})
                blocks[0].update({"semantic": "semantic"})
                blocks[0].update({"score": 0.0})

                qr_raw.append(blocks[0])

        result_output = self._cursor_to_qr_with_secondary_filter(query,qr_raw,filter_dict,result_count=result_count)

        if results_only:
            return result_output["results"]

        return result_output

    def similar_blocks_embedding(self, block, result_count=20, embedding_distance_threshold=10, results_only=True):

        """ Application of semantic embedding space - takes a block of text as input and finds most similar comparable
        text chunks. If you are comfortable with the normalization of the embedding vector space, then set a
        specific embedding_distance_threshold, e.g., embedding_distance_threshold=1.1 to limit the results to
        text blocks within a distance of 1.1 in the embedding space."""

        # will use embedding to find similar blocks from a given block
        # confirm that embedding model exists, or catch and raise error
        if self.embedding_model:
            self.query_embedding = self.embedding_model.embedding(block["text"])
        else:
            raise EmbeddingModelNotFoundException(self.library_name)

        if self.embedding_model and self.embedding_db:
            semantic_block_results = self.embeddings.search_index(self.query_embedding,
                                                                  embedding_db=self.embedding_db,
                                                                  model=self.embedding_model,
                                                                  sample_count=result_count)

        else:
            logger.error(f"error: Query - embedding record does not indicate embedding db- "
                         f"{self.embedding_db} and/or embedding model - {self.embedding_model}")

            raise UnsupportedEmbeddingDatabaseException(self.embedding_db)

        qr_raw = []

        # may need to conform the output structure of semantic_block_results
        for i, blocks in enumerate(semantic_block_results):
            # assume that each block has at least two components:  [0] core mongo block, and [1] distance metric
            if blocks[1] < embedding_distance_threshold:

                blocks[0].update({"distance": blocks[1]})
                blocks[0].update({"semantic": "semantic"})
                blocks[0].update({"score": 0.0})

                qr_raw.append(blocks[0])

        # pick up with boilerplate
        results_dict = self._cursor_to_qr("", qr_raw, result_count=result_count)

        if results_only:
            return results_dict["results"]

        return results_dict

    def dual_pass_query(self, query, result_count=20, primary="text",
                        safety_check=True, custom_filter=None, results_only=True):

        """ Executes a combination of text and semantic queries and attempts to interweave and re-rank based on
        correspondence between the two query attempts. """

        # safety check
        if safety_check and result_count > 100:
            logger.info("warning: Query().dual_pass_query runs a comparison of output rankings using semantic "
                        "and text.  This particular implementation is not optimized for sample lists longer "
                        "than ~100 X 100.  To remove this warning, there are two options - (1) set the "
                        "safety_check to False in the method declaration, or (2) keep sample count below 100.")

            result_count = 100

        # following keys are required for dual pass query to work, add them if user has omitted them
        keys_to_check = ['_id', 'doc_ID']
        for key in keys_to_check:
            if key not in self.query_result_return_keys:
                self.query_result_return_keys.append(key)
        
        # run dual pass - text + semantic
        # Choose appropriate text query method based on custom_filter
        if custom_filter:
            retrieval_dict_text = self.text_query_with_custom_filter(query, custom_filter,
                                                                     result_count=result_count, results_only=True)
        else:
            retrieval_dict_text = self.text_query(query, result_count=result_count, results_only=True)

        # Semantic query with custom filter
        retrieval_dict_semantic = self.semantic_query(query, result_count=result_count,
                                                      custom_filter=custom_filter, results_only=True)

        if primary == "text":
            first_list = retrieval_dict_text
            second_list = retrieval_dict_semantic
        else:
            first_list = retrieval_dict_semantic
            second_list = retrieval_dict_text

        confirming_list = []
        primary_only = []
        secondary_only = []
        matched_second_list = []

        # this is the time intensive "n-squared" loop - probably OK up to 100+
        for i, entry in enumerate(first_list):
            match = -1
            for j, entry2 in enumerate(second_list):
                if entry["_id"] == entry2["_id"]:
                    entry["match_status"] = "matched"  # Tagging as matched
                    confirming_list.append(entry)
                    match = 1
                    matched_second_list.append(entry2["_id"])
                    break
            if match == -1:
                entry["match_status"] = "primary_only"  # Tagging as primary only
                primary_only.append(entry)

        for k, entry2 in enumerate(second_list):
            if entry2["_id"] not in matched_second_list:
                entry2["match_status"] = "secondary_only"  # Tagging as secondary only
                secondary_only.append(entry2)

        # assemble merged top results
        merged_results = []
        merged_results += confirming_list

        select_primary = min(len(primary_only), 5)
        select_secondary = min(len(secondary_only), 5)

        merged_results += primary_only[0:select_primary]
        merged_results += secondary_only[0:select_secondary]

        doc_id_list = []
        doc_fn_list = []

        for qr in merged_results:
            if qr["doc_ID"] not in doc_id_list:
                doc_id_list.append(qr["doc_ID"])
            if qr["file_source"] not in doc_fn_list:
                doc_fn_list.append(qr["file_source"])

        retrieval_dict = {"results": merged_results,
                          "text_results": retrieval_dict_text,
                          "semantic_results": retrieval_dict_semantic,
                          "doc_ID": doc_id_list,
                          "file_source": doc_fn_list}

        if results_only:
            return merged_results

        return retrieval_dict

    def augment_qr (self, query_result, query_topic, augment_query="semantic"):

        """ Augments the set of query results using alternative retrieval strategy. """

        if augment_query == "semantic":
            qr_aug = self.semantic_query(query_topic,result_count=20, results_only=True)
        else:
            qr_aug = self.text_query(query_topic,result_count=20, results_only=True)

        # consolidate the qr lists
        updated_qr = []
        for qr in query_result:
            updated_qr.append(qr)   # start with original qr list

        # add up to 10 entries from semantic list
        semantic_return_max = 10

        for j, sem_entries in enumerate(qr_aug):
            if sem_entries not in updated_qr:
                updated_qr.append(sem_entries)
                if j > semantic_return_max:
                    break

        return updated_qr

    def apply_semantic_ranking(self, qr, issue_semantic):

        """ Apply ranking of query results by semantic query ranking. """

        #   designed to take a set of query results, and re-rank the order of results by their semantic distance
        #   --note:  possible to use a different query term for issue_semantic than the original query result

        #   heuristic - look for result targets of at least 20, but up to the exact len of the qr
        result_target = max(len(qr),20)

        semantic_qr = self.semantic_query(issue_semantic,result_count=result_target)

        reranked_qr = []
        for i, s in enumerate(semantic_qr):

            for q in qr:
                if s["_id"] == q["_id"]:
                    reranked_qr.append(q)
                    break

        for q in qr:
            if q not in reranked_qr:
                reranked_qr.append(q)

        return reranked_qr

    def document_filter (self, filter_topic, query_mode="text", result_count=30,
                         exact_mode = False, exhaust_full_cursor=True):

        """ Takes a filter_topic as input, along with query_mode, and generates a document filter as output. """

        result_dict = None

        if query_mode not in ["text", "semantic", "hybrid"]:

            logger.error(f"error: Query document_filter supports query types - 'text', "
                         f"'semantic', and 'hybrid' - type selected not recognized - {query_mode}")

            return result_dict

        if query_mode == "text":
            result_dict = self.text_query(filter_topic,exact_mode=exact_mode,result_count=result_count,
                                          exhaust_full_cursor=exhaust_full_cursor,results_only=False)

        if query_mode == "semantic":
            result_dict = self.semantic_query(filter_topic,result_count=result_count, results_only=False)

        if query_mode == "hybrid":
            result_dict = self.dual_pass_query(filter_topic)

        if not result_dict:

            logger.error(f"error: Query file_selector_only could not find a result - unexpected error - "
                         f"{filter_topic}")

            return result_dict

        doc_filter_output = {"doc_ID": result_dict["doc_ID"], "file_source": result_dict["file_source"]}

        return doc_filter_output

    def page_lookup(self, page_list=None, doc_id_list=None, text_only=False):

        """ Look up by specific pages, e.g, useful to retrieve the entire first page of a template document. """

        if not doc_id_list:
            doc_id_list = self.list_doc_id()
        else:
            if isinstance(doc_id_list,dict):
                if "doc_ID" in doc_id_list:
                    doc_id_list = doc_id_list["doc_ID"]
                else:
                    logger.warning("warning: could not recognize doc id list requested.  by default, "
                                   "will set to all documents in the library collection.")

                    doc_id_list = self.list_doc_id()

        if not page_list:
            logger.warning("warning: page lookup requested, but no value range identified.  by default, will set "
                           "to retrieve the first page only.")
            page_list = [1]

        if text_only:
            page_dict = {"doc_ID": {"$in":doc_id_list}, "master_index": {"$in": page_list}, "content_type":"text"}
        else:
            page_dict = {"doc_ID": {"$in":doc_id_list}, "master_index": {"$in": page_list}}

        cursor_results = CollectionRetrieval(self.library_name,
                                             account_name=self.account_name).filter_by_key_dict(page_dict)

        output = []

        for x in cursor_results:

            x.update({"matches": []})
            x.update({"page_num": x["master_index"]})

            output.append(x)

        return output

    def get_whole_library(self, selected_keys=None):

        """ Gets the whole library - and will return as a list in-memory. """

        match_results_cursor = CollectionRetrieval(self.library_name,
                                                   account_name=self.account_name).get_whole_collection()

        match_results = match_results_cursor.pull_all()

        qr = []

        # option to retrieve only user selected keys
        if not selected_keys:
            selected_keys = self.library.default_keys

        for i, block in enumerate(match_results):

            new_row = {}
            new_row.update({"_id": str(block["_id"])})
            new_row.update({"matches": []})
            new_row.update({"page_num": block["master_index"]})
            new_row.update({"score": 0.0})
            new_row.update({"similarity": 0.0})
            new_row.update({"distance": 0.0})

            for keys in selected_keys:
                if keys in block:
                    if keys not in new_row:
                        new_row.update({keys:block[keys]})

            qr.append(new_row)

        return qr

    def export_all_tables(self, query="", output_fp=None):

        """ Exports all tables, with query option to limit the list from a library. """

        table_csv_files_created = []

        if not output_fp:
            output_fp = self.library.misc_path

        if not query:

            match_results = CollectionRetrieval(self.library_name,
                                                account_name=self.account_name).filter_by_key("content_type","table")

        else:
            kv_dict = {"content_type": "table"}
            match_results = CollectionRetrieval(self.library_name, account_name=self.account_name).\
                text_search_with_key_value_dict_filter(query,kv_dict)

        counter = 0

        for i, entries in enumerate(match_results):

            table = entries["table"]

            output = []

            table_raw = table
            rows = table_raw.split("<tr>")
            cols_tracker = []
            coords_master = []

            for row in rows:

                new_row = []
                if row.strip().endswith("</tr>"):
                    row = row.strip()[:-5]

                cells = row.lstrip().split("<th>")
                cols_count = 0
                coords = []

                for c in cells:

                    if c.strip().endswith("</th>"):
                        c = c.strip()[:-5]

                    clean_cell = ""
                    bracket_on = 0

                    fields = c.split("<")

                    if fields[0]:
                        index = fields[1].rstrip()[0:-1]

                        main_entry = fields[2].split(">")
                        value = main_entry[-1]

                        co = main_entry[0].split(" ")

                        if len(co) > 2:
                            x = co[1]
                            y = co[2]

                            coords.append((int(x), int(y)))

                    for c1 in c:
                        if bracket_on == 0 and c1 not in ("<", ">"):
                            clean_cell += c1
                        if c1 == "<":
                            bracket_on = 1
                        if c1 == ">":
                            bracket_on = 0

                    if c:
                        c_strip = c.split(">")[-1]
                        new_row.append(c_strip.strip())
                        cols_count += 1

                coords_master.append(coords)
                cols_tracker.append(cols_count)
                output.append(new_row)

            new_file = "table_{}.csv".format(counter)

            counter += 1
            f = Utilities().file_save(output, output_fp, new_file)
            output = []

            table_csv_files_created.append(new_file)

        output_dict = {"library": self.library_name, "query": query, "tables_created": counter,
                       "file_names": table_csv_files_created, "output_fp": output_fp}

        return output_dict

    def export_one_table_to_csv(self, query_result, output_fp=None, output_fn=None):

        """ Exports a single table query result into a csv file. """

        table = query_result["table"]

        output = []

        table_raw = table
        rows = table_raw.split("<tr>")
        cols_tracker = []
        coords_master = []

        for row in rows:

            new_row = []
            if row.strip().endswith("</tr>"):
                row = row.strip()[:-5]

            cells = row.lstrip().split("<th>")
            cols_count = 0
            coords = []

            for c in cells:

                if c.strip().endswith("</th>"):
                    c = c.strip()[:-5]

                clean_cell = ""
                bracket_on = 0

                fields = c.split("<")

                if fields[0]:
                    index = fields[1].rstrip()[0:-1]
                    main_entry = fields[2].split(">")
                    value = main_entry[-1]
                    co = main_entry[0].split(" ")
                    if len(co) > 2:
                        x = co[1]
                        y = co[2]
                        coords.append((int(x), int(y)))

                for c1 in c:
                    if bracket_on == 0 and c1 not in ("<", ">"):
                        clean_cell += c1
                    if c1 == "<":
                        bracket_on = 1
                    if c1 == ">":
                        bracket_on = 0

                if c:
                    c_strip = c.split(">")[-1]
                    new_row.append(c_strip.strip())
                    cols_count += 1
            coords_master.append(coords)
            cols_tracker.append(cols_count)
            output.append(new_row)

        if not output_fn:
            new_file = "table_0.csv"
        else:
            new_file = output_fn

        f = Utilities().file_save(output, output_fp, new_file)

        return new_file

    def list_doc_id(self):

        """ Utility function - returns list of all doc_ids in the library. """

        doc_id_list = CollectionRetrieval(self.library_name, account_name=self.account_name).get_distinct_list("doc_ID")

        return doc_id_list

    def list_doc_fn(self):

        """ Utility function - returns list of all document names in the library. """

        doc_fn_raw_list = CollectionRetrieval(self.library_name,
                                              account_name=self.account_name).get_distinct_list("file_source")

        doc_fn_out = []
        for i, file in enumerate(doc_fn_raw_list):
            doc_fn_out.append(file.split(os.sep)[-1])
        return doc_fn_out

    def aggregate_text(self, qr_list):

        """ Utility method that take a list of query result dictionaries as input (with all of the associated metadata
        attributes) and repackages into two useful outputs:

            -- text_agg, which is the aggregated text across all of the query results in a single unbroken string, and
            -- meta_agg, which is a list of dictionaries with all of the 'start/stop' information in the text
                string, which can be used to map back a snippet of text back to its original block entry in the DB.
        """

        text_agg = ""
        meta_agg = []

        for i, entry in enumerate(qr_list):
            t = entry["text"]
            meta = {"start_char": len(text_agg), "stop_char": len(text_agg) + len(t), "block_id": entry["block_ID"],
                    "doc_ID": entry["doc_ID"], "page_num": entry["page_num"]}
            meta_agg.append(meta)
            text_agg += t

        return text_agg, meta_agg

    def document_lookup(self, doc_id="", file_source=""):

        """ Takes as an input either a doc_id or file_source (e.g., filename) that is in a Library, and
        returns all of the non-image text and table blocks in the document. """

        if doc_id:
            kv_dict = {"doc_ID": doc_id}
        elif file_source:
            kv_dict = {"file_source": file_source}
        else:
            raise RuntimeError("Query document_lookup method requires as input either a document ID or "
                               "the name of a file already parsed in the library ")

        output = CollectionRetrieval(self.library_name, account_name=self.account_name).filter_by_key_dict(kv_dict)

        if len(output) == 0:
            logger.warning(f"update: Query - document_lookup  - nothing found - {doc_id} - {file_source}")
            result = []

            return result

        output_final = []

        # exclude images to avoid potential duplicate text
        for entries in output:
            if entries["content_type"] != "image":
                entries.update({"matches": []})
                entries.update({"page_num": entries["master_index"]})
                output_final.append(entries)

        output_final = sorted(output_final, key=lambda x:x["block_ID"], reverse=False)

        return output_final

    def block_lookup(self, block_id, doc_id):

        """ Look up by a specific pair of doc_id and block_id in a library. """

        result = None

        kv_dict = {"doc_ID": doc_id, "block_ID": block_id}

        output = CollectionRetrieval(self.library_name, account_name=self.account_name).filter_by_key_dict(kv_dict)

        if len(output) == 0:
            logger.info(f"update: Query - Library - block_lookup - block not found: {block_id}")
            result = None
            
            return result
            
        if len(output) > 1:
            result = output[0]

        if len(output) == 1:
            result = output[0]
        
        # if arrived this point, then positive result has been identified
        result.update({"matches": []})
        result.update({"page_num": result["master_index"]})

        return result

    def get_header_text_from_collection(self, text_field="header_text"):

        """ Pulls the header_text from the collection, captured during parsing, useful to identify headlines. """

        ds_folder = self.library.nlp_path

        results = CollectionRetrieval(self.library_name, account_name=self.account_name).get_whole_collection()

        f = open(ds_folder + "header_text.txt", "w", encoding='utf-8')
        counter = 0
        for elements in results:
            text_sample = elements[text_field]
            if text_sample:
                f.write(text_sample)
                f.write("\n")
                f.write(elements["text"])
                f.write("\n")
                counter += 1

        f.close()
        results.close()
        return counter

    def get_core_text_from_collection(self, text_field="text"):

        """ Returns all core text from a collection. """

        ds_folder = self.library.nlp_path

        results = CollectionRetrieval(self.library_name, account_name=self.account_name).get_whole_collection()

        f = open(os.path.join(ds_folder,"core_text.txt"), "w", encoding='utf-8')
        counter = 0
        for elements in results:
            text_sample = elements[text_field]
            if text_sample:
                f.write(text_sample)
                f.write("\n")
                counter += 1

        f.close()
        results.close()
        return counter

    def get_user_tags(self):

        """ Returns user tags, if any, identified - note: this is experimental method and may change."""

        # look for all non-empty user_tags
        output = CollectionRetrieval(self.library_name,
                                     account_name=self.account_name).filter_by_key_ne_value("user_tags", "")

        counter = 0
        user_tags_out = []
        for elements in output:
            counter += 1
            user_tags_out.append((elements["block_ID"], elements["user_tags"]))

        return user_tags_out

    def filter_by_time_stamp (self, qr, first_date="", last_date=""):

        """ Filters results by condition of time range. """

        # apply filter dict to the qr results found
        time_str = "%Y-%m-%d"
        if first_date:
            first_date = datetime.strptime(first_date,time_str)

        if last_date:
            last_date = datetime.strptime(last_date, time_str)

        filtered_qr = []

        for i, entry in enumerate(qr):

            if entry["added_to_collection"]:

                try:
                    # First try Linux format
                    time_str = "%a %b %d %H:%M:%S %Y"
                    doc_date = datetime.strptime(entry["added_to_collection"], time_str)

                except ValueError:
                    # If it fails, try Windows format
                    time_str = "%m/%d/%y %H:%M:%S"
                    doc_date = datetime.strptime(entry["added_to_collection"], time_str)

                time_accept = self._time_window_filter(first_date,last_date,doc_date)

                if time_accept:
                    filtered_qr.append(entry)

        return filtered_qr

    def _time_window_filter(self, start_time,end_time, test_time, time_str="%a %b %d %H:%M:%S %Y"):

        """ Internal helper function to evaluate and compare time stamps. """

        if start_time and end_time:
            if start_time <= test_time <= end_time:
                return True

        if start_time and not end_time:
            if start_time <= test_time:
                return True

        if not start_time and end_time:
            if test_time <= end_time:
                return True

        return False

    def locate_query_match (self, query, core_text):

        """ Utility function to locate the character-level match of a query inside a core_text. """

        matches_found = []
        
        # edge case - but return empty match if query is null
        if not query:
            return matches_found
            
        b = CorpTokenizer(one_letter_removal=False, remove_stop_words=False, remove_punctuation=False,
                          remove_numbers=False)

        query_tokens = b.tokenize(query)

        for x in range(0, len(core_text)):
            match = 0
            for key_term in query_tokens:
                if len(key_term) == 0:
                    continue
                
                if key_term.startswith('"'):
                    key_term = key_term[1:-1]

                if core_text[x].lower() == key_term[0].lower():
                    match += 1
                    if (x + len(key_term)) <= len(core_text):
                        for y in range(1, len(key_term)):
                            if key_term[y].lower() == core_text[x + y].lower():
                                match += 1
                            else:
                                match = -1
                                break

                        if match == len(key_term):
                            new_entry = [x, key_term]
                            matches_found.append(new_entry)

        return matches_found

    def exact_query_prep(self, query):

        """ Prepares an exact query prep. """

        if query.startswith('"') and query.endswith('"'):
            prepared_query = '\"' + query[1:-1] + '\"'

        else:
            # even if user did not wrap in quotes, treat as exact search
            prepared_query = '\"' + query + '\"'

        return prepared_query

    def bibliography_builder_from_qr(self, query_results):

        """ Builds a bibliography from a query result. """

        bibliography = []
        doc_id_reviewed = []
        doc_fn_reviewed = []

        # first  - assemble the list of docs in the query_results
        for y in range(0,len(query_results)):
            if "doc_ID" in query_results[y]:
                if query_results[y]["doc_ID"] not in doc_id_reviewed:
                    doc_id_reviewed.append(query_results[y]["doc_ID"])
                    doc_fn_reviewed.append(query_results[y]["file_source"])

        # second - identify and sort the key pages associated with the doc
        for x in range(0,len(doc_id_reviewed)):
            pages_reviewed = []
            for z in range(0,len(query_results)):
                if "doc_ID" in query_results[z]:
                    if query_results[z]["doc_ID"] == doc_id_reviewed[x]:
                        pages_reviewed.append(query_results[z]["page_num"])

            pr = Counter(pages_reviewed)
            mc = pr.most_common()
            page_output_list = []
            for m in mc:
                page_output_list.append(m[0])

            if len(doc_fn_reviewed) > x:
                doc_fn_tmp = doc_fn_reviewed[x]
            else:
                doc_fn_tmp = "Doc# " + str(doc_id_reviewed[x])

            bibliography.append({doc_fn_tmp:page_output_list})

        return bibliography

    def filter_cursor_list(self, cursor, filter_dict, sample_count=20, exhaust_full_cursor=None):

        """ Applies filter to a cursor list. """

        validated_filter_dict = self.prep_validated_filter_dict(filter_dict)
        result_output = []

        for i, entry in enumerate(cursor):

            for key, value in validated_filter_dict.items():
                if key not in entry:
                    logger.warning(f"warning: Query - retrieval cursor does not contain filter key - {key}")
                else:
                    if entry[key] == value:
                        result_output.append(entry)

                if len(result_output) > sample_count and not exhaust_full_cursor:
                    break

        return result_output

    def prep_validated_filter_dict(self, filter_dict):

        """ Internal utility to prepare a validated filter dict. """

        validated_filter_dict = {}

        for key, values in filter_dict.items():
            if key in self.library.default_keys:
                validated_filter_dict.update({key:values})
            else:
                logger.warning(f"warning: Query - filter key not in library collection - {key}")

        return validated_filter_dict

    def block_lookup_by_collection_id(self, _id):

        """ Block lookup using collection id key specifically. """

        # specific to Mongo lookup - uses mongo '_id' which needs to be wrapped in ObjectId
        return CollectionRetrieval(self.library_name,
                                   account_name=self.account_name).filter_by_key("_id", ObjectId(_id))

    def compare_text_blocks(self, t1, t2):

        """ Token-by-token comparison of two text blocks. """

        b = CorpTokenizer(one_letter_removal=True, remove_numbers=True, remove_stop_words=True)
        tokens1 = b.tokenize(t1)
        tokens2 = b.tokenize(t2)
        match_per = 0
        match = 0

        for x in range(0, len(tokens1)):
            for y in range(0, len(tokens2)):
                if tokens1[x].lower() == tokens2[y].lower():
                    match += 1
                    break

        if len(tokens1) > 0:
            match_per = match / len(tokens1)

        return match_per

    def block_similarity_retrieval_more_like_this (self, target_text, qr, similarity_threshold=0.25):

        """ Block similarity by token comparison. """

        #   will rank and order a list of query results using a target text as the reference point
        output = []

        for i, block in enumerate(qr):

            compare_text = block["text"]
            similarity = self.compare_text_blocks(target_text, compare_text)

            if similarity > similarity_threshold:
                block.update({"similarity": similarity})

                output.append(block)

        output = sorted(output, key=lambda x:x["similarity"], reverse=True)

        return output

    def build_doc_id_fn_list(self, qr):

        """ Utility function to build a doc_id and filename list. """
        doc_id_list = []
        fn_list = []

        for q in qr:
            if q["doc_ID"] not in doc_id_list:
                doc_id_list.append(q["doc_ID"])
                fn_list.append(q["file_source"])

        return doc_id_list, fn_list

    def expand_text_result_before(self, block, window_size=400):

        """ Expands text result before. """

        block_id = block["block_ID"] -1
        doc_id = block["doc_ID"]

        before_text = ""
        pre_blocks = []

        while len(before_text) < window_size and block_id >= 0:

            before_block = self.block_lookup(block_id, doc_id)

            if before_block:
                before_text += before_block["text"]
                pre_blocks.append(before_block)

        output = {"expanded_text": before_text, "results": pre_blocks}

        return output

    def expand_text_result_after(self, block, window_size=400):

        """ Expands text result after. """

        block_id = block["block_ID"] + 1
        doc_id = block["doc_ID"]

        after_text = ""
        post_blocks = []

        while len(after_text) < window_size:
            after_block = self.block_lookup(block_id, doc_id)
            if not after_block:
                break  # Break if no block is found

            after_text += after_block["text"]
            post_blocks.append(after_block)
            block_id += 1  # Increment block_id for next iteration

        output = {"expanded_text": after_text, "results": post_blocks}
        return output

    def generate_csv_report(self):

        """Generates a csv report from the current query status. """

        output = QueryState(self).generate_query_report_current_state()
        return output
    
    def filter_by_key_value_range(self, key, value_range, results_only=True):

        """ Executes a filter by key value range. """

        cursor = CollectionRetrieval(self.library_name,
                                     account_name=self.account_name).filter_by_key_value_range(key,value_range)

        query= ""
        result_dict = self._cursor_to_qr(query, cursor, exhaust_full_cursor=True)

        if results_only:
            return result_dict["results"]

        return result_dict

