---
layout: default
title: Embedding Models
parent: Components
nav_order: 6
description: overview of the major modules and classes of LLMWare  
permalink: /components/embedding_models
---
# Embedding Models
---

llmware supports 30+ embedding models out of the box in the default ModelCatalog, with easy extensibility to add other 
popular open source embedding models from HuggingFace or Sentence Transformers.  

To get a list of the currently supported embedding models:  

```python
from llmware.models import ModelCatalog
embedding_models = ModelCatalog().list_embedding_models()
for i, models in enumerate(embedding_models):
    print(f"embedding models: {i} - {models}")
```

Supported popular models include:  
- Sentence Transformers - `all-MiniLM-L6-v2`, `all-mpnet-base-v2`  
- Jina AI - `jinaai/jina-embeddings-v2-base-en`, `jinaai/jina-embeddings-v2-small-en`  
- Nomic - `nomic-ai/nomic-embed-text-v1`  
- Industry BERT - `industry-bert-insurance`, `industry-bert-contracts`, `industry-bert-asset-management`, `industry-bert-sec`, `industry-bert-loans`  
- OpenAI - `text-embedding-ada-002`, `text-embedding-3-small`, `text-embedding-3-large`

We also support top embedding models from BAAI, thenlper, llmrails/ember, Google, and Cohere.  We are constantly looking to add new innovative open source models to this list 
so please let us know if you are looking for support for a specific embedding model, and usually within 1-2 days, we can test and add to the ModelCatalog.  

# Using an Embedding Model  

Embedding models in llmware can be installed directly by `ModelCatalog().load_model("model_name")`, but in most cases, 
the name of the embedding model will be passed to the `install_new_embedding` handler in the Library class when creating a new 
embedding.   Once that is completed, the embedding model is captured in the Library metadata on the LibraryCard as part of the 
embedding record for that library, and as a result, often times, does not need to be used explicitly again, e.g.,  

```python

from llmware.library import Library

library = Library().create_new_library("my_library")

# parses the content from the documents in the file path, text chunks and indexes in a text collection database
library.add_files(input_folder_path="/local/path/to/my_files", chunk_size=400, max_chunk_size=600, smart_chunking=1)

# creates embeddings - and keeps synchronized records of which text chunks have been embedded to enable incremental use
library.install_new_embedding(embedding_model_name="jinaai/jina-embeddings-v2-small-en", 
                              vector_db="milvus",
                              batch_size=100)
```

Once the embeddings are installed on the library, you can look up the embedding status to see the updated embeddings, and confirm that 
the model has been correctly captured:  

```python

from llmware.library import Library
library = Library().load_library("my_library")
embedding_record = library.get_embedding_status()
print("\nupdate:  embedding record - ", embedding_record)
```

And then you can run semantic retrievals on the Library, using the Query class in the retrievals module, e.g.:

```python 
from llmware.library import Library
from llmware.retrieval import Query
library = Library().load_library("my_library")
#   queries are constructed by creating a Query object, and passing a library as input
query_results = Query(library).semantic_query("my query", result_count=20)
for qr in query_results:
    print("my query results: ", qr)
```


Need help or have questions?
============================

Check out the [llmware videos](https://www.youtube.com/@llmware) and [GitHub repository](https://github.com/llmware-ai/llmware).

Reach out to us on [GitHub Discussions](https://github.com/llmware-ai/llmware/discussions).


# About the project

`llmware` is &copy; 2023-{{ "now" | date: "%Y" }} by [AI Bloks](https://www.aibloks.com/home).

## Contributing
Please first discuss any change you want to make publicly, for example on GitHub via raising an [issue](https://github.com/llmware-ai/llmware/issues) or starting a [new discussion](https://github.com/llmware-ai/llmware/discussions).
You can also write an email or start a discussion on our Discord channel.
Read more about becoming a contributor in the [GitHub repo](https://github.com/llmware-ai/llmware/blob/main/CONTRIBUTING.md).

## Code of conduct
We welcome everyone into the ``llmware`` community.
[View our Code of Conduct](https://github.com/llmware-ai/llmware/blob/main/CODE_OF_CONDUCT.md) in our GitHub repository.

## ``llmware`` and [AI Bloks](https://www.aibloks.com/home)
``llmware`` is an open source project from [AI Bloks](https://www.aibloks.com/home) - the company behind ``llmware``.
The company offers a Software as a Service (SaaS) Retrieval Augmented Generation (RAG) service.
[AI Bloks](https://www.aibloks.com/home) was founded by [Namee Oberst](https://www.linkedin.com/in/nameeoberst/) and [Darren Oberst](https://www.linkedin.com/in/darren-oberst-34a4b54/) in October 2022.

## License

`llmware` is distributed by an [Apache-2.0 license](https://github.com/llmware-ai/llmware/blob/main/LICENSE).

## Thank you to the contributors of ``llmware``!
<ul class="list-style-none">
{% for contributor in site.github.contributors %}
  <li class="d-inline-block mr-1">
     <a href="{{ contributor.html_url }}">
        <img src="{{ contributor.avatar_url }}" width="32" height="32" alt="{{ contributor.login }}">
    </a>
  </li>
{% endfor %}
</ul>


---
<ul class="list-style-none">
    <li class="d-inline-block mr-1">
        <a href="https://discord.gg/MhZn5Nc39h"><span><i class="fa-brands fa-discord"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://www.youtube.com/@llmware"><span><i class="fa-brands fa-youtube"></i></span></a>
    </li>
   <li class="d-inline-block mr-1">
    <a href="https://huggingface.co/llmware"><span> <img src="https://huggingface.co/front/assets/huggingface_logo-noborder.svg" alt="Hugging Face" class="hugging-face-logo"/> </span></a>
     </li>
    <li class="d-inline-block mr-1">
        <a href="https://www.linkedin.com/company/aibloks/"><span><i class="fa-brands fa-linkedin"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://twitter.com/AiBloks"><span><i class="fa-brands fa-square-x-twitter"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://www.instagram.com/aibloks/"><span><i class="fa-brands fa-instagram"></i></span></a>
    </li>
</ul>
---

