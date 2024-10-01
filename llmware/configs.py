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

"""The configs module implements the configuration logic using classes for llmware.

The implementation includes the central llmware config class LLMWareConfig, and the config classes for all
supported text index databases and vector databases.
"""

import os
import platform
import logging

from llmware.exceptions import HomePathDoesNotExistException, UnsupportedEmbeddingDatabaseException, \
    UnsupportedCollectionDatabaseException, UnsupportedTableDatabaseException, ConfigKeyException

try:
    from colorama import Fore
    COLOR_WHITE = Fore.WHITE
    COLOR_RESET = Fore.RESET
    COLOR_RED = Fore.RED
    COLOR_YELLOW = Fore.YELLOW
    COLOR_GREEN= Fore.GREEN
    COLOR_BLUE = Fore.BLUE
except:
    COLOR_WHITE = ""
    COLOR_RESET = ""
    COLOR_RED = ""
    COLOR_YELLOW = ""
    COLOR_GREEN = ""
    COLOR_BLUE = ""


class CustomFormatter(logging.Formatter):

    """ CustomFormatter - Configuration of global logging formatting - WIP. """

    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: COLOR_GREEN + format + COLOR_RESET,
        logging.INFO: COLOR_WHITE + format + COLOR_RESET,
        logging.WARNING: COLOR_YELLOW + format + COLOR_YELLOW,
        logging.ERROR: COLOR_RED + format + COLOR_RESET,
        logging.CRITICAL: COLOR_RED + format + COLOR_RESET,
        25: COLOR_BLUE + format + COLOR_RESET
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class LLMWareConfig:

    """LLMWare global configuration object - use set/get to update """

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
    _supported = {"vector_db": ["chromadb", "neo4j", "milvus", "pg_vector", "postgres", "redis", "pinecone", "faiss", "qdrant", "mongo_atlas","lancedb"],
                  "collection_db": ["mongo", "postgres", "sqlite"],
                  "table_db": ["postgres", "sqlite"]}

    _conf = {"collection_db": "mongo",
             "vector_db": "milvus",
             "table_db": "sqlite",
             "debug_mode": 0,
             "llmware_sample_files_bucket": "llmware-sample-docs",
             "llmware_public_models_bucket": "llmware-public-models",
             "shared_lib_path": os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib"),
             "logging_level": logging.WARNING,
             "logging_format": COLOR_WHITE + '%(levelname)-4s: %(message)s' + COLOR_RESET,
             "logging_level_by_module": {"llmware.embeddings": 20, "llmware.models": 20, "llmware.agents":20,
                                         "llmware.prompts": 20, "llmware.resources": 20,
                                         "llmware.setup": 20, "llmware.parsers": 20},
             "agent_writer_mode": "screen",
             "agent_log_file": "agent_log.txt",
             "model_register": {"module": "llmware.models", "method": "register"},
             "model_post_init": {"module": "llmware.models", "method": "post_init"},
             "model_validate": {"module": "llmware.models", "method": "validate"},
             "model_preview": {"module": "llmware.models", "method": "preview"},
             "model_fetch": {"module": "llmware.models", "method": "pull_snapshot_from_hf"},
             "model_router": {"module": "llmware.models", "method": "route_optimizer"},
             "apply_model_load_router": False,
             "apply_default_fetch_override": False
             }

    @classmethod
    def get_config(cls,name):
        """Get config value by key"""

        if name in cls._conf:
            return cls._conf[name]
        raise ConfigKeyException(name)

    @classmethod
    def set_config(cls,name, value):
        """Set config value by key"""
        cls._conf[name] = value

    @classmethod
    def get_home(cls):
        """Get home directory path"""
        return cls._base_fp["home_path"]

    @classmethod
    def set_home(cls, new_value):
        """Set home directory path"""
        cls._base_fp["home_path"] = new_value

    @classmethod
    def set_llmware_path_name(cls, new_value):
        """Set main path name for llmware data path"""
        cls._base_fp["llmware_path_name"] = new_value

    @classmethod
    def get_fp_name(cls,file_path):
        """Get file path from configs"""
        if file_path in cls._fp:
            return cls._fp[file_path]
        raise ConfigKeyException(file_path)

    @classmethod
    def set_fp_name(cls,file_path, new_value):
        """Set file path in configs"""
        if file_path in cls._fp:
            cls._fp.update({file_path, new_value})

    @classmethod
    def get_llmware_path(cls):
        """Get llmware absolute folder directory path"""
        return os.path.join(cls._base_fp["home_path"], cls._base_fp["llmware_path_name"])

    @classmethod
    def get_library_path(cls):
        """Get library absolute folder directory path"""
        return os.path.join(cls._base_fp["home_path"], cls._base_fp["llmware_path_name"], cls._fp["library_path_name"])

    @classmethod
    def get_model_repo_path(cls):
        """Get model repo absolute folder directory path"""
        return os.path.join(cls._base_fp["home_path"],cls._base_fp["llmware_path_name"], cls._fp["model_repo_path_name"])

    @classmethod
    def get_input_path(cls):
        """Get input absolute folder directory path"""
        return os.path.join(cls._base_fp["home_path"], cls._base_fp["llmware_path_name"], cls._fp["input_path_name"])

    @classmethod
    def get_parser_path(cls):
        """Get parser absolute folder directory path"""
        return os.path.join(cls._base_fp["home_path"],cls._base_fp["llmware_path_name"], cls._fp["parser_path_name"])

    @classmethod
    def get_query_path(cls):
        """Get query absolute folder directory path"""
        return os.path.join(cls._base_fp["home_path"],cls._base_fp["llmware_path_name"], cls._fp["query_path_name"])

    @classmethod
    def get_prompt_path(cls):
        """Get prompt absolute folder directory path"""
        return os.path.join(cls._base_fp["home_path"], cls._base_fp["llmware_path_name"],cls._fp["prompt_path_name"])

    @classmethod
    def get_tmp_path(cls):
        """Get tmp absolute folder directory path"""
        return os.path.join(cls._base_fp["home_path"], cls._base_fp["llmware_path_name"],cls._fp["tmp_path_name"])

    @classmethod
    def get_path(cls, name):
        """Get absolute folder path by name"""

        if name+"_name" in cls._fp:
            return os.path.join(cls._base_fp["home_path"], cls._base_fp["llmware_path_name"],
                                cls._fp[name+"_name"])

        raise HomePathDoesNotExistException(name)

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
    def get_table_db(cls):

        """ Gets the default table (SQL) database """

        return cls._conf["table_db"]

    @classmethod
    def set_table_db(cls, table_db_name):

        """ Sets the default table (SQL) database """

        if table_db_name in cls._supported["table_db"]:
            cls._conf["table_db"] = table_db_name
        else:
            raise UnsupportedTableDatabaseException(table_db_name)

    @classmethod
    def get_supported_vector_db(cls):
        return cls._supported["vector_db"]

    @classmethod
    def get_supported_collection_db(cls):
        return cls._supported["collection_db"]

    @classmethod
    def get_supported_table_db(cls):
        return cls._supported["table_db"]

    @classmethod
    def setup_llmware_workspace (cls):

        """Set up llmware main working folder directory"""

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

        """Sets up a new secondary account file structure"""

        #   Useful in deploying llmware in multi-account and multi-user applications
        #   note: assumes account user permissions to be implemented in calling application

        library_path = cls.get_library_path()
        new_account_path = os.path.join(library_path, account_name)
        os.mkdir(new_account_path)

        return 0

    @classmethod
    def get_db_uri_string(cls):

        """ Retrieves the db_uri_string for the current active default text collection database """

        active_db = cls.get_active_db()

        uri_string = None

        if active_db == "mongo": uri_string = MongoConfig.get_uri_string()
        if active_db == "postgres": uri_string = PostgresConfig.get_uri_string()
        if active_db == "sqlite": uri_string = SQLiteConfig.get_uri_string()

        return uri_string

    @classmethod
    def get_db_configs(cls):

        """ Gets the db configs for the selected default text collection database """

        active_db = cls.get_active_db()

        configs = {}

        if active_db == "mongo": configs = MongoConfig.get_db_configs()
        if active_db == "postgres": configs = PostgresConfig.get_db_configs()
        if active_db == "sqlite": configs = SQLiteConfig.get_db_configs()

        return configs

    @classmethod
    def get_db_user_name(cls):

        """ Get the db user name for the default db """

        active_db = cls.get_active_db()

        user_name = ""

        if active_db == "mongo": user_name = MongoConfig.get_user_name()
        if active_db == "postgres": user_name = PostgresConfig.get_user_name()
        if active_db == "sqlite": user_name = SQLiteConfig.get_user_name()

        return user_name

    @classmethod
    def get_db_pw(cls):

        """ Get the db password for the default db """

        active_db = cls.get_active_db()

        pw = ""

        if active_db == "mongo": pw = MongoConfig.get_db_pw()
        if active_db == "postgres": pw = PostgresConfig.get_db_pw()
        if active_db == "sqlite": pw = SQLiteConfig.get_db_pw()

        return pw

    @classmethod
    def get_logging_level(cls):
        return cls._conf["logging_level"]

    @classmethod
    def set_logging_level(cls, log_level_str):

        log_level_str = log_level_str.upper()

        accepted_levels = ["INFO", "DEBUG", "WARNING", "ERROR","CRITICAL"]
        if log_level_str not in accepted_levels:
            raise ConfigKeyException(f"Exception: proposed logging level does not correspond to a "
                                     f"recognized level, e.g., {accepted_levels}")

        if log_level_str == "INFO": new_level = logging.INFO
        elif log_level_str == "DEBUG": new_level = logging.DEBUG
        elif log_level_str == "WARNING": new_level = logging.WARNING
        elif log_level_str == "ERROR": new_level = logging.ERROR
        elif log_level_str == "CRITICAL": new_level = logging.CRITICAL
        else:
            new_level = logging.DEBUG

        cls._conf["logging_level"] = new_level

        return new_level

    @classmethod
    def get_logging_format(cls):
        return cls._conf["logging_format"]

    @classmethod
    def set_logging_format(cls, formatting_str):
        cls._conf["logging_format"] = formatting_str
        return True

    @classmethod
    def get_logging_level_by_module(cls, module):
        if module in cls._conf["logging_level_by_module"]:
            return cls._conf["logging_level_by_module"][module]
        else:
            raise ConfigKeyException(module)

    @classmethod
    def set_logging_level_by_module(cls, module, level):

        if module in cls._conf["logging_level_by_module"]:
            cls._conf["logging_level_by_module"][module] = level
        else:
            cls._conf["logging_level_by_module"].update({module: level})

        return cls._conf["logging_level_by_module"]

    @classmethod
    def get_agent_writer_mode(cls):
        return cls._conf["agent_writer_mode"]

    @classmethod
    def set_agent_writer_mode(cls, mode):

        if mode in ["screen", "file", "off"]:
            cls._conf["agent_writer_mode"] = mode
        else:
            raise ConfigKeyException(mode)

        return cls._conf["agent_writer_mode"]

    @classmethod
    def get_agent_log_file(cls):
        return cls._conf["agent_log_file"]

    @classmethod
    def set_agent_log_file(cls, log_file_name):
        cls._conf["agent_log_file"] = log_file_name
        return cls._conf["agent_log_file"]


