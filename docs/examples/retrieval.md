---
layout: default
title: Retrieval
parent: Examples
nav_order: 7
description: overview of the major modules and classes of LLMWare  
permalink: /examples/retrieval
---
# Retrieval - Introduction by Examples
We introduce ``llmware`` through self-contained examples.

# SEMANTIC Retrieval Example

```python

"""
This 'getting started' example demonstrates how to use basic semantic retrieval with the Query class
      1. Create a sample library
      2. Run a basic semantic query
      3. View the results
"""

import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup
from llmware.configs import LLMWareConfig


def create_fin_docs_sample_library(library_name):

    print(f"update: creating library - {library_name}")

    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files(over_write=False)
    ingestion_folder_path = os.path.join(sample_files_path, "FinDocs")
    parsing_output = library.add_files(ingestion_folder_path)

    print(f"update: building embeddings - may take a few minutes the first time")

    #   note: if you have installed Milvus or another vector DB, please feel free to substitute
    #   note: if you have any memory constraints on laptop:
    #       (1) reduce embedding batch_size or ...
    #       (2) substitute "mini-lm-sbert" as embedding model

    library.install_new_embedding(embedding_model_name="industry-bert-sec", vector_db="chromadb",batch_size=200)

    return library


def basic_semantic_retrieval_example (library):

    # Create a Query instance
    q = Query(library)

    # Set the keys that should be returned - optional - full set of keys will be returned by default
    q.query_result_return_keys = ["distance","file_source", "page_num", "text"]

    # perform a simple query
    my_query = "ESG initiatives"
    query_results1 = q.semantic_query(my_query, result_count=20)

    # Iterate through query_results, which is a list of result dicts
    print(f"\nQuery 1 -  {my_query}")
    for i, result in enumerate(query_results1):
        print("results - ", i, result)

    # perform another query
    my_query2 = "stock performance"
    query_results2 = q.semantic_query(my_query2, result_count=10)

    print(f"\nQuery 2 - {my_query2}")
    for i, result in enumerate(query_results2):
        print("results - ", i, result)

    # perform another query
    my_query3 = "cloud computing"

    # note: use of embedding_distance_threshold will cap results with distance < 1.0
    query_results3 = q.semantic_query(my_query3, result_count=50, embedding_distance_threshold=1.0)

    print(f"\nQuery 3 - {my_query3}")
    for i, result in enumerate(query_results3):
        print("result - ", i, result)

    return [query_results1, query_results2, query_results3]


if __name__ == "__main__":

    print(f"Example - Running a Basic Semantic Query")

    LLMWareConfig().set_active_db("sqlite")

    # step 1- will create library + embeddings with Financial Docs
    lib = create_fin_docs_sample_library("lib_semantic_query_1")

    # step 2- run query against the library and embeddings
    my_results = basic_semantic_retrieval_example(lib)
```

For more examples, see the [retrieval examples]((https://www.github.com/llmware-ai/llmware/tree/main/examples/Retrieval/) in the main repo.   

Check back often - we are updating these examples regularly - and many of these examples have companion videos as well.  



# More information about the project - [see main repository](https://www.github.com/llmware-ai/llmware.git)


# About the project

`llmware` is &copy; 2023-{{ "now" | date: "%Y" }} by [AI Bloks](https://www.aibloks.com/home).

## Contributing
Please first discuss any change you want to make publicly, for example on GitHub via raising an [issue](https://github.com/llmware-ai/llmware/issues) or starting a [new discussion](https://github.com/llmware-ai/llmware/discussions).
You can also write an email or start a discussion on our Discrod channel.
Read more about becoming a contributor in the [GitHub repo](https://github.com/llmware-ai/llmware/blob/main/CONTRIBUTING.md).

## Code of conduct
We welcome everyone into the ``llmware`` community.
[View our Code of Conduct](https://github.com/llmware-ai/llmware/blob/main/CODE_OF_CONDUCT.md) in our GitHub repository.

## ``llmware`` and [AI Bloks](https://www.aibloks.com/home)
``llmware`` is an open source project from [AI Bloks](https://www.aibloks.com/home) - the company behind ``llmware``.
The company offers a Software as a Service (SaaS) Retrieval Augmented Generation (RAG) service.
[AI Bloks](https://www.aibloks.com/home) was founded by [Namee Oberst](https://www.linkedin.com/in/nameeoberst/) and [Darren Oberst](https://www.linkedin.com/in/darren-oberst-34a4b54/) in October 2022.

## License

`llmware` is distributed by an [Apache-2.0 license](https://www.github.com/llmware-ai/llmware/blob/main/LICENSE).

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
        <a href="https://huggingface.co/llmware"><span><img src="assets/images/hf-logo.svg" alt="Hugging Face" class="hugging-face-logo"/></span></a>
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

