
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


import logging
import os
from collections import Counter
from datetime import datetime
from bson.objectid import ObjectId

from llmware.configs import LLMWareConfig
from llmware.embeddings import EmbeddingHandler
from llmware.resources import CollectionRetrieval, QueryState
from llmware.util import Utilities, CorpTokenizer
from llmware.models import ModelCatalog
from llmware.exceptions import LibraryObjectNotFoundException,UnsupportedEmbeddingDatabaseException,\
    ImportingSentenceTransformerRequiresModelNameException, EmbeddingModelNotFoundException


class Query:

    def __init__(self, library, embedding_model=None, tokenizer=None, vector_db_api_key=None,
                 query_id=None, from_hf=False, from_sentence_transformer=False,embedding_model_name=None,
                 save_history=True, query_mode=None):

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

                logging.info("update: Query - embedding record lookup - %s - %s", embedding_model_name, emb)

                if emb["embedding_model"] == embedding_model_name:

                    if emb["embedding_status"] == "yes":
                        self.embedding_db = emb["embedding_db"]
                        self.search_mode = "semantic"
                        matched_lib_model = True
        else:
            if len(embedding_record) > 0:
                last_emb_record = embedding_record[-1]
                if last_emb_record["embedding_status"] == "yes":
                    self.embedding_db = last_emb_record["embedding_db"]
                    self.search_mode = "semantic"
                    self.embedding_model_name = last_emb_record["embedding_model"]
                    matched_lib_model = True

        if matched_lib_model:

            logging.info("update: Query - found matches in embedding record - %s - %s",
                         self.embedding_db, self.embedding_model_name)

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

    def load_embedding_model(self):

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
                    self.embedding_model = ModelCatalog().load_model(selected_model=self.embedding_model_name)
                else:
                    logging.info("update: Query - selected embedding model could not be found- %s ",
                                    self.embedding_model_name)

        return self

    def get_output_keys(self):
        # list of keys that will be provided in each query_result
        return self.query_result_return_keys

    def set_output_keys(self, result_key_list):

        # set the output keys
        validated_list = []
        for key in result_key_list:
            if key in self.library.default_keys:
                validated_list.append(key)

        # minimum required list
        for rk in self.query_result_min_required_keys:
            if rk not in validated_list:
                validated_list.append(rk)
                logging.warning("warning: Query - adding required keys useful in downstream processing - %s ", rk)

        # setting updated query_return_keys that is used in packaging query results
        self.query_result_return_keys = validated_list

        return validated_list

    def start_query_session(self, query_id=None):

        if query_id:
            self.query_id = query_id

        if self.query_id:
            QueryState(self).load_state(self.query_id)
        else:
            query_id = QueryState(self).initiate_new_state_session()

        return query_id

    def register_query (self, retrieval_dict):

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
        state = QueryState(self).load_state(query_id)
        return self

    def save_query_state(self):
        QueryState(self).save_state()
        return self

    def clear_query_state(self):
        # need to reset state variables
        QueryState(self).initiate_new_state_session()
        return self

    def dump_current_query_state(self):

        query_state_dict = {"query_id": self.query_id,
                            "query_history": self.query_history,
                            "results": self.results,
                            "doc_ID": self.doc_id_list,
                            "file_source": self.doc_fn_list
                            }

        return query_state_dict

    def query(self, query, query_type="text", result_count=20, results_only=True):

        output_result = {"results": [], "doc_ID": [], "file_source": []}

        if query_type not in ["text", "semantic"]:
            logging.error("error: Query().query expects a query type of either 'text' or 'semantic'")
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

    # basic simple text query method - only requires entering the query
    def text_query (self, query, exact_mode=False, result_count=20, exhaust_full_cursor=False, results_only=True):

        # prepare query if exact match required
        if exact_mode:
            query = self.exact_query_prep(query)

        # query the text collection
        cursor = CollectionRetrieval(self.library.collection).basic_query(query)

        # package results, with correct sample counts and output keys requested
        results_dict = self._cursor_to_qr(query, cursor,result_count=result_count,exhaust_full_cursor=
                                          exhaust_full_cursor)

        if results_only:
            return results_dict["results"]

        return results_dict

    def text_query_with_document_filter(self, query, doc_filter, result_count=20, exhaust_full_cursor=False,
                                        results_only=True, exact_mode=False):

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
            logging.warning("warning: Query - expected to receive document filter with keys of 'doc_ID' or "
                            "'file_source' - as a safe fall-back - will run the requested query without a filter.")

        if key:
            cursor = CollectionRetrieval(self.library.collection). \
                    text_search_with_key_value_range(query, key, value_range)
        else:
            # as fallback, if no key found, then run query without filter
            cursor = CollectionRetrieval(self.library.collection).basic_query(query)

        result_dict = self._cursor_to_qr(query, cursor, result_count=result_count,
                                         exhaust_full_cursor=exhaust_full_cursor)

        if results_only:
            return result_dict["results"]

        return result_dict

    def text_query_by_content_type (self, query, content_type,results_only=True):

        filter_dict = {"content_type": content_type}
        retrieval_dict = self.text_query_with_custom_filter(query,filter_dict,results_only=True)
        return retrieval_dict

    def image_query(self, query, results_only=True):

        filter_dict = {"content_type": "image"}
        retrieval_dict = self.text_query_with_custom_filter(query, filter_dict,results_only=True)
        return retrieval_dict

    def table_query(self, query, export_tables_to_csv=False, results_only=True):

        filter_dict = {"content_type": "table"}
        retrieval_dict = self.text_query_with_custom_filter(query, filter_dict,results_only=True)

        # output and write tables to csv files
        if export_tables_to_csv:
            for i, entry in enumerate(retrieval_dict["results"]):
                f = self.export_one_table_to_csv(entry,output_fp=LLMWareConfig.get_query_path(),
                                                 output_fn="table_{}.csv".format(i))

                logging.warning("update: csv created - %s - %s", LLMWareConfig.get_query_path(),f)

        return retrieval_dict

    def text_search_by_page (self, query, page_num=1, results_only=True):

        key = "master_index"  # parsing uses "master_index" across multiple input sources, interpret as "page_num"

        if not isinstance(page_num, list):
            page_num = [page_num]

        cursor_results = CollectionRetrieval(self.library.collection).\
            text_search_with_key_value_range(query, key, page_num)

        retrieval_dict = self._cursor_to_qr(query, cursor_results)

        if results_only:
            return retrieval_dict["results"]

        return retrieval_dict

    def text_query_by_author_or_speaker(self, query, author_or_speaker, results_only=True):

        filter_dict = {"author_or_speaker": author_or_speaker}
        retrieval_dict = self.text_query_with_custom_filter(query,filter_dict,results_only=results_only)
        return retrieval_dict

    def text_query_with_custom_filter (self, query, filter_dict, result_count=20,
                                       exhaust_full_cursor=False, results_only=True):

        # filter_dict is a dict with indefinite number of key:value pairs - each key will be interpreted
        #   as "$and" in the query, requiring a match against all of the key:values in the filter_dict

        # validate filter dict
        validated_filter_dict = {}
        for key, values in filter_dict.items():
            for valid_keys in self.library.default_keys:
                if key in valid_keys:
                    validated_filter_dict.update({key:values})

        if validated_filter_dict:
            cursor = CollectionRetrieval(self.library.collection).\
                text_search_with_key_value_dict_filter(query,validated_filter_dict)

        else:
            logging.error("error: Query text_query_with_custom_filter - keys in filter_dict are not"
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
                        logging.warning("warning: Query() - selected output key not found in result - %s ", key)
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
                    logging.warning("warning: Query() - selected output key not found in result - %s ", key)
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

        # basic semantic query
    def semantic_query (self, query, result_count=20, embedding_distance_threshold=None, results_only=True):

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
            logging.error("error: Query - embedding record does not indicate embedding db - %s "
                          "and/or embedding model - %s ", self.embedding_db, self.embedding_model)

            raise UnsupportedEmbeddingDatabaseException(self.embedding_db)

        qr_raw = []

        # may need to conform the output structure of semantic_block_results
        for i, blocks in enumerate(semantic_block_results):

            # assume that each block has at least two components:  [0] core mongo block, and [1] distance metric
            if blocks[1] < embedding_distance_threshold:

                blocks[0]["distance"] = blocks[1]
                blocks[0]["semantic"] = "semantic"
                blocks[0]["score"] = 0.0

                qr_raw.append(blocks[0])

        # pick up with boilerplate
        results_dict = self._cursor_to_qr (query, qr_raw,result_count=result_count)

        if results_only:
            return results_dict["results"]

        return results_dict

    # basic semantic query
    def semantic_query_with_document_filter(self, query, filter_dict, embedding_distance_threshold=None,
                                            result_count=100, results_only=True):

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
            logging.error("error: Query - embedding record does not indicate embedding db- %s and/or "
                          "an embedding_model - %s ", self.embedding_db, self.embedding_model)

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
            logging.error("error: Query - embedding record does not indicate embedding db- %s and/or "
                          "embedding model - %s ", self.embedding_db, self.embedding_model)

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

    def dual_pass_query (self, query, result_count=20, primary="text", safety_check=True,results_only=True):

        # safety check
        if safety_check and result_count > 100:

            logging.warning("warning: Query().dual_pass_query runs a comparison of output rankings using semantic "
                            "and text.  This particular implementation is not optimized for sample lists longer "
                            "than ~100 X 100.  To remove this warning, there are two options - (1) set the "
                            "safety_check to False in the method declaration, or (2) keep sample count below 100.")

            result_count = 100

        # run dual pass - text + semantic
        retrieval_dict_text = self.text_query(query, result_count=result_count,results_only=True)
        retrieval_dict_semantic = self.semantic_query(query, result_count=result_count,results_only=True)

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
                    confirming_list.append(entry)
                    match = 1
                    matched_second_list.append(entry2["_id"])
                    break
            if match == -1:
                primary_only.append(entry)

        for k, entry2 in enumerate(second_list):
            if entry2["_id"] not in matched_second_list:
                secondary_only.append(entry2)

        # assemble merged top results
        merged_results = []
        merged_results += confirming_list

        select_primary = min(len(primary_only),5)
        select_secondary = min(len(secondary_only),5)

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
                          "text_results": retrieval_dict_semantic,
                          "semantic_results": retrieval_dict_semantic,
                          "doc_ID": doc_id_list,
                          "file_source": doc_fn_list}

        if results_only:
            return merged_results

        return retrieval_dict

    def augment_qr (self, query_result, query_topic, augment_query="semantic"):

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

        result_dict = None

        if query_mode not in ["text", "semantic", "hybrid"]:

            logging.error("error: Query document_filter supports query types - 'text', "
                          "'semantic', and 'hybrid' - type selected not recognized - %s ", query_mode)

            return result_dict

        if query_mode == "text":
            result_dict = self.text_query(filter_topic,exact_mode=exact_mode,result_count=result_count,
                                          exhaust_full_cursor=exhaust_full_cursor,results_only=False)

        if query_mode == "semantic":
            result_dict = self.semantic_query(filter_topic,result_count=result_count, results_only=False)

        if query_mode == "hybrid":
            result_dict = self.dual_pass_query(filter_topic)

        if not result_dict:

            logging.error("error: Query file_selector_only could not find a result - unexpected error - %s ",
                          filter_topic)

            return result_dict

        doc_filter_output = {"doc_ID": result_dict["doc_ID"], "file_source": result_dict["file_source"]}

        return doc_filter_output

    def page_lookup(self, page_list=None, doc_id_list=None, text_only=False):

        doc_id = doc_id_list
        page = page_list

        if text_only:
            page_dict = {"doc_ID": doc_id, "master_index": page, "content_type": "text"}
        else:
            page_dict = {"doc_ID": doc_id, "master_index": page}

        cursor_results = CollectionRetrieval(self.library.collection).filter_by_key_dict(page_dict)

        counter = 0
        output = []

        for x in cursor_results:
            x.update({"matches": []})
            x.update({"page_num": x["master_index"]})

            output.append(x)
            counter += 1
            if counter > 10:
                break

        return output

    # new method to extract whole library
    def get_whole_library(self, selected_keys=None):

        match_results = CollectionRetrieval(self.library.collection).get_whole_collection()

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

    # new method to generate csv files for each table entry
    def export_all_tables(self, query="", output_fp=None):

        table_csv_files_created = []

        if not output_fp:
            output_fp = self.library.misc_path

        if not query:

            match_results = CollectionRetrieval(self.library.collection).filter_by_key("content_type","table")

        else:
            kv_dict = {"content_type": "table"}
            match_results = CollectionRetrieval(self.library.collection).\
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

        # utility function - returns list of all doc_ids in the library
        doc_id_list = CollectionRetrieval(self.library.collection).get_distinct_list("doc_ID")

        return doc_id_list

    def list_doc_fn(self):

        # utility function -returns list of all document names in the library
        doc_fn_raw_list = CollectionRetrieval(self.library.collection).get_distinct_list("file_source")

        doc_fn_out = []
        for i, file in enumerate(doc_fn_raw_list):
            doc_fn_out.append(file.split(os.sep)[-1])
        return doc_fn_out

    def block_lookup(self, block_id, doc_id):

        result = None

        kv_dict = {"doc_ID": doc_id, "block_ID": block_id}

        output = CollectionRetrieval(self.library.collection).filter_by_key_dict(kv_dict)

        if len(output) == 0:
            logging.info("update: Query - Library - block_lookup - block not found: %s ", block_id)
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

        ds_folder = self.library.nlp_path

        results = CollectionRetrieval(self.library.collection).get_whole_collection()

        f = open(ds_folder + "header_text.txt", "w")
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

        ds_folder = self.library.nlp_path

        results = CollectionRetrieval(self.library.collection).get_whole_collection()

        f = open(os.path.join(ds_folder,"core_text.txt"), "w")
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

        # look for all non-empty user_tags
        output = CollectionRetrieval(self.library.collection).filter_by_key_ne_value("user_tags", "")

        counter = 0
        user_tags_out = []
        for elements in output:
            counter += 1
            user_tags_out.append((elements["block_ID"], elements["user_tags"]))

        return user_tags_out

    def filter_by_time_stamp (self, qr, first_date="", last_date=""):

        # apply filter dict to the qr results found
        time_str = "%Y-%m-%d"
        if first_date:
            first_date = datetime.strptime(first_date,time_str)

        if last_date:
            last_date = datetime.strptime(last_date, time_str)

        filtered_qr = []

        for i, entry in enumerate(qr):

            if entry["added_to_collection"]:

                time_str="%a %b %d %H:%M:%S %Y"

                doc_date = datetime.strptime(entry["added_to_collection"], time_str)

                time_accept = self._time_window_filter(first_date,last_date,doc_date)

                if time_accept:
                    filtered_qr.append(entry)

        return filtered_qr

    def _time_window_filter(self, start_time,end_time, test_time, time_str="%a %b %d %H:%M:%S %Y"):

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

        if query.startswith('"') and query.endswith('"'):
            prepared_query = '\"' + query[1:-1] + '\"'

        else:
            # even if user did not wrap in quotes, treat as exact search
            prepared_query = '\"' + query + '\"'

        return prepared_query

    def bibliography_builder_from_qr(self, query_results):

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

        validated_filter_dict = self.prep_validated_filter_dict(filter_dict)
        result_output = []

        for i, entry in enumerate(cursor):

            for key, value in validated_filter_dict.items():
                if key not in entry:
                    logging.warning("warning: Query - retrieval cursor does not contain filter key - %s ", key)
                else:
                    if entry[key] == value:
                        result_output.append(entry)

                if len(result_output) > sample_count and not exhaust_full_cursor:
                    break

        return result_output

    def prep_validated_filter_dict(self, filter_dict):

        validated_filter_dict = {}

        for key, values in filter_dict.items():
            if key in self.library.default_keys:
                validated_filter_dict.update({key:values})
            else:
                logging.warning("warning: Query - filter key not in library collection - %s ", key)

        return validated_filter_dict

    def block_lookup_by_collection_id(self, _id):
        # specific to Mongo lookup - uses mongo '_id' which needs to be wrapped in ObjectId
        return CollectionRetrieval(self.library.collection).filter_by_key("_id", ObjectId(_id))

    def compare_text_blocks(self, t1, t2):

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

        doc_id_list = []
        fn_list = []

        for q in qr:
            if q["doc_ID"] not in doc_id_list:
                doc_id_list.append(q["doc_ID"])
                fn_list.append(q["file_source"])

        return doc_id_list, fn_list

    def expand_text_result_before(self, block, window_size=400):

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

    def expand_text_result_after (self, block, window_size=400):

        block_id = block["block_ID"] + 1
        doc_id = block["doc_ID"]

        after_text = ""
        post_blocks = []

        while len(after_text) < window_size and block_id >= 0:

            after_block = self.block_lookup(block_id, doc_id)

            if after_block:
                after_text += after_block["text"]
                post_blocks.append(after_block)

        output = {"expanded_text": after_text, "results": post_blocks}

        return output

    def generate_csv_report(self):
        output = QueryState(self).generate_query_report_current_state()
        return output
    
    #   starting new method here
    def filter_by_key_value_range(self, key, value_range, results_only=True):

        cursor = CollectionRetrieval(self.library.collection).filter_by_key_value_range(key,value_range)

        query= ""
        result_dict = self._cursor_to_qr(query, cursor, exhaust_full_cursor=True)

        if results_only:
            return result_dict["results"]

        return result_dict