class VectorDBRegistry:

    """ Registry of supported Vector DBs, and the class module used to interface with the DB. """

    vector_db_list = {"milvus": {"module": "llmware.embeddings", "class": "EmbeddingMilvus"},
                      "chromadb": {"module": "llmware.embeddings", "class": "EmbeddingChromaDB"},
                      "qdrant": {"module": "llmware.embeddings", "class": "EmbeddingQdrant"},
                      "postgres": {"module": "llmware.embeddings", "class": "EmbeddingPGVector"},
                      "pg_vector": {"module": "llmware.embeddings", "class": "EmbeddingPGVector"},
                      "redis": {"module": "llmware.embeddings", "class": "EmbeddingRedis"},
                      "neo4j": {"module": "llmware.embeddings", "class": "EmbeddingNeo4j"},
                      "lancedb": {"module": "llmware.embeddings", "class": "EmbeddingLanceDB"},
                      "faiss": {"module": "llmware.embeddings", "class": "EmbeddingFAISS"},
                      "pinecone": {"module": "llmware.embeddings", "class": "EmbeddingPinecone"},
                      "mongo_atlas": {"module": "llmware.embeddings", "class": "EmbeddingMongoAtlas"}
                      }
    @classmethod
    def get_vector_db_list(cls):
        """ List current view of implemented supported vector db for embeddings. """
        return cls.vector_db_list

    @classmethod
    def add_vector_db(cls, db_name, vector_db_class, module="llmware.embeddings"):
        """ Adds a vector db including the module and class. """
        new_entry = {db_name: {"module": module, "class": vector_db_class}}
        cls.vector_db_list.update(new_entry)
        return True


