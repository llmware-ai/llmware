
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


"""The util module implements general helper functions that are used across LLMWare, primarily within the Utilities
class, along with a whole word (white space) tokenizer (CorpTokenizer) class, TextChunker and AgentWriter classes. """


import csv
from collections import Counter
import sys
import os
import random

import platform
from pathlib import Path
import re
from tokenizers import Tokenizer
from datetime import datetime
from ctypes import *
import logging

from llmware.resources import CloudBucketManager
from llmware.configs import LLMWareConfig
from llmware.exceptions import ModelNotFoundException, DependencyNotInstalledException, ModuleNotFoundException

logger = logging.getLogger(__name__)


class Utilities:

    """ Utility functions used throughout LLMWare """

    def __init__(self, library=None):
        self.start = 0
        self.library = library

    def get_module_graph_functions(self):

        """ Loads shared libraries for Graph module based on current platform/architecture. """

        # Detect based on machine architecture
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

        # deprecation warning for aarch64 linux
        if system == 'linux' and machine == 'aarch64':
            logger.warning("Deprecation warning: as of llmware 0.2.7, we are deprecating support for aarch64 "
                           "linux - we build, support and test on six other major platforms - Linux x86_64, "
                           "Linux x86_64 with CUDA, Windows x86_64, Windows x86_64 with CUDA, Mac Metal, and "
                           "Mac x86_64.  We will revisit platform support from time-to-time, due "
                           "to availability and interest.  If you have an important need for "
                           "support for aarch 64 linux, please raise an issue at github/llmware-ai/llmware.git")

        # Construct the path to a specific lib folder.  Eg. .../llmware/lib/darwin/x86_64
        machine_dependent_lib_path = os.path.join(LLMWareConfig.get_config("shared_lib_path"), system, machine)

        # replace for local testing:  file_ext -> .dylib
        _path_graph = os.path.join(machine_dependent_lib_path, "llmware", "libgraph_llmware" + file_ext)

        _mod_utility = None

        try:
            _mod_utility = cdll.LoadLibrary(_path_graph)
        except:
            logger.warning(f"warning: Module 'Graph Processor' could not be loaded from path - "
                           f"\n {_path_graph}.\n")

        if not _mod_utility:
            raise ModuleNotFoundException("Graph Processor")

        return _mod_utility

    def get_module_pdf_parser(self):

        """ Loads shared libraries for the Parser module, based on machine architecture. """

        # Detect machine architecture
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

        # deprecation warning for aarch64 linux
        if system == 'linux' and machine == 'aarch64':
            logger.warning("Deprecation warning: as of llmware 0.2.7, we are deprecating support for aarch64 "
                           "linux - we build, support and test on six other major platforms - Linux x86_64, "
                           "Linux x86_64 with CUDA, Windows x86_64, Windows x86_64 with CUDA, Mac Metal, and "
                           "Mac x86_64.  We will revisit from time-to-time, due "
                           "to availability and interest.  If you have an important need for "
                           "support for aarch 64 linux, please raise an issue at github/llmware-ai/llmware.git")

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
            logger.warning(f"warning: Module 'PDF Parser' could not be loaded from path - "
                           f"\n {_path_pdf}.\n")

        #   if no module loaded, then raise exception
        if not _mod_pdf:
            raise ModuleNotFoundException("PDF Parser")

        return _mod_pdf

    def get_module_office_parser(self):

        """ Load shared libraries for Office parser module based on machine architecture. """

        # Detect machine architecture
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

        # deprecation warning for aarch64 linux
        if system == 'linux' and machine == 'aarch64':
            logger.warning("Deprecation warning: as of llmware 0.2.7, we are deprecating support for aarch64 "
                           "linux - we build, support and test on six other major platforms - Linux x86_64, "
                           "Linux x86_64 with CUDA, Windows x86_64, Windows x86_64 with CUDA, Mac Metal, and "
                           "Mac x86_64.  We will revisit from time-to-time, due "
                           "to availability and interest.  If you have an important need for "
                           "support for aarch 64 linux, please raise an issue at github/llmware-ai/llmware.git")

        # Construct the path to a specific lib folder.  Eg. .../llmware/lib/darwin/x86_64
        machine_dependent_lib_path = os.path.join(LLMWareConfig.get_config("shared_lib_path"), system, machine)

        _path_office = os.path.join(machine_dependent_lib_path, "llmware", "liboffice_llmware" + file_ext)

        _mod = None

        try:
            # attempt to load the shared library with ctypes
            _mod = cdll.LoadLibrary(_path_office)

        except:

            # catch the error, if possible
            logger.warning(f"warning: Module 'Office Parser' could not be loaded from path - "
                           f"\n {_path_office}.\n")

        # if no module loaded, then raise exception
        if not _mod:
            raise ModuleNotFoundException("Office Parser")

        return _mod

    def get_default_tokenizer(self):

        """ Retrieves an instance of default tokenizer. In most cases, this is the GPT2 tokenizer, which is a
        good proxy for OpenAI and OpenAI-like GPTNeo models. """

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

            logger.info("Utilities - get_default_tokenizer - if no tokenizer found, then as a backup, "
                        "the gpt2 tokenizer will be used - not in local model repository, "
                        "so pulling from global repo - this may take a few seconds the first time to download.")

            files = CloudBucketManager().pull_single_model_from_llmware_public_repo(model_name="gpt2")

            #   quick check to confirm that model is present
            models = os.listdir(local_model_repo)
            if "gpt2" not in models:
                raise ModelNotFoundException("gpt2_tokenizer")

        tokenizer = Tokenizer.from_file(os.path.join(local_model_repo, "gpt2", "tokenizer.json"))

        return tokenizer

    def load_tokenizer_from_file(self, fp):

        """ Loads tokenizer from file. """

        tokenizer = Tokenizer.from_file(fp)
        return tokenizer

    def get_uuid(self):

        """ Generates a UUID. """

        import uuid
        # uses unique id creator from uuid library
        return uuid.uuid4()

    @staticmethod
    def file_save (cfile, file_path, file_name):

        """ Saves an in-memory array to CSV file. """

        max_csv_size = 20000
        csv.field_size_limit(max_csv_size)

        out_file = os.path.join(file_path, file_name)

        with open(out_file, 'w', newline='') as csvfile:
            c = csv.writer(csvfile, dialect='excel', doublequote=False, delimiter=',',escapechar = ']')

            for z in range(0, len(cfile)):
                # intercept a line too large here
                if sys.getsizeof(cfile[z]) < max_csv_size:
                    try:
                        # unusual, but if unable to write a particular element, then will catch error and skip
                        c.writerow(cfile[z])
                    except:
                        logger.warning(f"warning: could not write item in row {z} - skipping")
                        pass
                else:
                    logger.error(f"error:  CSV ERROR:   Row exceeds MAX SIZE: {sys.getsizeof(cfile[z])} - "
                                 f"{cfile[z]}")

        csvfile.close()

        return 0

    @staticmethod
    def file_load (in_path, delimiter=",",encoding='ISO-8859-1',errors='ignore'):

        """ Loads a CSV array and outputs an in-memory array corresponding to the CSV structure. """

        record_file = open(in_path, encoding=encoding,errors=errors)
        c = csv.reader(record_file, dialect='excel', doublequote=False, delimiter=delimiter)
        output = []
        for lines in c:
            output.append(lines)
        record_file.close()

        return output

    @staticmethod
    def csv_save(rows, file_dir, file_name):

        """ Saves CSV from in memory array consisting of list of rows as input. """

        full_path = Path(file_dir, file_name)

        with full_path.open('w', encoding='utf-8') as out:
            writer = csv.writer(out)
            try:
                writer.writerows(rows)
            except csv.Error as e:
                logger.error("Exception writing csv file - not successful.")
                return False

        return True

    @staticmethod
    def get_top_bigrams (tokens, top_n):

        """ Returns a list of top_n bigrams based on a list of tokens. """

        bigrams = []
        for z in range(1, len(tokens)):
            entry = (tokens[z-1] + "_" + tokens[z])
            bigrams.append(entry)

        d = Counter(bigrams)
        dc = d.most_common(top_n)

        return dc

    @staticmethod
    def get_top_trigrams (tokens, top_n):

        """ Returns a list of top_n trigrams based on a list of tokens. """

        trigrams = []
        for z in range(2 ,len(tokens)):
            entry = (tokens[ z -2] + "_" + tokens[ z -1] + "_" + tokens[z])
            trigrams.append(entry)

        d = Counter(trigrams)
        dc = d.most_common(top_n)

        return dc

    @staticmethod
    def get_top_4grams (tokens, top_n):

        """ Returns a list of top_n 4grams based on a list of tokens. """

        four_grams = []
        for z in range(3 ,len(tokens)):
            entry = (tokens[ z -3 ]+ "_" + tokens[ z -2] + "_" + tokens[ z -1] + "_" + tokens[z])
            four_grams.append(entry)

        d = Counter(four_grams)
        dc = d.most_common(top_n)

        return dc

    @staticmethod
    def compare_timestamps (t1, t2, time_str="%a %b %d %H:%M:%S %Y"):

        """ Compares two time-stamps t1 and t2 provided as input and returns a time_delta_obj, along
        with explicitly passing the days and seconds from the time_delta_obj. """

        t1_obj = datetime.strptime(t1, time_str)
        t2_obj = datetime.strptime(t2, time_str)

        time_delta_obj = t1_obj - t2_obj

        days = time_delta_obj.days
        seconds = time_delta_obj.seconds

        return time_delta_obj, days, seconds

    @staticmethod
    def get_current_time_now (time_str="%a %b %e %H:%M:%S %Y"):

        """ Returns the current time, used for time-stamps - delivered in format from the optional input
        time_str. """

        #   if time stamp is used in file_name, needs to be Windows standards compliant
        if platform.system() == "Windows":
            time_str = "%Y-%m-%d_%H%M%S"

        return datetime.now().strftime(time_str)

    @staticmethod
    def get_time_string_standard():

        """ Returns the time stamp string standard used. """

        time_str_standard = "%a %b %e %H:%M:%S %Y"
        return time_str_standard

    @staticmethod
    def isfloat(num):

        """ Checks if an input is a float number. """

        try:
            float(num)
            return True
        except ValueError:
            return False

    @staticmethod
    def prep_filename_alt(filename_in, accepted_file_formats_list):

        """ Prepares a filename and offers options to configure and provide safety checks to provide a 'safe'
        filename. """

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

        """ Confirms that a string is a safe url. """

        try:
            import urllib.parse
            return urllib.parse.quote_plus(string)
        except TypeError:
            logger.error(f"Error encoding string - {string}")
            return ""

    @staticmethod
    def get_stop_words_master_list():

        """ Returns a common set of english stop words. """

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

        """ Loads a stop words list from file. """

        stop_words = self.get_stop_words_master_list()

        s = open(os.path.join(library_fp, "stop_words_list.txt"), "w", encoding='utf-8')

        for words in stop_words:
            s.write((words + ","))
        s.close()
        os.chmod((library_fp+ "stop_words_list.txt"), 0o777)

        return stop_words

    def remove_stop_words(self, token_list):

        """ Filters a list of tokens and removes stop words. """

        stop_words = self.get_stop_words_master_list()

        tokens_out = []
        for z in range(0, len(token_list)):
            if token_list[z] not in stop_words:
                tokens_out.append(token_list[z])

        return tokens_out

    @staticmethod
    def clean_list (token_list):

        """ Used by CorpTokenizer to provide a clean list stripping punctuation. """

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

        """ Splits a sentence around a marker word. """

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

        """ Prepares a custom masked language label. """

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

        """ Executes a fast in-memory exact search across a list of dictionaries

            -- query: filtering query (exact match)
            -- output_dicts: can be any list of dicts provided that the text_key is found in the dict
            -- text_key: by default, this is "text", but can be configured to any field in the dict
            -- remove_stop_words: set to True by default.

            Returns a subset of the list of the dicts with only those entries that match the query
        """

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

        """ Utility method that runs search for key_term in sentence. """

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

        """ Takes a raw_query, text and answer_window as input and returns a context window around matches
        to the query with the size of the answer_window. """

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

        """ Splits a context row - internal utility method to support Graph class. """

        entries_list = []
        entries_weights = []

        for z in range(0,len(context_row)):
            entries_list.append(context_row[z][0])
            entries_weights.append(int(context_row[z][1]))

        return entries_list, entries_weights

    def dataset_smart_packager(self, text_block, min_th=200, max_th=400):

        """ Deprecated - will remove in future release. """

        # best outcome is to split at the end of a sentence
        # use simple regex command to split the sentence on end punctuation (e.g., '.', '!', '?')

        sentences = list(re.split('(?<=[.!?])', text_block))

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

        """ Replaces word numbers with the actual number value.

            -- uses the word2number python library, which can be imported separately with pip install.
        """

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
                            from word2number import w2n
                            my_num = w2n.word_to_num(num_toks_in_progress) * 0.01
                        except:
                            my_num = -9999.1234
                            logger.info("update: could not import word2number to look for 'number-words' - if "
                                        "you wish to use, `pip3 install word2number`")
                    else:
                        try:
                            from word2number import w2n
                            my_num = w2n.word_to_num(num_toks_in_progress)
                        except:
                            my_num = -9999.1234
                            logger.info("update: could not import word2number to look for 'number-words' - if "
                                        "you wish to use, `pip3 install word2number`")

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

        logger.info(f"update: text_with_numbers output: {text_with_numbers}")
        logger.info(f"update: nums found list: {nums_in_text_list}")

        return text_with_numbers, nums_in_text_list, token_index_of_match_found

    def convert_media_file_to_wav(self, path_to_file_to_convert, save_path=None, file_out="converted_file.wav"):

        """ Utility method that converts wide range of video/audio file formats into .wav for transcription.
        To use this method requires two separate installs:

            1.  pydub - e.g., `pip3 install pydub`
            2.  lib install ffmpeg, e.g., brew install ffmpeg (MacOS)
        """

        # import ffmpeg -> need to import the core lib (brew install ffmpeg)

        try:
            from pydub import AudioSegment
        except:
            raise DependencyNotInstalledException("pydub")

        # format
        #   format = "m4a" works
        fmt = path_to_file_to_convert.split(".")[-1]
        if fmt not in ["mp3", "m4a", "mp4", "wma", "aac", "ogg", "flv"]:
            logger.warning(f"warning: file format - {fmt} - is not recognized and can not be converted.")
            return None

        try:
            given_audio = AudioSegment.from_file(path_to_file_to_convert, format=fmt, channels=2, frame_rate=16000)
            outfile_path = os.path.join(save_path, file_out)
            given_audio.export(outfile_path, format="wav")
        except:
            logger.warning(f"warning: could not successfully convert file @ {path_to_file_to_convert} to .wav - "
                           f"one common issue is the need to install ffmpeg which is a core audio/video "
                           f"processing library.  It can be installed with apt (linux) ; brew (mac) ; or "
                           f"downloaded directly (windows).")
            return None

        return outfile_path

    def secure_filename(self, fn):

        """ New utility method to remove os.sep from proposed filenames. """

        # strip os.sep from file name
        safe_file_name = str(fn)
        if safe_file_name.startswith(os.sep):
            safe_file_name = safe_file_name[1:]

        # removes os separator
        secure_fn = safe_file_name.replace(os.sep, "_")

        # converts spaces into underscores
        secure_fn = secure_fn.replace(" ", "_")

        return secure_fn

    def split_ocr_special_field1(self,special_field_text):

        """ Utility method to unpack a special_field text from an OCR block that will have the link
        back to the original document and block id. """

        doc_block = special_field_text.split("&")
        output_dict = {}

        for elements in doc_block:

            key, value = elements.split("-")
            try:
                value = int(value)
            except:
                logger.warning(f"warning: could not convert value into integer as expected - {key} - {value}")

            output_dict.update({key: value})

        return output_dict

    @staticmethod
    def md5checksum(fp, fn):

        """ Creates MD5 Checksum against a selected file. """
        md5_output = None

        try:
            import hashlib

            md5 = hashlib.md5()

            # handle content in binary form
            f = open(os.path.join(fp, fn), "rb")

            while chunk := f.read(4096):
                md5.update(chunk)

            md5_output = md5.hexdigest()

        except:
            logger.debug("Utilities - md5checksum - could not create md5 hex")

        return md5_output

    @staticmethod
    def create_md5_stamp (fp, save=True, md5_fn="md5_record.json"):

        """ Creates MD5 Stamp for all files in a folder. """

        import random
        md5_record = {}

        fp_files = os.listdir(fp)

        for file in fp_files:
            if file == md5_fn:
                logging.warning(f"Utilities - create_md5_stamp - found existing md5_record")
                r = random.randint(0,10000000)
                rec_core = str(md5_fn).split(".")[0]
                md5_record = rec_core + "_" + str(r) + ".json"

            md5 = Utilities().md5checksum(fp, file)
            md5_record.update({file: md5})

        time_stamp = Utilities().get_current_time_now()

        md5_record.update({"time_stamp": time_stamp})

        if save:

            logger.debug(f"Utilities - create_md5_stamp - config output: {md5_record}")

            import json
            f = open(os.path.join(fp, md5_fn), "w")
            j = json.dumps(md5_record, indent=1)
            f.write(j)
            f.close()

        return md5_record


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

        """ Tokenizes an input text. """

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

        """ Converts text into chunks. """

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

        """ Produces a 'smooth edge' between starter and stopper. """

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


