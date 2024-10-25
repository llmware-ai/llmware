---
layout: default
title: FAQ
parent: Community
nav_order: 1
description: overview of the major modules and classes of LLMWare  
permalink: /community/faq
---
# Frequently Asked Questions (FAQ)


### How can I set the chunk size?
#### "I want to parse my documents into smaller chunks"
You can set the chunk size with the ``chunk_size`` parameter of the ``add_files`` method.

The ``add_files`` method from the ``Library`` class has a ``chunk_size`` parameter that controls the chunk size.
The method in addition has a parameter to control the maximum chunk size with ``max_chunk_size``.
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
You can set the embedding store with the ``vector_db`` parameter of the ``install_new_embedding`` method, which you call on a ``Library`` object each time you want to create an embedding for a *library*.

The ``install_new_embedding`` method from the ``Library`` class has a ``vector_db`` parameter that sets the embedding store.
At the moment of this writing, *LLMWare* supports the embedding stores [chromadb](https://github.com/chroma-core/chroma), [neo4j](https://github.com/neo4j/neo4j), [milvus](https://github.com/milvus-io/milvus), [pg_vector](https://github.com/pgvector/pgvector), [postgres](https://github.com/postgres/postgres), [redis](https://github.com/redis/redis), [pinecone](https://www.pinecone.io/), [faiss](https://github.com/facebookresearch/faiss), [qdrant](https://github.com/qdrant/qdrant), [mongo atlas](https://www.mongodb.com/products/platform/atlas-database), and [lancedb](https://github.com/lancedb/lancedb).
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
At the time of writing, **LLMWare** supports the three collection stores *MongoDB*, *Postgres*, and *SQLite* - which is the default.
You can retrieve the supported collection store with the method ``get_supported_collection_db``.
In the example below, we first print the currently active collection store, then we retrieve the supported collection stores, before we switch to *Postgres*.

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
One way to retrieve more context is to set the ``result_count`` parameter of the ``query``, ``text_query``, and ``semantic_query`` methods from the ``Query`` class.
By increasing ``result_count``, the number of retrieved results is increased which increases the context size.

The ``Query`` class has the methods ``query``, ``text_query``, and ``semantic_query`` methods which allow to set the number of retrieved results with ``result_count``.
On a side note, ``query`` is a wrapper function for ``text_query`` and ``semantic_query``.
The value of ``result_count`` is passed on to the queried embedding store to control the number of retrieved results.
For example, for *pgvector* ``result_count`` is passed on to the value after the ``LIMIT`` keyword.
In the ``SQL`` example below, you can see the resulting ``SQL`` query of ``LLMWare`` if ``result_count=10``, the name of the collection being ``agreements``, and the query vector being ``[1, 2, 3]``.
```sql
SELECT
    id,
    block_mongo_id,
    embedding <-> '[1, 2, 3]' AS distance,
    text
FROM agreements
ORDER BY distance
LIMIT 10;
```
In the following example, we execute the same query against a library twice but change the number of retrieved results from ``3`` to ``6``.
```python
import logging
from pathlib import Path

from llmware.configs import LLMWareConfig
from llmware.library import Library
from llmware.retrieval import Query

logging.info(f'Currently supported embedding stores: {LLMWareConfig().get_supported_vector_db()}')

library = Library().create_new_library(library_name='context_size_example')
library.add_files(input_foler_path=Path('~/llmware_data/sample_files/Agreements'))
library.install_new_embedding(vector_db="pg_vector")

query = Query(library)
query_results = query.semantic_query(query='salary', result_count=3, results_only=True)
logging.info(f'Number of results: {len(query_results)}')
query_results = query.semantic_query(query='salary', result_count=6, results_only=True)
logging.info(f'Number of results: {len(query_results)}')
```

### How can I set the Large Language Model?
#### "I want to use a different LLM"
You can set the Large Language Model (LLM) with the ``gen_model`` parameter of the ``load_model`` method from the ``Prompt`` class.

The ``Prompt`` class has the method ``load_model`` with the ``gen_model`` parameter which sets the LLM.
The ``gen_model`` parameter is passed on to the ``ModelCatalog`` class, which loads the LLM either from HuggingFace or from another source.
The ``ModelCatalog`` allows you to **list all available models** with the method ``list_generative_models``, or just the local models ``list_generative_local_models``, or just the open source models ``list_open_source_models``.
In the example below, we log all available LLMs, including the ones that are available locally and the open source ones, and also create the prompters.
Each prompter uses a different LLM from our [BLING model series](https://llmware.ai/about), which you can also find on [HuggingFace](https://huggingface.co/collections/llmware/bling-models-6553c718f51185088be4c91a).

```python
import logging

from llmware.models import ModelCatalog
from llmware.prompts import Prompt


llm_gen = ModelCatalog().list_generative_models()
logging.info(f'List of all LLMs: {llm_gen}')

llm_gen_local = ModelCatalog().list_generative_local_models()
logging.info(f'List of all local LLMs: {llm_local}')

llm_gen_open_source = ModelCatalog().list_open_source_models()
logging.info(f'List of all open source LLMs: {llm_gen_open_source}')


prompter_bling_1b = Prompt().load_model(gen_model='llmware/bling-1b-0.1')
prompter_bling_tiny_llama = Prompt().load_model(gen_model='llmware/bling-tiny-llama-v0')
prompter_bling_falcon_1b = Prompt().load_model(gen_model='llmware/bling-falcon-1b-0.1')
```

### How can I set the embedding model?
#### "I want to use a different embedding model"
You can set the embedding model with the ``embedding_model_name`` parameter of the ``install_new_embedding`` method from the ``Library`` class.

The ``Library`` class has the method ``install_new_embedding`` with the ``embedding_model_name`` parameter which sets the embedding model.
The ``ModelCatalog`` allows you to **list all available embedding models** with the ``list_embedding_models`` method.
In the following example, we list all available embedding models, and then we create a library with the name ``embedding_models_example``, which we embed two times with embedding models ``'mini-lm-sber'`` and ``'industry-bert-contracts'``.

```python
import logging

from llmware.models import ModelCatalog
from llmware.library import Library


embedding_models = ModelCatalog().list_generative_models()
logging.info(f'List of embedding models: {embedding_models}')


library = Library().create_new_library(library_name='embedding_models_example')
library.add_files(input_foler_path=Path('~/llmware_data/sample_files/Agreements'))

library.install_new_embedding(embedding_model_name='mini-lm-sber')
library.install_new_embedding(embedding_model_name='industry-bert-contracts')
```

### Why is the model running slowly in Google Colab? 
#### "I want to improve the performance of my model on Google Colab"

Our models are designed to run on at least 16GB of RAM. By default Google Colab provides ~13GB of RAM, which significantly slows computational speed. To ensure the best performance when using our models, we highly recommend enabling the T4 GPU in Colab. This will provide the notebook with additional resources, including 16GB of RAM, allowing our models to run smoothly and efficiently.

Steps to enabling T4 GPU in Colab:
1. In your Colab notebook, click on the "Runtime" tab
2. Select "Change runtime type"
3. Under "Hardware Accelerator", select T4 GPU

NOTE: There is a weekly usage limit on using T4 for free.