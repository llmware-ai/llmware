---
layout: default
title: Home | llmware
nav_order: 1
description: llmware is an integrated framework with over 50+ models for quickly developing LLM-based applications including Retrieval Augmented Generation (RAG) and Multi-Step Orchestration of Agent Workflows.
permalink: /
---
## Welcome to  
<ul class="list-style-none">
    <li class="d-inline-block mr-1">
        <a href="https://llmware.ai/"><span><img src="assets/images/llmware_logo_color_cropped.png" alt="llmware" width="360" height="60"/></span></a>
    </li>
</ul>  

## 🧰🛠️🔩The Ultimate Toolkit for Enterprise RAG Pipelines with Small, Specialized Models   

From quickly building POCs to scalable LLM Apps for the enterprise, LLMWare is packed with all the tools you need. 

`llmware` is an integrated framework with over 50+ small, specialized, open source models for quickly developing LLM-based applications including Retrieval Augmented Generation (RAG) and Multi-Step Orchestration of Agent Workflows.  

This project provides a comprehensive set of tools that anyone can use - from a beginner to the most sophisticated AI developer - to rapidly build industrial-grade, knowledge-based enterprise LLM applications. 

Our specific focus is on making it easy to integrate open source small specialized models and connecting enterprise knowledge safely and securely. 


##  Getting Started 

1.  Install llmware - `pip3 install llmware`  


2.  Make sure that you are running on a [supported platform](https://www.github.com/llmware-ai/llmware/tree/main/docs/getting_started/platforms.md#platform-support).  


3.  Learn by example:  

    -- [Fast Start examples](https://www.github.com/llmware-ai/llmware/tree/main/fast_start) - structured set of 6 examples (with no DB installations required) to learn the main concepts of RAG with LLMWare - each example has extensive comments, and a supporting video on Youtube to walk you through it.    

    -- [Getting Started examples](https://www.github.com/llmware-ai/llmware/tree/main/examples/Getting_Started) - heavily-annotated examples that review many getting started elements - selecting a database, loading sample files, working with libraries, and how to use the Model Catalog.  

    -- [Use Case examples](https://www.github.com/llmware-ai/llmware/tree/main/examples/Use_Cases) - longer examples that integrate several components of LLMWare to provide a framework for a solution for common use case patterns.  

    -- Dive into specific area of interest - [Parsing](https://www.github.com/llmware-ai/llmware/tree/main/examples/Parsing) - [Models](https://www.github.com/llmware-ai/llmware/tree/main/examples/Models) - [Prompts](https://www.github.com/llmware-ai/llmware/tree/main/examples/Models) - [Agents](https://www.github.com/llmware-ai/llmware/tree/main/examples/SLIM-Agents)  - and many more ...


4.  We provide extensive [sample files](https://www.github.com/llmware-ai/tree/main/examples/Getting_Started/loading_sample_files.py) integrated into the examples, so you can copy-paste-run, and quickly validate that the installation is set up correctly, and to start seeing key classes and methods in action.  We would encourage you to start with the 'out of the box' example first, and then use the example as the launching point for inserting your documents, models, queries, and workflows.  


5.  Learn by watching: check out the [LLMWare Youtube channel](https://www.youtube.com/@llmware).  


6.  Share with the community:  join us on [Discord](https://discord.gg/MhZn5Nc39h).  


[Install llmware](#install-llmware){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }  
[Common Setup & Configuration Items](#platform-support){: .btn .fs-5 .mb-4 .mb-md-0 }  
[Architecture](architecture.md/#llmware-architecture){: .btn .fs-5 .mb-4 .mb-md-0 }  
[View llmware on GitHub](https://www.github.com/llmware-ai/llmware/tree/main){: .btn .fs-5 .mb-4 .mb-md-0 }  
[Open an Issue on GitHub](https://www.github.com/llmware-ai/llmware/issues){: .btn .fs-5 .mb-4 .mb-md-0 }  



# Install llmware 

___  
**Using Pip Install**  

- Installing llmware is easy:  `pip3 install llmware` 


- If you prefer, we also provide a set of recent wheels in the [wheel archives](https://www.github.com/llmware-ai/llmware/tree/main/wheel_archives) in this repository, which can be downloaded individually and used as follows:  

```bash
pip3 install llmware-0.2.12-py3-none-any.wheel
````  

- We generally keep the main branch of this repository current with all changes, but we only publish new wheels to PyPi approximately once per week  

___

___
**Cloning the Repository**  

- If you prefer to clone the repository:  

```bash
git clone git@github.com:llmware-ai/llmware.git
```

- The llmware package is contained entirely in the /llmware folder path, so you should be able to drop this folder (with all of its contents) into a project tree, and use the llmware module essentially the same as a pip install.  

- Please ensure that you are capturing and updating the /llmware/lib folder, which includes required compiled shared libraries.  If you prefer, you can keep only those libs required for your OS platform.  

- After cloning the repo, we provide a short 'welcome to llmware' automation script, which can be used to install the projects requirements (from llmware/requirements.txt), install several optional dependencies that are commonly used in examples, copy several good 'getting started' examples into the root folder, and then run a 'welcome_example.py' script to get started using our models.  To use the "welcome to llmware" script:  

Windows:  
```bash
.\welcome_to_llmware_windows.sh
```

Mac/Linux:
```bash
sh ./welcome_to_llmware.sh
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