logging.basicConfig(format=LLMWareConfig().get_logging_format(), level=LLMWareConfig().get_logging_level())


class MilvusConfig:

    """Configuration object for Milvus"""

    _conf = {"host": os.environ.get("MILVUS_HOST", "localhost"),
             "port": os.environ.get("MILVUS_PORT", 19530),
             "db_name": os.environ.get("MILVUS_DB", "default"),
             "partitions": [],

             # new attributes to support embedded milvus lite
             "lite": False,
             "lite_folder_path": LLMWareConfig().get_library_path(),
             "lite_name": "milvus_lite.db",
             }

    @classmethod
    def get_config(cls, name):
        if name in cls._conf:
            return cls._conf[name]
        raise "Key not found in configs"

    @classmethod
    def set_config(cls, name, value):
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

        # canonical simple format of postgres uri string
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

    _conf = {
        "pinecone_api_key": os.environ.get("USER_MANAGED_PINECONE_API_KEY"),
        "pinecone_cloud": os.environ.get("USER_MANAGED_PINECONE_CLOUD"),
        "pinecone_region": os.environ.get("USER_MANAGED_PINECONE_REGION")
    }

    @classmethod
    def get_config(cls, name):
        if name in cls._conf:
            return cls._conf[name]
        raise ConfigKeyException(name)

    @classmethod
    def set_config(cls, name, value):
        cls._conf[name] = value


