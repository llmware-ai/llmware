

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
import platform

from llmware.exceptions import HomePathDoesNotExistException, ConfigKeyException, \
    UnsupportedEmbeddingDatabaseException, UnsupportedCollectionDatabaseException


class LLMWareConfig:

    # initial setting will pull from environ variables - future updates must be set directly
    if platform.system() == "Windows":
        _base_fp = {"home_path": os.environ.get("USERPROFILE"),
                    "llmware_path_name": "llmware_data" + os.sep}
    else:
        _base_fp = {"home_path": os.environ.get("HOME"),
                    "llmware_path_name": "llmware_data" + os.sep}

    _fp = {"model_repo_path_name": "model_repo" + os.sep,
           "library_path_name": "accounts" + os.sep,
           "input_path_name": "input_channel" + os.sep,
           "parser_path_name": "parser_history" + os.sep,
           "query_path_name": "query_history" + os.sep,
           "prompt_path_name": "prompt_history" + os.sep,
           "tmp_path_name": "tmp" + os.sep}

    # note: two alias for postgres vector db - "postgres" and "pg_vector" are the same
    _supported = {"vector_db": ["milvus", "pg_vector", "postgres", "redis", "pinecone",
                                "faiss", "qdrant", "mongo_atlas"],

                  # coming soon - more options!
                  "collection_db": ["mongo"],
                  "table_db": []}

    _conf = {"collection_db_uri": os.environ.get("COLLECTION_DB_URI", "mongodb://localhost:27017/"),

             "collection_db_username": "", # Not used for now
             "collection_db_password": "", # Not used for now

             "collection_db": "mongo",
             "vector_db": "milvus",

             # note: Milvus configs moving to separate MilvusConfig object - these options will be removed
             "milvus_host": os.environ.get("MILVUS_HOST","localhost"),
             "milvus_port": int(os.environ.get("MILVUS_PORT",19530)),
             "milvus_db": os.environ.get("MILVUS_DB", "default"),

             "debug_mode": 0,
             "llmware_sample_files_bucket": "llmware-sample-docs",
             "llmware_public_models_bucket": "llmware-public-models",
             "shared_lib_path": os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib")
             }

    @classmethod
    def get_config(cls,name):
        if name in cls._conf:
            return cls._conf[name]
        raise ConfigKeyException(name)

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
        raise ConfigKeyException(file_path)

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

    @classmethod
    def get_active_db(cls):

        """ Returns the current selected default database for Library text collections """

        return cls._conf["collection_db"]

    @classmethod
    def set_active_db(cls, new_db):

        """ Sets the default database for Library text collections """

        if new_db in cls._supported["collection_db"]:
            cls._conf["collection_db"] = new_db
        else:
            raise UnsupportedCollectionDatabaseException(new_db)

    @classmethod
    def get_vector_db(cls):

        """ Gets the default vector database selection """

        return cls._conf["vector_db"]

    @classmethod
    def set_vector_db(cls, vector_db_name):

        """ Sets the default vector database """

        if vector_db_name in cls._supported["vector_db"]:
            cls._conf["vector_db"] = vector_db_name
        else:
            raise UnsupportedEmbeddingDatabaseException(vector_db_name)

    @classmethod
    def get_supported_vector_db(cls):
        return cls._supported["vector_db"]

    @classmethod
    def get_supported_collection_db(cls):
        return cls._supported["collection_db"]


class MilvusConfig:

    """Configuration object for Milvus"""

    _conf = {"host": os.environ.get("MILVUS_HOST", "localhost"),
             "port": os.environ.get("MILVUS_PORT", 19530),
             "db_name": os.environ.get("MILVUS_DB", "default"),
             "partitions": []}

    @classmethod
    def get_config(cls, name):

        """ Gets current Milvus config by key name,
        e.g. MilvusConfig().get_config("port") returns 19530 """

        if name in cls._conf:
            return cls._conf[name]
        raise ConfigKeyException(name)

    @classmethod
    def set_config(cls, name, value):

        """ Sets Milvus config by key name,
        e.g., MilvusConfig().set_config("port", 8080) sets port = 8080 """

        cls._conf[name] = value


class MongoConfig:

    """Configuration object for MongoDB"""

    _conf = {"db_uri": os.environ.get("COLLECTION_DB_URI", "mongodb://localhost:27017/"),
             "user_name": "",
             "pw": "",
             "atlas_db_uri": "",
             "db_name":""}

    @classmethod
    def get_config(cls, name):
        if name in cls._conf:
            return cls._conf[name]
        raise ConfigKeyException(name)

    @classmethod
    def set_config(cls, name, value):
        cls._conf[name] = value

    @classmethod
    def get_uri_string(cls):
        return cls._conf["db_uri"]

    @classmethod
    def get_db_configs(cls):
        configs = {}
        for keys, values in cls._conf.items():
            configs.update({keys:values})
        return configs

    @classmethod
    def get_user_name(cls):
        return cls._conf["user_name"]

    @classmethod
    def get_db_pw(cls):
        return cls._conf["pw"]


