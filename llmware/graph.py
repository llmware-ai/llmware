
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

""" Graph module implements the Graph class, which contains an automated high-speed pipeline to extract
    NLP statistics from a Library - and use the derived statistical correlations to build a
    knowledge graph consisting of the relationships between words formed from the co-occurrence matrix build among
    the most frequent words in the Library (excluding stop words). """


import os
import time
import logging
import json
import numpy as np
from collections import Counter
from ctypes import *

from llmware.util import Utilities, CorpTokenizer
from llmware.configs import LLMWareConfig
from llmware.resources import CollectionRetrieval

logger = logging.getLogger(__name__)
logger.setLevel(level=20)


class Graph:

    """Graph is a set of NLP statistical functions that generate statistical relationships between key words and
    concepts in a library. """

    def __init__(self, library):

        self.library = library
        self.account_name = library.account_name
        self.library_name = library.library_name

        # nlp analytics settings shifted from Library to Graph
        self.bigram_count = 100

        self.targets_len_max = 5000
        self.context_len_max = 10000

        # expand vocab_len_max = 100000
        self.vocab_len_max = 50000

        # new parameter - max size of BOW file before starting new one
        self.bow_max = 10000000

        self.bow_count = 0

        # nltk.download('averaged_perceptron_tagger', quiet=True)

        self.pre_initialization_bow_data = {}
        self.post_initialization_bow_data = {}

        # create stop words txt file in nlp path
        self.stop_words = Utilities().load_stop_words_list(self.library.nlp_path)

        # load graph c modules - note: if any issues loading module, will be captured in get_module_graph_functions()
        self._mod_utility = Utilities().get_module_graph_functions()

    # new method - used to track 'counter' inside the bow files for incremental read/write/analysis
    def bow_locator(self):

        """ Internal utility method used to enable scalability across multiple underlying BOW (Bag-of-Word)
        files which are created by the graph module. """

        # iterate thru bow_fp_list to find correct BOW + right split to start
        dataset_fp = self.library.nlp_path

        ds_files = os.listdir(dataset_fp)

        bow_files = []
        for f in ds_files:
            if f.startswith("bow"):
                bow_files.append(f)

        bow_index = 0
        bow_byte_index = 0
        bow_tokens = 0
        no_bow = True

        if len(bow_files) > 0:
            bow_files_sorted = sorted(bow_files, reverse=True)
            top_bow_file = bow_files_sorted[0]
            no_bow = False
            try:
                bow_index = int(top_bow_file.split(".")[0][3:])
            except:
                logger.warning(f"warning - Graph - unexpected - could not identify bow index on bow file - "
                               f"{top_bow_file}")
                bow_index = 0

            fp = open(os.path.join(dataset_fp, top_bow_file), "r", encoding='utf-8')
            fp.seek(0, 2)
            bow_byte_index = fp.tell()
            fp.seek(0, 0)  # rewind
            bow_tokens = len(fp.read().split(","))
            fp.close()

        return bow_index, bow_byte_index, bow_tokens, bow_files, no_bow

    def build_graph(self):

        """ Generates multiple valuable nlp artifacts in the library's /nlp folder path, with the
        primary objective of generating the co-occurrence matrix. """

        os.makedirs(self.library.nlp_path, exist_ok=True)

        # note: this function uses a list of ~750 common english stop words
        #   -- it can and should be substituted for use with other languages
        stop_words = Utilities().load_stop_words_list(self.library.nlp_path)

        #   first major step -> build the BOW

        bow_index, bow_byte_index, bow_token_index, bow_files, no_bow = self.bow_locator()

        # save the 'pre_initialization bow data"

        self.pre_initialization_bow_data = {"bow_index": bow_index, "bow_byte_index": bow_byte_index,
                                            "bow_token_index": bow_token_index, "bow_files": bow_files,
                                            "no_bow": no_bow}

        logger.info(f"update: Graph().initialization - bow parameters at start: {self.pre_initialization_bow_data}")

        t0 = time.time()

        # no need to capture outputs directly from .bow_builder() method -> will pick indirectly thru .bow_locator()
        _ = self.bow_builder()

        logger.info(f"update: initialization - Step 1- BOW processing - time - {time.time()-t0} ")

        bow_index, bow_byte_index, bow_token_index, bow_files, no_bow = self.bow_locator()

        # get and save the 'post_initialization bow data"

        self.post_initialization_bow_data = {"bow_index": bow_index, "bow_byte_index": bow_byte_index,
                                             "bow_token_index": bow_token_index, "bow_files": bow_files,
                                             "no_bow": no_bow}

        logger.info(f"update: Graph().initialization - bow parameters post: {self.post_initialization_bow_data}")

        # second major step -> build the MCW
        t1 = time.time()
        vocab_len, targets_len, context_len, min_len = self.mcw_builder()

        logger.info(f"update: Graph().initialization - Step 2- MCW processing - time - {time.time()-t1} - {vocab_len}")

        # third major step -> build the BG
        t3 = time.time()

        graph_output = self.build_graph_raw(vocab_len, targets_len, context_len, min_len)

        logger.info(f"update: Graph().initialization - Step 3 - Graph building - time - {time.time()-t1}")

        # extract key files from /nlp & create new dataset folder
        # shifting from build_dataset to core initialization
        dummy = self.bg_text_package()

        t4 = time.time()

        graph_summary = self.post_initialization_bow_data
        bow_count = len(graph_summary["bow_files"])
        if bow_count == 0:
            bow_total = 0
        else:
            bow_total = (bow_count - 1) * self.bow_max + graph_summary["bow_token_index"]

        graph_summary.update({"bow_count": len(graph_summary["bow_files"])})
        graph_summary.update({"bow_total": bow_total})
        graph_summary.update({"unique_vocab": vocab_len})
        graph_summary.update({"library_name": self.library_name})
        ts = str(Utilities().get_current_time_now())
        graph_summary.update({"time_stamp": ts})

        #   write to manifest.json for knowledge graph
        json_dict = json.dumps(graph_summary,indent=2)
        with open(os.path.join(self.library.nlp_path,"manifest.json"),"w", encoding='utf-8') as outfile:
            outfile.write(json_dict)

        return graph_summary

    def bow_builder(self):

        """ First step in building the graph is removing stop words and numbers and extracting the remaining tokens
        in order from the library and creating BOW files. """

        # key inputs for c functions
        input_account_name = self.account_name
        input_library_name = self.library_name
        account_name = create_string_buffer(input_account_name.encode('ascii', 'ignore'))
        library_name = create_string_buffer(input_library_name.encode('ascii', 'ignore'))

        input_db_path = LLMWareConfig.get_db_uri_string()
        # input_db_path = MongoConfig.get_config("collection_db_uri")

        db_path_c = create_string_buffer(input_db_path.encode('ascii', 'ignore'))

        input_stop_words_fp = self.library.nlp_path + "stop_words_list.txt"
        stop_words_c = create_string_buffer(input_stop_words_fp.encode('ascii', 'ignore'))

        # pass core_path -> will pick up {}.txt in c file
        input_bow_fp = self.library.nlp_path + "bow"
        bow_fp_c = create_string_buffer(input_bow_fp.encode('ascii', 'ignore'))

        input_text_field = "text"
        text_field_c = create_string_buffer(input_text_field.encode('ascii', 'ignore'))

        # int text_extract_main_handler(char * input_account_name, char * input_library_name,
        # char * db, int new_bow, char * db_uri_string,
        # char * input_stop_words_fp, char * input_bow_fp,
        # char * input_text_field, int bow_index, int bow_len)

        db = LLMWareConfig().get_active_db()
        db_c = create_string_buffer(db.encode('ascii','ignore'))

        # new signature
        teh = self._mod_utility.text_extract_main_handler
        teh.argtypes = (c_char_p, c_char_p, c_char_p, c_int, c_char_p, c_char_p, c_char_p, c_char_p, c_int, c_int)

        # old
        # teh.argtypes = (c_char_p, c_char_p, c_int, c_char_p, c_char_p, c_char_p, c_char_p, c_int, c_int)
        # end - current code

        teh.restype = c_int

        # note: key input - is there an existing bow already to build off ('a'), or start new ('w') ?

        if self.pre_initialization_bow_data["no_bow"]:
            new_bow = 0
        else:
            new_bow = 1

        bow_index_current = self.pre_initialization_bow_data["bow_index"]
        bow_len_remainder_only = self.pre_initialization_bow_data["bow_token_index"]

        new_bow_c = c_int(new_bow)
        bow_index_current_c = c_int(bow_index_current)

        bow_len_current_c = c_int(bow_len_remainder_only)

        logger.info(f"update: Graph() bow_builder - calling on text_extract handler - bow vars - "
                    f"{bow_index_current} - {bow_len_remainder_only}")

        # int text_extract_main_handler(char * input_account_name, char * input_library_name,
        # char * db, int new_bow, char * db_uri_string,
        # char * input_stop_words_fp, char * input_bow_fp,
        # char * input_text_field, int bow_index, int bow_len)

        bow_count = teh(account_name,
                        library_name,
                        db_c,
                        new_bow_c,
                        db_path_c,
                        stop_words_c,
                        bow_fp_c,
                        text_field_c,
                        bow_index_current_c,
                        bow_len_current_c)

        logger.info(f"update: Graph() - completed BOW function step - utility BOW create - {bow_count}")

        return 0

    def mcw_builder(self):

        """ Creates analytical artifacts derived from the BOW in terms of most common words (MCW) and other
        frequency data from the BOW. """

        dataset_fp = self.library.nlp_path

        # open bow0.txt as default start -> in most cases, this will be the only BOW
        bow = open(dataset_fp + "bow0.txt", mode="r", encoding="utf-8", errors='ignore').read().split(",")
        bow_len = len(bow)

        # hard-coded scaling principle - target most_common_words list = bow len / 300
        # experimenting with ratio
        targets_len = bow_len // 300

        # will need to set a floor for very small BOW
        if targets_len < 100:
            targets_len = 100

        bow_files = self.post_initialization_bow_data["bow_files"]

        number_of_bow = len(bow_files)

        # run counter and most common on bow0.txt list

        co = Counter(bow)
        mc = co.most_common()

        #   build prune_count approximation
        #   this is the lowest entry on the target mcw list
        #   guiding assumption:   in worst case, if each bow had an entry with this quantity...
        #   it would still be less than .... lowest number in the target

        if len(mc) > targets_len:
            prune_count = mc[targets_len][1] // number_of_bow

        else:
            #   cap len of targets at the length of the most common words
            #   safety check for very small libraries
            targets_len = len(mc) - 1
            prune_count = mc[targets_len][1] // number_of_bow

        mc_pruned = []

        prune_count = 0

        for z in range(0, len(mc)):
            if mc[z][1] > prune_count:
                mc_pruned.append((mc[z][0], mc[z][1]))
            else:
                break

        # this may be the end in default case if only one BOW

        mc_final = mc_pruned

        if len(bow_files) > 1:

            for z in range(1, len(bow_files)):

                bow_new = open(os.path.join(dataset_fp, "bow{}.txt".format(z)), mode="r", encoding="utf-8",
                               errors='ignore').read().split(",")

                # bow_new_len = len(bow_new)
                c_tmp = Counter(bow_new)
                mcw_new = c_tmp.most_common()
                added_new = 0

                for y in range(0, len(mcw_new)):
                    new_entry = (mcw_new[y][0], mcw_new[y][1])
                    if mcw_new[y][1] > prune_count:
                        mc_pruned.append(new_entry)
                        added_new += 1
                    else:
                        logger.info(f"update: mcw analysis - stopping at prune_count: "
                                    f"{y} - {prune_count} - {mcw_new[y]}")
                        break

                mc_combined = sorted(mc_pruned, key=lambda x: x[0])

                mc_final = []
                current_entry = mc_combined[0][0]
                current_count = mc_combined[0][1]

                one_left = 0
                for w in range(1, len(mc_combined)):

                    if mc_combined[w][0] == current_entry:
                        current_count += mc_combined[w][1]
                        one_left = 0
                    else:
                        new_entry = (current_entry, current_count)
                        mc_final.append(new_entry)
                        current_entry = mc_combined[w][0]
                        current_count = mc_combined[w][1]
                        one_left = 1

                if one_left == 1:
                    final_entry = (current_entry, current_count)
                    mc_final.append(final_entry)

                mc_final = sorted(mc_final, key=lambda x: x[1], reverse=True)

        mcw = open(os.path.join(dataset_fp,"most_common_words.txt"), 'w', encoding='utf-8')

        #   for vocab lookup, cap vocab at .vocab_len_max, e.g., 50,000 by default
        logger.info(f"update: Graph() mcw_builder - vocab len: {len(mc_final)}")

        if len(mc_final) > self.vocab_len_max:
            max_len = self.vocab_len_max
        else:
            max_len = len(mc_final)

        vocab_dict = {}
        target_list = []

        mcw_counter_out = []

        new_entry_counter = 0
        for x in range(0, max_len):
            new_entry = mc_final[x][0]
            # strip out special markers in the BOW
            if not new_entry.startswith("[") and not new_entry.startswith("<"):
                mcw.write((new_entry + ","))
                new_dict_entry = {new_entry: new_entry_counter}
                vocab_dict.update(new_dict_entry)
                target_list.append(new_entry)
                mcw_counter_out.append((new_entry, mc_final[x][1]))
                new_entry_counter += 1
        mcw.close()

        # create bigrams list from the bow_list -> initialization (store in nlp)

        bigrams = self.get_bigrams(bow_files)
        bi = open(os.path.join(dataset_fp,"bigrams.txt"), 'w', encoding='utf-8')
        for x in range(0, len(bigrams)):
            bi.write((bigrams[x][0] + ","))
            bi.write((str(bigrams[x][1]) + ","))
        bi.close()

        json_dict = json.dumps(vocab_dict)
        with open(os.path.join(dataset_fp,"vocab_lookup.json"), "w", encoding='utf-8') as outfile:
            outfile.write(json_dict)

        reverse_look_up_dict = {v: k for k, v in vocab_dict.items()}
        rlu_json_dict = json.dumps(reverse_look_up_dict)
        with open(os.path.join(dataset_fp,"token_lookup.json"), "w", encoding='utf-8') as outfile:
            outfile.write(rlu_json_dict)

        mcw_alt = open(os.path.join(dataset_fp,"mcw_counts.txt"), 'w', encoding='utf-8')

        min_len = -1
        MIN_COUNT = 5

        for x in range(0, len(mcw_counter_out)):
            if mcw_counter_out[x][1] < MIN_COUNT and min_len == -1:
                min_len = x - 1
            mcw_alt.write((mcw_counter_out[x][0] + ","))
            mcw_alt.write((str(mcw_counter_out[x][1]) + ","))
        mcw_alt.close()

        vocab_len = len(mc_final)

        if targets_len > vocab_len:
            targets_len = vocab_len

        context_len = 2 * targets_len

        if context_len > vocab_len:
            context_len = vocab_len

        if min_len == -1:
            min_len = vocab_len

        return vocab_len, targets_len, context_len, min_len

    def build_graph_raw(self, vocab_len, targets_len, context_len, min_len):

        """ Main step in the graph building process, applies the artifacts from the previous steps to
        build the co-occurence matrix. """

        #   default - targets_len_max = 5000
        if targets_len > self.targets_len_max:
            targets_len = self.targets_len_max

        #   default - context_len_max = 10000
        if context_len > self.context_len_max:
            context_len = self.context_len_max

        #   default - vocab len max = 50000
        if vocab_len > self.vocab_len_max:
            vocab_len = self.vocab_len_max

        if min_len > vocab_len:
            min_len = vocab_len

        #   bow_len passed is the total size of all BOW files
        #   in simple case, bow_len = # of tokens in bow0.txt
        #   check if greater than 10M -> need to check multiple bow files

        #   default bow_len_max = 10000000

        bow_count = self.post_initialization_bow_data["bow_index"] + 1
        bow_len_remainder = self.post_initialization_bow_data["bow_token_index"]

        logger.info(f"update: build_graph_raw: bow len - {bow_count} - {bow_len_remainder}")

        graph_handler = self._mod_utility.graph_builder

        graph_handler.argtypes = (c_char_p,
                                  c_char_p,
                                  c_char_p,
                                  c_char_p,
                                  c_int,
                                  c_int,
                                  c_int,
                                  c_int,
                                  c_int,
                                  c_char_p,
                                  c_int,
                                  c_int,
                                  c_int)

        graph_handler.restype = c_int

        account_name = create_string_buffer(self.account_name.encode('ascii', 'ignore'))
        library_name = create_string_buffer(self.library.library_name.encode('ascii', 'ignore'))

        input_bow_fp = self.library.nlp_path + "bow"
        bow_fp_c = create_string_buffer(input_bow_fp.encode('ascii', 'ignore'))

        input_mcw_fp = self.library.nlp_path + "most_common_words.txt"

        mcw_fp_c = create_string_buffer(input_mcw_fp.encode('ascii', 'ignore'))

        graph_fp = self.library.nlp_path + "bg.txt"
        graph_fp_c = create_string_buffer(graph_fp.encode('ascii', 'ignore'))

        #   bow_len_remainder -> only the remainder from the last bow file
        #   in usual, simple case -> this is the len of bow0.txt

        bow_len_c = c_int(bow_len_remainder)

        # target len set at half of context len window

        mcw_context_len = context_len
        # mcw_target_len = mcw_len // 2
        mcw_target_len = targets_len

        mcw_context_len_c = c_int(mcw_context_len)
        mcw_target_len_c = c_int(mcw_target_len)
        vocab_len_c = c_int(vocab_len)
        # end - setting target/context mcw lens

        graph_index_c = c_int(0)
        graph_max_size_c = c_int(1000000)

        bow_index = c_int(bow_count)

        min_len_c = c_int(min_len)

        # key parameters - account/library = find BOW + target most_common_words list
        # parameters:   min_counts, targets, window_size == 3

        logger.info(f"update: Graph - initiating call to graph handler - {vocab_len} - {mcw_target_len} - "
                    f"{mcw_context_len} - {min_len}")

        # input to bow_handler:  bow.txt & most_common_words.txt
        # output to bow_handler: bg.txt
        dummy = graph_handler(account_name,
                              library_name,
                              bow_fp_c,
                              mcw_fp_c,
                              bow_index,
                              bow_len_c,
                              mcw_target_len_c,
                              mcw_context_len_c,
                              vocab_len_c,
                              graph_fp_c,
                              graph_index_c,
                              graph_max_size_c,
                              min_len_c)

        logger.info(f"update: Graph() - completed graph build - output value is - {dummy}")

        return 0

    def bg_text_package(self):

        """ Creates an alternative packaging of the co-occurence matrix as a text file. """

        # output
        text_out = []

        fp = os.path.join(self.library.nlp_path, "bg.txt")

        # defensive check - if file path does not exist, then build_graph
        if not os.path.exists(fp):
            self.build_graph()

        # once graph is built, this path should exist
        try:
            f = open(fp, encoding="utf-8", errors="ignore").read().split("\n")

            for z in range(0, len(f)):
                entry_tokens = f[z].split(",")
                entry = ""
                entry += entry_tokens[0] + " "
                new_tokens_added = 1
                for y in range(2, len(entry_tokens), 2):
                    if entry_tokens[y] != "<END>":
                        entry += entry_tokens[y] + " "
                        new_tokens_added += 1
                    if y > 100:
                        break

                if new_tokens_added > 7:
                    text_out.append(entry)

        except:
            logger.error("error: Graph - could not identify correct file in nlp path")

        # write to file
        g = open(os.path.join(self.library.nlp_path,"bg_text.txt"), "w", encoding='utf-8')
        for t in text_out:
            g.write((t + "\n"))
        g.close()

        return text_out

    def _get_top_bigrams_exclude_special_tokens(self, tokens, top_n):

        """ Builds a list of the top bigrams in the library. """

        bigrams = []
        for z in range(1, len(tokens)):

            # skip special tokens in the BOW starting with "[" and "<"
            if str(tokens[z - 1]).startswith("[") or str(tokens[z - 1]).startswith("<") or \
                    str(tokens[z]).startswith("[") or str(tokens[z]).startswith("<"):
                do_nothing = 0
            else:
                # excluded the special tokens - capture bigram

                entry = (tokens[z - 1] + "_" + tokens[z])
                bigrams.append(entry)

        d = Counter(bigrams)
        dc = d.most_common(top_n)

        return dc

    def get_bigrams(self, bow_list):

        """ Builds the list of bigrams from a list of BOW files. """

        top_bigrams_out = []

        for x in bow_list:

            bow_fp = os.path.join(self.library.nlp_path,x)

            bow = open(bow_fp, mode="r", encoding="utf-8", errors='ignore').read().split(",")

            bigrams = self._get_top_bigrams_exclude_special_tokens(bow, self.bigram_count)

            for b in bigrams:
                # floor for asserting bigram
                if b[1] > 10:
                    top_bigrams_out.append(b)

        # prune size of bigrams list
        if len(top_bigrams_out) > self.bigram_count:
            top_bigrams_out = top_bigrams_out[0:self.bigram_count]

        bigrams_sorted = sorted(top_bigrams_out, key=lambda x: x[1], reverse=True)

        return bigrams_sorted

    def get_bow_list(self):

        """ Returns the list of BOW files for a particular library. """

        ds_fp = self.library.nlp_path
        files = os.listdir(ds_fp)
        bow_list = []
        for x in files:
            if str(x).startswith("bow"):
                bow_list.append(x)

        if len(bow_list) > 1:
            bow_list = sorted(bow_list)
            last_bow = open(os.path.join(ds_fp,bow_list[-1]), "r", encoding='utf-8').read().split(",")
            bow_count = (len(bow_list) - 1) * self.bow_max + len(last_bow)
        elif len(bow_list) == 1:
            only_bow = open(os.path.join(ds_fp,bow_list[0]), "r", encoding='utf-8').read().split(",")
            bow_count = len(only_bow)
        else:
            bow_count = 0

        return bow_count, bow_list

    def export_graph_to_visualize (self, graph_target_size):

        """ Exports graph elements in node/edge dataset, packaged for popular visualization libraries
        #   e.g., vis.Network (Javascript)
        #   e.g., networkX (Python) """

        if self.library.get_knowledge_graph_status() != "yes":
            self.build_graph()

        context_search = self.retrieve_knowledge_graph()

        # Step 1 - build full graph from context_search_table

        node_dataset = []
        edge_dataset = []

        if len(context_search) > 2 * graph_target_size:
            max_ct = 2 * graph_target_size
        else:
            max_ct = len(context_search)

        edge_counter = 0
        node_counter = 0

        for z in range(0, max_ct):
            t = context_search[z][0]
            l = len(context_search[z][1])

            new_node = {"id": t, "label": t, "shape": "dot", "size": 10}
            if new_node not in node_dataset:
                node_dataset.append(new_node)
                node_counter += 1

            if l > graph_target_size:
                l = graph_target_size

            for y in range(0, l):
                c = context_search[z][1][y][0]
                w = context_search[z][1][y][1]

                # G_viz.add_edge(t,c,weight=w,title="")

                new_c_node = {"id": c, "label": c, "shape": "dot", "size": 10}
                if new_c_node not in node_dataset:
                    node_dataset.append(new_c_node)
                    node_counter += 1

                new_edge = {"from": t, "title": "", "to": c, "weight": w}
                new_edge_rev = {"from": c, "title": "", "to": t, "weight": w}
                if new_edge not in edge_dataset:
                    edge_dataset.append(new_edge)
                    edge_counter += 1

        return node_dataset, edge_dataset

    def export_graph_with_query_to_visualize(self, graph_target_size, query):

        """ Runs a 'pseudo-query' on graph, and retrieves elements from graph 'neighborhood' for visualization,
        and exports graph elements in node/edge dataset, packaged for popular visualization libraries
            e.g., vis.Network (Javascript)
            e.g., networkX (Python)  """

        if self.library.get_knowledge_graph_status() != "yes":
            self.build_graph()

        b = CorpTokenizer(one_letter_removal=True, remove_stop_words=True, remove_numbers=True)

        query_tokens = CorpTokenizer().tokenize(query)

        context_search = self.retrieve_knowledge_graph()

        if context_search is None or len(context_search) == 0:
            logger.info("update: Graph - knowledge graph appears to be empty")

        # Step 0 - find targeted keyword in context_search

        node_dataset = []
        edge_dataset = []

        # G = nx.Graph()
        counter = 0
        red_nodes = []

        for tokens in query_tokens:
            for z in range(0, len(context_search)):
                if tokens.lower() == context_search[z][0].lower():
                    # G.add_node(context_search[z][0],color="red")
                    t = context_search[z][0]
                    new_node = {"color": "red", "id": t, "label": t, "shape": "dot", "size": 10}
                    if new_node not in node_dataset:
                        node_dataset.append(new_node)
                        red_nodes.append(new_node)

                    if len(context_search[z][1]) > graph_target_size:
                        l = graph_target_size
                    else:
                        l = len(context_search[z][1])

                    logger.debug(f"update: Graph - in targeted_build - found match:  "
                                 f"{len(context_search[z][1])} - {l} - {tokens} - {new_node}")

                    for y in range(0, l):
                        c = context_search[z][1][y][0]
                        w = context_search[z][1][y][1]

                        # G.add_edge(context_search[z][0],c,weight=w,title="")

                        t = context_search[z][0]

                        new_c_node = {"id": c, "label": c, "shape": "dot", "size": 10}

                        if new_c_node not in node_dataset and c.lower() not in query_tokens:
                            logger.info(f"update: Graph - adding node:  {new_c_node}")
                            node_dataset.append(new_c_node)

                        new_edge = {"from": t, "title": "", "to": c, "weight": w}
                        if new_edge not in edge_dataset:
                            edge_dataset.append(new_edge)
                            counter += 1

                        for x in range(0, len(context_search)):
                            if c.lower() == context_search[x][0].lower():
                                if len(context_search[x][1]) > int(graph_target_size / 2):
                                    l2 = int(graph_target_size / 2)
                                else:
                                    l2 = len(context_search[x][1])

                                for y2 in range(0, l2):
                                    c2 = context_search[x][1][y2][0]
                                    w2 = context_search[x][1][y2][1]

                                    # G.add_edge(context_search[x][0],c2,weight=w2,title="")

                                    t = context_search[x][0]

                                    new_node = {"id": t, "label": t, "shape": "dot", "size": 10}
                                    if new_node not in node_dataset and t.lower() not in query_tokens:
                                        node_dataset.append(new_node)

                                    new_c_node = {"id": c2, "label": c2, "shape": "dot", "size": 10}
                                    if new_c_node not in node_dataset and c2.lower() not in query_tokens:
                                        node_dataset.append(new_c_node)

                                    new_edge = {"from": t, "title": "", "to": c2, "weight": w2}
                                    if new_edge not in edge_dataset:
                                        edge_dataset.append(new_edge)

                                    counter += 1

        return red_nodes, node_dataset, edge_dataset

    def get_unique_vocab_len(self):

        """ Returns the length of the unique vocab list found in the Library corpus. """

        return len(self.get_unique_vocab_lookup())

    def get_unique_vocab_lookup(self):

        """ Returns the unique vocab list found in the Library corpus. """

        if self.library.get_knowledge_graph_status() != "yes":
            self.build_graph()

        j = json.load(open(os.path.join(self.library.nlp_path,"vocab_lookup.json"), "r", encoding='utf-8'))

        return j

    def get_unique_vocab_reverse_lookup(self):

        """ Returns the reverse lookup list for the unique vocab of the Library corpus. """

        if self.library.get_knowledge_graph_status() != "yes":
            self.build_graph()

        j = json.load(open(os.path.join(self.library.nlp_path,"token_lookup.json"), "r", encoding='utf-8'))

        return j

    def retrieve_knowledge_graph(self):

        """ Returns the knowledge graph in a dense format consisting of a list of the most frequent target
        words and the surrounding context set of words for each of the target words. """

        ct = []

        if not os.path.exists(os.path.join(self.library.nlp_path,"bg.txt")):
            d = -1
            if d == -1:
                # initialization failed - so contexts_np = []
                contexts_np = np.array([], dtype=object)
                return contexts_np

        if os.path.exists(os.path.join(self.library.nlp_path,"bg.txt")):

            ct_raw = open(os.path.join(self.library.nlp_path,"bg.txt"),
                          mode='r', encoding='utf-8', errors='ignore').read().split(',')

            new_row = []
            target = ct_raw[0]
            start = 0
            got_tuple = 0

            for x in range(1, len(ct_raw)):

                if "<END>" in ct_raw[x]:
                    full_row = (target, new_row)
                    ct.append(full_row)
                    start = 0
                    target = ct_raw[x].split("\n")[-1]
                    # if x < len(ct_raw) - 2:  target = ct_raw[x + 1]

                if start == 1:
                    if got_tuple == 0:
                        new_row.append((ct_raw[x], ct_raw[x + 1]))
                        got_tuple = 1
                    else:
                        got_tuple = 0

                if ct_raw[x] == "<START>":
                    new_row = []
                    start = 1

        contexts_np = np.array(ct, dtype=object)

        return contexts_np

    def retrieve_mcw_counts(self):

        """ Retrieves the counts of most common words. """

        if self.library.get_knowledge_graph_status() != "yes":

            logger.warning("update: to retrieve_mcw_counts, the knowledge graph must be created for this library. "
                           "This is a 'one-time' build, and depending upon the size of the library, may take a little "
                           "bit of time.")

            self.build_graph()

        try:
            mcw = open(os.path.join(self.library.nlp_path,"mcw_counts.txt"), "r", encoding='utf-8').read().split(",")

        except OSError:
            logger.warning("error:  Graph - opening mcw_counts file - path not found.")
            return [], []

        mcw_count_list = []
        mcw_names_only = []

        for z in range(0, len(mcw), 2):

            if (z + 1) < len(mcw):
                try:
                    new_entry = (mcw[z], int(mcw[z + 1]))
                    mcw_count_list.append(new_entry)
                    mcw_names_only.append(mcw[z])

                except:
                    logger.error(f"error: Graph - unexpected mcw file issue - "
                                 f"{z} - {mcw[z]} - {mcw[z+1]}")

        return mcw_count_list, mcw_names_only

    def retrieve_bigrams(self):

        """ Retrieves the top bigrams derived from the corpus. """

        if self.library.get_knowledge_graph_status() != "yes":
            self.build_graph()

        try:
            bigrams = open(os.path.join(self.library.nlp_path,"bigrams.txt"), "r", encoding='utf-8').read().split(",")

        except OSError:
            logger.error("error: Graph - unexpected error opening bigrams file.")
            return []

        bigram_pairs_list = []

        for z in range(0, len(bigrams), 2):

            if (z + 1) < len(bigrams):
                try:
                    bigs = bigrams[z].split("_")
                    new_entry = (bigrams[z], int(bigrams[z + 1]), bigs[0], bigs[1])
                    bigram_pairs_list.append(new_entry)

                except:
                    logger.error(f"error: Graph - unexpected problem with bigram file"
                                 f"- {z} - {bigrams[z]} - {bigrams[z+1]}")

        return bigram_pairs_list

    def get_library_data_stats(self):

        """ Returns a set of library statistical artifacts. """

        library_stats = {}

        lib_card = self.library.get_library_card(self.library.library_name)

        # basic library counting data
        doc_count = {"documents": lib_card["documents"]}
        block_count = {"blocks": lib_card["blocks"]}
        image_count = {"images": lib_card["images"]}
        table_count = {"tables": lib_card["tables"]}

        library_stats.update(doc_count)
        library_stats.update(block_count)
        library_stats.update(image_count)
        library_stats.update(table_count)

        # statistical analysis prepared during initialization
        bigrams = self.retrieve_bigrams()

        if len(bigrams) > 50:
            bigrams = bigrams[0:50]

        library_stats.update({"bigrams": bigrams})

        mcw_list, mcw_names_only = self.retrieve_mcw_counts()

        if len(mcw_list) > 50:
            mcw_list = mcw_list[0:50]

        library_stats.update({"mcw": mcw_list})

        # repackage summary of bg
        bg = self.retrieve_knowledge_graph()

        if len(bg) > 50:
            bg = bg[0:50]
        bg_out = []
        for t in bg:

            if len(t) > 1:
                target = t[0]
                context = t[1]
                context_out = []
                if len(context) > 0:
                    if len(context) > 10:
                        context = context[0:10]
                        for y in range(0, len(context)):
                            context_out.append(context[y])
                        new_row = {"target": target, "context": context_out}
                        bg_out.append(new_row)

        library_stats.update({"graph_top": bg_out})

        # get BOW + unique vocab data from manifest.json in /nlp

        try:
            data_manifest = json.load(open(os.path.join(self.library.nlp_path,"manifest.json"), "r", encoding='utf-8'))

        except OSError:
            logger.error(f"error: Graph - could not open manifest file at path- {self.library.nlp_path}")
            data_manifest = {}

        if "bow_count" in data_manifest:
            library_stats.update({"bow_count": data_manifest["bow_count"]})

        if "unique_vocab_len" in data_manifest:
            library_stats.update({"unique_vocab_len": data_manifest["unique_vocab_len"]})

        return library_stats

    def bow_adhoc_builder(self, sentence_list):

        """ Rapid ad hoc builder of BOW for small set of sentences. """

        bow_out = []
        b = CorpTokenizer(one_letter_removal=True, remove_stop_words=True, remove_numbers=True)

        for sentences in sentence_list:
            tokens = b.tokenize(sentences)
            for t in tokens:
                bow_out.append(t)

        return bow_out

    def mcw_adhoc_builder(self, bow):

        """ Rapid ad hoc builder of most common words in a small BOW file. """

        c = Counter(bow)
        mc = c.most_common()

        return mc

    def retrieve_mcw(self):

        """ Returns the most common words lists. """

        if self.library.get_knowledge_graph_stats() != "yes":
            self.build_graph()

        mcw = open(os.path.join(self.library.nlp_path,"mcw_counts.txt"), "r", encoding='utf-8').read().split(",")
        mcw_pairs_list = []

        for z in range(0, len(mcw), 2):

            if (z + 1) < len(mcw):
                new_entry = (mcw[z], mcw[z + 1])
                mcw_pairs_list.append(new_entry)

        return mcw_pairs_list

    def assemble_top_blocks(self, block_scores_list,doc_id, max_samples=3):

        """ Assembles a list of top text chunks per the weighting of terms in the co-occurence matrix. """

        blocks_to_get = min(max_samples, len(block_scores_list))
        bloks_out = ""

        for x in range(0,blocks_to_get):

            if len(block_scores_list[x]) == 2:
                if block_scores_list[x][0].startswith("block_id="):
                    bid = int(block_scores_list[x][0][len("block_id="):])

                    filter_dict = {"doc_ID": int(doc_id), "block_ID": bid}
                    blok_qr = CollectionRetrieval(self.library_name,
                                                  account_name=self.account_name).filter_by_key_dict(filter_dict)
                    if blok_qr:
                        bloks_out += blok_qr[0]["text"] + "\n"

        return bloks_out

    def doc_graph_builder (self):

        """ Doc Graph Builder iterates through a lot of key analytical artifacts at a document level *
        * there are several commented out items which we will look to explore/add in future versions *
        * ... will also look to shift this to C + background process for performance ... * """

        dataset_fp = self.library.nlp_path

        nlp_files = os.listdir(dataset_fp)

        my_bow_iter_list = []
        for files in nlp_files:
            if files.startswith("bow") and files.endswith(".txt"):
                my_bow_iter_list.append(files)

        my_bow_iter_list = sorted(my_bow_iter_list)

        doc_graph = []

        bow_byte_index = 0

        for b in range(0,len(my_bow_iter_list)):

            bow_file = my_bow_iter_list[b]

            bow_file_object = open(os.path.join(dataset_fp,bow_file), mode="r", encoding="utf-8",errors="ignore")

            if b == 0:
                # skip ahead to the current byte index
                bow_file_object.seek(bow_byte_index,0)

            bow = bow_file_object.read().split("<")

            last_found_block = 0
            doc_start = 1

            for x in range(doc_start,len(bow)):

                entry = bow[x].split(",")

                if len(entry) > 1 and entry[0].startswith("doc_id"):
                    ct = []
                    doc_bow = entry[1:]
                    doc_id_tmp = entry[0][7:-1]
                    c = Counter(doc_bow)
                    mc = c.most_common(20)
                    mc_updated = []

                    for y in range(0, len(mc)):
                        my_context_row = []

                        if not(mc[y][0].startswith("[") or mc[y][0].startswith("<")):
                            mc_updated.append(mc[y])

                            for z in range(0, len(doc_bow)):
                                if mc[y][0] == doc_bow[z]:

                                    if z - 3 >= 0: lb = 3
                                    else: lb = z

                                    if z + 4 < len(doc_bow): lf = 3
                                    else: lf = len(doc_bow) - z - 1

                                    for a in range(z - lb, z):
                                        if not doc_bow[a].startswith("["):
                                            my_context_row.append(doc_bow[a])
                                    for b in range(z + 1, z + 1 + lf):
                                        if not doc_bow[b].startswith("["):
                                            my_context_row.append(doc_bow[b])

                            cs = Counter(my_context_row)
                            new_row = cs.most_common(10)

                            o = (mc[y][0], new_row)
                            ct.append(o)

                            for nr in new_row:
                                c = nr[0]
                                w = nr[1]

                    blocks = bow[x].split("[")

                    doc_id_confirm = blocks[0].split(",")[0]
                    if len(blocks) >= 1:
                        try:
                            first_block_in_doc = blocks[1].split(",")[0][:-1]
                            last_block_in_doc = blocks[-1].split(",")[0][:-1]
                        except:
                            logger.error("error: malformed BOW - need to investigate root cause")
                            first_block_in_doc = "block_id=" + str(last_found_block)
                            last_block_in_doc = "block_id=" + str(last_found_block)
                    else:
                        first_block_in_doc = "block_id=" + str(last_found_block)
                        last_block_in_doc = "block_id=" + str(last_found_block)

                    last_found_block = last_block_in_doc

                    block_scores = []
                    for b in blocks:
                        score = 0
                        elements = b.split(",")
                        block_id = elements[0][:-1]
                        tokens = elements[1:]
                        for t in tokens:
                            for a in range(0,len(mc)):
                                if t == mc[a][0]:
                                    score += mc[a][1]
                        if score > 0:
                            new_entry = (block_id, score)
                            block_scores.append(new_entry)

                    block_scores = sorted(block_scores, key=lambda j:j[1], reverse=True)
                    if len(block_scores) > 20:
                        block_scores = block_scores[0:20]

                    d = {"doc_ID": doc_id_tmp,
                         "block_scores": block_scores,
                         "most_common_words": mc_updated,
                         "context_table": ct,
                         "first_block_in_doc": first_block_in_doc,
                         "last_block_in_doc": last_block_in_doc}

                    doc_graph.append(d)

        #   write to manifest.json for knowledge graph
        json_dict = json.dumps(doc_graph,indent=1)
        with open(self.library.nlp_path + "doc_graph.json","w", encoding='utf-8') as outfile:
            outfile.write(json_dict)

        return doc_graph

    def kg_query_counts(self, query):

        """ Queries the knowledge graph to find related terms. """

        if self.library.get_knowledge_graph_status() != "yes":

            logger.info(f"update: use of this method requires a 'one-time' creation of knowledge graph on the "
                        f"library, which is being created now - this may take some time depending upon the size "
                        f"of the library {self.library}")

            self.library.build_graph()

        bigram_list = Graph(self.library).retrieve_bigrams()
        mcw_count, mcw_names_only = Graph(self.library).retrieve_mcw_counts()
        context_search = Graph(self.library).retrieve_knowledge_graph()
        query_tokens = CorpTokenizer().tokenize(query)

        count_dict = {}

        for tok in query_tokens:

            for j, entry in enumerate(mcw_count):
                if tok == entry[0]:
                    count_dict.update({tok:entry[1]})
                    break

        return count_dict

    def kg_query_related_bigrams(self, query):

        """ 'Queries' the knowledge graph to find related terms. """

        if self.library.get_knowledge_graph_status() != "yes":

            logger.info("update: use of this method requires a 'one-time' creation of knowledge graph on the "
                         f"library, which is being created now - this may take some time depending upon the size "
                         f"of the library {self.library}")

            self.library.build_graph()

        enhanced_search_terms = []

        bigram_list = Graph(self.library).retrieve_bigrams()
        mcw_count, mcw_names_only = Graph(self.library).retrieve_mcw_counts()
        context_search = Graph(self.library).retrieve_knowledge_graph()
        query_tokens = CorpTokenizer().tokenize(query)

        output_dict = {}
        count_dict = {}

        for tok in query_tokens:
            for i, bigram in enumerate(bigram_list):
                bigram_splitter = bigram[0].split("_")
                if tok in bigram_splitter:
                    output_dict.update({bigram[0]: bigram[1]})

            for j, entry in enumerate(mcw_count):
                if tok == entry[0]:
                    count_dict.update({tok:entry[1]})
                    break

        bigrams_out = {"bigrams": output_dict, "counts": count_dict}

        logger.info(f"update: Graph - bigrams out - {bigrams_out}")

        return bigrams_out

    def kg_query(self, query, th=10):

        """ 'Queries' the knowledge graph to find related terms. """

        if self.library.get_knowledge_graph_status() != "yes":

            logger.info(f"update: use of this method requires a 'one-time' creation of knowledge graph on the "
                        f"library, which is being created now - this may take some time depending upon the size "
                        f"of the library {self.library}")

            self.library.build_graph()

        enhanced_search_terms = []

        bigrams = Graph(self.library).retrieve_bigrams()
        mcw_count = Graph(self.library).retrieve_mcw_counts()

        context_search = Graph(self.library).retrieve_knowledge_graph()

        query_tokens = CorpTokenizer().tokenize(query)

        output_dict = {}

        for z in range(0, len(query_tokens)):

            output_dict.update({query_tokens[z]: []})

            for y in range(0, len(context_search)):
                if query_tokens[z] == context_search[y][0]:
                    if context_search[y][1]:
                        for c in range(0, len(context_search[y][1])):
                            tmp_count = context_search[y][1][c][1]

                            if int(tmp_count) > th:
                                g_entry = context_search[y][1][c][0]

                                if g_entry not in output_dict[query_tokens[z]]:
                                    output_dict[query_tokens[z]].append(g_entry)

                                if g_entry not in enhanced_search_terms:
                                    enhanced_search_terms.append(g_entry)

                            if c > 3:
                                break

        return output_dict