class LanceDBConfig:

    _conf = {'uri': '/tmp/lancedb/'}

    @classmethod
    def get_config(cls,name):
        if name in cls._conf:
            return cls._conf[name]
        raise ConfigKeyException(name)
    @classmethod
    def set_config(cls, name, value):
        cls._conf[name] = value


class SQLiteConfig:

    """Configuration object for SQLite"""

    _conf = {"host": os.environ.get("USER_MANAGED_SQLITE_HOST", "localhost"),
             "port": os.environ.get("USER_MANAGED_SQLITE_PORT", 6333),
             "sqlite_db_folder_path": LLMWareConfig().get_library_path(),
             "user_name": "",
             "pw": "",
             "db_name": "sqlite_llmware.db",
             # add new parameter for SQLTables
             "db_experimental": "sqlite_experimental.db"}

    @classmethod
    def get_config(cls, name):
        if name in cls._conf:
            return cls._conf[name]
        raise ConfigKeyException(name)

    @classmethod
    def set_config(cls, name, value):
        cls._conf[name] = value

    @classmethod
    def get_uri_string (cls):
        """For SQLite the URI string is the local file with full absolute path"""
        db_file = os.path.join(cls._conf["sqlite_db_folder_path"], cls._conf["db_name"])
        return db_file

    @classmethod
    def get_uri_string_experimental_db(cls):
        """For SQLite the URI string is the local file with full absolute path"""

        # used in SQLTables DB in llmware.agents module

        db_file = os.path.join(cls._conf["sqlite_db_folder_path"], cls._conf["db_experimental"])
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

    _conf = {
        "location": os.environ.get("USER_MANAGED_QDRANT_LOCATION", None),
        "host": os.environ.get("USER_MANAGED_QDRANT_HOST", None),
        "url": os.environ.get("USER_MANAGED_QDRANT_URL", None),
        "path": os.environ.get("USER_MANAGED_QDRANT_PATH", None),
        "port": os.environ.get("USER_MANAGED_QDRANT_PORT", 6333),
        "grpc_port": os.environ.get("USER_MANAGED_QDRANT_GRPC_PORT", 6334),
        "https": os.environ.get("USER_MANAGED_QDRANT_HTTPS", None),
        "api_key": os.environ.get("USER_MANAGED_QDRANT_API_KEY", None),
        "prefix": os.environ.get("USER_MANAGED_QDRANT_PREFIX", None),
        "timeout": os.environ.get("USER_MANAGED_QDRANT_TIMEOUT", None),
        "prefer_grpc": os.environ.get("USER_MANAGED_QDRANT_PREFER_GRPC", False),
        "force_disable_check_same_thread": os.environ.get(
            "USER_MANAGED_QDRANT_FORCE_DISABLE_CHECK_SAME_THREAD", False
        ),
    }

    @classmethod
    def get_config(cls, name=None):
        if not name:
            return cls._conf

        if name in cls._conf:
            return cls._conf[name]
        raise ConfigKeyException(name)

    @classmethod
    def set_config(cls, name, value):
        cls._conf[name] = value


