
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

""" The datasets module implements the Datasets class, which is a set of versatile tools to rapidly develop
a variety of 'model-ready' datasets from llmware prompt interactions, parsing and libraries. """

import os
import json
import random
import logging
from zipfile import ZipFile, ZIP_DEFLATED

from llmware.util import Utilities
from llmware.configs import LLMWareConfig
from llmware.resources import CollectionRetrieval, PromptState
from llmware.exceptions import FilePathDoesNotExistException, LibraryObjectNotFoundException, DatasetTypeNotFoundException

logger = logging.getLogger(__name__)


class Datasets:

    """Datasets class implements a set of data packaging tools to create 'model-ready' datasets using a variety of
    packaging strategies automatically derived from artifacts across llmware. """

    def __init__(self, library=None, ds_folder=None, validation_split=0.1, testing_split=0.1, tokenizer=None,
                 ds_id_mode="uuid"):

        #   loading a library object is required for most, but not all, of the dataset builds
        #   if no library passed, and it is required, then exception raised in the dataset builder method

        self.library = library
        self.library_name = None
        self.account_name = "llmware"

        if library:
            self.library_name = library.library_name
            self.account_name = library.account_name

        #   set up path where dataset files will be created and stored

        if not ds_folder:

            if library:
                #   default preferred path - put /dataset folder archives in library path structure
                self.work_folder = self.library.dataset_path
            else:
                #   backup - will place in /tmp path
                self.work_folder = LLMWareConfig().get_tmp_path()
        else:
            #   will put in passed ds_folder path
            self.work_folder = ds_folder

        # incorporate tokenizer
        if tokenizer:
            self.tokenizer = tokenizer
        else:
            self.tokenizer = Utilities().get_default_tokenizer()

        #   these are char-level tests, so 'independent' of specific tokenization
        self.text_sample_max_len = 512
        self.text_long_sample_max_len = 2048
        self.text_long_sample_min_len = 64
        self.text_short_sample_max_len = 128
        self.text_empty_min_threshold = 50

        #   base folder path for newly created dataset asset will start with .ds_base_name
        self.ds_base_name = "dataset_"
        self.ds_id_mode = ds_id_mode

        #   after building dataset, this will be populated with the name of the current ds
        self.current_ds_name = ""

        # separator configs
        self.separator = "\n"

        self.file_batch_size = 50000

        #TODO: add more options to package datasets for 'User-Assistant' templates

        self.alpaca = {"intro_blurb": "Below is an instruction that describes a task. "
                                      "Write a response that appropriately completes the request.",
                       "user_separator": " ### Instruction: ",
                       "response_separator": " ### Response: ",
                       "end_of_text_separator": "<|endoftext|>"
                       }

        self.human_bot = {"intro_blurb": "",
                          "user_separator": "<human>: ",
                          "response_separator":  "\n<bot>: ",
                          "end_of_text_separator": "<|endoftext|>" }

        self.chatgpt = {"system_instruction": "You are a helpful assistant who speaks with facts and no wasted words."}

        self.testing_split = testing_split
        self.validation_split = validation_split

        self.training_sample_file_name_base = "training_samples"
        self.testing_sample_file_name_base = "testing_samples"
        self.validation_sample_file_name_base = "validation_samples"

        #   available dataset builder types
        self.dataset_available_types = ["build_text_ds", "build_gen_ds_headline_topic_prompter",
                                        "build_gen_ds_headline_text_xsum", "build_gen_dialog_ds",
                                        "build_gen_ds_from_prompt_history", "build_visual_ds_image_labels",
                                        "build_gen_ds_targeted_text_completion"]

        #   dataset catalog
        self.dataset_catalog = [

            {"dataset_name": "build_text_ds",
             "description": "Core unsupervised text chunk dataset useful for text embedding "
                            "fine-tuning and domain adaptation with token span size between "
                            "{} - {}",
             "features": ["text", "file_source", "sample_number"],
             "input_configs": ["min_tokens", "max_tokens"]},

            {"dataset_name": "build_gen_ds_headline_topic_prompter",
             "description": "Generative AI Dataset created in self-supervised extraction of 'headlines', "
                            "paired with longer neighboring text passages.  In this dataset, the 'headline' "
                            "is used a prompter topic with the expected Generative output to be a longer "
                            "paragraph or text on the selected headline subject matter- assembled in format "
                            "{} for generative model fine-tuning",
             "features": ["text", "file_source", "sample_number"],
             "input_configs": ["prompt_wrapper"]},

            {"dataset_name": "build_gen_ds_headline_text_xsum",
             "description": "Generative AI Dataset for 'XSUM' or extreme summarization, created in "
                            "self-supervised extraction of 'headlines' paired with neighboring text "
                            "passages, and assembled in {} format for generative model "
                            "fine-tuning.",
             "features": ["text", "file_source", "sample_number"],
             "input_configs": ["prompt_wrapper"]},

            {"dataset_name": "build_gen_ds_dialog",
             "description": "Generative AI fine-tuning dataset, generated in self-supervised process using "
                            "dialog transcripts to re-create role-based dialog.",
             "features": ["text"],
             "input_configs": ["prompt_wrapper"]},

            {"dataset_name": "build_gen_ds_from_prompt_history",
             "description": "Generative AI Dataset created self-supervised from AI audit log records that "
                            "capture all facets of generative AI inferences, and can be re-packaged to enhance "
                            "fine-tuning.",
             "features": ["text"],
             "input_configs": ["prompt_wrapper"]},

            {"dataset_name": "build_visual_ds_image_labels",
             "description": "Generative Visual dataset, captured in self-supervised automated process "
                            "by associating nearby text with images for training visual description "
                            "generation.",
             "features": ["sample_number","image_ref","doc_ID","block_ID","text_long","text_short"],
             "input_configs": []},

            {"dataset_name": "build_gen_ds_targeted_text_completion",
             "description": "Generative Text/Completion Dataset - splits selected sentences to "
                            "create an open-context 'what is the completion?' text gen dataset.",
             "features": ["text"],
             "input_configs": ["prompt_wrapper"]}
        ]

    def get_dataset_card(self, ds_name):

        """ Returns information about the selected dataset type. """

        for entries in self.dataset_catalog:
            if entries["dataset_name"] == ds_name:
                return entries
        return {}

    def token_counter(self, text_sample):

        """ Simple inline tokenizer provided as convenience to get approximate token counts. """

        toks = self.tokenizer.encode(text_sample).ids
        return len(toks)

    def tokenize_text(self, text_sample):

        """ Simple inline tokenizer provided as convenience to tokenize text.  """

        toks = self.tokenizer.encode(text_sample).ids
        return toks

    def get_dataset_sample(self, ds_name, ds_path=None, sample_range=1000):

        """ Useful for testing to randomly sample an element from a dataset - based on the input ds_name,
        it will be output a sample randomly selected from the first training sample file. """

        if ds_path:
            self.work_folder = ds_path

        ds_folder = os.path.join(self.work_folder,ds_name)

        first_training_file = self.training_sample_file_name_base + "_0.jsonl"

        if not os.path.exists(os.path.join(ds_folder, first_training_file)):
            raise FilePathDoesNotExistException(os.path.join(ds_folder, first_training_file))

        # picks from first training file
        train_file = []
        my_file = open(os.path.join(ds_folder, first_training_file), 'r', encoding='utf-8')
        for lines in my_file:
            new_row = json.loads(lines)
            train_file.append(new_row)

        if len(train_file) > sample_range:
            r = random.randint(0, sample_range)
        else:
            r = random.randint(0, len(train_file) - 1)

        ds_sample = train_file[r]

        return ds_sample

    def issue_new_ds_id (self, custom_id=None, mode=None):

        """ Issues a new dataset id - which will be a UUID by default. """

        if mode:
            self.ds_id_mode = mode

        # issue new ds_id
        ds_id = "default_new"

        if custom_id:
            ds_id = custom_id
        else:

            if self.ds_id_mode == "time_stamp":
                ds_id = str(Utilities().get_current_time_now())

            elif self.ds_id_mode == "uuid":
                ds_id = str(Utilities().get_uuid())

            elif self.ds_id_mode == "random_number":
                ds_id = str(random.randint(1000000, 9999999))

        # create new dataset specific folder
        self.current_ds_name = self.ds_base_name + ds_id
        new_ds_folder = os.path.join(self.work_folder,self.current_ds_name)
        if not os.path.exists(new_ds_folder):
            os.mkdir(new_ds_folder)

        return ds_id, new_ds_folder

    def package_chatgpt_sample(self, turn1, turn2, add_system_instruction=True):

        """ Creates a dataset sample 'wrapped' in ChatGPT style formalism with system-user-assistant. """

        if "system_instruction" in self.chatgpt:
            system_instruction = self.chatgpt["system_instruction"]
        else:
            system_instruction = "You are a helpful assistant."

        if add_system_instruction:
            new_sample = [{"role": "system", "content": system_instruction},
                          {"role": "user", "content": turn1},
                          {"role": "assistant", "content": turn2}]
        else:
            # if no system instruction, then do not add
            new_sample = [{"role": "user", "content": turn1}, {"role": "assistant", "content": turn2}]

        return new_sample

    def package_human_bot_sample(self, turn1, turn2):

        """ Creates a dataset sample wrapped in a simple 'human' and 'bot' wrapper. """

        if "intro_blurb" in self.human_bot:
            intro_blurb = self.human_bot["intro_blurb"]
            if intro_blurb:
                intro_blurb += self.separator
        else:
            intro_blurb = ""

        if "user_separator" in self.human_bot:
            user_separator = self.human_bot["user_separator"]
        else:
            user_separator = "<human>: "

        if "response_separator" in self.human_bot:
            response_separator = self.human_bot["response_separator"]
        else:
            response_separator = "\n<bot>: "

        if "end_of_text" in self.human_bot:
            end_of_text = self.human_bot["end_of_text"]
        else:
            end_of_text = "<|endoftext|>"

        content = intro_blurb + user_separator + turn1 + self.separator + response_separator + turn2 + end_of_text

        sample = {"text": content}

        return sample

    def package_alpaca_sample(self, instruction, response):

        """ Creates a dataset sample wrapped in Alpaca style prompt template wrapper. """

        if "intro_blurb" in self.alpaca:
            intro_blurb = self.alpaca["intro_blurb"]
        else:
            intro_blurb = "Below is an instruction that describes a task. " \
                          "Write a response that appropriately completes the request."

        if "user_separator" in self.alpaca:
            user_separator = self.alpaca["user_separator"]
        else:
            user_separator = " ### Instruction: "

        if "response_separator" in self.alpaca:
            response_separator = self.alpaca["response_separator"]
        else:
            response_separator = " ### Response: "

        if "end_of_text" in self.alpaca:
            end_of_text = self.alpaca["end_of_text"]
        else:
            end_of_text = "<|endoftext|>"

        content = intro_blurb + self.separator + \
                  user_separator + instruction + \
                  response_separator + response + self.separator + end_of_text

        sample = {"text": content}

        return sample

    def build_ds_by_name(self, ds_name, min_tokens=100, max_tokens=1000,query=None,
                         filter_dict=None, qr=None, custom_id=None,prompt_wrapper="human_bot",
                         role_dict=None, human_first=True):

        """ Builds a dataset by the selected dataset name, passed as input 'ds_name' with optional parameters
        for configuration."""

        dataset_dict = None

        # available dataset build types in self.dataset_catalog:
        #   "build_text_ds", "build_gen_ds_headline_topic_prompter",
        #   "build_gen_ds_headline_text_xsum", "build_gen_dialog_ds",
        #   "build_gen_ds_from_prompt_history", "build_visual_ds_image_labels",
        #   "build_gen_ds_targeted_text_completion"

        if ds_name not in self.dataset_available_types:
            raise DatasetTypeNotFoundException(ds_name)

        if ds_name == "build_text_ds":
            dataset_dict = self.build_text_ds(min_tokens=min_tokens, max_tokens=max_tokens,query=query,
                                              filter_dict=filter_dict, qr=qr, custom_id=custom_id)

        if ds_name == "build_gen_ds_headline_topic_prompter":
            dataset_dict = self.build_gen_ds_headline_topic_prompter(prompt_wrapper=prompt_wrapper,
                                                                     custom_id=custom_id, qr=qr)

        if ds_name == "build_gen_ds_headline_text_xsum":
            dataset_dict = self.build_gen_ds_headline_text_xsum(prompt_wrapper=prompt_wrapper,
                                                                custom_id=custom_id, qr=qr)

        if ds_name == "build_gen_dialog_ds":
            dataset_dict = self.build_gen_dialog_ds(prompt_wrapper=prompt_wrapper, custom_id=custom_id, qr=qr,
                                                    human_first=human_first, role_dict=role_dict)

        if ds_name == "build_gen_ds_from_prompt_history":
            dataset_dict = self.build_gen_ds_from_prompt_history(prompt_wrapper=prompt_wrapper, custom_id=custom_id)

        if ds_name == "build_visual_ds_image_labels":
            dataset_dict = self.build_visual_ds_image_labels(query=query, filter_dict=filter_dict,
                                                             qr=qr, custom_id=custom_id)

        if ds_name == "build_gen_ds_targeted_text_completion":
            dataset_dict = self.build_gen_ds_targeted_text_completion (prompt_wrapper=prompt_wrapper,
                                                                       query=query, filter_dict=filter_dict,
                                                                       qr=qr, custom_id=custom_id)

        return dataset_dict

    def build_text_ds (self, min_tokens=100, max_tokens=1000,query=None,filter_dict=None, qr=None, custom_id=None):

        """ Generates a text dataset useful for self-supervised fine-tuning. """

        #   create specific folder for dataset artifacts inside library dataset path
        ds_id, ds_folder = self.issue_new_ds_id(custom_id=custom_id)

        if not qr:

            #   optional:  by passing query and/or filter_dict, allows targeted 'subset' of library to be used
            if not query and not filter_dict:

                # by default, will get only text and table entries, but no images (since text is duplicative)
                filter_list = ["text", "table"]

                if self.library:
                    results = CollectionRetrieval(self.library_name,
                                                  account_name=self.account_name).filter_by_key_value_range("content_type",filter_list)
                else:
                    raise LibraryObjectNotFoundException("no-library-loaded-in-Dataset-constructor")

            else:

                if self.library:
                    results = CollectionRetrieval(self.library_name,account_name=self.account_name).\
                        text_search_with_key_value_dict_filter(query, filter_dict)
                else:
                    raise LibraryObjectNotFoundException("no-library-loaded-in-Dataset-constructor")

        else:
            results = qr

        counter = 0
        batch_counter = 0
        output = []
        text_out = []
        batch_number = 0
        total_sample_count = 0
        training_sample_count = 0
        testing_sample_count = 0
        validation_sample_count = 0
        training_files_created = []
        validation_files_created = []
        testing_files_created = []

        text_sample = ""
        current_doc = 0

        results = sorted(results, key=lambda x:x["doc_ID"], reverse=False)

        for i, elements in enumerate(results):

            if i == 0:
                current_doc = elements["doc_ID"]
                text_sample = elements["text"]

            tok_count = self.token_counter(text_sample)

            # if in target range or if last sample in doc
            if min_tokens <= tok_count <= max_tokens or elements["doc_ID"] != current_doc:

                # create sample
                # replace in output doc_ID for file_source? "doc_ID" | current_doc
                new_entry = {"sample_number": counter, "file_source": elements["file_source"], "text": text_sample}
                output.append(new_entry)
                text_out.append(text_sample)
                counter += 1
                batch_counter += 1

                # edge case for i==0
                if i == 0:
                    text_sample = ""
                else:
                    # start fresh
                    text_sample = elements["text"]
                    current_doc = elements["doc_ID"]
            else:
                if tok_count <= min_tokens:
                    text_sample += " " + elements["text"]
                    tok_count = self.token_counter(text_sample)

                if tok_count >= max_tokens:

                    while tok_count > max_tokens:

                        tokens = self.tokenize_text(text_sample)
                        chopped = tokens[0:max_tokens]
                        remainder = tokens[max_tokens:]
                        remainder_text = self.tokenizer.decode(remainder)
                        chopped_text = self.tokenizer.decode(chopped)

                        smooth_stop = self._smooth_stopper(chopped_text,200)

                        new_text_sample = chopped_text[:smooth_stop]
                        new_remainder = chopped_text[smooth_stop:] + remainder_text

                        # replacing doc_ID: current_doc
                        new_entry = {"sample_number": counter, "file_source": elements["file_source"],
                                     "text": new_text_sample}

                        output.append(new_entry)
                        text_out.append(text_sample)
                        counter += 1
                        batch_counter += 1
                        text_sample = new_remainder
                        tok_count = self.token_counter(text_sample)

                    # pick up last entry, if any
                    if len(text_sample) > 0:

                        #   replacing "doc_ID" | current_doc
                        new_entry = {"sample_number": counter, "file_source": elements["file_source"],
                                     "text": text_sample}

                        output.append(new_entry)
                        text_out.append(text_sample)
                        counter += 1
                        batch_counter += 1

            # pick up last remaining sample, if any
            if len(text_sample) > 0:

                #   replacing "doc_ID" | current_doc
                new_entry = {"sample_number": counter, "file_source": elements["file_source"], "text": text_sample}
                output.append(new_entry)
                text_out.append(text_sample)
                counter += 1
                batch_counter += 1

            if batch_counter >= self.file_batch_size:
                # write samples to file + start new batch

                output, text_out, testing_set, validation_set, testing_text, validation_text = \
                    self.test_validation_splitter(output, text_out)

                training_sample_count += len(output)
                validation_sample_count += len(validation_set)
                testing_sample_count += len(testing_set)

                tr, va, te = self.save_tr_va_te_sets(output, text_out, validation_set, validation_text,
                                                     testing_set, testing_text, ds_folder, batch_number)

                if tr:
                    for f in tr:
                        training_files_created.append(f)

                if va:
                    for f in va:
                        validation_files_created.append(f)

                if te:
                    for f in te:
                        testing_files_created.append(f)

                batch_number += 1
                total_sample_count += len(output)
                total_sample_count += len(validation_set)
                total_sample_count += len(testing_set)
                output = []
                text_out = []
                batch_counter = 0

        if len(output) > 0:

            output, text_out, testing_set, validation_set, testing_text, validation_text = \
                self.test_validation_splitter(output, text_out)

            training_sample_count += len(output)
            validation_sample_count += len(validation_set)
            testing_sample_count += len(testing_set)

            tr, va, te = self.save_tr_va_te_sets(output, text_out, validation_set, validation_text,
                                                 testing_set, testing_text, ds_folder, batch_number)

            if tr:
                for f in tr:
                    training_files_created.append(f)

            if va:
                for f in va:
                    validation_files_created.append(f)

            if te:
                for f in te:
                    testing_files_created.append(f)

            total_sample_count += len(output)
            total_sample_count += len(validation_set)
            total_sample_count += len(testing_set)

        ds_name = "build_text_ds"
        dataset_card = self.get_dataset_card(ds_name)

        dataset_dict = {"ds_type": dataset_card["dataset_name"],
                        "ds_id": ds_id,
                        "training_samples": training_sample_count,
                        "training_files": training_files_created,
                        "validation_samples": validation_sample_count,
                        "validation_files": validation_files_created,
                        "testing_samples": testing_sample_count,
                        "testing_files": testing_files_created,
                        "batches": batch_number + 1,
                        "prompt_wrapper": "None",
                        "description": dataset_card["description"].format(str(min_tokens),str(max_tokens)),
                        "features": dataset_card["features"],
                        "time_stamp": str(Utilities().get_current_time_now())
                        }

        # save dataset dict -> and put in ds folder
        json_dict = json.dumps(dataset_dict,indent=2)
        with open(os.path.join(ds_folder, "manifest.json"),"w", encoding='utf-8') as outfile:
            outfile.write(json_dict)

        return dataset_dict

    def build_gen_ds_headline_topic_prompter (self, prompt_wrapper="human_bot", custom_id=None, qr=None):

        """ Generates a dataset consisting of pairs of headline and text passages, automatically extracted from
        document parsing into library - experimental self-supervised dataset building strategy - results may
        vary widely depending upon the underlying source documents. """

        #   create specific folder for dataset artifacts inside library dataset path
        ds_id, ds_folder = self.issue_new_ds_id(custom_id=custom_id)

        if not qr:
            #   basic filter to get all text and tables in collection
            filter_list = ["text", "table"]

            if self.library:
                results = CollectionRetrieval(self.library_name, account_name=self.account_name).\
                    filter_by_key_value_range("content_type", filter_list)
            else:
                raise LibraryObjectNotFoundException("no-library-loaded-in-Dataset-constructor")

        else:
            results = qr

        total_sample_count = 0
        training_sample_count = 0
        validation_sample_count = 0
        testing_sample_count = 0
        batch_number = 0
        text_out = []
        training_files_created = []
        validation_files_created = []
        testing_files_created = []
        batch_counter = 0
        counter = 0
        output = []
        new_sample = None
        features = []

        for elements in results:

            text_long = elements["text"]
            if not text_long:
                text_long = elements["table"]

            text_short = elements["header_text"]
            doc_id = elements["doc_ID"]

            # looking for samples that are 'organically' paired
            if text_long and text_short:

                if len(text_long) > self.text_long_sample_min_len and len(text_short) > self.text_empty_min_threshold:
                    # need to additional checks if text_long is > max

                    if prompt_wrapper == "human_bot":

                        instruction = "Please write a paragraph based on the topic: "
                        new_sample = self.package_human_bot_sample(text_short,text_long)
                        features = ["text"]

                    if prompt_wrapper == "alpaca":

                        instruction = "Please write a paragraph based on the topic: " + text_short
                        response = text_long
                        new_sample = self.package_alpaca_sample(instruction,response)
                        features = ["text"]

                    if prompt_wrapper == "chat_gpt":

                        instruction = "Please write a paragraph based on the topic: " + text_short
                        new_sample = self.package_chatgpt_sample(instruction, text_long)
                        features = ["role", "text"]

                    if prompt_wrapper == "dict" or not new_sample:

                        new_sample = {"sample_number": counter, "file_source": elements["file_source"],
                                      "text_long": text_long,
                                      "text_short": text_short}

                        features = ["sample_number", "file_source", "text_long", "text_short"]

                    text_entry = text_long + self.separator + text_short
                    text_out.append(text_entry)
                    output.append(new_sample)

                    counter += 1
                    batch_counter += 1

            if batch_counter >= self.file_batch_size:

                output, text_out, testing_set, validation_set, testing_text, validation_text = \
                    self.test_validation_splitter(output, text_out)

                training_sample_count += len(output)
                validation_sample_count += len(validation_set)
                testing_sample_count += len(testing_set)

                tr, va, te = self.save_tr_va_te_sets(output, text_out, validation_set, validation_text,
                                                     testing_set, testing_text, ds_folder, batch_number)

                if tr:
                    for f in tr:
                        training_files_created.append(f)

                if va:
                    for f in va:
                        validation_files_created.append(f)

                if te:
                    for f in te:
                        testing_files_created.append(f)

                total_sample_count += batch_counter
                batch_counter = 0
                output = []
                text_out = []
                batch_number += 1

        if len(output) > 0:

            output, text_out, testing_set, validation_set, testing_text, validation_text = \
                self.test_validation_splitter(output, text_out)

            training_sample_count += len(output)
            validation_sample_count += len(validation_set)
            testing_sample_count += len(testing_set)

            tr, va, te = self.save_tr_va_te_sets(output, text_out, validation_set, validation_text,
                                                 testing_set, testing_text, ds_folder, batch_number)

            if tr:
                for f in tr: training_files_created.append(f)

            if va:
                for f in va: validation_files_created.append(f)

            if te:
                for f in te: testing_files_created.append(f)

            total_sample_count += batch_counter

        # results.close()
        ds_name = "build_gen_ds_headline_topic_prompter"
        dataset_card = self.get_dataset_card(ds_name)

        dataset_dict = {"ds_type": dataset_card["dataset_name"],
                        "ds_id": ds_id,
                        "training_samples": training_sample_count,
                        "training_files": training_files_created,
                        "validation_samples": validation_sample_count,
                        "validation_files": validation_files_created,
                        "testing_samples": testing_sample_count,
                        "testing_files": testing_files_created,
                        "batches": batch_number + 1,
                        "prompt_wrapper": prompt_wrapper,
                        "description": dataset_card["description"].format(prompt_wrapper),
                        "features": features,   # note may differ from dataset_card
                        "time_stamp": str(Utilities().get_current_time_now())}

        # save dataset dict -> and put in ds folder
        json_dict = json.dumps(dataset_dict,indent=2)
        with open(os.path.join(ds_folder, "manifest.json"),"w", encoding='utf-8') as outfile:
            outfile.write(json_dict)

        return dataset_dict

    def build_gen_ds_headline_text_xsum(self, prompt_wrapper="human_bot", custom_id=None, qr=None):

        """ Generates a dataset using headline formatted text extracted from a set of documents in Library. """

        #   create specific folder for dataset artifacts inside library dataset path
        ds_id, ds_folder = self.issue_new_ds_id(custom_id=custom_id)

        if not qr:
            filter_list = ["text"]  # includes only text - should tables be excluded ?

            if self.library:
                results = CollectionRetrieval(self.library_name, account_name=self.account_name).\
                    filter_by_key_value_range("content_type", filter_list)
            else:
                raise LibraryObjectNotFoundException("no-library-loaded-in-Dataset-constructor")

        else:
            results = qr

        total_sample_count = 0
        training_sample_count = 0
        validation_sample_count = 0
        testing_sample_count = 0
        batch_number = 0
        text_out = []
        training_files_created = []
        validation_files_created = []
        testing_files_created = []
        batch_counter = 0
        counter = 0
        output = []
        new_sample = None
        features = []

        for elements in results:

            text_long = elements["text"]
            if not text_long:
                text_long = elements["table"]

            text_short = elements["header_text"]
            doc_id = elements["doc_ID"]

            # looking for samples that are 'organically' paired
            if text_long and text_short:

                if len(text_long) > self.text_long_sample_min_len and len(text_short) > self.text_empty_min_threshold:
                    # need to additional checks if text_long is > max

                    if prompt_wrapper == "human_bot":
                        instruction = "Please read the following passage, and provide a short summary.\n" + text_long
                        new_sample = self.package_human_bot_sample(instruction, text_short)
                        features = ["text"]

                    if prompt_wrapper == "alpaca":
                        instruction = "Please read the following passage, and provide a short summary.\n" + text_long
                        response = text_short
                        new_sample = self.package_alpaca_sample(instruction, response)
                        features = ["text"]

                    if prompt_wrapper == "chat_gpt":
                        instruction = "Please read the following passage, and provide a short summary.\n" + text_long
                        new_sample = self.package_chatgpt_sample(instruction, text_short)
                        features = ["role", "text"]

                    if prompt_wrapper == "dict" or not new_sample:
                        new_sample = {"sample_number": counter, "file_source": elements["file_source"],
                                      "text_long": text_long,
                                      "text_short": text_short}
                        features = ["sample_number", "file_source", "text_long", "text_short"]

                    text_entry = text_long + self.separator + text_short
                    text_out.append(text_entry)
                    output.append(new_sample)

                    counter += 1
                    batch_counter += 1

            if batch_counter >= self.file_batch_size:

                output, text_out, testing_set, validation_set, testing_text, validation_text = \
                    self.test_validation_splitter(output, text_out)

                training_sample_count += len(output)
                validation_sample_count += len(validation_set)
                testing_sample_count += len(testing_set)

                tr, va, te = self.save_tr_va_te_sets(output, text_out, validation_set, validation_text,
                                                     testing_set, testing_text, ds_folder, batch_number)

                if tr:
                    for f in tr:
                        training_files_created.append(f)

                if va:
                    for f in va:
                        validation_files_created.append(f)

                if te:
                    for f in te:
                        testing_files_created.append(f)

                total_sample_count += batch_counter
                batch_counter = 0
                output = []
                text_out = []
                batch_number += 1

        if len(output) > 0:

            output, text_out, testing_set, validation_set, testing_text, validation_text = \
                self.test_validation_splitter(output, text_out)

            training_sample_count += len(output)
            validation_sample_count += len(validation_set)
            testing_sample_count += len(testing_set)

            tr, va, te = self.save_tr_va_te_sets(output, text_out, validation_set, validation_text,
                                                 testing_set, testing_text, ds_folder, batch_number)

            if tr:
                for f in tr: training_files_created.append(f)

            if va:
                for f in va: validation_files_created.append(f)

            if te:
                for f in te: testing_files_created.append(f)

            total_sample_count += batch_counter

        # results.close()
        ds_name = "build_gen_ds_headline_text_xsum"
        dataset_card = self.get_dataset_card(ds_name)

        dataset_dict = {"ds_type": dataset_card["dataset_name"],
                        "ds_id": ds_id,
                        "training_samples": training_sample_count,
                        "training_files": training_files_created,
                        "validation_samples": validation_sample_count,
                        "validation_files": validation_files_created,
                        "testing_samples": testing_sample_count,
                        "testing_files": testing_files_created,
                        "batches": batch_number + 1,
                        "prompt_wrapper": prompt_wrapper,
                        "description": dataset_card["description"].format(prompt_wrapper),
                        "features": features,   # note: may differ from dataset_card
                        "time_stamp": str(Utilities().get_current_time_now())}

        # save dataset dict -> and put in ds folder
        json_dict = json.dumps(dataset_dict, indent=2)
        with open(os.path.join(ds_folder, "manifest.json"), "w", encoding='utf-8') as outfile:
            outfile.write(json_dict)

        return dataset_dict

    def build_gen_dialog_ds (self, prompt_wrapper="human_bot", human_first=True, role_dict=None,
                             custom_id=None, qr=None):

        """ Generates a dataset consisting of dialogs extracted from conversation-oriented transcript documents with
        identifiable speaker roles. """

        #   create specific folder for dataset artifacts inside library dataset path
        ds_id, ds_folder = self.issue_new_ds_id(custom_id=custom_id)

        if not qr:

            if self.library:
                dialogs = CollectionRetrieval(self.library_name,account_name=self.account_name).filter_by_key("dialog", "true")
            else:
                raise LibraryObjectNotFoundException("no-library-loaded-in-Dataset-constructor")

            dialogs = sorted(dialogs, key=lambda x:x["doc_ID"], reverse=False)

            if len(dialogs) == 0:
                logger.error("error:  Datasets builder - not able to identify text as dialog conversation turns")
                return - 1
        else:
            dialogs = qr

        # counters
        output = []
        total_sample_count = 0
        training_sample_count = 0
        validation_sample_count = 0
        testing_sample_count = 0
        training_files_created = []
        validation_files_created = []
        testing_files_created = []
        text_out = []
        batch_number = 0
        batch_counter = 0

        if len(dialogs) == 0:
            logger.error("error: Datasets - no dialog transcripts found")
            return -1

        # pull the doc_id for the first document
        current_doc = dialogs[0]["doc_ID"]
        current_transcript = []
        current_speaker_list = []

        for x in range(0,len(dialogs)):

            # bundle all of the conversational turns by document
            if dialogs[x]["doc_ID"] == current_doc:
                current_transcript.append(dialogs[x])
                if dialogs[x]["author_or_speaker"] not in current_speaker_list:
                    current_speaker_list.append(dialogs[x]["author_or_speaker"])

            else:
                # process transcript

                transcript_output, trans_text = self._conversation_builder(current_transcript, current_speaker_list,
                                                                           prompt_wrapper="human_bot")

                output += transcript_output
                text_out += trans_text
                batch_counter = len(output)

                # reset
                current_transcript = [dialogs[x]]
                current_speaker_list = [dialogs[x]["author_or_speaker"]]
                current_doc = dialogs[x]["doc_ID"]

        # need to confirm "dialog" & then transcript-by-transcript - assigning roles by different speakers

            if batch_counter >= self.file_batch_size:

                output, text_out, testing_set, validation_set, testing_text, validation_text = \
                    self.test_validation_splitter(output, text_out)

                training_sample_count += len(output)
                validation_sample_count += len(validation_set)
                testing_sample_count += len(testing_set)

                tr, va, te = self.save_tr_va_te_sets(output, text_out, validation_set, validation_text,
                                                     testing_set, testing_text, ds_folder, batch_number)

                if tr:
                    for f in tr:
                        training_files_created.append(f)

                if va:
                    for f in va:
                        validation_files_created.append(f)

                if te:
                    for f in te:
                        testing_files_created.append(f)

                total_sample_count += batch_counter
                batch_counter = 0
                output = []
                text_out = []
                batch_number += 1

        if len(output) > 0:

            output, text_out, testing_set, validation_set, testing_text, validation_text = \
                self.test_validation_splitter(output, text_out)

            training_sample_count += len(output)
            validation_sample_count += len(validation_set)
            testing_sample_count += len(testing_set)

            tr, va, te = self.save_tr_va_te_sets(output, text_out, validation_set, validation_text,
                                                 testing_set, testing_text, ds_folder, batch_number)

            if tr:
                for f in tr: training_files_created.append(f)

            if va:
                for f in va: validation_files_created.append(f)

            if te:
                for f in te: testing_files_created.append(f)

            total_sample_count += batch_counter

        # results.close()
        ds_name = "build_gen_ds_dialog"
        dataset_card = self.get_dataset_card(ds_name)

        dataset_dict = {"ds_type": dataset_card["dataset_name"],
                        "ds_id": ds_id,
                        "training_samples": training_sample_count,
                        "training_files": training_files_created,
                        "validation_samples": validation_sample_count,
                        "validation_files": validation_files_created,
                        "testing_samples": testing_sample_count,
                        "testing_files": testing_files_created,
                        "batches": batch_number + 1,
                        "prompt_wrapper": prompt_wrapper,
                        "description": dataset_card["description"],
                        "features": dataset_card["features"],
                        "time_stamp": str(Utilities().get_current_time_now())}

        # save dataset dict -> and put in ds folder
        json_dict = json.dumps(dataset_dict, indent=2)
        with open(os.path.join(ds_folder, "manifest.json"), "w", encoding='utf-8') as outfile:
            outfile.write(json_dict)

        return dataset_dict

    def _conversation_builder(self, conversation_blocks, speaker_list, prompt_wrapper="chat_gpt"):

        """ Internal utility function to build up a conversation dialog turn. """

        #   note: currently only supports a human_bot format, and assumes human is first speaker

        # inner loop that builds output from a list of conversational turns within a single transcript
        dialog_turn = []
        first_speaker = ""
        last_speaker = ""
        running_convo = ""
        output = []
        text_output = []

        for i, convo in enumerate(conversation_blocks):

            if i == 0:
                first_speaker = convo["author_or_speaker"]
                running_convo = convo["text"]
                dialog_turn.append([first_speaker, running_convo])
                last_speaker = convo["author_or_speaker"]
            else:
                # general case
                if convo["author_or_speaker"] == last_speaker:
                    running_convo += convo["text"]
                    for j, speakers in enumerate(dialog_turn):
                        if speakers[0] == last_speaker:
                            dialog_turn[j] = [last_speaker, running_convo]
                else:
                    # new speaker
                    if convo["author_or_speaker"] == first_speaker:

                        # wrap up the convo thread

                        # prepare output record
                        turns = []
                        for k, convo_turns in enumerate(dialog_turn):
                            turns.append(convo_turns[1])

                        prompt_wrapper = "human_bot"
                        if prompt_wrapper == "human_bot":
                            sample = ""
                            p = "<human>: "
                            for t in turns:
                                sample += p + t + "\n"
                                # alternate
                                if p == "<human>: ":
                                    p = "<bot>: "
                                else:
                                    p = "<human>: "

                            sample_record = {"text": sample}
                            output.append(sample_record)
                            text_output.append(sample)

                            # resets
                            dialog_turn = []
                            dialog_turn.append([first_speaker, convo["text"]])
                            running_text = convo["text"]
                            last_speaker = first_speaker

                    else:

                        running_convo = convo["text"]
                        last_speaker = convo["author_or_speaker"]
                        in_list = False
                        for s, speakers in enumerate(dialog_turn):
                            if last_speaker == speakers[0]:
                                dialog_turn[s] = [last_speaker, running_convo]
                                in_list = True
                        if not in_list:
                            dialog_turn.append([last_speaker,running_convo])

        return output, text_output

    def build_gen_ds_from_prompt_history (self, prompt_wrapper="alpaca", custom_id=None):

        """ Generates a dataset constructed from a prompt interaction history. """

        #   create specific folder for dataset artifacts inside library dataset path
        ds_id, ds_folder = self.issue_new_ds_id(custom_id=custom_id)

        ai_results = PromptState().full_history()

        # counters
        batch_counter = 0
        counter = 0
        output = []
        total_sample_count = 0
        training_sample_count = 0
        validation_sample_count = 0
        testing_sample_count = 0
        training_files_created = []
        validation_files_created = []
        testing_files_created = []
        text_out = []
        batch_number = 0

        for i, entries in enumerate(ai_results):

            prompt = str(entries["prompt"])
            evidence = str(entries["evidence"])
            ai_output = str(entries["llm_response"])
            instruction = str(entries["instruction"])
            sample = None

            if prompt_wrapper not in ["human_bot", "alpaca", "chat_gpt"]:

                prompt_wrapper = "human_bot"

            if prompt_wrapper == "human_bot":

                turn1 = evidence + "\n" + prompt
                turn2 = ai_output
                sample = self.package_human_bot_sample(turn1,turn2)

            if prompt_wrapper == "alpaca":

                instruction = evidence + "\n" + prompt
                response = ai_output
                sample = self.package_alpaca_sample(instruction,response)

            if prompt_wrapper == "chat_gpt":

                turn1 = evidence + "\n" + prompt
                turn2 = ai_output
                sample = self.package_chatgpt_sample(turn1,turn2)

            if sample:

                output.append(sample)

                text_agg = instruction + "\n" + prompt + "\n" + evidence + "\n" + ai_output
                text_out.append(text_agg)

            if batch_counter >= self.file_batch_size:

                output, text_out, testing_set, validation_set, testing_text, validation_text = \
                    self.test_validation_splitter(output, text_out)

                training_sample_count += len(output)
                validation_sample_count += len(validation_set)
                testing_sample_count += len(testing_set)

                tr, va, te = self.save_tr_va_te_sets(output, text_out, validation_set, validation_text,
                                                     testing_set, testing_text, ds_folder, batch_number)

                if tr:
                    for f in tr:
                        training_files_created.append(f)

                if va:
                    for f in va:
                        validation_files_created.append(f)

                if te:
                    for f in te:
                        testing_files_created.append(f)

                total_sample_count += batch_counter
                batch_counter = 0
                output = []
                text_out = []
                batch_number += 1

        if len(output) > 0:

            output, text_out, testing_set, validation_set, testing_text, validation_text = \
                self.test_validation_splitter(output, text_out)

            training_sample_count += len(output)
            validation_sample_count += len(validation_set)
            testing_sample_count += len(testing_set)

            tr, va, te = self.save_tr_va_te_sets(output, text_out, validation_set, validation_text,
                                                 testing_set, testing_text, ds_folder, batch_number)

            if tr:
                for f in tr: training_files_created.append(f)

            if va:
                for f in va: validation_files_created.append(f)

            if te:
                for f in te: testing_files_created.append(f)

            total_sample_count += batch_counter

        # results.close()
        ds_name = "build_gen_ds_from_prompt_history"
        dataset_card = self.get_dataset_card(ds_name)

        dataset_dict = {"ds_type": dataset_card["dataset_name"],
                        "ds_id": ds_id,
                        "training_samples": training_sample_count,
                        "training_files": training_files_created,
                        "validation_samples": validation_sample_count,
                        "validation_files": validation_files_created,
                        "testing_samples": testing_sample_count,
                        "testing_files": testing_files_created,
                        "batches": batch_number + 1,
                        "prompt_wrapper": prompt_wrapper,
                        "description": dataset_card["description"],
                        "features": dataset_card["features"],
                        "time_stamp": str(Utilities().get_current_time_now())}

        # save dataset dict -> and put in ds folder
        json_dict = json.dumps(dataset_dict, indent=2)
        with open(os.path.join(ds_folder, "manifest.json"), "w", encoding='utf-8') as outfile:
            outfile.write(json_dict)

        return dataset_dict

    def build_visual_ds_image_labels (self, query=None, filter_dict=None, qr=None, custom_id=None):

        """ Generates a dataset by pairing images extracted from parsed documents, with nearby text that may
        serve as a 'label' or explanation of the image - experimental self-supervised dataset building
        technique - note that results will vary widely depending upon the nature and structure of the underlying
        source documents. """

        #   create specific folder for dataset artifacts inside library dataset path
        ds_id, ds_folder = self.issue_new_ds_id(custom_id=custom_id)

        if not qr:

            #   optional:  by passing query and/or filter_dict, allows targeted 'subset' of library to be used
            if not query and not filter_dict:

                # by default, will get only text and table entries, but no images (since text is duplicative)
                filter_list = ["image"]

                if self.library:
                    results = CollectionRetrieval(self.library_name,
                                                  account_name=self.account_name).filter_by_key_value_range("content_type",
                                                                                                 filter_list)
                else:
                    raise LibraryObjectNotFoundException("no-library-loaded-in-Dataset-constructor")

            else:
                # 'assert' content_type == image in filter_dict to only retrieve images
                filter_dict.update({"content_type": "image"})

                if self.library:
                    results = CollectionRetrieval(self.library_name, account_name=self.account_name). \
                        text_search_with_key_value_dict_filter(query, filter_dict)
                else:
                    raise LibraryObjectNotFoundException("no-library-loaded-in-Dataset-constructor")

        else:
            results = qr

        batch_counter = 0
        counter = 0
        output = []
        total_sample_count = 0
        training_sample_count = 0
        validation_sample_count = 0
        testing_sample_count = 0
        training_files_created = []
        validation_files_created = []
        testing_files_created = []
        text_out = []
        batch_number = 0

        for elements in results:
            text_long = elements["text"]
            text_short = elements["header_text"]
            doc_id = elements["doc_ID"]
            block_id = elements["block_ID"]
            file_name = elements["external_files"]

            if text_long or text_short:

                if len(text_long) > self.text_empty_min_threshold or len(text_short) > self.text_empty_min_threshold:

                    new_entry = {"sample_number": counter, "image_ref": file_name, "doc_ID": doc_id,
                                 "block_ID": block_id, "text_long": text_long, "text_short": text_short}

                    output.append(new_entry)
                    text_entry = text_long + self.separator + text_short
                    text_out.append(text_entry)

                    counter += 1
                    batch_counter += 1

            if batch_counter >= self.file_batch_size:

                output, text_out, testing_set, validation_set, testing_text, validation_text = \
                    self.test_validation_splitter(output, text_out)

                training_sample_count += len(output)
                validation_sample_count += len(validation_set)
                testing_sample_count += len(testing_set)

                tr, va, te = self.save_tr_va_te_sets(output, text_out, validation_set, validation_text,
                                                     testing_set, testing_text, ds_folder, batch_number)

                if tr:
                    for f in tr: training_files_created.append(f)

                if va:
                    for f in va: validation_files_created.append(f)

                if te:
                    for f in te: testing_files_created.append(f)

                total_sample_count += batch_counter

                batch_counter = 0
                output = []
                text_out = []
                batch_number += 1

        if len(output) > 0:

            output, text_out, testing_set, validation_set, testing_text, validation_text = \
                self.test_validation_splitter(output, text_out)

            training_sample_count += len(output)
            validation_sample_count += len(validation_set)
            testing_sample_count += len(testing_set)

            tr, va, te = self.save_tr_va_te_sets(output, text_out, validation_set, validation_text,
                                                 testing_set, testing_text, ds_folder, batch_number)

            if tr:
                for f in tr: training_files_created.append(f)

            if va:
                for f in va: validation_files_created.append(f)

            if te:
                for f in te: testing_files_created.append(f)

            total_sample_count += batch_counter

        # results.close()

        # need to package up images into zip folder
        ds_name = "build_visual_ds_image_labels"
        dataset_card = self.get_dataset_card(ds_name)

        dataset_dict = {"ds_type": dataset_card["dataset_name"],
                        "ds_id": ds_id,
                        "training_samples": training_sample_count,
                        "training_files": training_files_created,
                        "validation_samples": validation_sample_count,
                        "validation_files": validation_files_created,
                        "testing_samples": testing_sample_count,
                        "testing_files": testing_files_created,
                        "batches": batch_number + 1,
                        "description": dataset_card["description"],
                        "features": dataset_card["features"],
                        "time_stamp": str(Utilities().get_current_time_now())
                        }

        # save dataset dict -> and put in ds folder
        json_dict = json.dumps(dataset_dict, indent=2)
        with open(os.path.join(ds_folder, "manifest.json"), "w", encoding='utf-8') as outfile:
            outfile.write(json_dict)

        return dataset_dict

    def build_gen_ds_targeted_text_completion (self, prompt_wrapper="alpaca",
                                               query=None, filter_dict=None, qr=None, custom_id=None):

        """ Generates a targeted text completion from dataset. """

        #   create specific folder for dataset artifacts inside library dataset path
        ds_id, ds_folder = self.issue_new_ds_id(custom_id=custom_id)

        if not qr:

            #   optional:  by passing query and/or filter_dict, allows targeted 'subset' of library to be used
            if not query and not filter_dict:

                # by default, will get only text and table entries, but no images (since text is duplicative)
                filter_list = ["text", "table"]

                if self.library:
                    results = CollectionRetrieval(self.library.library_name,
                                                  account_name=self.library.account_name).filter_by_key_value_range("content_type",
                                                                                                 filter_list)
                else:
                    raise LibraryObjectNotFoundException("no-library-loaded-in-Dataset-constructor")
            else:

                if self.library:
                    results = CollectionRetrieval(self.library.library_name,
                                                  account_name=self.library.account_name).\
                        text_search_with_key_value_dict_filter(query, filter_dict)
                else:
                    raise LibraryObjectNotFoundException("no-library-loaded-in-Dataset-constructor")

        else:
            results = qr

        batch_number = 0
        training_files_created = []
        validation_files_created = []
        testing_files_created = []

        counter = 0
        batch_counter = 0
        training_sample_count = 0
        validation_sample_count = 0
        testing_sample_count = 0
        total_sample_count = 0
        text_sample = ""
        current_doc = -1
        min_tokens = 100
        max_tokens = 1000
        new_sample = ""
        text_out = []
        output = []

        for i, elements in enumerate(results):

            if i == 0:
                current_doc = elements["doc_ID"]
                text_sample = elements["text"]

            tok_count = self.token_counter(text_sample)

            # if in target range or if last sample in doc
            if min_tokens <= tok_count <= max_tokens or elements["doc_ID"] != current_doc:

                # split the sample
                text_tokens = self.tokenize_text(text_sample)
                tok_count = len(text_tokens)
                r = random.randint(0, tok_count-1)
                t1 = self.tokenizer.decode(text_tokens[0:r])
                t2 = self.tokenizer.decode(text_tokens[r:])

                if prompt_wrapper == "human_bot":
                    instruction = "Please read the following text, and provide a completion.\n" + t1
                    new_sample = self.package_human_bot_sample(instruction, t2)
                    features = ["text"]

                if prompt_wrapper == "alpaca":
                    instruction = "Please read the following text, and provide a completion.\n" + t1
                    new_sample = self.package_alpaca_sample(instruction, t2)
                    features = ["text"]

                if prompt_wrapper == "chat_gpt":
                    instruction = "Please read the following text, and provide a completion.\n" + t1
                    new_sample = self.package_chatgpt_sample(instruction, t2)
                    features = ["role", "text"]

                if prompt_wrapper == "dict" or not new_sample:
                    new_sample = {"sample_number": counter, "file_source": elements["file_source"],
                                  "text": t1,
                                  "completion": t2}
                    features = ["sample_number", "file_source", "text", "completion"]

                text_entry = t1 + self.separator + t2
                text_out.append(text_entry)

                output.append(new_sample)
                text_out.append(text_sample)
                counter += 1
                batch_counter += 1

                # edge case for i==0
                if i == 0:
                    text_sample = ""
                else:
                    # start fresh
                    text_sample = elements["text"]
                    current_doc = elements["doc_ID"]
            else:
                if tok_count <= min_tokens:
                    text_sample += " " + elements["text"]
                    tok_count = self.token_counter(text_sample)

                if tok_count >= max_tokens:

                    while tok_count > max_tokens:

                        tokens = self.tokenize_text(text_sample)
                        chopped = tokens[0:max_tokens]
                        remainder = tokens[max_tokens:]
                        remainder_text = self.tokenizer.decode(remainder)
                        chopped_text = self.tokenizer.decode(chopped)

                        smooth_stop = self._smooth_stopper(chopped_text,200)

                        new_text_sample = chopped_text[:smooth_stop]
                        new_remainder = chopped_text[smooth_stop:] + remainder_text

                        # split the sample
                        text_tokens = self.tokenize_text(text_sample)
                        tok_count = len(text_tokens)
                        r = random.randint(0, tok_count - 1)
                        t1 = self.tokenizer.decode(text_tokens[0:r])
                        t2 = self.tokenizer.decode(text_tokens[r:])

                        if prompt_wrapper == "human_bot":
                            instruction = "Please read the following text, and provide a completion.\n" + t1
                            new_sample = self.package_human_bot_sample(instruction, t2)
                            features = ["text"]

                        if prompt_wrapper == "alpaca":
                            instruction = "Please read the following text, and provide a completion.\n" + t1
                            new_sample = self.package_alpaca_sample(instruction, t2)
                            features = ["text"]

                        if prompt_wrapper == "chat_gpt":
                            instruction = "Please read the following text, and provide a completion.\n" + t1
                            new_sample = self.package_chatgpt_sample(instruction, t2)
                            features = ["role", "text"]

                        if prompt_wrapper == "dict" or not new_sample:
                            new_sample = {"sample_number": counter, "file_source": elements["file_source"],
                                          "text": t1,
                                          "completion": t2}
                            features = ["sample_number", "file_source", "text", "completion"]

                        text_sample = t1 + "\n" + t2
                        output.append(new_sample)
                        text_out.append(text_sample)
                        counter += 1
                        batch_counter += 1
                        text_sample = new_remainder
                        tok_count = self.token_counter(text_sample)

            # pick up last remaining sample, if any
            if len(text_sample) > 0:

                # split the sample
                text_tokens = self.tokenize_text(text_sample)
                tok_count = len(text_tokens)
                r = random.randint(0, tok_count - 1)
                t1 = self.tokenizer.decode(text_tokens[0:r])
                t2 = self.tokenizer.decode(text_tokens[r:])

                if prompt_wrapper == "human_bot":
                    instruction = "Please read the following text, and provide a completion.\n" + t1
                    new_sample = self.package_human_bot_sample(instruction, t2)
                    features = ["text"]

                if prompt_wrapper == "alpaca":
                    instruction = "Please read the following text, and provide a completion.\n" + t1
                    new_sample = self.package_alpaca_sample(instruction, t2)
                    features = ["text"]

                if prompt_wrapper == "chat_gpt":
                    instruction = "Please read the following text, and provide a completion.\n" + t1
                    new_sample = self.package_chatgpt_sample(instruction, t2)
                    features = ["role", "text"]

                if prompt_wrapper == "dict" or not new_sample:
                    new_sample = {"sample_number": counter, "file_source": elements["file_source"],
                                  "text": t1,
                                  "completion": t2}
                    features = ["sample_number", "file_source", "text", "completion"]

                #   replacing "doc_ID" | current_doc
                text_sample = t1 + "\n" + t2
                output.append(new_sample)
                text_out.append(text_sample)
                counter += 1
                batch_counter += 1

            if batch_counter >= self.file_batch_size:
                # write samples to file + start new batch

                output, text_out, testing_set, validation_set, testing_text, validation_text = \
                    self.test_validation_splitter(output, text_out)

                training_sample_count += len(output)
                validation_sample_count += len(validation_set)
                testing_sample_count += len(testing_set)

                tr, va, te = self.save_tr_va_te_sets(output, text_out, validation_set, validation_text,
                                                     testing_set, testing_text, ds_folder, batch_number)

                if tr:
                    for f in tr:
                        training_files_created.append(f)

                if va:
                    for f in va:
                        validation_files_created.append(f)

                if te:
                    for f in te:
                        testing_files_created.append(f)

                batch_number += 1
                total_sample_count += len(output)
                total_sample_count += len(validation_set)
                total_sample_count += len(testing_set)
                output = []
                text_out = []
                batch_counter = 0

        if len(output) > 0:

            output, text_out, testing_set, validation_set, testing_text, validation_text = \
                self.test_validation_splitter(output, text_out)

            training_sample_count += len(output)
            validation_sample_count += len(validation_set)
            testing_sample_count += len(testing_set)

            tr, va, te = self.save_tr_va_te_sets(output, text_out, validation_set, validation_text,
                                                 testing_set, testing_text, ds_folder, batch_number)

            if tr:
                for f in tr:
                    training_files_created.append(f)

            if va:
                for f in va:
                    validation_files_created.append(f)

            if te:
                for f in te:
                    testing_files_created.append(f)

            total_sample_count += len(output)
            total_sample_count += len(validation_set)
            total_sample_count += len(testing_set)

        ds_name = "build_gen_ds_targeted_text_completion"
        dataset_card = self.get_dataset_card(ds_name)

        dataset_dict = {"ds_type": dataset_card["dataset_name"],
                        "ds_id": ds_id,
                        "training_samples": training_sample_count,
                        "training_files": training_files_created,
                        "validation_samples": validation_sample_count,
                        "validation_files": validation_files_created,
                        "testing_samples": testing_sample_count,
                        "testing_files": testing_files_created,
                        "batches": batch_number + 1,
                        "description": dataset_card["description"],
                        "features": dataset_card["features"],
                        "time_stamp": str(Utilities().get_current_time_now())}

        # save dataset dict -> and put in ds folder
        json_dict = json.dumps(dataset_dict, indent=2)
        with open(os.path.join(ds_folder, "manifest.json"), "w", encoding='utf-8') as outfile:
            outfile.write(json_dict)

        return dataset_dict

    def test_validation_splitter(self, output, text_out):

        """ Splits the datasets into testing and validation sets. """

        # 100% training with no validation and testing split option
        if self.validation_split == 0.0 and self.testing_split == 0.0:
            return output, text_out, [], [], [], []

        validation_count = int(self.validation_split * len(output))
        testing_count = int(self.testing_split * len(output))

        output_new = []
        text_out_new = []
        testing_set = []
        validation_set = []
        testing_text = []
        validation_text = []

        random_samples_list = []
        first_entry = random.randint(0, len(output) - 1)
        random_samples_list.append(first_entry)

        for x in range(1, validation_count + testing_count):
            i = first_entry
            while i in random_samples_list:
                i = random.randint(0, len(output) - 1)
            random_samples_list.append(i)

        validation_adder = 0
        for x in range(0, len(output)):
            if x not in random_samples_list:
                # keep in training set
                output_new.append(output[x])
                text_out_new.append(text_out[x])
            else:
                # put in either validation or testing set
                if validation_adder < validation_count:
                    # fill up validation first
                    validation_set.append(output[x])
                    validation_text.append(text_out[x])
                    validation_adder += 1
                else:
                    # once validation set filled, then build testing set
                    testing_set.append(output[x])
                    testing_text.append(text_out[x])

        return output_new, text_out_new, testing_set, validation_set, testing_text, validation_text

    def save_tr_va_te_sets(self, tr_output, tr_text, va_output, va_text, te_output, te_text, ds_folder, batch_number):

        """ Saves the generated datasets into files. """

        training_files_created = []
        validation_files_created = []
        testing_files_created = []

        # save training files
        json_batch = self.training_sample_file_name_base + "_{}.jsonl".format(str(batch_number))
        with open(os.path.join(ds_folder,json_batch), "w", encoding='utf-8') as outfile:
            for i, sample_dict in enumerate(tr_output):
                jsonl_row = json.dumps(sample_dict)
                outfile.write(jsonl_row)
                outfile.write("\n")

        outfile.close()

        training_files_created.append(json_batch)

        # save validation set

        if len(va_output) > 0:

            new_json_batch = self.validation_sample_file_name_base + "_{}.jsonl".format(str(batch_number))
            with open(os.path.join(ds_folder,new_json_batch), "w", encoding='utf-8') as outfile:
                for i, sample_dict in enumerate(va_output):
                    jsonl_row = json.dumps(sample_dict)
                    outfile.write(jsonl_row)
                    outfile.write("\n")

            outfile.close()

            validation_files_created.append(new_json_batch)

        # save testing set

        if len(te_output) > 0:

            new_json_batch = self.testing_sample_file_name_base + "_{}.jsonl".format(str(batch_number))
            with open(os.path.join(ds_folder,new_json_batch), "w", encoding='utf-8') as outfile:

                for i, sample_dict in enumerate(te_output):
                    jsonl_row = json.dumps(sample_dict)
                    outfile.write(jsonl_row)
                    outfile.write("\n")

            outfile.close()

            testing_files_created.append(new_json_batch)

        # save text only version for easy access
        new_txt_batch = self.training_sample_file_name_base + "_text_{}.txt".format(str(batch_number))
        t = open(os.path.join(ds_folder,new_txt_batch), 'w', encoding='utf-8')
        for x in range(0, len(tr_text)):
            t.write((str(tr_text[x]) + "\n"))
        t.close()

        training_files_created.append(new_txt_batch)

        # save validation text only version for easy access

        if len(va_text) > 0:
            new_txt_batch = self.validation_sample_file_name_base + "_text_{}.txt".format(str(batch_number))
            t = open(os.path.join(ds_folder,new_txt_batch), 'w', encoding='utf-8')
            for x in range(0, len(va_text)):
                t.write((str(va_text[x]) + "\n"))
            t.close()

            validation_files_created.append(new_txt_batch)

        # save testing text only version for easy access

        if len(te_text) > 0:
            new_txt_batch = self.testing_sample_file_name_base + "_text_{}.txt".format(str(batch_number))
            t = open(os.path.join(ds_folder,new_txt_batch), 'w', encoding='utf-8')
            for x in range(0, len(te_text)):
                t.write((str(te_text[x]) + "\n"))
            t.close()

            testing_files_created.append(new_txt_batch)

        return training_files_created, validation_files_created, testing_files_created

    # not connected yet - will evaluate further
    def _create_image_zip(self, image_list, ds_path):

        zip_name = os.path.join(ds_path, "image.zip")
        ds_folder = self.library.image_path

        with ZipFile(zip_name, 'w') as ZipF:
            for f in image_list:
                ZipF.write(ds_folder + f, f, compress_type=ZIP_DEFLATED)

        ZipF.close()

        return zip_name

    def _smooth_stopper(self, text_chunk, look_back_range):

        """ Implementation of text chunking as an internal utility to help 'chop' datasets along with
        preferred token sizes with relatively smooth truncations. """

        # default case is to return the whole text sample as single chunk
        smooth_stop = len(text_chunk)

        # look back is the full range that will be reviewed to find proper stopping point
        if len(text_chunk) > look_back_range:
            look_back = len(text_chunk) - look_back_range
        else:
            look_back = 0

        # best case - look for a period
        found_period = -1
        for x in range(len(text_chunk)-1,look_back,-1):

            # found a period followed by white space marker (space, \n, \r) - best case
            if ord(text_chunk[x]) == 46:

                # first confirm that '.' is followed by white space or is the end of the text
                if x+1 == len(text_chunk) or ord(text_chunk[x + 1]) in [32, 13, 10]:

                    # exclude 'several edge cases where '.' is not a reliable sentence end
                    short_window = text_chunk[x-5:x-1]

                    # (A) first edge case - "two periods close to each other", e.g., "x.y."
                    if "." not in short_window:

                        # (B) second edge case - "period after number in list", e.g., "point 2."
                        if not 47 < ord(short_window[-1]) < 58:

                            # (C) third edge case - common abbreviations
                            if short_window[:-2] != "Mr" and short_window[:3] != "Mrs" and short_window[:2] != "Dr":

                                # if none of (A) - (B) - (C) or apply, then consider period valid stopping point
                                found_period = x + 1
                                break

            # alternate solid stopper is presence of \n\n | \n\r | \r\r -> usually marks a section/para end
            if ord(text_chunk[x]) in [10,13]:
                if x+1 == len(text_chunk) or ord(text_chunk[x+1]) in [10,13]:
                    found_period = x+1
                    break

        # if found a period, then smooth stop is the char right after the period
        if found_period > - 1:
            smooth_stop = found_period

        else:
            # if no period found, then next best case is to look for whitespace between words
            for y in range(len(text_chunk) - 1, look_back,-1):

                # look for a white space separator
                if ord(text_chunk[y]) in [32, 13, 10]:
                    smooth_stop = y
                    break

        # if no period or white space found, then return the original stopper

        return smooth_stop

