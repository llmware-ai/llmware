---
layout: default
title: Platforms Supported
parent: Getting Started
nav_order: 5
permalink: /getting_started/platforms
---
___  
# Platform Support
___

**Platform Supported**

- **Python 3.9+**  (note that we just added support for 3.12 starting in llmware version 0.2.12)  


- **System RAM**:  recommended 16 GB RAM minimum (to run most local models on CPU)  


- **OS Supported**:  Mac OS M1/M2/M3, Windows, Linux Ubuntu 20/22.  We regularly build and test on Windows and Linux platforms with and without CUDA drivers.


- **Deprecated OS**:  Linux Aarch64 (0.2.6) and Mac x86 (0.2.10) - most features of llmware should work on these platforms, but new features integrated since those versions will not be available.  If you have a particular need to work on one of these platforms, please raise an Issue, and we can work with you to try to find a solution.  


- **Linux**:  we build to GLIBC 2.31+ - so Linux versions with older GLIBC drivers will generally not work (e.g., Ubuntu 18).  To check the GLIBC version, you can use the command `ldd --version`.  If it is 2.31 or any higher version, it should work.  

___

___
**Database**  

- LLMWare is an enterprise-grade data pipeline designed for persistent storage of key artifacts throughout the pipeline.  We provide several options to parse 'in-memory' and write to jsonl files, but most of the functionality of LLMWare assumes that a persistent scalable data store will be used.   


- There are three different types of data storage used in LLMWare:

    1.  **Text Collection database** - all of the LLMWare parsers, by default, parse and text chunk unstructured content (and associated metadata) into one of three databases used for text collections, organized in Libraries - **MongoDB**, **Postgres** and **SQLite**.  

    2.  **Vector database** - for storing and retrieving semantic embedding vectors, LLMWare supports the following vector databases - Milvus, PG Vector / Postgres, Qdrant, ChromaDB, Redis, Neo4J, Lance DB, Mongo-Atlas, Pinecone and FAISS.  
  
    3.  **SQL Tables database** - for easily integrating table-based data into LLM workflows through the CustomTable class and for using in conjunction with a Text-2-SQL workflow - supported on Postgres and SQLite.  


- **Fast Start** option:  you can start using SQLite locally without any separate installation by setting `LLMWareConfig.set_active_db("sqlite")` as shown in [configure_db_example](https://www.github.com/llmware-ai/llmware/blob/main/examples/Getting_Started/configure_db.py).  For vector embedding examples, you can use ChromaDB, LanceDB or FAISS - all of which provide no-install options - just start using.  


- **Install DB dependencies**:  we provide a number of Docker-Compose scripts which can be used, or follow install instructions provided by the database - generally easiest to install locally with Docker.  


**LLMWare File Storage**

- llmware stores a variety of artifacts during its operation locally in the /llmware_data path, which can be found as follows:  

```python
from llmware.configs import LLMWareConfig
llmware_fp = LLMWareConfig().get_llmware_path()
print("llmware_data path: ", llmware_fp)
```

- to change the llmware path, we can change both the 'home' path, which is the main filepath, and the 'llmware_data' path name 
as follows:  

```python

from llmware.configs import LLMWareConfig

# changing the llmware home path - change home + llmware_path_name
LLMWareConfig().set_home("/my/new/local/home/path")
LLMWareConfig().set_llmware_path_name("llmware_data2")

# check the new llmware home path
llmware_fp = LLMWareConfig().get_llmware_path()
print("updated llmware path: ", llmware_fp)

```

___

___
**Local Models**

- LLMWare treats open source and locally deployed models as "first class citizens" with all classes, methods and examples designed to work first with smaller, specialized, locally-deployed models.  
- By default, most models are pulled from public HuggingFace repositories, and cached locally.  LLMWare will store all models locally at the /llmware_data/model_repo path, with all assets found in a folder tree with the models name.  
- If a Pytorch model is pulled from HuggingFace, then it will appear in the default HuggingFace /.cache path.   
- To view the local model path:  

```python
from llmware.configs import LLMWareConfig

model_fp = LLMWareConfig().get_model_repo_path()
print("model repo path: ", model_fp)

```


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