class AWSS3Config:

    """Configuration object for AWS S3"""

    _conf = {"access_key": os.environ.get("USER_MANAGED_S3_ACCESS_KEY", ""),
             "secret_key": os.environ.get("USER_MANAGED_S#_SECRET_KEY", "")}

    @classmethod
    def get_config(cls, name):
        if name in cls._conf:
            return cls._conf[name]
        raise ConfigKeyException(name)

    @classmethod
    def set_config(cls, name, value):
        cls._conf[name] = value


class LLMWareTableSchema:

    """ Table Schema used for Parsing, Library Cards and other llmware modules.  """

    #   notes:
    #   1.  bigserial type for Postgres
    #   2.  "text" and "table" replaced with "text_block" and "table_block" in SQL DB for safety / reserved

    _block = {"_id": "bigserial",
              "block_ID": "integer",
              "doc_ID": "integer",
              "content_type": "text",
              "file_type": "text",
              "master_index": "integer",
              "master_index2": "integer",
              "coords_x": "integer",
              "coords_y": "integer",
              "coords_cx": "integer",
              "coords_cy": "integer",
              "author_or_speaker": "text",
              "added_to_collection": "text",
              "file_source": "text",
              "table_block": "text",
              "modified_date": "text",
              "created_date": "text",
              "creator_tool": "text",
              "external_files": "text",
              "text_block": "text",
              "header_text": "text",
              "text_search": "text",
              "user_tags": "text",
              "special_field1": "text",
              "special_field2": "text",
              "special_field3": "text",
              "graph_status": "text",
              "dialog": "text",
              "embedding_flags": "jsonb",
              "PRIMARY KEY": "(_id)"}

    _library_card = {"library_name": "text",
                     "embedding": "json",
                     "knowledge_graph": "text",
                     "unique_doc_id": "integer",
                     "documents": "integer",
                     "blocks": "integer",
                     "images": "integer",
                     "pages": "integer",
                     "tables": "integer",
                     "account_name": "text",
                     "PRIMARY KEY": "(library_name)"}

    #   used for basic tests of db connectivity and access
    _simple_test = {"library_name": "text",
                    "hello_number": "integer"}

    _status = {"key": "text",
               "summary": "text",
               "start_time": "text",
               "end_time": "text",
               "total": "integer",
               "current": "integer",
               "units": "text",
               "PRIMARY KEY": "(key)"}

    _parser_record = {"_id": "bigserial",
                      "job_id": "text",
                      "parser_type": "text",
                      "library_name": "text",
                      "account_name": "text",
                      "file_name": "text",
                      "message": "text",
                      "ocr_flag": "text",
                      "fail_flag": "text",
                      "time_stamp": "text",
                      "PRIMARY KEY": "(_id)"}

    _reserved_schema_names = ["block", "library", "status", "parser_record"]

    _custom_schema_names = []

    _custom_schema = []

    @classmethod
    def get_block_schema(cls):
        return cls._block

    @classmethod
    def get_library_card_schema(cls):
        return cls._library_card

    @classmethod
    def get_status_schema(cls):
        return cls._status

    @classmethod
    def get_parser_table_schema(cls):
        return cls._parser_record

    @classmethod
    def register_custom_schema(cls, table_name, schema,replace=False):

        if table_name not in cls._custom_schema_names:
            cls._custom_schema_names.append(table_name)

        if table_name not in cls._custom_schema:
            cls._custom_schema.append({table_name: schema})
        else:
            if replace:
                cls._custom_schema.append({table_name: schema})

        return cls._custom_schema

    @classmethod
    def get_custom_tables(cls):
        return cls._custom_schema_names

    @classmethod
    def get_custom_schema(cls):
        return cls._custom_schema


