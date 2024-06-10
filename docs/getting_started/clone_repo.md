---
layout: default
title: Clone Repo
parent: Getting Started
nav_order: 3
permalink: /getting_started/clone_repo
---

## ✍️ Working with the llmware Github repository

The llmware repo can be pulled locally to get access to all the examples, or to work directly with the latest version of the llmware code.  

```bash
git clone git@github.com:llmware-ai/llmware.git
```  

We have provided a **welcome_to_llmware** automation script in the root of the repository folder.  After cloning:  
- On Windows command line:  `.\welcome_to_llmware_windows.sh`  
- On Mac / Linux command line:  `sh ./welcome_to_llmware.sh`  

Alternatively, if you prefer to complete setup without the welcome automation script, then the next steps include:  

1.  **install requirements.txt** - inside the /llmware path - e.g., ```pip3 install -r llmware/requirements.txt```  

2.  **install requirements_extras.txt** - inside the /llmware path - e.g., ```pip3 install -r llmware/requirements_extras.txt```  (Depending upon your use case, you may not need all or any of these installs, but some of these will be used in the examples.)  

3.  **run examples** - copy one or more of the example .py files into the root project path.   (We have seen several IDEs that will attempt to run interactively from the nested /example path, and then not have access to the /llmware module - the easy fix is to just copy the example you want to run into the root path).  

4.  **install vector db** - no-install vector db options include milvus lite, chromadb, faiss and lancedb - which do not require a server install, but do require that you install the python sdk library for that vector db, e.g., `pip3 install pymilvus`, or `pip3 install chromadb`.  If you look in [examples/Embedding](https://github.com/llmware-ai/llmware/tree/main/examples/Embedding), you will see examples for getting started with various vector DB, and in the root of the repo, you will see easy-to-get-started docker compose scripts for installing milvus, postgres/pgvector, mongo, qdrant, neo4j, and redis.  

5.  Note:  we have seen recently issues with Pytorch==2.3 on some platforms - if you run into any issues, we have seen that uninstalling Pytorch and downleveling to Pytorch==2.1 usually solves the problem.  


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
