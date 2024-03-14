
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

"""The util module implements general helper functions with the Utilities class, and more specialized
 other classes.

Among the more specializes other classes is whole word tokenizer with CorpTokenizer, and statistical
NLP functions to calculate relationships between key words and concepts in a library.
"""


import csv
from collections import Counter
import sys
import os
import random
import urllib.parse
import platform
import sysconfig
from pathlib import Path
# from PIL import Image
import json
from zipfile import ZipFile, ZIP_DEFLATED
import numpy as np
import re
from tokenizers import Tokenizer
from datetime import datetime
import time
from ctypes import *
import logging
import requests
import uuid

try:
    from word2number import w2n
except ImportError:
    pass

try:
    from wikipediaapi import Wikipedia, ExtractFormat
except ImportError:
    pass

try:
    import yfinance
except ImportError:
    pass

from llmware.resources import CollectionRetrieval, PromptState, CloudBucketManager
from llmware.configs import LLMWareConfig
from llmware.exceptions import ModelNotFoundException, DependencyNotInstalledException, \
    FilePathDoesNotExistException, LibraryObjectNotFoundException, DatasetTypeNotFoundException, \
    ModuleNotFoundException


class Utilities:

    """ Utility functions used throughout LLMWare """

    def __init__(self, library=None):
        self.start = 0
        self.library = library

    def get_module_graph_functions(self):

        #   * C Utility functions *
        # Load shared libraries based on current platform/architecture

        # Best ways we've found to detect machine architecture
        if platform.system() == "Windows":
            system = "windows"
            machine = "x86_64"
            file_ext = ".dll"
        else:
            system = platform.system().lower()
            machine = os.uname().machine.lower()
            file_ext = ".so"

        # Default to known architectures if we encounter an unknown one
        if system == 'darwin' and machine not in ['arm64', 'x86_64']:
            machine = 'arm64'
        if system == 'linux' and machine not in ['aarch64', 'x86_64']:
            machine = 'x86_64'

        # Construct the path to a specific lib folder.  Eg. .../llmware/lib/darwin/x86_64
        machine_dependent_lib_path = os.path.join(LLMWareConfig.get_config("shared_lib_path"), system, machine)

        # replace for local testing:  file_ext -> .dylib
        _path_graph = os.path.join(machine_dependent_lib_path, "llmware", "libgraph_llmware" + file_ext)

        _mod_utility = None

        try:
            _mod_utility = cdll.LoadLibrary(_path_graph)
        except:
            logging.warning("warning: Module 'Graph Processor' could not be loaded from path - \n %s.\n",
                            _path_graph)

        if not _mod_utility:
            raise ModuleNotFoundException("Graph Processor")

        return _mod_utility

    def get_module_pdf_parser(self):

        # Best ways we've found to detect machine architecture
        if platform.system() == "Windows":
            system = "windows"
            machine = "x86_64"
            file_ext = ".dll"
        else:
            system = platform.system().lower()
            machine = os.uname().machine.lower()
            file_ext = ".so"

        # Default to known architectures if we encounter an unknown one
        if system == 'darwin' and machine not in ['arm64', 'x86_64']:
            machine = 'arm64'
        if system == 'linux' and machine not in ['aarch64', 'x86_64']:
            machine = 'x86_64'

        # Construct the path to a specific lib folder.  Eg. .../llmware/lib/darwin/x86_64
        machine_dependent_lib_path = os.path.join(LLMWareConfig.get_config("shared_lib_path"), system, machine)

        # shift to file_ext
        _path_pdf = os.path.join(machine_dependent_lib_path, "llmware", "libpdf_llmware" + file_ext)

        _mod_pdf = None

        try:
            # attempt to load the shared library with ctypes
            _mod_pdf = cdll.LoadLibrary(_path_pdf)

        except:
            # catch error, if possible
            logging.warning("warning: Module 'PDF Parser' could not be loaded from path - \n %s.\n",
                            _path_pdf)

        #   if no module loaded, then raise exception
        if not _mod_pdf:
            raise ModuleNotFoundException("PDF Parser")

        return _mod_pdf

    def get_module_office_parser(self):

        # Best ways we've found to detect machine architecture
        if platform.system() == "Windows":
            system = "windows"
            machine = "x86_64"
            file_ext = ".dll"
        else:
            system = platform.system().lower()
            machine = os.uname().machine.lower()
            file_ext = ".so"

        # Default to known architectures if we encounter an unknown one
        if system == 'darwin' and machine not in ['arm64', 'x86_64']:
            machine = 'arm64'
        if system == 'linux' and machine not in ['aarch64', 'x86_64']:
            machine = 'x86_64'

        # Construct the path to a specific lib folder.  Eg. .../llmware/lib/darwin/x86_64
        machine_dependent_lib_path = os.path.join(LLMWareConfig.get_config("shared_lib_path"), system, machine)

        _path_office = os.path.join(machine_dependent_lib_path, "llmware", "liboffice_llmware" + file_ext)

        _mod = None

        try:
            # attempt to load the shared library with ctypes
            _mod = cdll.LoadLibrary(_path_office)

        except:

            # catch the error, if possible
            logging.warning("warning: Module 'Office Parser' could not be loaded from path - \n %s.\n",
                            _path_office)

        # if no module loaded, then raise exception
        if not _mod:
            raise ModuleNotFoundException("Office Parser")

        return _mod

    def get_default_tokenizer(self):

        # gpt2 tokenizer is used in several places as a default tokenizer

        # check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):

            # if not explicitly set up by user, then create folder directory structure
            LLMWareConfig.setup_llmware_workspace()

        # first, check if it is in the local repo
        local_model_repo = LLMWareConfig.get_model_repo_path()
        models = os.listdir(local_model_repo)

        if "gpt2" not in models:

            #   if not found locally, then pull from global repo

            logging.info("update: gpt2 tokenizer used as default - not in local model repository, so pulling "
                            "from global repo - this may take a few seconds the first time to download.")

            files = CloudBucketManager().pull_single_model_from_llmware_public_repo(model_name="gpt2")

            #   quick check to confirm that model is present
            models = os.listdir(local_model_repo)
            if "gpt2" not in models:
                raise ModelNotFoundException("gpt2_tokenizer")

        tokenizer = Tokenizer.from_file(os.path.join(local_model_repo, "gpt2", "tokenizer.json"))

        return tokenizer

    def load_tokenizer_from_file(self, fp):
        tokenizer = Tokenizer.from_file(fp)
        return tokenizer

    def get_uuid(self):
        # uses unique id creator from uuid library
        return uuid.uuid4()

    @staticmethod
    def file_save (cfile, file_path, file_name):

        max_csv_size = 20000
        csv.field_size_limit(max_csv_size)

        out_file = os.path.join(file_path, file_name)

        with open(out_file, 'w', newline='') as csvfile:
            c = csv.writer(csvfile, dialect='excel', doublequote=False, delimiter=',',escapechar = ']')

            for z in range(0, len(cfile)):
                # intercept a line too large here
                if sys.getsizeof(cfile[z]) < max_csv_size:
                    c.writerow(cfile[z])
                else:
                    logging.error("error:  CSV ERROR:   Row exceeds MAX SIZE: %s %s", sys.getsizeof(cfile[z])
                                  ,cfile[z])

        csvfile.close()

        return 0

    @staticmethod
    def file_load (in_path):
        record_file = open(in_path, encoding='ISO-8859-1')
        c = csv.reader(record_file, dialect='excel', doublequote=False, delimiter=',')
        output = []
        for lines in c:
            output.append(lines)
        record_file.close()

        return output

    @staticmethod
    def csv_save(rows, file_dir, file_name):

        full_path = Path(file_dir, file_name)

        with full_path.open('w', encoding='utf-8') as out:
            writer = csv.writer(out)
            try:
                writer.writerows(rows)
            except csv.Error as e:
                logging.exception("Exception writing csv file")
                return False

        return True

    @staticmethod
    def get_top_bigrams (tokens, top_n):

        bigrams = []
        for z in range(1, len(tokens)):
            entry = (tokens[z-1] + "_" + tokens[z])
            bigrams.append(entry)

        d = Counter(bigrams)
        dc = d.most_common(top_n)

        return dc

    @staticmethod
    def get_top_trigrams (tokens, top_n):

        trigrams = []
        for z in range(2 ,len(tokens)):
            entry = (tokens[ z -2] + "_" + tokens[ z -1] + "_" + tokens[z])
            trigrams.append(entry)

        d = Counter(trigrams)
        dc = d.most_common(top_n)

        return dc

    @staticmethod
    def get_top_4grams (tokens, top_n):

        four_grams = []
        for z in range(3 ,len(tokens)):
            entry = (tokens[ z -3 ]+ "_" + tokens[ z -2] + "_" + tokens[ z -1] + "_" + tokens[z])
            four_grams.append(entry)

        d = Counter(four_grams)
        dc = d.most_common(top_n)

        return dc

    @staticmethod
    def compare_timestamps (t1, t2, time_str="%a %b %d %H:%M:%S %Y"):

        t1_obj = datetime.strptime(t1, time_str)
        t2_obj = datetime.strptime(t2, time_str)

        time_delta_obj = t1_obj - t2_obj

        days = time_delta_obj.days
        seconds = time_delta_obj.seconds

        return time_delta_obj, days, seconds

    @staticmethod
    def get_current_time_now (time_str="%a %b %e %H:%M:%S %Y"):

        #   if time stamp is used in file_name, needs to be Windows standards compliant
        if platform.system() == "Windows":
            time_str = "%Y-%m-%d_%H%M%S"

        return datetime.now().strftime(time_str)

    @staticmethod
    def get_time_string_standard():
        time_str_standard = "%a %b %e %H:%M:%S %Y"
        return time_str_standard

    @staticmethod
    def isfloat(num):
        try:
            float(num)
            return True
        except ValueError:
            return False

    @staticmethod
    def prep_filename_alt(filename_in, accepted_file_formats_list):

        success_code = 1

        fn_toks = filename_in.split(".")
        fn_base = fn_toks[0]
        ext = fn_toks[-1]

        # only accept upload files with file extension in accepted_file_formats_list
        if ext.lower() in accepted_file_formats_list and not filename_in.startswith("."):

            # prepend a random number to the front of the secure filename

            if len(fn_base) > 240:
                # cap len of filename at 240
                filename_in = fn_base[0:240] + "." + ext

            fn_out = str(random.randint(100000, 999999)) + "_" + filename_in

        else:
            success_code = -1
            fn_out = filename_in

        return success_code, fn_out

    @staticmethod
    def safe_url(string):

        try:
            return urllib.parse.quote_plus(string)
        except TypeError:
            logging.exception("Error encoding string (%s)", string)
            return ""

    @staticmethod
    def get_stop_words_master_list():

        stop_words = ["a", "able", "about","above","accordance","according", "accordingly","across","act","actually",
                      "added" ,"adj" ,"affected" ,"affecting" ,"affects" ,"after" ,"afterwards" ,"again" ,"against",
                      "ah","al" ,"all", "almost" ,"alone" ,"along" ,"already", "also" ,"although" ,"always" ,"am" ,
                      "among" ,"amongst" ,"an","and","announce" ,"another" ,"any" ,"anybody" ,"anyhow" ,"anymore" ,
                      "anyone" ,"anything" ,"anyway","anyways","anywhere" ,"apparently" ,"approximately" ,"are" ,
                      "aren" ,"arent" ,"arise", "around", "as" ,"aside", "ask", "asked" ,"asking" ,"at" ,"auth",
                      "available" ,"away" ,"awfully" ,"b" ,"back", "basically" ,"be", "became" ,"because",
                      "become" ,"becomes", "becoming" ,"been", "before" ,"beforehand", "begin", "beginning" ,"beginnings",
                      "begins" ,"behind" ,"being" ,"believe" ,"below" ,"beside" ,"besides" ,"between" ,"beyond", "biol"
                      ,"both", "brief" ,"briefly" ,"but" ,"by" ,"c" ,"ca" ,"came" ,"can" ,"cannot" ,"can't" ,"cant" ,"cause"
                      ,"causes", "certain" ,"certainly" ,"co" ,"com" ,"come" ,"comes" ,"contain" ,"containing" ,"contains",
                      "could","couldnt", "d" ,"date" ,"did" ,"didnt" ,"didn't", "different" ,"do" ,"does" ,"doesn't",
                      "doesnt" ,"doing","done","don't" ,"dont" ,"down" ,"downwards" ,"due" ,"during" ,"e" ,"each" ,
                      "ed","edu","effect","eg","e.g." ,"eight", "eighty" ,"either" ,"else" ,"elsewhere" ,"end" ,
                      "ending" ,"enough" ,"especially" ,"et" ,"etal" ,"etc" ,"even","ever" ,"every" ,"everybody",
                      "everyone" ,"everything" ,"everywhere" ,"ex" ,"except" ,"f" ,"far" ,"few" ,"ff", "fifth",
                      "first" ,"five" ,"fix" ,"followed" ,"following" ,"follows" ,"for" ,"former" ,"formerly","forth",
                      "found" ,"four" ,"from" ,"further" ,"furthermore" ,"g" ,"gave" ,"generally" ,"get" ,"gets" ,"getting"
                      ,"give" ,"given", "gives" ,"giving" ,"go" ,"goes" ,"gone" ,"got" ,"gotten" ,"h" ,"had" ,"happens",
                      "hardly" ,"has","hasn't","have" ,"haven't" ,"having" ,"he" ,"hed" ,"hence" ,"her" ,"here",
                      "hereafter" ,"hereby" ,"herein","heres", "here's" ,"hereupon" ,"hers" ,"herself" ,"hes" ,"he's",
                      "hi" ,"hid" ,"him" ,"himself" ,"his" ,"hither" ,"home", "how" ,"howbeit" ,"however" ,"hundred",
                      "i" ,"id" ,"ie" ,"i.e." ,"if" ,"i'll" ,"ill" ,"im" ,"i'm" ,"immediate", "immediately" ,"importance",
                      "important" ,"in" ,"inc" ,"inc." ,"indeed" ,"index" ,"information","instead", "into",
                      "invention","inward" ,"is" ,"isn't" ,"isnt" ,"it" ,"itd" ,"it'll","its","it's" ,"itself"
                      ,"i've" ,"ive" ,"j", "just" ,"k" ,"keep" ,"keeps" ,"kept" ,"kg" ,"km" ,"know","known","knows",
                      "l","largely","last","lately", "later","latter","latterly","least","less","lest","let","lets",
                      "let's" ,"like" ,"liked","likely", "line" ,"little" ,"'ll" ,"look" ,"looking" ,"looks",
                      "ltd" ,"m" ,"made" ,"mainly" ,"make" ,"makes","many", "may" ,"maybe" ,"me" ,"mean" ,"means" ,
                      "meantime" ,"meanwhile" ,"merely" ,"mg" ,"might" ,"million","miss", "ml" ,"more" ,"moreover",
                      "most" ,"mostly" ,"mr" ,"mr." ,"mrs" ,"mrs." ,"ms", "ms." ,"much" ,"mug","must" ,"my" ,"myself",
                      "n" ,"na" ,"name" ,"namely" ,"nay" ,"nd" ,"near" ,"nearly" ,"necessarily" ,"necessary" ,"need"
                      ,"needs", "neither" ,"never""nevertheless" ,"new" ,"next" ,"nine" ,"ninety" ,"no" ,"nobody",
                      "non" ,"none","nonetheless","noone" ,"nor" ,"normally" ,"nos" ,"not" ,"note" ,"noted" ,
                      "nothing" ,"now" ,"nowhere" ,"o" ,"obtain","obtained", "obviously" ,"of" ,"off" ,"often",
                      "oh" ,"ok" ,"okay" ,"old" ,"omit" ,"omitted" ,"on" ,"once" ,"one","ones","only" ,"onto" ,"or",
                      "ord" ,"other" ,"others" ,"otherwise" ,"ought" ,"our" ,"ours" ,"ourselves","out",
                      "outside" ,"over" ,"overall" ,"owing" ,"own" ,"p" ,"page" ,"pages" ,"part" ,"particular"
                      ,"particularly", "past" ,"per" ,"perhaps" ,"placed" ,"please" ,"plus" ,"poorly" ,"possible",
                      "possibly" ,"potentially","pp","predominantly" ,"present" ,"previously" ,"primarily","probably",
                      "promptly" ,"proud" ,"provide", "provides" ,"put" ,"q" ,"que" ,"quickly" ,"quite" ,"qv" ,
                      "r" ,"ran" ,"rather" ,"rd" ,"re" ,"readily","really","recent" ,"recently" ,"ref" ,"refs",
                      "regarding" ,"regardless" ,"regards" ,"regard" ,"related","relative", "relatively" ,
                      "research","respectively" ,"resulted" ,"resulting" ,"results" ,"right" ,"run" ,"s","said",
                      "same" ,"saw" ,"say" ,"saying" ,"says" ,"see" ,"seeing" ,"seem" ,"seemed","seeming","seems",
                      "seen" ,"self","selves" ,"sent" ,"seven" ,"several" ,"shall" ,"she" ,"shed" ,"she'll" ,"shes",
                      "she's" ,"should","shouldn't", "shouldnt" ,"show" ,"showed" ,"shown" ,"showns" ,"shows" ,
                      "significant" ,"significantly" ,"similar", "similarly" ,"since" ,"six" ,"slightly" ,"so" ,
                      "some" ,"somebody" ,"somehow" ,"someone" ,"somethan","something" ,"sometime" ,"sometimes" ,
                      "somewhat" ,"somewhere" ,"soon" ,"sorry" ,"specifically","specified", "specify" ,
                      "specifying" ,"still" ,"stop" ,"strongly" ,"sub" ,"substantially" ,"successfully" ,"such",
                      "sufficiently" ,"suggest" ,"sup" ,"sure" ,"t" ,"take" ,"taken" ,"taking" ,"talk" ,
                      "talked" ,"td","tell" ,"tends" ,"th" ,"than", "thank" ,"thanks" ,"thanx" ,"that" ,"that'll" ,
                      "thats" ,"that've" ,"the" ,"their" ,"theirs" ,"them", "themselves" ,"then" ,"thence" ,
                      "there" ,"thereafter", "thereby" ,"thered" ,"therefore" ,"therein","there'll" ,"thereof",
                      "therere" ,"theres" ,"thereto" ,"thereupon" ,"there've" ,"these", "they",
                      "theyd" ,"they'll" ,"theyre" ,"they've" ,"think" ,"this" ,"those" ,"thou" ,"though" ,"thoughh"
                      ,"thousand", "throug" ,"through" ,"throughout" ,"thru" ,"thus" ,"til" ,"tip" ,"to" ,
                      "together" ,"too" ,"took","toward","towards" ,"tr" ,"tried" ,"tries" ,"truly" ,"try" ,
                      "trying" ,"ts" ,"twice" ,"two", "u" ,"un" ,"under", "unfortunately" ,"unless" ,"unlike" ,
                      "unlikely" ,"until" ,"unto" ,"up" ,"upon" ,"ups" ,"us" ,"use","used","useful",
                      "usefully" ,"usefulness" ,"uses" ,"using" ,"usually" ,"v" ,"value" ,"various" ,"ve" ,"very"
                      ,"via","viz" ,"vol" ,"vols" ,"vs" ,"w" ,"want" ,"wants" ,"was" ,"wasnt" ,"way" ,
                      "we" ,"wed" ,"welcome","well" ,"we'll" ,"went","were" ,"werent" ,"we've" ,"what" ,"whatever",
                      "what'll" ,"whats" ,"when" ,"whence" ,"whenever","where","whereafter", "whereas",
                      "whereby" ,"wherein" ,"wheres" ,"whereupon" ,"wherever" ,"whether" ,"which",
                      "while" ,"whim" ,"whither" ,"who" ,"whod" ,"whoever" ,"whole" ,"who'll" ,"whom","whomever","whos"
                      ,"whose", "why" ,"widely" ,"willing" ,"will" ,"wish" ,"with" ,"within" ,"without","wont",
                      "words" ,"world" ,"would" ,"wouldnt","www" ,"x" ,"xx" ,"xxx", "y" ,"yes" ,"yet" ,
                      "you" ,"youd" ,"you'll" ,"your" ,"youre" ,"yours" ,"yourself","yourselves" ,"you've" ,"z",
                      "zero" ,"xoxo", "ii", "iii", "iv" ,"ix" ,"vi" ,"vii" ,"viii" ,"<th>",
                      "<tr>" ,"three" ,"ten" ,"view" ,"met" ,"follow" ,"consist" ,"lack" ,"lacks" ,"base" ,"based" ,"ago",
                      "addition" ,"additional" ,"depend" ,"depends" ,"include" ,"includes" ,"including" ,"continue"
                      ,"bring", "brings" ,"ahead" ,"add" ,"adds" ,"attribute" ,"attributes" ,"associated" ,"associate", "follow",
                      "happen" ,"happened" ,"happening" ,"single" ,"consider" ,"considered" ,"looked" ,"involve"
                      ,"involves", "involved" ,"thing" ,"things" ,"going", "brought", "lot"]

        return stop_words

    def load_stop_words_list (self, library_fp):

        stop_words = self.get_stop_words_master_list()

        s = open(os.path.join(library_fp, "stop_words_list.txt"), "w", encoding='utf-8')

        for words in stop_words:
            s.write((words + ","))
        s.close()
        os.chmod((library_fp+ "stop_words_list.txt"), 0o777)

        return stop_words

    def remove_stop_words(self, token_list):
        stop_words = self.get_stop_words_master_list()

        tokens_out = []
        for z in range(0, len(token_list)):
            if token_list[z] not in stop_words:
                tokens_out.append(token_list[z])

        return tokens_out

    # used by CorpTokenizer
    @staticmethod
    def clean_list (token_list):

        punctuation = ("-" ,"," ,"'", "/" ,"(')", "'('" ,":" ,".", "?" ,"%", "[", "]" ,"(')'" ,"('('" ,"'–'")
        clean_out = []
        for z in range(0 ,len(token_list)):
            t = token_list[z]
            clean_word = ""
            for y in range(0 ,len(t)):
                if t[y] in punctuation:
                    if len(clean_word) == len(t) -1:
                        # if last letter in word, then skip, no additional space added
                        char_out = ""
                    else:
                        char_out = ""
                else:
                    char_out = t[y]
                clean_word += char_out

            if clean_word != "":
                clean_out.append(clean_word)

        return clean_out

    def sentence_splitter(self, sentence, key_word, marker_list):

        text = []
        completion = []
        # will split sentence either 'before' or 'after' the marker
        # simplest pattern - split at marker

        for m in marker_list:

            # if key_word is at the start of the sentence, e.g., marker = 0, include in text ...
            if m < len(key_word):
                text.append(sentence[0:m+len(key_word)])
                completion.append(sentence[m+len(key_word):])
            else:
                text.append(sentence[0:m])
                completion.append(sentence[m:])

        return text, completion

    def prep_custom_mlm_label (self, input_sentence,key_word_list, mask_token_value="<mask>", mlm_prob=0.15):

        label_id = []
        for x in input_sentence:
            r = random.randint(1,100)
            if r <= (mlm_prob * 100):
                r2 = random.randint(1,10)
                if r2 <= 10:
                    label_id.append(mask_token_value)
            else:
                # keep original value
                label_id.append(x)

        return label_id

    def fast_search_dicts(self, query,output_dicts, text_key="text", remove_stop_words=True):

        #   will return a subset of the output_dicts that have the key_terms
        #   no ranking or prioritization - "match" or "no-match" only
        #   designed primarily to filter in-memory sources and parser outputs

        matched_dicts = []

        c = CorpTokenizer(remove_stop_words=remove_stop_words, remove_numbers=False, one_letter_removal=True,
                          remove_punctuation=True)

        key_terms = c.tokenize(query)

        # handle edge case - if empty search result, then return all dicts with updated keys
        if len(key_terms) == 0:
            for i, entries in enumerate(output_dicts):
                if "page_num" not in entries:
                    if "master_index" in entries:
                        page_num = entries["master_index"]
                    else:
                        page_num = 0
                    entries.update({"page_num": page_num})
                if "query" not in entries:
                    entries.update({"query": ""})
                matched_dicts.append(entries)
            return matched_dicts

        # len of key_terms >= 1 -> initiate key term match search
        for i, entries in enumerate(output_dicts):

            text_tokens = c.tokenize(entries[text_key])

            for j, toks in enumerate(text_tokens):
                match_found = 0
                if toks.lower() == key_terms[0].lower():
                    match_found += 1

                    if len(key_terms) > 1:
                        if len(text_tokens) > (j + len(key_terms)):
                            for x in range(1,len(key_terms)):
                                if text_tokens[j+x].lower() == key_terms[x].lower():
                                    match_found += 1
                                else:
                                    match_found = 0
                                    break

                    if match_found == len(key_terms):
                        # found confirmed match

                        if "page_num" not in entries:

                            if "master_index" in entries:
                                page_num = entries["master_index"]
                            else:
                                page_num = 0

                            entries.update({"page_num": page_num})

                        if "query" not in entries:
                            entries.update({"query": query})

                        matched_dicts.append(entries)
                        break

        return matched_dicts
        
    def find_match(self, key_term, sentence):

        matches_found = []
        for x in range(0,len(sentence)):
            match = 0
            if sentence[x].lower() == key_term[0].lower():
                match += 1
                if (x+len(key_term)) <= len(sentence):
                    for y in range(1,len(key_term)):
                        if key_term[y].lower() == sentence[x+y].lower():
                            match += 1
                        else:
                            match = -1
                            break

                    if match == len(key_term):
                        matches_found.append(x)

        return matches_found

    def package_answer(self, raw_query, text_core, answer_window, x):

        answer = []
        l = len(text_core)

        for t in range(0, l):
            match = 0
            if text_core[t].lower() == raw_query[0].lower():
                if (t + len(raw_query)) < l:
                    for z in range(1, len(raw_query)):

                        if text_core[t + z].lower() == raw_query[z].lower():
                            match = z
                        else:
                            match = -1
                            break
                    if match > 1:

                        stop_slice = min(t + len(raw_query) + answer_window, t + l)
                        ans = text_core[t + len(raw_query) + 1:stop_slice]
                        doc = x['doc_ID']
                        block = x['block_ID']
                        page_num = x['master_index']
                        fn = x['file_source']
                        text_out = x['text']
                        slice = t + len(raw_query) + 1
                        answer.append((fn, doc, block, page_num, raw_query, slice, ans, text_out))

        return answer

    def split_context_row (self, context_row):

        entries_list = []
        entries_weights = []

        for z in range(0,len(context_row)):
            entries_list.append(context_row[z][0])
            entries_weights.append(int(context_row[z][1]))

        return entries_list, entries_weights

    # need to update / remove
    def dataset_smart_packager(self, text_block, min_th=200, max_th=400):

        # best outcome is to split at the end of a sentence
        # use simple regex command to split the sentence on end punctuation (e.g., '.', '!', '?')

        sentences = list(re.split('(?<=[.!?])', text_block))

        # logging.info("update: dataset smart packager - len sentences: %s ", len(sentences))

        if len(sentences) == 1 or len(sentences) == 0:
            # easy case - text block ends with "." -> return the whole block
            return text_block, ""

        if len(sentences) > 1:
            # check if last sentence ends with exclamation mark - otherwise, return as remainder
            last_sentence = sentences[-1]
            if last_sentence.endswith(".") or last_sentence.endswith("!") or last_sentence.endswith("?"):
                return text_block, ""
            else:
                # re-assemble the sentences (excluding the last fragment)
                output_text = ""
                remainder_text = ""
                for x in range(0, len(sentences) - 1):
                    if len(output_text) + len(sentences[x]) < max_th:
                        output_text += sentences[x] + " "
                    else:
                        remainder_text += sentences[x] + " "

                remainder_text += last_sentence

                if len(output_text) < min_th:
                    # in this case, retain the text_block as "remainder" and keep going
                    return "", text_block
                else:
                    # the assembled sentences are longer than the min threshold
                    # if the remainder is very short, then append to output
                    if len(remainder_text) > 20:
                        return output_text, remainder_text
                    output_text += " " + remainder_text
                    return output_text, ""

        # something has gone wrong unexpectedly if this is reached
        return text_block, ""

    def replace_word_numbers(self, evidence):
        evidence_toks = evidence.split(" ")

        word_numbers_lookup = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
                               "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
                               "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
                               "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
                               "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100,
                               "thousand": 1000, "million": 1000000, "billion": 1000000000, "percent": 0.01}

        num_toks_in_progress = ""
        text_with_numbers = ""
        build_num = False
        nums_in_text_list = []
        percent_flag = False

        # new - added on aug 26, 2023
        token_index_of_match_found = []

        for i, toks in enumerate(evidence_toks):

            if toks in word_numbers_lookup or (build_num and toks in ["and", "plus"]):
                build_num = True
                if toks not in ["and", "plus", "percent", "percentage"]:
                    num_toks_in_progress += toks + " "
                if toks in ["percent", "percentage"]:
                    percent_flag = True

            else:
                # add any number in progress, if any
                if build_num:

                    if percent_flag:
                        try:
                            my_num = w2n.word_to_num(num_toks_in_progress) * 0.01
                        except:
                            my_num = -9999.1234
                    else:
                        try:
                            my_num = w2n.word_to_num(num_toks_in_progress)
                        except:
                            my_num = -9999.1234

                    if my_num != -9999.1234:
                        text_with_numbers += str(my_num) + " "
                        nums_in_text_list.append(my_num)

                        # new add - aug 26
                        token_index_of_match_found.append(i)

                    build_num = False
                    percent_flag = False
                    num_toks_in_progress = ""

                # add next token
                text_with_numbers += toks + " "

        logging.info("update: text_with_numbers output: %s ", text_with_numbers)
        logging.info("update: nums found list: %s ", nums_in_text_list)

        return text_with_numbers, nums_in_text_list, token_index_of_match_found


