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

## 🧰🛠️🔩The Ultimate Toolkit for Building LLM Apps

From quickly building POCs to scalable LLM Apps for the enterprise, LLMWare is packed with all the tools you need. 

`llmware` is an integrated framework with over 50+ small, specialized, open source models for quickly developing LLM-based applications including Retrieval Augmented Generation (RAG) and Multi-Step Orchestration of Agent Workflows.  

This project provides a comprehensive set of tools that anyone can use - from a beginner to the most sophisticated AI developer - to rapidly build industrial-grade, knowledge-based enterprise LLM applications. 

Our specific focus is on making it easy to integrate open source small specialized models and connecting enterprise knowledge safely and securely. 


##  Getting Started 

1.  Install llmware - `pip3 install llmware`  


2.  Make sure that you are running on a [supported platform](#platform-support).  


3.  Learn by example:  

    -- [Fast Start examples](www.github.com/llmware-ai/llmware/tree/main/fast_start) - structured set of 6 examples (with no DB installations required) to learn the main concepts of RAG with LLMWare - each example has extensive comments, and a supporting video on Youtube to walk you through it.    

    -- [Getting Started examples](www.github.com/llmware-ai/llmware/tree/main/examples/Getting_Started) - heavily-annotated examples that review many getting started elements - selecting a database, loading sample files, working with libraries, and how to use the Model Catalog.  

    -- [Use Case examples](www.github.com/llmware-ai/llmware/tree/main/examples/Use_Cases) - longer examples that integrate several components of LLMWare to provide a framework for a solution for common use case patterns.  

    -- Dive into specific area of interest - [Parsing](www.github.com/llmware-ai/llmware/tree/main/examples/Parsing) - [Models](www.github.com/llmware-ai/llmware/tree/main/examples/Models) - [Prompts](www.github.com/llmware-ai/llmware/tree/main/examples/Models) - [Agents](www.github.com/llmware-ai/llmware/tree/main/examples/SLIM-Agents)  - and many more ...


4.  We provide extensive [sample files](www.github.com/llmware-ai/tree/main/examples/Getting_Started/loading_sample_files.py) integrated into the examples, so you can copy-paste-run, and quickly validate that the installation is set up correctly, and to start seeing key classes and methods in action.  We would encourage you to start with the 'out of the box' example first, and then use the example as the launching point for inserting your documents, models, queries, and workflows.  


5.  Learn by watching: check out the [LLMWare Youtube channel](www.youtube.com/@llmware).  


6.  Share with the community:  join us on [Discord](https://discord.gg/MhZn5Nc39h).  


[Install llmware](#install-llmware){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }  
[Common Setup & Configuration Items](#platform-support){: .btn .fs-5 .mb-4 .mb-md-0 }  
[Troubleshooting](#common-troubleshooting-issues){: .btn .fs-5 .mb-4 .mb-md-0 }  
[Architecture](architecture.md/#llmware-architecture){: .btn .fs-5 .mb-4 .mb-md-0 }  
[View llmware on GitHub](https://github.com/llmware-ai/llmware/tree/main){: .btn .fs-5 .mb-4 .mb-md-0 }  
[Open an Issue on GitHub](https://github.com/llmware-ai/llmware/issues){: .btn .fs-5 .mb-4 .mb-md-0 }  



# Install llmware 

___  
**Using Pip Install**  

- Installing llmware is easy:  `pip3 install llmware` 


- If you prefer, we also provide a set of recent wheels in the [wheel archives](github.com/llmware-ai/llmware/tree/main/wheel_archives) in this repository, which can be downloaded individually and used as follows:  

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

___  
# Platform Support

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


- **Fast Start** option:  you can start using SQLite locally without any separate installation by setting `LLMWareConfig.set_active_db("sqlite")` as shown in [configure_db_example](www.github.com/llmware-ai/llmware/blob/main/examples/Getting_Started/configure_db.py).  For vector embedding examples, you can use ChromaDB, LanceDB or FAISS - all of which provide no-install options - just start using.  


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
___

# Common Troubleshooting Issues
___


1. **Can not install the pip package**  

    -- Check your Python version.   If using Python 3.9-3.11, then almost any version of llmware should work.  If using an older Python (before 3.9), then it is likely that dependencies will fail in the pip process.  If you are using Python 3.12, then you need to use llmware>=0.2.12.  
    
    -- Dependency constraint error.   If you receive a specific error around a dependency version constraint, then please raise an issue and include details about your OS, Python version, any unique elements in your virtual environment, and specific error.   


2. **Parser module not found**

    -- Check your OS and confirm that you are using a [supported platform](#platform-support).  
    -- If you cloned the repository, please confirm that the /lib folder has been copied into your local path.  


3.  **Pytorch Model not loading**

   -- Confirm the obvious stuff - correct model name, model exists in Huggingface repository, connected to the Internet with open ports for HTTPS connection, etc.  

   -- Check Pytorch version - update Pytorch to >2.0, which is required for many recent models released in the last 6 months, and in some cases, may require other dependencies not included in the llmware package.  


4.  **GGUF Model not loading**

   -- Confirm that you are using llmware>=0.2.11 for the latest GGUF support.  

   -- Confirm that you are using a [supported platform](#platform-support).  We provide pre-built binaries for llama.cpp as a back-end GGUF engine on the following platforms:  
        
        - Mac M1/M2/M3 - OS version 14 - "with accelerate framework"
        - Mac M1/M2/M3 - OS older versions - "without accelerate framework"  
        - Windows - x86
        - Windows with CUDA  
        - Linux - x86  (Ubuntu 20+)
        - Linux with CUDA  (Ubuntu 20+)  
   
If you are using a different OS platform, you have the option to "bring your own llama.cpp" lib as follows:  

```python
from llmware.gguf_configs import GGUFConfigs
GGUFConfigs().set_config("custom_lib_path", "/path/to/your/libllama_binary")  
```

If you have any trouble, feel free to raise an Issue and we can provide you with instructions and/or help compiling llama.cpp for your platform.  
        
   -- Specific GGUF model - if you are successfully using other GGUF models, and only having problems with a specific model, then please raise an Issue, and share the specific model and architecture.  


5.  **Example not working as expected** - please raise an issue, so we can evaluate and fix any bugs in the example code.  Also, pull requests are always especially welcomed with a fix or improvement in an example.  


6.  **Model not leveraging CUDA available in environment.**  

    -- **Check CUDA drivers installed correctly** - easy check of the NVIDIA CUDA drivers is to use `nvidia-smi` and `nvcc --version` from the command line.  Both commands should respond positively with details on the versions and implementations.  Any errors indicates that either the driver or CUDA toolkit are not installed or recognized.  It can be complicated at times to debug the environment, usually with some trial and error.   See extensive [Nvidia Developer documentation](docs.nvidia.com) for trouble-shooting steps, specific to your environment.  

    -- **Check CUDA drivers are up to date** - we build to CUDA 12.1, which translates to a minimum of 525.60 on Linux, and 528.33 on Windows.  

    -- **Pytorch model** - check that Pytorch is finding CUDA, e.g., `torch.cuda.is_available()` == True.   We have seen issues on Windows, in particular, to confirm that your Pytorch version has been compiled with CUDA drivers.  For Windows, in particular, we have found that you may need to compile a CUDA-specific version of Pytorch, using the following command:  
    
    ```pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121```
    
    -- **GGUF model** - logs will be displayed on the screen confirming that CUDA is being used, or whether 'fall-back' to CPU drivers.  We run a custom CUDA install check, which you can run on your system with:  
        ```gpu_status = ModelCatalog().gpu_available``` 
        
       If you are confirming CUDA present, but fall-back to CPU is being used, you can set the GGUFConfigs to force to CUDA:  
        ```GGUFConfigs().set_config("force_gpu", True)```  
      
       If you are looking to use specific optimizations, you can bring your own llama.cpp lib as follows:
        ```GGUFConfigs().set_config("custom_lib_path", "/path/to/your/custom/llama_cpp_backend")``` 

    -- If you can not debug after these steps, then please raise an Issue.   We are happy to dig in and work with you to run FAST local inference.  


7.  **Model result inconsistent**  

    -- when loading the model, set `temperature=0.0` and `sample=False` -> this will give a deterministic output for better testing and debugging.  

    -- usually the issue will be related to the retrieval step and formation of the Prompt, and as always, good pipelines and a little experimentation usually help !  


# More information about the project - [see main repository](www.github.com/llmware-ai/llmware.git)


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
