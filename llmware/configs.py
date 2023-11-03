

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

from llmware.exceptions import HomePathDoesNotExistException


class LLMWareConfig:

    # initial setting will pull from environ variables - future updates must be set directly

    _base_fp = {"home_path": os.environ.get("HOME"),
                "llmware_path_name": "llmware_data/"}

    _fp = {"model_repo_path_name": "model_repo" + os.sep,
           "library_path_name": "accounts" + os.sep,
           "input_path_name": "input_channel" + os.sep,
           "parser_path_name": "parser_history" + os.sep,
           "query_path_name": "query_history" + os.sep,
           "prompt_path_name": "prompt_history" + os.sep,
           "tmp_path_name": "tmp" + os.sep}

    _conf = {"collection_db_uri": os.environ.get("COLLECTION_DB_URI", "mongodb://localhost:27017/"),
             "collection_db_username": "", # Not used for now
             "collection_db_password": "", # Not used for now
             "collection_db": "mongo",
             "milvus_host": os.environ.get("MILVUS_HOST","localhost"),
             "milvus_port": int(os.environ.get("MILVUS_PORT",19530)),
             "debug_mode": 0,
             "llmware_sample_files_bucket": "llmware-sample-docs",
             "llmware_public_models_bucket": "llmware-public-models",
             "shared_lib_path": os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib")
             }

    @classmethod
    def get_config(cls,name):
        if name in cls._conf:
            return cls._conf[name]
        raise "Key not found in configs"

    @classmethod
    def set_config(cls,name, value):
        cls._conf[name] = value

    @classmethod
    def get_home(cls):
        return cls._base_fp["home_path"]

    @classmethod
    def set_home(cls, new_value):
        cls._base_fp["home_path"] = new_value

    @classmethod
    def set_llmware_path_name(cls, new_value):
        cls._base_fp["llmware_path_name"] = new_value

    @classmethod
    def get_fp_name(cls,file_path):
        if file_path in cls._fp:
            return cls._fp[file_path]
        raise "File path not found in configs"

    @classmethod
    def set_fp_name(cls,file_path, new_value):
        if file_path in cls._fp:
            cls._fp.update({file_path, new_value})

    @classmethod
    def get_llmware_path(cls):
        return os.path.join(cls._base_fp["home_path"], cls._base_fp["llmware_path_name"])

    @classmethod
    def get_library_path(cls):
        return os.path.join(cls._base_fp["home_path"], cls._base_fp["llmware_path_name"], cls._fp["library_path_name"])

    @classmethod
    def get_model_repo_path(cls):
        return os.path.join(cls._base_fp["home_path"],cls._base_fp["llmware_path_name"], cls._fp["model_repo_path_name"])

    @classmethod
    def get_input_path(cls):
        return os.path.join(cls._base_fp["home_path"], cls._base_fp["llmware_path_name"], cls._fp["input_path_name"])

    @classmethod
    def get_parser_path(cls):
        return os.path.join(cls._base_fp["home_path"],cls._base_fp["llmware_path_name"], cls._fp["parser_path_name"])

    @classmethod
    def get_query_path(cls):
        return os.path.join(cls._base_fp["home_path"],cls._base_fp["llmware_path_name"], cls._fp["query_path_name"])

    @classmethod
    def get_prompt_path(cls):
        return os.path.join(cls._base_fp["home_path"], cls._base_fp["llmware_path_name"],cls._fp["prompt_path_name"])

    @classmethod
    def get_tmp_path(cls):
        return os.path.join(cls._base_fp["home_path"], cls._base_fp["llmware_path_name"],cls._fp["tmp_path_name"])

    @classmethod
    def get_path(cls, name):

        if name+"_name" in cls._fp:
            return os.path.join(cls._base_fp["home_path"], cls._base_fp["llmware_path_name"],
                                cls._fp[name+"_name"])

        raise HomePathDoesNotExistException(name)

    @classmethod
    def setup_llmware_workspace (cls):

        # create file structure - configured through use of env variable ["HOME"]
        home_path = cls._base_fp["home_path"]

        if not os.path.exists(home_path):
            raise HomePathDoesNotExistException(home_path)

        llmware_path = cls.get_llmware_path()
        if not os.path.exists(llmware_path):
            os.mkdir(llmware_path)

        library_path = cls.get_library_path()
        if not os.path.exists(library_path):
            os.mkdir(library_path)

        input_path = cls.get_input_path()
        if not os.path.exists(input_path):
            os.mkdir(input_path)

        model_repo_path = cls.get_model_repo_path()
        if not os.path.exists(model_repo_path):
            os.mkdir(model_repo_path)

        parser_path = cls.get_parser_path()
        if not os.path.exists(parser_path):
            os.mkdir(parser_path)

        query_path = cls.get_query_path()
        if not os.path.exists(query_path):
            os.mkdir(query_path)

        prompt_path = cls.get_prompt_path()
        if not os.path.exists(prompt_path):
            os.mkdir(prompt_path)

        tmp_path = cls.get_tmp_path()
        if not os.path.exists(tmp_path):
            os.mkdir(tmp_path)

        # set 'open' read/write directory permissions, e.g., chmod 777
        os.chmod(library_path, 0o777)
        os.chmod(input_path, 0o777)
        os.chmod(model_repo_path, 0o777)
        os.chmod(parser_path, 0o777)
        os.chmod(query_path, 0o777)
        os.chmod(prompt_path, 0o777)
        os.chmod(tmp_path, 0o777)

        return 0

    @classmethod
    def create_new_account(cls, account_name):

        #   will set up a secondary account file structure
        #   no management of account permissions in llmware- assumed to be handled in calling application

        library_path = cls.get_library_path()
        new_account_path = os.path.join(library_path, account_name)
        os.mkdir(new_account_path)

        return 0