class CorpTokenizer:

    """ Simple Custom 'Whole-word' Tokenizer implementation """

    def __init__(self, lower_case=True, remove_punctuation=True, remove_stop_words=True,
                 remove_numbers=True, one_letter_removal=False):

        self.lower_case = lower_case
        self.remove_punctuation = remove_punctuation
        self.remove_stop_words = remove_stop_words
        self.remove_numbers = remove_numbers
        self.one_letter_removal = one_letter_removal

    def tokenize(self, text):
        
        # strip the whitespace from the beginning and end of the text so we can tokenize the data
        text = text.strip()
        # start with basic whitespace tokenizing, 
        #is there a reason the text is being split on one space only?   
        #text2 = text.split(" ")
        # this line will split on whitespace regardless of tab or multispaces between words
        text2 = text.split()


        if self.remove_punctuation:
            text2 = Utilities().clean_list(text2)

        if self.lower_case:
            text_l = []
            for z in range(0, len(text2)):
                text_l.append(str(text2[z]).lower())
            text2 = text_l

        if self.remove_stop_words:
            text2 = Utilities().remove_stop_words(text2)

        if self.remove_numbers:
            text_n = []
            for z in range(0, len(text2)):
                if not str(text2[z]).isnumeric():
                    text_n.append(text2[z])
            text2 = text_n

        if self.one_letter_removal:
            text_out = []
            for z in range(0, len(text2)):
                if len(text2[z]) > 1:
                    text_out.append(text2[z])
            text2 = text_out

        return text2


