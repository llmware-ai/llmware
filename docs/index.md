---
layout: default
title: Home | llmware
nav_order: 1
description: llmware is an integrated framework with over 50+ models in Hugging Face for quickly developing LLM-based applications including Retrieval Augmented Generation (RAG) and Multi-Step Orchestration of Agent Workflows.
permalink: /
---
# Welcome to
<ul class="list-style-none">
    <li class="d-inline-block mr-1">
        <a href="https://llmware.ai/"><span><img src="assets/images/llmware_logo_color_cropped.png" alt="llmware"/></span></a>
    </li>
</ul>

`llmware` is an integrated framework with over 50+ models in Hugging Face for quickly developing LLM-based applications including Retrieval Augmented Generation (RAG) and Multi-Step Orchestration of Agent Workflows.
{: .fs-6 .fw-300 }

[Install llmware](#install-llmware){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[View llmware on GitHub](https://github.com/llmware-ai/llmware/tree/main){: .btn .fs-5 .mb-4 .mb-md-0 }
[Open an Issue on GitHub](https://github.com/llmware-ai/llmware/issues){: .btn .fs-5 .mb-4 .mb-md-0 }

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

# Install llmware 

{: .note}
> New wheels are built generally on PyPy on a weekly basis and updated on PyPy versioning.
> The development repo is updated and current at all times, but may have updates that are not yet in the PyPy wheel.
> All wheels are built and tested on
> - Mac Metal
> - Mac x86
> - Windows x86 (+ with CUDA)
> - Linux x86 (+ with CUDA) - most testing on Ubuntu 22 and Ubuntu 20 - which are recommended.
> - Linux aarch64

{: .note}
> We recommend that you use at least ``llmware >= 0.2.0``. Other than that, make sure that you have the following
> set up.
> - Platforms: Mac M1, Mac x86, Windows, Linux (Ubuntu 22 preferred)
> - Hardware: 16 GB RAM minimum
> - Python versions: 3.9, 3.10, 3.11

You can install ``llmware`` via the Python Package Index (PIP), or you can manually download the ``wheel`` files from
the [GitHub repository](https://github.com/llmware-ai/llmware/tree/main/wheel_archives).

## PIP
You can easily install `llmware` via `pip`.

```bash
pip install llmware 
```

## Manual install of wheel files
First, go to the [wheel\_archives](https://github.com/llmware-ai/llmware/tree/main/wheel_archives) folder
and download the *wheel* you want to install.
For example, if you want to install ``llmware`` version ``0.2.5`` then choose ``llmware-0.2.5-py3-none-any.whl``.
After downloading, place the ``wheel`` archive in a folder.
Finally, navigate to that folder and and run ``pip3 install llmware-0.2.5-py3-none-any.whl``.
On linux, a typical work flow would be the following.

```bash
cd Downloads

mkdir llmware
cd llmware

wget https://github.com/\
llmware-ai/llmware/\
blob/432b5530cda158f57442a3fe4a9f03a20945a41c/\
wheel_archives/llmware-0.2.5-py3-none-any.whl

pip3 install llmware-0.2.5-py3-none-any.whl
```

# When to use llmware 

``llmware`` focuses on making it easy to integrate open source small specialized models and connecting enterprise knowledge safely and securely.


# Usage

```python
from llmware.models import ModelCatalog

# get all SLIM models, delivered as small, fast quantized tools
ModelCatalog().get_llm_toolkit()

# see the model in action with test script included
ModelCatalog().tool_test_run("slim-sentiment-tool") 
```

# About the project

`llmware` is &copy; 2023-{{ "now" | date: "%Y" }} by [AI Bloks](https://www.aibloks.com/home).

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
