---
layout: default
title: Installation
parent: Getting Started
nav_order: 2
permalink: /getting_started/installation
---

##  Installation

Set up  

`pip3 install llmware` or, if you prefer clone the github repo locally, e.g., `git clone git@github.com:llmware-ai/llmware.git
`.   

Platforms: 
- Mac M1/M2/M3, Windows, Linux (Ubuntu 20 or Ubuntu 22 preferred)  
- RAM: 16 GB minimum  
- Python 3.9, 3.10, 3.11 (note: not supported on 3.12 - coming soon!)  
- Pull the latest version of llmware == 0.2.11 (as of end of April 2024)  
- Please note that we have updated the examples from the original versions, to use new features in llmware, so there may be minor differences with the videos, which are annotated in the comments in each example.    
  

##  Wheel Archive  

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