class XlTable:

    """ XLTable class for handling and processing XL tables. """

    def __init__(self, xl_table_block, account, library):

        self.table = xl_table_block["table"]
        self.table_rows = self.table.split("<tr>")
        self.row_count = len(self.table_rows)
        self.new_table_blocks = []
        self.search_query = []
        self.search_tokens = []
        self.search_len = 0
        self.row_list = []
        self.col_list = []
        self.neighborhood = []

        self.account = account
        self.library = library

        # info about table block
        self.file_source = xl_table_block["file_source"]

        self.sheet_num = 1

        if "master_index" in xl_table_block:
            self.sheet_num = xl_table_block["master_index"]
        if "page_num" in xl_table_block:
            self.sheet_num = xl_table_block["page_num"]

        self.batch_num = xl_table_block["coords_y"]

        # batch_num starts at 0
        if self.batch_num == 0:
            self.first_batch = self.table
        else:
            self.first_batch = ""

    def get_first_batch(self):

        empty_result = ""

        if self.batch_num == 0:
            return self.table

        else:
            key_dict = {"file_source": self.file_source, "master_index": self.sheet_num, "coords_y": 0}
            results = CollectionRetrieval(self.library.library_name,
                                          account_name=self.library.account_name).filter_by_key_dict(key_dict)

            if results:
                first_batch = list(results)
                if len(first_batch) == 1:
                    return first_batch[0]["table"]

        return empty_result

    def get_xl_cell_contents (self, ind):

        # takes table block str, e.g., block["content1_core"] and index, e.g, "C6"
        # ... and returns full string content from that cell

        index_with_brackets = "<" + ind + ">"
        my_cell_str = ""

        found_search_term_in_cell = -1

        for x in range(0, self.row_count):
            tok = self.table_rows[x].lower().split(" ")
            for y in range(0, len(tok)):

                if my_cell_str != "":
                    break

                if tok[y].lower() == index_with_brackets:

                    if len(tok) > y + 1:
                        for z in range(y,len(tok)):

                            if not tok[z] in ("<tr>","<td>","<th>"):
                                if tok[z].lower() in self.search_tokens:

                                    if tok[z].startswith("<") and tok[z].endswith(">"):
                                        tok_display = ""
                                    else:
                                        tok_display = tok[z]
                                    my_cell_str += "<b> " + tok_display.strip("\n") + " </b>" + " "
                                    found_search_term_in_cell = 1
                                else:
                                    my_cell_str += tok[z].strip("\n") + " "
                            else:
                                break

        return my_cell_str, found_search_term_in_cell

    def get_xl_cell_contents_passed_table_str (self, ind, table_str):

        table_rows = table_str.split("<tr>")

        index_with_brackets = "<" + ind + ">"
        my_cell_str = ""

        for x in range(0, len(table_rows)):
            tok = table_rows[x].lower().split(" ")
            for y in range(0, len(tok)):

                if my_cell_str != "":
                    break

                if tok[y].lower() == index_with_brackets:

                    if len(tok) > y + 1:
                        for z in range(y + 1, len(tok)):

                            if not tok[z].startswith("<"):
                                if tok[z].lower() in self.search_tokens:
                                    my_cell_str += "<b> " + tok[z].strip("\n") + " </b>" + " "
                                else:
                                    my_cell_str += tok[z].strip("\n") + " "
                            else:
                                break

        return my_cell_str

    def get_row_col_from_xl_index (self,ind):

        # unpacks a "C9" index into row = 3 & column = 9

        col = []
        column = 0
        row = 0
        num_started = -1

        for x in range(0,len(ind)):

            # found lower-case letter char
            if (96 < ord(ind[x]) < 123) and num_started == -1:
                col.append((ord(ind[x]) - 96))

            if 47 < ord(ind[x]) < 58:
                num_started = 1
                row = int(ind[x:])
                break

        if len(col) == 1:
            column = col[0]

        if len(col) == 2:
            column = (col[0] * 26) + col[1]

        if len(col) == 3:
            column = (col[0] * 26 * 26) + (col[1] * 26) + col[2]

        if len(col) > 3:
            column = 0

        return column, row

    def convert_col_to_letter (self,col_num):

        # utility to convert column number back to letter, e.g., column 3 = "C"

        col_str = ""
        if col_num < 27:
            col_str += chr(col_num-1 + 65)

        if 26 < col_num < 53:
            col_str += chr(65)
            col_str += chr(65 + (col_num - 26))

        if 52 < col_num < 79:
            col_str += chr(66)
            col_str += chr(65 + (col_num - 52))

        if col_num > 79:
            dummy = 0

        return col_str

    def prep_xl_cell_neighborhood (self, col, row,context_window=3,header="yes"):

        new_table_str = ""
        my_col = ""
        col_list = []

        if col > context_window:
            for x in range(1,context_window+1):
                col_list.append(self.convert_col_to_letter(col-x))
        else:
            for x in range(1,col):
                col_list.append(self.convert_col_to_letter(col-x))

        for y in range(0,context_window+1):
            col_tmp = self.convert_col_to_letter(col+y)
            if y == 0:
                my_col = col_tmp

            col_list.append(col_tmp)

        row_list = []

        if row > context_window:
            for x in range(1,context_window + 1):
                row_list.append((row-x))
        else:
            for x in range(1,row):
                row_list.append((row-x))

        for y in range(0,context_window + 1):
            row_list.append((row+y))

        if header == "yes":
            header_rows = self.get_header_rows(my_col,row,col_list)
            new_table_str += header_rows

        row_list = sorted(row_list)
        col_list = sorted(col_list)

        self.row_list = row_list
        self.col_list = col_list

        for x in range(0,len(row_list)):
            new_row = "<tr> "
            for y in range(0,len(col_list)):
                my_index = col_list[y].lower() + str(row_list[x])
                self.neighborhood.append(my_index)
                my_cell, search_term_found = self.get_xl_cell_contents(my_index)

                if search_term_found > 0:
                    new_row += '<td style="background-color:#f7eac3">' + " " + my_index.upper() + " " + \
                               my_cell + " </style> </td> "
                else:
                    new_row += "<td>" + " " + my_index.upper() + " " + my_cell + " </td> "

            new_row += " </tr>"

            new_table_str += new_row

        return new_table_str

    def get_header_rows(self,my_col_str, my_row_num, column_list):

        first_batch = ""
        row_list_first_batch = []

        if my_row_num > 15:
            stopper_row = 15
        else:
            stopper_row = my_row_num - 1

        if self.batch_num > 0:
            stopper_row = 15
            first_batch = self.get_first_batch()
            if first_batch:
                row_list_first_batch = first_batch.split("<tr>")

        my_header_row = -1
        header_row = ""

        row_rank = []
        max_cols = 0
        max_col_num = 0
        my_row = []

        for z in range(0,stopper_row):

            if self.batch_num == 0:
                my_row = self.table_rows[z]

            else:
                if len(row_list_first_batch) > z:
                    my_row = row_list_first_batch[z]

                else:
                    my_row = []

            if my_row:
                cols_in_row = my_row.split("<th>")
            else:
                cols_in_row = []

            if cols_in_row:
                total_cols, alpha_cols, row_num = self.count_alpha_items_in_row(cols_in_row)
                row_rank.append((alpha_cols,z, row_num))

        r = sorted(row_rank, key=lambda x:x[0], reverse=True)
        top_three = r[0:3]
        top_three = sorted(top_three,key=lambda x:x[1])

        if top_three:

            for t in range(0,len(top_three)):
                my_header_row = top_three[t][2]
                header_row += '<tr style="background-color: rgba(246, 248, 252, 1)"> '

                for y in sorted(column_list):
                    my_index_tmp = y + str(my_header_row)
                    if self.batch_num == 0:
                        my_cell, search_term_found = self.get_xl_cell_contents(my_index_tmp.lower())
                    else:
                        my_cell = self.get_xl_cell_contents_passed_table_str(my_index_tmp.lower(),first_batch)

                    header_tmp = "<td> <em> " + " " + my_index_tmp + " " + my_cell + " </em> </td>"
                    header_row += header_tmp

                header_row += " </style> </tr>"

        return header_row

    def count_alpha_items_in_row(self,row_list):

        total_count = 0
        alpha_count = 0

        row_num = 0

        for z in range(0,len(row_list)):
            alpha = self.check_if_alpha_string(row_list[z])
            if z < 3:
                row_num = self.get_row_num(row_list[z])
            if alpha > 0:
                alpha_count += 1
            total_count += 1

        return total_count, alpha_count, row_num

    def get_row_num(self,row_cell):

        row_num_str = ""
        row_num = 0

        row_toks = row_cell.split(" ")

        for z in range(0,len(row_toks)):

            if row_num_str:
                break

            if row_toks[z].startswith("<"):
                if len(row_toks[z]) > 2:
                    if row_toks[z] not in ("<tr>","<td>","<th>", "</tr>","</td>","</th>"):
                        c = row_toks[z][1:-1]
                        row_num_str = ""

                        for y in range(0,len(c)):
                            if 47 < ord(c[y]) < 58:
                                row_num_str += c[y]
                        try:
                            row_num = int(row_num_str)
                        except:
                            # print("must be error converting str: ", row_num_str)
                            row_num = 0

                        break

        return row_num

    def check_if_alpha_string(self,s):

        alpha = -1
        escape_on = -1

        for x in range(0,len(s)):

            if ord(s[x]) == 60:
                escape_on = 1

            # simple test - look for any alpha character outside of < >
            if escape_on == -1:
                if (64 < ord(s[x]) < 91) or (96 < ord(s[x]) < 123):
                    alpha = 1
                    break

            if ord(s[x]) == 62:
                escape_on = -1

        return alpha

    def get_index (self, search_query):

        self.search_query = search_query.lower()
        self.search_tokens = self.search_query.split(" ")

        c = 0
        r = 0
        current_index = ""

        for x in range(0, self.row_count):

            tok = self.table_rows[x].lower().split(" ")
            current_index = ""

            for y in range(0, len(tok)):

                if tok[y].startswith("<"):
                    if len(tok[y]) > 3:
                        if tok[y][1:2] not in ("td", "tr", "th"):
                            current_index = tok[y][1:-1]

                if search_query.lower() == tok[y]:
                    c, r = self.get_row_col_from_xl_index(current_index)
                    break

        return current_index, c, r

    def main_parse(self, search_query):

        new_table_blocks_out = []

        self.search_query = search_query.lower()
        self.search_tokens = self.search_query.split(" ")
        self.search_len = len(self.search_tokens)

        for x in range(0, self.row_count):

            tok = self.table_rows[x].lower().split(" ")

            current_index = ""

            for y in range(0, len(tok)):

                if tok[y].startswith("<"):
                    if len(tok[y]) > 3:
                        if tok[y][1:2] not in ("td", "tr", "th"):
                            current_index = tok[y][1:-1]

                match = -1
                if self.search_tokens[0] == tok[y]:
                    match = 1

                    if self.search_len > 1 and len(tok) > (y + self.search_len - 1):
                        for s in range(1,self.search_len):
                            if self.search_tokens[s] != tok[y+s]:
                                match = -1
                                break

                    if match == 1:
                        if current_index not in self.neighborhood:
                            c, r = self.get_row_col_from_xl_index(current_index)
                            new_table_str = self.prep_xl_cell_neighborhood(c, r)
                            new_table_blocks_out.append(new_table_str)

        self.new_table_blocks = new_table_blocks_out

        return new_table_blocks_out


