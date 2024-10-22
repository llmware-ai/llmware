---
layout: default
title: Query  
parent: Components
nav_order: 8
description: overview of the major modules and classes of LLMWare  
permalink: /components/query
---
# Retrieval & Query
---

Query libraries with mix of text, semantic, hybrid, metadata, and custom filters.  The retrieval.py module implements the 
`Query` class, which is the primary way that search and retrieval is performed.   Each `Query` object, when constructed, 
requires that a Library is passed as a mandatory parameter in the constructor.  The Query object will operate against that 
Library, and have access to all of Library's specific attributes, metadata and methods.  

Retrievals in llmware leverage the Library abstraction as the primary unit against which a particular query or retrieval is 
executed.  This provides the ability to have multiple distinct knowledge-bases, potentially aligned to different use cases, and/or 
users, accounts and permissions.  

# Executing Queries

```python
from llmware.retrieval import Query
from llmware.library import Library

#   step 1 - load a previously created library
lib = Library().load_library("my_library")

#   step 2 - create a query object
q = Query(lib)

#    step 3 - run lots of different queries  (many other options in the examples)

#    basic text query
results1 = q.text_query("text query", result_count=20, exact_mode=False)

#    semantic query
results2 = q.semantic_query("semantic query", result_count=10)

#    combining a text query restricted to only certain documents in the library and "exact" match to the query
results3 = q.text_query_with_document_filter("new query", {"file_name": "selected file name"}, exact_mode=True)

#   to apply a specific embedding (if multiple on library), pass the names when creating the query object
q2 = Query(lib, embedding_model_name="mini_lm_sbert", vector_db="milvus")
results4 = q2.semantic_query("new semantic query")
```



Need help or have questions?
============================

Check out the [llmware videos](https://www.youtube.com/@llmware) and [GitHub repository](https://github.com/llmware-ai/llmware).

Reach out to us on [GitHub Discussions](https://github.com/llmware-ai/llmware/discussions).


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
[AI Bloks](https://www.aibloks.com/home) was founded by [Namee Oberst](https://www.linkedin.com/in/nameeoberst/) and [Darren Oberst](https://www.linkedin.com/in/darren-oberst-34a4b54/) in Oktober 2022.

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