class PostgresConfig:

    """Configuration object for Postgres DB"""

    _conf = {"host": os.environ.get("USER_MANAGED_PG_HOST", "localhost"),
             "port": os.environ.get("USER_MANAGED_PG_PORT", 5432),
             "db_name": os.environ.get("USER_MANAGED_PG_DB_NAME", "postgres"),
             "user_name": os.environ.get("USER_MANAGED_PG_USER_NAME", "postgres"),
             "pw": os.environ.get("USER_MANAGED_PG_PW", ""),

             # to create full copy, set "postgres_schema" to "full"
             "pgvector_schema": "vector_only"}

    @classmethod
    def get_config(cls, name):
        if name in cls._conf:
            return cls._conf[name]
        raise ConfigKeyException(name)

    @classmethod
    def set_config(cls, name, value):
        cls._conf[name] = value

    @classmethod
    def get_uri_string(cls):

        port = cls._conf["port"]
        host = cls._conf["host"]
        db_name = cls._conf["db_name"]
        input_collection_db_path = f"postgresql://postgres@{host}:{port}/{db_name}"
        return input_collection_db_path

    @classmethod
    def get_db_configs(cls):
        configs = {}
        for keys, values in cls._conf.items():
            configs.update({keys:values})
        return configs

    @classmethod
    def get_user_name(cls):
        return cls._conf["user_name"]

    @classmethod
    def get_db_pw(cls):
        return cls._conf["pw"]


class RedisConfig:

    """Configuration object for Redis"""

    _conf = {"host": os.environ.get("USER_MANAGED_REDIS_HOST", "localhost"),
             "port": os.environ.get("USER_MANAGED_REDIS_PORT", 6379),
             "user_name": "",
             "pw": "",
             "db_name": ""}

    @classmethod
    def get_config(cls, name):
        if name in cls._conf:
            return cls._conf[name]
        raise ConfigKeyException(name)

    @classmethod
    def set_config(cls, name, value):
        cls._conf[name] = value


class PineconeConfig:

    """Configuration object for Pinecone"""

    _conf = {"pincone_api_key": os.environ.get("USER_MANAGED_PINECONE_API_KEY"),
             "pinecone_environment": os.environ.get("USER_MANAGED_PINECONE_ENVIRONMENT")}

    @classmethod
    def get_config(cls, name):
        if name in cls._conf:
            return cls._conf[name]
        raise ConfigKeyException(name)

    @classmethod
    def set_config(cls, name, value):
        cls._conf[name] = value


class SQLiteConfig:

    """ Configuration object for SQLite - note: SQLite integration coming soon! """

    _conf = {"host": os.environ.get("USER_MANAGED_SQLITE_HOST", "localhost"),
             "port": os.environ.get("USER_MANAGED_SQLITE_PORT", 6333),
             "sqlite_db_folder_path": LLMWareConfig().get_library_path(),
             "user_name": "",
             "pw": "",
             "db_name": "sqlite_llmware.db"}

    @classmethod
    def get_config(cls, name):
        if name in cls._conf:
            return cls._conf[name]
        raise ConfigKeyException(name)

    @classmethod
    def set_config(cls, name, value):

        """ Sets the configs for SQLite - e.g., to create a new 'database' -
        SQLiteConfig().set_config("db_name": "my_new_db_name.db") """

        cls._conf[name] = value

    @classmethod
    def get_uri_string (cls):

        """For SQLite the URI string is the local file with full absolute path"""

        db_file = os.path.join(cls._conf["sqlite_db_folder_path"], cls._conf["db_name"])

        return db_file

    @classmethod
    def get_db_configs(cls):
        configs = {}
        for keys, values in cls._conf.items():
            configs.update({keys:values})
        return configs

    @classmethod
    def get_user_name(cls):
        return cls._conf["user_name"]

    @classmethod
    def get_db_pw(cls):
        return cls._conf["pw"]


class QdrantConfig:

    """Configuration object for Qdrant"""

    _conf = {"host": os.environ.get("USER_MANAGED_QDRANT_HOST", "localhost"),
             "port": os.environ.get("USER_MANAGED_QDRANT_PORT", 6333)}

    @classmethod
    def get_config(cls, name):
        if name in cls._conf:
            return cls._conf[name]
        raise ConfigKeyException(name)

    @classmethod
    def set_config(cls, name, value):
        cls._conf[name] = value