class Neo4jConfig:
    """Configuration object for Neo4j"""

    _conf = {
        'uri': os.environ.get('NEO4J_URI', 'neo4j://localhost:7687'),
        'user': os.environ.get('NEO4J_USERNAME', 'neo4j'),
        'password': os.environ.get('NEO4J_PASSWORD', 'neo4j'),
        'database': os.environ.get('NEO4J_DATABASE', 'llmware')
    }

    @classmethod
    def get_db_configs(cls):
        configs = {}
        for keys, values in cls._conf.items():
            configs.update({keys:values})
        return configs

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
        return cls._conf["uri"]

    @classmethod
    def get_user_name(cls):
        return cls._conf["user"]

    @classmethod
    def get_db_pw(cls):
        return cls._conf["password"]

    @classmethod
    def get_database_name(cls):
        return cls._conf["database"]


class ChromaDBConfig:

    """Configuration object for chroma.

    Update - v0.2.12 - default is set to use chroma as a file-based local persistent storage.
    This is a change from the previous default which used chroma as an in-memory (ephemeral) store.

    Chroma can be used with or without (default) a client/server architecture. If it is used with a client/server
    architecture, you have to set the authentication mechanism. The authentication mechanism can be either
    username/password or token.
    - env variable CHROMA_HOST is None -> not client/server mode (default),
    - env variable CHROMA_HOST is set -> client/server mode

    If you want to use Chroma without the client/server architecture, the env variable CHROMA_HOST has to be
    None (default). In this mode, you can choose between in-memory (also called ephemeral, non-persistent) and
    persistent.

    Update: starting v0.2.12 - persistent path set as default to LLMWareConfigs().library_path(), which is the
    same default path for a local sqlite.db
    - to change to in-memory / non-persistent, set this config to None
    -   e.g.,  ChromaDBConfig().set_config("persistent_path", None)

    If you want to use Chroma in client/server mode, the env variable CHROMA_HOST needs to be set. In addition,
    you have to set
    - env variable CHROMA_SERVER_AUTH_PROVIDER, and
    - env variable CHROMA_SERVER_AUTH_CREDENTIALS_PROVIDER
    the value depends on the authentication mechanism you want to use.

    For more information, please visit https://docs.trychroma.com/getting-started
    """

    _conf = {

        # update - v0.2.12 -> collection on ChromaDB corresponds with the LLMWare library name
        # 'collection': os.environ.get('CHROMA_COLLECTION', 'llmware'),

        #
        # update - v0.2.12 -> by default, persistent path set to make chroma persistent.
        # If this is None, then an in-memory only chroma instance will be created.
        #

        'persistent_path': LLMWareConfig().get_library_path(),

        #
        # Configs below are only relevant when chromadb is run in client/server mode.
        #

        'host': os.environ.get('CHROMA_HOST', None),
        'port': os.environ.get('CHROMA_PORT', 8000),
        'ssl': os.environ.get('CHROMA_SSL', False),
        'headers': os.environ.get('CHROMA_HEADERS', {}),

        # The provider decides whether we use authentication via username and password, or via a token.
        # - For the username and password, this has to be set to chromadb.auth.basic.BasicAuthServerProvider
        # - For the token, this has to be set to chromadb.auth.token.TokenAuthServerProvider
        'auth_provider': os.environ.get('CHROMA_SERVER_AUTH_PROVIDER', None),

        # The credential provider supplies the username and password or the token. This setting hence
        # depends on the variable just above.
        # - For the username and password, this has to be set to chromadb.auth.providers.HtpasswdFileServerAuthCredentialsProvider
        # - For the token, this has to be set to chromadb.auth.token.TokenAuthServerProvider
        'auth_credentials_provider': os.environ.get('CHROMA_SERVER_AUTH_CREDENTIALS_PROVIDER', None),

        # Settings for authentication via username and password.
        'user': os.environ.get('CHROMA_USERNAME', 'admin'),
        'password': os.environ.get('CHROMA_PASSWORD', 'admin'),
        'auth_credentials_file': os.environ.get('CHROMA_SERVER_AUTH_CREDENTIALS_FILE', 'server.htpasswd'),

        # Settings for authentication via token.
        'auth_credentials': os.environ.get('CHROMA_SERVER_AUTH_CREDENTIALS', None),
        'auth_token_transport_header': os.environ.get('CHROMA_SERVER_AUTH_TOKEN_TRANSPORT_HEADER', None),
    }

    @classmethod
    def get_db_configs(cls):
        configs = {}
        for keys, values in cls._conf.items():
            configs.update({keys:values})
        return configs

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
        return cls._conf["uri"]

    @classmethod
    def get_user_name(cls):
        return cls._conf["user"]

    @classmethod
    def get_db_pw(cls):
        return cls._conf["password"]

    @classmethod
    def get_auth_provider(cls):
        return cls._conf["auth_provider"]

    @classmethod
    def get_auth_credentials_provider(cls):
        return cls._conf["auth_credentials_provider"]

    @classmethod
    def get_auth_credentials_file(cls):
        return cls._conf["auth_credentials_file"]

    @classmethod
    def get_auth_credentials(cls):
        return cls._conf["auth_credentials"]

    @classmethod
    def get_auth_token_transport_header(cls):
        return cls._conf["auth_token_transport_header"]


class OpenAIConfig:

    """Configuration object for OpenAI - primarily for configuring Azure OpenAI credentials.

     Primary use is to setup an AzureOpenAI client that will be used in place of the standard
     OpenAI client.

     Within LLMWare, the OpenAI model classes will check this config before creating a new OpenAI client.

     If there is a client already established in _conf["openai_client"], that client will be used in the
     inference/embedding process.

     For example:

        # create your AzureOpenAI client

        from openai import AzureOpenAI

        client = AzureOpenAI(
                            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                            api_version="2024-02-01")

        # add that client to the OpenAIConfig:

        OpenAIConfig().set_azure_client(client)

     """

    _conf = {"openai_client": None,
             "api_key": None,               # placeholder / not used currently
             "api_version": None,           # placeholder / not used currently
             "use_azure_endpoint": False}   # placeholder / not used currently

    @classmethod
    def get_config(cls, name):
        if name in cls._conf:
            return cls._conf[name]
        raise ConfigKeyException(name)

    @classmethod
    def set_config(cls, name, value):
        cls._conf[name] = value

    @classmethod
    def set_azure_client(cls, azure_client):
        cls._conf["openai_client"] = azure_client

    @classmethod
    def get_azure_client(cls):
        return cls._conf["openai_client"]


