---
layout: default
title: Embedding
parent: Examples
nav_order: 5
description: overview of the major modules and classes of LLMWare  
permalink: /examples/embedding
---
# Embedding - Introduction by Examples
We introduce ``llmware`` through self-contained examples.

```python

""" This example is a fast start with Milvus Lite, which is a 'no-install' file-based version of Milvus, intended
for rapid prototyping.   A couple of key points to note:

    -- Platform - per Milvus docs, Milvus Lite is designed for Mac and Linux (not on Windows currently)
    -- PyMilvus - need to `pip install pymilvus>=2.4.2`
    -- within LLMWare:  set MilvusConfig().set_config("lite", True)
"""

import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup
from llmware.status import Status
from llmware.models import ModelCatalog
from llmware.configs import LLMWareConfig, MilvusConfig

from importlib import util

if not util.find_spec("pymilvus"):
    print("\nto run this example with pymilvus, you need to install pymilvus:  pip3 install pymilvus>=2.4.2")


def setup_library(library_name):

    """ Note: this setup_library method is provided to enable a self-contained example to create a test library """

    #   Step 1 - Create library which is the main 'organizing construct' in llmware
    print ("\nupdate: Creating library: {}".format(library_name))

    library = Library().create_new_library(library_name)

    #   check the embedding status 'before' installing the embedding
    embedding_record = library.get_embedding_status()
    print("embedding record - before embedding ", embedding_record)

    #   Step 2 - Pull down the sample files from S3 through the .load_sample_files() command
    #   --note: if you need to refresh the sample files, set 'over_write=True'
    print ("update: Downloading Sample Files")

    sample_files_path = Setup().load_sample_files(over_write=False)

    #   Step 3 - point ".add_files" method to the folder of documents that was just created
    #   this method parses the documents, text chunks, and captures in database

    print("update: Parsing and Text Indexing Files")

    library.add_files(input_folder_path=os.path.join(sample_files_path, "Agreements"),
                      chunk_size=400, max_chunk_size=600, smart_chunking=1)

    return library


def install_vector_embeddings(library, embedding_model_name):

    """ This method is the core example of installing an embedding on a library.
        -- two inputs - (1) a pre-created library object and (2) the name of an embedding model """

    library_name = library.library_name
    vector_db = LLMWareConfig().get_vector_db()

    print(f"\nupdate: Starting the Embedding: "
          f"library - {library_name} - "
          f"vector_db - {vector_db} - "
          f"model - {embedding_model_name}")

    #   *** this is the one key line of code to create the embedding ***
    library.install_new_embedding(embedding_model_name=embedding_model, vector_db=vector_db,batch_size=100)

    #   note: for using llmware as part of a larger application, you can check the real-time status by polling Status()
    #   --both the EmbeddingHandler and Parsers write to Status() at intervals while processing
    update = Status().get_embedding_status(library_name, embedding_model)
    print("update: Embeddings Complete - Status() check at end of embedding - ", update)

    # Start using the new vector embeddings with Query
    sample_query = "incentive compensation"
    print("\n\nupdate: Run a sample semantic/vector query: {}".format(sample_query))

    #   queries are constructed by creating a Query object, and passing a library as input
    query_results = Query(library).semantic_query(sample_query, result_count=20)

    for i, entries in enumerate(query_results):

        #   each query result is a dictionary with many useful keys

        text = entries["text"]
        document_source = entries["file_source"]
        page_num = entries["page_num"]
        vector_distance = entries["distance"]

        #   to see all of the dictionary keys returned, uncomment the line below
        #   print("update: query_results - all - ", i, entries)

        #  for display purposes only, we will only show the first 125 characters of the text
        if len(text) > 125:  text = text[0:125] + " ... "

        print("\nupdate: query results - {} - document - {} - page num - {} - distance - {} "
              .format( i, document_source, page_num, vector_distance))

        print("update: text sample - ", text)

    #   lets take a look at the library embedding status again at the end to confirm embeddings were created
    embedding_record = library.get_embedding_status()

    print("\nupdate:  embedding record - ", embedding_record)

    return 0


if __name__ == "__main__":

    #   Fast Start configuration - will use no-install embedded sqlite
    #   -- if you have installed Mongo or Postgres, then change the .set_active_db accordingly

    LLMWareConfig().set_active_db("sqlite")

    #   set the "lite" flag in MilvusConfig to True -> to use server version, set to False (which is default)
    MilvusConfig().set_config("lite", True)
    LLMWareConfig().set_vector_db("milvus")

    #   Step 1 - create library
    library = setup_library("ex2_milvus_lite")

    #   Step 2 - Select any embedding model in the LLMWare catalog

    #   to see a list of the embedding models supported, uncomment the line below and print the list
    embedding_models = ModelCatalog().list_embedding_models()

    #   for i, models in enumerate(embedding_models):
    #       print("embedding models: ", i, models)

    #   for this first embedding, we will use a very popular and fast sentence transformer
    embedding_model = "mini-lm-sbert"

    #   note: if you want to swap out "mini-lm-sbert" for Open AI 'text-embedding-ada-002', uncomment these lines:
    #   embedding_model = "text-embedding-ada-002"
    #   os.environ["USER_MANAGED_OPENAI_API_KEY"] = "<insert-your-openai-api-key>"

    #   run the core script
    install_vector_embeddings(library, embedding_model)
```


For more examples, see the [embedding examples]((https://www.github.com/llmware-ai/llmware/tree/main/examples/Embedding/) in the main repo.   


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