class WikiKnowledgeBase:

    """ WikiKnowledgeBase implements Wikipedia API """

    def __init__(self):

        # importing here to suppress log warnings produced by urllib3
        import urllib3
        urllib3.disable_warnings()

        self.user_agent = "Examples/3.0"

        self.wiki = Wikipedia(user_agent=self.user_agent, extract_format=ExtractFormat.WIKI, verify=False)
        self.wiki_search_api_url = 'http://en.wikipedia.org/w/api.php'

    def get_article(self, article_name):

        article_response = {"title": "", "summary": "", "text": ""}

        try:
            page_py = self.wiki.page(article_name)

            if page_py.exists():

                logging.info("update: page_py - %s - %s", page_py.title, page_py.summary)
                logging.info("update: text - %s ", page_py.text)

                article_response = {"title": page_py.title, "summary": page_py.summary, "text": page_py.text}

            else:
                logging.info("update: connected with Wikipedia - selected article does not exist - %s ", article_name)

        except:
            logging.error("error: could not retrieve wikipedia article - please try again")

        return article_response

    def search_wikipedia(self, query, result_count=10, suggestion=False):

        # output result
        output = []

        # search params passed to the wikipedia api
        search_params = {'list': 'search', 'srprop': '', 'srlimit': result_count, 'srsearch': query,
                         'format': 'json', 'action': 'query'}

        if suggestion: search_params['srinfo'] = 'suggestion'

        headers = {'User-Agent': self.user_agent}

        try:
            r = requests.get(self.wiki_search_api_url, params=search_params, headers=headers, verify=False)

            for i, title in enumerate(r.json()["query"]["search"]):

                logging.info("update:  wiki results - %s - %s", i, title)

                new_entry = {"num": i, "title": title["title"], "pageid": title["pageid"]}
                output.append(new_entry)

        except:
            logging.error("error: could not connect with Wikipedia to retrieve search results")

        return output


