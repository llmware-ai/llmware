from llmware.configs import LLMWareConfig
from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection

connections.connect("default", host=LLMWareConfig().milvus_host, port=LLMWareConfig().milvus_port)
collections = utility.list_collections()
for collection in collections:
    utility.drop_collection(collection)