class AgentWriter:

    """ Specialized Logging utility designed for capturing 'agent' and 'agent-like' inference outputs where
    the intent is to capture a 'show-your-work' chain of logic, rather than a traditional log output, which is
    generated through logging.  AgentWriter provides three basic options for capturing
    this output:

        -- 'screen'     - default - writes to stdout
        -- 'file'       - writes to file
        -- 'off'        - turns off (no action taken)
        """

    def __init__(self):

        # options configured through global LLMWareConfigs
        self.mode = LLMWareConfig().get_agent_writer_mode()
        self.fp_base = LLMWareConfig().get_llmware_path()
        self.fn = LLMWareConfig().get_agent_log_file()

        self.file = os.path.join(self.fp_base, self.fn)

        if self.mode == "screen":
            self.writer = sys.stdout
            self.file = None
        elif self.mode == "file":
            if os.path.exists(self.file):
                self.writer = open(self.file, "a")
            else:
                self.writer = open(self.file, "w")
        else:
            # takes no action
            self.writer = None
            self.file = None

    def write(self, text_message):

        """ Writes output to selected output stream. """

        if self.writer:
            if self.mode == "file":
                try:
                    escape_ansi_color_codes = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                    text_message = escape_ansi_color_codes.sub('', text_message)
                except:
                    pass
            self.writer.write(text_message+"\n")

    def close(self):

        """ Closes at end of process if needed to close the file. """

        if self.file:
            self.writer.close()