class TextChunker:

    """ Text Chunker - input is a big chunk of text and output is a chunked set of smaller text chunks. """

    # simple class that can be inserted for OCR, Text or HTML
    # class expects to be passed a big chunk of text, e.g., output from OCR or full read of text file
    #   --will chop up blocks out of the text
    #   --uses a "chisel" approach, so starts with 'max_block_size' and looks back to find sentence edges
    #   --in testing with a number of files, it results in avg block size ~500 with 90%+ ending on sentence or \n\r

    def __init__(self, text_chunk=None, max_char_size=600, look_back_char_range=300):

        self.text_chunk = text_chunk
        self.max_char_size = max_char_size
        self.look_back_range = look_back_char_range

        self.chunks = []

        self.avg_char_size = 0
        self.smallest_chunk = self.max_char_size
        self.largest_chunk = 0
        self.chunks_ending_with_period = 0

    def convert_text_to_chunks (self):

        starter = 0

        while starter < len(self.text_chunk):

            if (starter + self.max_char_size) < len(self.text_chunk):
                stopper = starter + self.max_char_size
            else:
                stopper = len(self.text_chunk)

            smooth_stop = self.smooth_edge(starter, stopper)
            chunk = self.text_chunk[starter:smooth_stop]

            starter = smooth_stop

            # if very short chunk, then concatenate with the previous chunk
            if len(chunk) < self.look_back_range:
                if len(self.chunks) > 0:
                    self.chunks[-1] += chunk
                else:
                    self.chunks.append(chunk)

            else:
                # general case - create next chunk
                # chunk_pp = re.sub("[\n\r]", " ", chunk)
                self.chunks.append(chunk)

                if len(chunk) < self.smallest_chunk:
                    self.smallest_chunk = len(chunk)

                if len(chunk) > self.largest_chunk:
                    self.largest_chunk = len(chunk)

                if len(chunk) > 0:
                    if ord(chunk[-1]) in [46,10,13]:
                        self.chunks_ending_with_period += 1

            self.avg_char_size += len(chunk)

        return self.chunks

    def smooth_edge(self,starter,stopper):

        # default case is to return the whole text sample as single chunk
        smooth_stop = stopper

        # look back is the full range that will be reviewed to find proper stopping point
        if (stopper - self.look_back_range) > starter:
            look_back = stopper - self.look_back_range
        else:
            look_back = starter

        # best case - look for a period
        found_period = -1
        for x in range(stopper-1,look_back,-1):

            # found a period followed by white space marker (space, \n, \r) - best case
            if ord(self.text_chunk[x]) == 46:

                # first confirm that '.' is followed by white space or is the end of the text
                if x+1 == stopper or ord(self.text_chunk[x + 1]) in [32, 13, 10]:

                    # exclude 'several edge cases where '.' is not a reliable sentence end
                    short_window = self.text_chunk
                    if x > 5:
                        short_window = self.text_chunk[x-5:x-1]

                    # (A) first edge case - "two periods close to each other", e.g., "x.y."
                    if "." not in short_window and short_window != "":

                        # (B) second edge case - "period after number in list", e.g., "point 2."
                        if not 47 < ord(short_window[-1]) < 58:

                            # (C) third edge case - common abbreviations
                            if short_window[:-2] != "Mr" and short_window[:3] != "Mrs" and short_window[:2] != "Dr":

                                # if none of (A) - (B) - (C) or apply, then consider period valid stopping point
                                found_period = x + 1
                                break

            # alternate solid stopper is presence of \n\n | \n\r | \r\r -> usually marks a section/para end
            if ord(self.text_chunk[x]) in [10,13]:
                if x+1 == stopper or ord(self.text_chunk[x+1]) in [10,13]:
                    found_period = x+1
                    break

        # if found a period, then smooth stop is the char right after the period
        if found_period > - 1:
            smooth_stop = found_period

        else:
            # if no period found, then next best case is to look for whitespace between words
            for y in range(stopper - 1, look_back,-1):

                # look for a white space separator
                if ord(self.text_chunk[y]) in [32, 13, 10]:
                    smooth_stop = y
                    break

        # if no period or white space found, then return the original stopper

        return smooth_stop


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
                logging.warning("warning - Graph - unexpected - could not identify bow index on bow file - %s ", top_bow_file)
                bow_index = 0

            fp = open(os.path.join(dataset_fp, top_bow_file), "r", encoding='utf-8')
            fp.seek(0, 2)
            bow_byte_index = fp.tell()
            fp.seek(0, 0)  # rewind
            bow_tokens = len(fp.read().split(","))
            fp.close()

        return bow_index, bow_byte_index, bow_tokens, bow_files, no_bow

    def build_graph(self):

        #  Generates multiple valuable nlp artifacts in /nlp folder
        #  Primary objective is generation of co-occurrence matrix

        os.makedirs(self.library.nlp_path, exist_ok=True)

        # note: this function has been updated -> ~750 stop words
        stop_words = Utilities().load_stop_words_list(self.library.nlp_path)

        #   first major step -> build the BOW

        bow_index, bow_byte_index, bow_token_index, bow_files, no_bow = self.bow_locator()

        # save the 'pre_initialization bow data"

        self.pre_initialization_bow_data = {"bow_index": bow_index, "bow_byte_index": bow_byte_index,
                                            "bow_token_index": bow_token_index, "bow_files": bow_files,
                                            "no_bow": no_bow}

        logging.info(f"update: Graph().initialization - bow parameters at start: {self.pre_initialization_bow_data}")

        t0 = time.time()

        # no need to capture outputs directly from .bow_builder() method -> will pick indirectly thru .bow_locator()
        _ = self.bow_builder()

        logging.info("update: initialization - Step 1- BOW processing - time - %s ", time.time() - t0)

        bow_index, bow_byte_index, bow_token_index, bow_files, no_bow = self.bow_locator()

        # get and save the 'post_initialization bow data"

        self.post_initialization_bow_data = {"bow_index": bow_index, "bow_byte_index": bow_byte_index,
                                             "bow_token_index": bow_token_index, "bow_files": bow_files,
                                             "no_bow": no_bow}

        logging.info("update: Graph().initialization - bow parameters post: %s ", self.post_initialization_bow_data)

        # second major step -> build the MCW
        t1 = time.time()
        vocab_len, targets_len, context_len, min_len = self.mcw_builder()

        logging.info("update: Graph().initialization - Step 2- MCW processing - time - %s ", time.time() - t1, vocab_len)

        # third major step -> build the BG
        t3 = time.time()

        graph_output = self.build_graph_raw(vocab_len, targets_len, context_len, min_len)

        logging.info("update: Graph().initialization - Step 3 - Graph building - time - %s ", time.time() - t3)

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

        print("update: graph_builder - python - db, db_uri - ", db_c, input_db_path)

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

        logging.info("update: Graph() bow_builder - calling on text_extract handler - bow vars - %s - %s ", bow_index_current,
                     bow_len_remainder_only)

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

        logging.info("update: Graph() - completed major C function step - utility BOW create - %s -", bow_count)

        return 0

    def mcw_builder(self):

        # new utility function - builds most common words across library, based on multiple BOW files
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
                        logging.info("update: mcw analysis - stopping at prune_count: %s %s %s ", y, prune_count, mcw_new[y])
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
        logging.info("update: Graph() mcw_builder - vocab len: %s ", len(mc_final))

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

        logging.info("update: build_graph_raw: bow len - %s %s: ", bow_count, bow_len_remainder)

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

        logging.info("update: Graph - initiating call to graph handler - %s - %s - %s - %s ", vocab_len, mcw_target_len,
                     mcw_context_len, min_len)

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

        logging.info("update: Graph() - completed graph build - output value is - %s ", dummy)

        return 0

    def bg_text_package(self):

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
            logging.error("error: Graph - could not identify correct file in nlp path")

        # write to file
        g = open(os.path.join(self.library.nlp_path,"bg_text.txt"), "w", encoding='utf-8')
        for t in text_out:
            g.write((t + "\n"))
        g.close()

        return text_out

    def _get_top_bigrams_exclude_special_tokens(self, tokens, top_n):

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

        #   exports graph elements in node/edge dataset, packaged for popular visualization libraries
        #   e.g., vis.Network (Javascript)
        #   e.g., networkX (Python)

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

        #   runs a 'pseudo-query' on graph, and retrieves elements from graph 'neighborhood' for visualization
        #   exports graph elements in node/edge dataset, packaged for popular visualization libraries
        #   e.g., vis.Network (Javascript)
        #   e.g., networkX (Python)

        if self.library.get_knowledge_graph_status() != "yes":
            self.build_graph()

        b = CorpTokenizer(one_letter_removal=True, remove_stop_words=True, remove_numbers=True)

        query_tokens = CorpTokenizer().tokenize(query)

        context_search = self.retrieve_knowledge_graph()

        if context_search is None or len(context_search) == 0:
            logging.info("update: Graph - knowledge graph appears to be empty")

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

                    logging.info("update: Graph - in targeted_build - found match:  %s %s %s %s", len(context_search[z][1]), l,
                                 tokens, new_node)

                    for y in range(0, l):
                        c = context_search[z][1][y][0]
                        w = context_search[z][1][y][1]

                        # G.add_edge(context_search[z][0],c,weight=w,title="")

                        t = context_search[z][0]

                        new_c_node = {"id": c, "label": c, "shape": "dot", "size": 10}

                        if new_c_node not in node_dataset and c.lower() not in query_tokens:
                            logging.info("update: Graph - adding node:  %s", new_c_node)
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
        return len(self.get_unique_vocab_lookup())

    def get_unique_vocab_lookup(self):

        if self.library.get_knowledge_graph_status() != "yes":
            self.build_graph()

        j = json.load(open(os.path.join(self.library.nlp_path,"vocab_lookup.json"), "r", encoding='utf-8'))

        return j

    def get_unique_vocab_reverse_lookup(self):

        if self.library.get_knowledge_graph_status() != "yes":
            self.build_graph()

        j = json.load(open(os.path.join(self.library.nlp_path,"token_lookup.json"), "r", encoding='utf-8'))

        return j

    def retrieve_knowledge_graph(self):

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

        if self.library.get_knowledge_graph_status() != "yes":

            logging.info("update: to retrieve_mcw_counts, the knowledge graph must be created for this library. "
                         "This is a 'one-time' build, and depending upon the size of the library, may take a little "
                         "bit of time.")

            self.build_graph()

        try:
            mcw = open(os.path.join(self.library.nlp_path,"mcw_counts.txt"), "r", encoding='utf-8').read().split(",")

        except OSError:
            logging.exception("error:  Graph - opening mcw_counts file - path not found.")
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
                    logging.error("error: Graph - unexpected mcw file issue - %s %s %s", z, mcw[z], mcw[z + 1])

        return mcw_count_list, mcw_names_only

    def retrieve_bigrams(self):

        if self.library.get_knowledge_graph_status() != "yes":
            self.build_graph()

        try:
            bigrams = open(os.path.join(self.library.nlp_path,"bigrams.txt"), "r", encoding='utf-8').read().split(",")

        except OSError:
            logging.exception("error: Graph - unexpected error opening bigrams file.")
            return []

        bigram_pairs_list = []

        for z in range(0, len(bigrams), 2):

            if (z + 1) < len(bigrams):
                try:
                    bigs = bigrams[z].split("_")
                    new_entry = (bigrams[z], int(bigrams[z + 1]), bigs[0], bigs[1])
                    bigram_pairs_list.append(new_entry)

                except:
                    logging.error("error: Graph - unexpected problem with bigram file"
                                  "- %s %s %s ", z, bigrams[z], bigrams[z + 1])

        return bigram_pairs_list

    def get_library_data_stats(self):

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
            logging.exception("error: Graph - could not open manifest file at path- %s ", self.library.nlp_path)
            data_manifest = {}

        if "bow_count" in data_manifest:
            library_stats.update({"bow_count": data_manifest["bow_count"]})

        if "unique_vocab_len" in data_manifest:
            library_stats.update({"unique_vocab_len": data_manifest["unique_vocab_len"]})

        return library_stats

    def bow_adhoc_builder(self, sentence_list):

        bow_out = []
        b = CorpTokenizer(one_letter_removal=True, remove_stop_words=True, remove_numbers=True)

        for sentences in sentence_list:
            tokens = b.tokenize(sentences)
            for t in tokens:
                bow_out.append(t)

        return bow_out

    def mcw_adhoc_builder(self, bow):

        c = Counter(bow)
        mc = c.most_common()

        return mc

    def retrieve_mcw(self):

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

        #   * note: this method loops through a lot of key analytical artifacts at a document level *
        #   * there are several commented out items which we will look to explore/add in future versions *
        #   * ... will also look to shift this to C + background process for performance ... *

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
                            logging.error("error: malformed BOW - need to investigate root cause")
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

        #   'queries' the knowledge graph to find related terms

        if self.library.get_knowledge_graph_status() != "yes":

            logging.info("update: use of this method requires a 'one-time' creation of knowledge graph on the "
                         "library, which is being created now - this may take some time depending upon the size "
                         "of the library %s", self.library)

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

        #   'queries' the knowledge graph to find related terms

        if self.library.get_knowledge_graph_status() != "yes":

            logging.info("update: use of this method requires a 'one-time' creation of knowledge graph on the "
                         "library, which is being created now - this may take some time depending upon the size "
                         "of the library %s", self.library)

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

        logging.info("update: Graph - bigrams out - %s ", bigrams_out)

        return bigrams_out

    def kg_query(self, query, th=10):

        #   'queries' the knowledge graph to find related terms

        if self.library.get_knowledge_graph_status() != "yes":

            logging.info("update: use of this method requires a 'one-time' creation of knowledge graph on the "
                         "library, which is being created now - this may take some time depending upon the size "
                         "of the library %s", self.library)

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


