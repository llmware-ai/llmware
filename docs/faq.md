---
layout: default
title: Freqently Asked Questions
nav_order: 12
permalink: /faq
---
# Frequently Asked Questions (FAQ)


### How can I set the chunk size?
#### "I wnat to parse my documents into smaller chunks"
You can set the chunk size with the ``chunk_size`` parameter of the ``add_files`` method.

The ``add_files`` method from the ``Library`` class has a ``chunk_size`` parameter that controls the chunk size.
The method in addition has a parameter to control the maxium chunk size with ``max_chunk_size``.
These two parameters are passed on to the ``Parser`` class.
In the following example, we add the same files with different chunk sizes to the library ``chunk_size_example``.
```python
from pathlib import Path

from llmware.library import Library


path_to_my_library_files = Path('~/llmware_data/sample_files/Agreements')

my_library = Library().create_new_library(library_name='chunk_size_example')
my_library.add_files(input_folder_path=path_to_my_library_files, chunk_size=400)
my_library.add_files(input_folder_path=path_to_my_library_files, chunk_size=600)
```

### How can I set the embedding store?
#### "I want to use a specific embedding store"
You can set the embedding store with the ``vector_db`` parameter of the ``install_new_embedding`` method, which you call on a ``Library`` object eacht time you want to create an embedding for a *library*.

The ``install_new_embedding`` method from the ``Library`` class has a ``vector_db`` parameter that sets the embedding store.
At the moment of this writting, *LLMWare* supports the embedding stores [chromadb](https://github.com/chroma-core/chroma), [neo4j](https://github.com/neo4j/neo4j), [milvus](https://github.com/milvus-io/milvus), [pg_vector](https://github.com/pgvector/pgvector), [postgres](https://github.com/postgres/postgres), [redis](https://github.com/redis/redis), [pinecone](https://www.pinecone.io/), [faiss](https://github.com/facebookresearch/faiss), [qdrant](https://github.com/qdrant/qdrant), [mongo atlas](https://www.mongodb.com/products/platform/atlas-database), and [lancedb](https://github.com/lancedb/lancedb).
In the following example, we create the same embeddings three times for the same library, but store them in three different embedding stores.
```python
import logging
from pathlib import Path

from llmware.configs import LLMWareConfig
from llmware.library import Library


logging.info(f'Currently supported embedding stores: {LLMWareConfig().get_supported_vector_db()}')

library = Library().create_new_library(library_name='embedding_store_example')
library.add_files(input_foler_path=Path('~/llmware_data/sample_files/Agreements'))

library.install_new_embedding(vector_db="pg_vector")
library.install_new_embedding(vector_db="milvus")
library.install_new_embedding(vector_db="faiss")
```

### How can I set the collection store?
#### "I want to use a specific collection store"
You can set the collection store with the ``set_active_db`` method of the ``LLMWareConfig`` class.

The collection store is set using the ``LLMWareConfig`` class with the ``set_active_db`` method.
At the time of writting, **LLMWare** supports the three collection stores *MongoDB*, *Postgres*, and *SQLite* - which is the default.
You can retrieve the supported collection store with the method ``get_supported_collection_db``.
In the example below, we first print the currently active collection store, then we retrieve the supported collection stores, before we swith to *Postgres*.

```python
import logging

from llmware.configs import LLMWareConfig


logging.info(f'Currently active collection store: {LLMWareConfig.get_active_db()}')
logging.info(f'Currently supported collection stores: {LLMWareConfig().get_supported_collection_db()}')

LLMWareConfig.set_active_db("postgres")
logging.info(f'Currently active collection store: {LLMWareConfig.get_active_db()}')
```


### How can I retrieve more context?
#### "I want to retrieve more context from a query"


### How can I set the Large Language Model?
#### "I want to use a different LLM"

### How can I set the embedding model?
#### "I want to use a different embedding model"
