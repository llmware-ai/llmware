---
layout: default
title: Release History 
parent: Components  
nav_order: 15
description: llmware is an integrated framework with over 50+ models for quickly developing LLM-based applications including Retrieval Augmented Generation (RAG) and Multi-Step Orchestration of Agent Workflows.
permalink: /components/release_history
---
Release History
---

- For Specific Wheels:  [Wheel Archives](https://www.github.com/llmware-ai/llmware/tree/main/wheel_archives)  
- For Features Details: [Main README-'Release notes and Change Log'](https://www.github.com/llmware-ai/llmware/tree/main/)  

New wheels are built generally on PyPy on a weekly basis and updated on PyPy versioning.   The development repo is updated  
and current at all times, but may have updates that are not yet in the PyPy wheel.  

All wheels are built and tested on:  

1.  Mac Metal  
2.  Windows x86 (+ with CUDA)  
3.  Linux x86 (+ with CUDA) - most testing on Ubuntu 22 and Ubuntu 20 - which are recommended.  
4.  Mac x86 (see 0.2.11 note below)  
5.  Linux aarch64* (see 0.2.7 note below)  

**Release Notes**  

--**0.3.0** released in the week of June 4, 2024 - continued pruning of required dependencies with split of python dependencies into a small minimal set of requirements (~10 in requirements.txt) that are included in the pip install, with an additional set of optional dependencies provided as 'extras', reflected in both the requirements_extras.txt file, and available over pip with the added instruction - `pip3 install 'llmware[full]'`.  Notably, commonly used libraries such as transformers, torch and openai are now in the 'extras' as most llmware use cases do not require them, and this greatly simplifies the ability to install llmware.  The `welcome_to_llmware.sh` and `welcome_to_llmware_windows.sh` have also been updated to install both the 'core' and 'extra' set of requirements.  Other subtle, but significant, architectural changes include offering more extensibility for adding new model classes, configurable global base model methods for post_init and register, a new InferenceHistory state manager, and enhanced logging options.  

--**0.2.15** released in the week of May 20, 2024 - removed pytorch dependency as a global import, and shifted to dynamically loading of torch in the event that it is called in a specific model class.   This enables running most of llmware code and examples without pytorch or transformers loaded.   The main areas of torch (and transformers) dependency is in using HFGenerativeModels and HFEmbeddingModels.   

  - note: we have seen some new errors caused with Pytorch 2.3 - which are resolved by down-leveling to `pip3 install torch==2.1`  
  - note: there are a couple of new warnings from within transformers and huggingface_hub libraries - these can be safely ignored.  We have seen that keeping `local_dir_use_symlinks = False` when pulling model artifacts from Huggingface is still the safer option in some environments.   

--**0.2.13** released in the week of May 12, 2024 - clean up of dependencies in both requirements.txt and Setup (PyPi) - install of vector db python sdk (e.g., pymilvus, chromadb, etc) is now required as a separate step outside of the pip3 install llmware - attempt to keep dependency matrix as simple as possible and avoid potential dependency conflicts on install, especially for packages which in turn have a large number of dependencies.  If you run into any issues with install dependencies, please raise an issue. 

    
--**0.2.12** released in the week of May 5, 2024 - added Python 3.12 support, and deprecated the use of faiss for v3.12+.   We have changed the "Fast Start" no-install option to use chromadb or lancedb rather than faiss.   Refactoring of code especially with Datasets, Graph and Web Services as separate modules.  

--**0.2.11** released in the week of April 29, 2024 - updated GGUF libs for Phi-3 and Llama-3 support, and added new prebuilt shared libraries to support WhisperCPP.  We are also deprecating support for Mac x86 going forward - will continue to support on most major components but not all new features going forward will be built specifically for Mac x86 (which Apple stopped shipping in 2022).  Our intent is to keep narrowing our testing matrix to provide better support on key platforms.  We have also added better safety checks for older versions of Mac OS running on M1/M2/M3 (no_acc option in GGUF and Whisper libs), as well as a custom check to find CUDA drivers on Windows (independent of Pytorch).  

--**0.2.9** released in the week of April 15, 2024 - minor continued improvements to the parsers plus roll-out of new CustomTable class for rapidly integrating structured information into LLM-based workflows and data pipelines, including converting JSON/JSONL files and CSV files into structured DB tables.  
  
--**0.2.8** released in the week of April 8, 2024 - significant improvements to the Office parser with new libs on all platforms.   Conforming changes with the PDF parser in terms of exposing more options for text chunking strategies, encoding, and range of capture options (e.g., tables, images, header text, etc).  Linux aarch64 libs deprecated and kept at 0.2.6 - some new features will not be available on Linux aarch64 - we recommend using Ubuntu20+ on x86_64 (with and without CUDA).  

--**0.2.7** released in the week of April 1, 2024 - significant improvements to the PDF parser with new libs on all platforms.   Important note that we are keeping linux aarch64 at 0.2.6 libs - and will be deprecating support going forward.  For Linux, we recommend Ubuntu20+ and x86_64 (with and without CUDA).  

--**0.2.5** released in the week of March 12, 2024 - continued enhancements of the GGUF implementation, especially for CUDA support, and re-compiling of all binaries to support Ubuntu 20 and Ubuntu 22.  Ubuntu requirements are:  CUDA 12.1 (to use GPU), and GLIBC 2.31+.  

--**GGUF on Windows CUDA**: useful notes and debugging tips -  

    1.  Requirement:  Nvidia CUDA 12.1+  
    
        -- how to check:  `nvcc --version` and `nvidia-smi` - if not found, then drivers are either not installed or not in $PATH and need to be configured 
        -- if you have older drivers (e.g., v11), then you will need to update them.  
        
    2.  Requirement:  CUDA-enabled Pytorch  (pre-0.2.11)  
    
        -- starting with 0.2.11, we have implemented a custom check to evaluate if CUDA is present, independent of Pytorch.  
        -- for pre-0.2.11, we use Pytorch to check for CUDA drivers, e.g., `torch.cuda.is_available()` and `torch.version.cuda`  

    3.  Installing a CUDA-enabled Pytorch - useful install script:  (not required post-0.2.11 for GGUF on Windows)  
    
        -- `pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`  

    4.  Fall-back to CPU - if llmware can not load the CUDA-enabled drivers, it will automatically try to fall back to the CPU version of the drivers.  
    
        -- you can also adjust the GGUFConfigs().set_config - ("use_gpu", False) - and then it will automatically go to the CPU drivers.  

    5.  Custom GGUF libraries - if you have a unique system requirement, you can build llama_cpp from source, and apply custom build settings - or find in the community a prebuilt llama_cpp library that matches your platform.  Happy to help if you share the requirements.  

        -- to "bring your own GGUF":  GGUFConfigs().set_config("custom_lib_path", "/path/to/your/custom/llama_cpp_backend" -> and llmware will try to load that library.  

    6.  Issues?  - please raise an Issue on Github, or on Discord - and we can work with you to get you up and running!  
    
--**0.2.4** released in the week of February 26, 2024 - major upgrade of GGUF implementation to support more options, including CUDA support - which is the main source of growth in the size of the wheel package.   

  -- Note: We will look at making some of the CUDA builds as 'optional' or 'bring your own' over time.    
  -- Note: We will also start to 'prune' the list of wheels kept in the archive to keep the total repo size manageable for cloning.  

--**0.2.2** introduced SLIM models and the new LLMfx class, and the capabilities for multi-model, multi-step Agent-based processes.  

--**0.2.0** released in the week of January 22, 2024 - significant enhancements, including integration of Postgres and SQLite drivers into the c lib parsers.  

--New examples involving Postgres or SQLite support (including 'Fast Start' examples) will require a fresh pip install of 0.2.0 or clone of the repo.  

--If cloning the repo, please be especially careful to pick up the new updated /lib dependencies for your platform.  

--New libs have new dependencies in Linux in particular - most extensive testing on Ubuntu 22. If any issues on a specific version of Linux, please raise a ticket.  





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