class Datasets:

    """Datasets class implements a set of data packaging tools to create 'model-ready' datasets using a variety of
    packaging strategies automatically derived from artifacts across llmware. """

    def __init__(self, library=None, ds_folder=None, validation_split=0.1, testing_split=0.1, tokenizer=None):

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
        self.ds_id_mode = "uuid"

        #   after building dataset, this will be populated with the name of the current ds
        self.current_ds_name = ""

        # separator configs
        self.separator = "\n"

        self.file_batch_size = 50000

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

        for entries in self.dataset_catalog:
            if entries["dataset_name"] == ds_name:
                return entries
        return {}

    def token_counter(self, text_sample):
        toks = self.tokenizer.encode(text_sample).ids
        return len(toks)

    def tokenize_text(self, text_sample):
        toks = self.tokenizer.encode(text_sample).ids
        return toks

    def get_dataset_sample(self, ds_name, ds_path=None, sample_range=1000):

        #   useful for testing to randomly sample an element from the dataset
        #   picks a sample randomly from the first training sample file

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

    def issue_new_ds_id (self, custom_id=None, mode="uuid"):

        # issue new ds_id
        ds_id = "default_new"

        if custom_id:
            ds_id = custom_id
        else:

            if mode == "time_stamp":
                ds_id = str(Utilities().get_current_time_now())

            elif mode == "uuid":
                ds_id = str(Utilities().get_uuid())

            elif mode == "random_number":
                ds_id = str(random.randint(1000000, 9999999))

        # create new dataset specific folder
        self.current_ds_name = self.ds_base_name + ds_id
        new_ds_folder = os.path.join(self.work_folder,self.current_ds_name)
        if not os.path.exists(new_ds_folder):
            os.mkdir(new_ds_folder)

        return ds_id, new_ds_folder

    def package_chatgpt_sample(self, turn1, turn2, add_system_instruction=True):

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

        #   create specific folder for dataset artifacts inside library dataset path
        ds_id, ds_folder = self.issue_new_ds_id(custom_id=custom_id)

        if not qr:

            if self.library:
                dialogs = CollectionRetrieval(self.library_name,account_name=self.account_name).filter_by_key("dialog", "true")
            else:
                raise LibraryObjectNotFoundException("no-library-loaded-in-Dataset-constructor")

            dialogs = sorted(dialogs, key=lambda x:x["doc_ID"], reverse=False)

            if len(dialogs) == 0:
                logging.error("error:  Datasets builder - not able to identify text as dialog conversation turns")
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
            logging.error("error: Datasets - no dialog transcripts found")
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


# simple API wrapper around popular Yahoo Finance - used in Prompt to pull in real-time info

class YFinance:

    """ YFinance class implements the Yahoo Finance API. """

    def __init__(self, ticker=None):

        """
        Widely used Yahoo Finance API - key object = "
        TickerObj = yahooFinance.Ticker("META")
        print("All Info : ", TickerObj.info)
        for keys, values in TickerObj.info.items():
            print("keys: ", keys, values)

        # display Company Sector
        print("Company Sector : ", TickerObj.info['sector'])

        # display Price Earnings Ratio
        print("Price Earnings Ratio : ", TickerObj.info['trailingPE'])

        # display Company Beta
        print(" Company Beta : ", TickerObj.info['beta'])
        print(" Financials : ", TickerObj.get_financials())
        """

        self.company_info = None

        self.financial_summary_keys = ["shortName", "symbol","marketCap", "totalRevenue", "ebitda", "revenueGrowth", "grossMargins",
                                   "freeCashflow", "priceToSalesTrailing12Months", "grossMargins","currency"]

        self.stock_summary_keys = ["shortName", "symbol", "exchange","bid", "ask", "fiftyTwoWeekLow", "fiftyTwoWeekHigh", "symbol",
                                   "shortName", "longName", "currentPrice", "targetHighPrice", "targetLowPrice",
                                   "returnOnAssets", "returnOnEquity", "trailingPE", "forwardPE", "volume",
                                   "forwardEps", "pegRatio", "currency"]

        self.risk_summary_keys = ["shortName","symbol", "auditRisk", "boardRisk", "compensationRisk", "shareHolderRightsRisk", "overallRisk",
                                  "shortName", "longBusinessSummary"]

        self.company_summary_keys = ["shortName", "longName", "symbol", "marketCap", "companyOfficers", "website",
                                     "industry", "sector", "longBusinessSummary", "fullTimeEmployees"]

        self.keys = ["address1", "city", "state", "zip", "country", "phone","website","industry",
                     "industryDisp", "sector", "sectorDisp", "longBusinessSummary", "fullTimeEmployees",
                     "companyOfficers", "auditRisk", "boardRisk", "compensationRisk", "shareHolderRightsRisk",
                     "overallRisk", "previousClose", "open", "dayLow", "dayHigh", "regularMarketPreviousClose",
                     "regularMarketOpen", "regularMarketDayLow", "regularMarketDayHigh", "payoutRatio", "beta",
                     "trailingPE", "forwardPE", "volume", "regularMarketVolume", "averageVolume",
                     "averageVolume10days", "bid", "ask", "bidSize", "askSize", "marketCap", "fiftyTwoWeekLow",
                     "fiftyTwoWeekHigh", "priceToSalesTrailing12Months", "fiftyDayAverage", "twoHundredDayAverage",
                     "trailingAnnualDividendRate", "trailingAnnualDividendYield", "currency", "enterpriseValue",
                     "profitMargins", "floatShares", "sharesOutstanding", "sharesShort", "sharesShortPriorMonth",
                     "sharesShortPreviousMonthDate", "dateShortInterest", "sharesPercentSharesOut",
                     "heldPercentInsiders", "heldPercentInstitutions", "shortRatio", "shortPercentOfFloat",
                     "impliedSharesOutstanding", "bookValue", "priceToBook", "lastFiscalYearEnd",
                     "nextFiscalYearEnd", "mostRecentQuarter", "earningsPerQuarterlyGrowth", "netIncomeToCommon",
                     "trailingEps", "forwardEps", "pegRatio", "enterpriseToRevenue", "enterpriseToEbitda",
                     "52WeekChange", "SandP52WeekChange", "exchange", "quoteType", "symbol", "underlyingSymbol",
                     "shortName", "longName", "currentPrice", "targetHighPrice", "targetLowPrice", "targetMeanPrice",
                     "targetMedianPrice", "recommendationMean", "recommendationKey", "numberOfAnalystOpinions",
                     "totalCash", "totalCashPerShare", "ebitda", "totalDebt", "quickRatio", "currentRatio",
                     "totalRevenue", "debtToEquity", "revenuePerShare", "returnOnAssets" "returnOnEquity", "grossProfits",
                     "freeCashflow", "operatingCashflow", "earningsGrowth", "revenueGrowth", "grossMargins",
                     "ebitdaMargins", "operatingMargins", "financialCurrency", "trailingPegRatio"]

        if ticker:
            self.company_info = yfinance.Ticker(ticker)
        else:
            self.company_info = None

    def ticker(self, company_ticker):
        company_info = yfinance.Ticker(company_ticker)
        return company_info

    def get_company_summary(self, ticker=None):
        output_info = {}
        company_info = yfinance.Ticker(ticker).info
        for targets in self.company_summary_keys:
            for keys, values in company_info.items():
                if targets == keys:
                    output_info.update({targets: values})
        return output_info

    def get_financial_summary(self, ticker=None):
        output_info = {}
        company_info = yfinance.Ticker(ticker).info
        for targets in self.financial_summary_keys:
            for keys, values in company_info.items():
                if targets == keys:
                    output_info.update({targets: values})
        return output_info

    def get_stock_summary(self, ticker=None):
        output_info = {}
        company_info = yfinance.Ticker(ticker).info
        for targets in self.stock_summary_keys:
            for keys,values in company_info.items():
                if targets == keys:
                    output_info.update({targets: values})
        return output_info

