---
layout: default
title: GGUF
parent: Components
nav_order: 14
description: overview of the major modules and classes of LLMWare  
permalink: /components/gguf
---
# GGUF
---

llmware packages its own build of the llama.cpp backend engine to enable running quantized models in GGUF format, which provides an 
effective packaging to run small language models on both CPUs and GPUs, which fast loading and inference.  

The GGUF capability is implemented in the models.py module in the class `GGUFGenerativeModel` with an extensive set of interfaces and 
configurations provided in the gguf_configs.py module (which for most users and use cases do not need to adjusted).  

To use a GGUF model is the same as using any other model in the ModelCatalog, e.g.,

```python
from llmware.models import ModelCatalog

gguf_model = ModelCatalog().load_model("phi-3-gguf")  
response = gguf_model.inference("What are the benefits of small specialized language models?")
print("response: ", response)
```

#   GGUF Platform Support 
Within the llmware library, we currently package 6 separate builds of the gguf llama.cpp engine for the following platforms:  

# Mac M1/M2/M3
 - with Accelerate:  "libllama_mac_metal.dylib"
 - without Accelerate: "libllama_mac_metal_no_acc.dylib" (note: if you have an old Mac OS installed, it may not have full Accelerate support)  
 - By default on Mac M1/M2/M3, it will attempt to use the Accelerate (faster) back-end, and if that fails, then it will automatically revert to the no-acc version 

# Windows
  - CUDA version 
  - CPU version 
  - Will look for CUDA drivers, and if found, will try to use the CUDA build, but if that fails, then it will automatically revert to the CPU version.  

# Linux
  - CUDA version
  - CPU version 
  - Will look for CUDA drivers, and if found, will try to use the CUDA build, but if that fails, then it will automatically revert to the CPU version.  


# Troubleshooting CUDA on Windows and Linux

Requirement:  Nvidia CUDA 12.1+  
-- how to check:  `nvcc --version` and `nvidia-smi` - if not found, then drivers are either not installed or not in $PATH and need to be configured 
-- if you have older drivers (e.g., v11), then you will need to update them.  

# Bring your own custom llama.cpp gguf backend

If you have a unique system requirement, or are looking to optimize for a particular BLAS library with your own build, you can bring your own as follows:  
if you have a unique system requirement, you can build llama_cpp from source, and apply custom build settings - or find in the community a prebuilt llama_cpp library that matches your platform.  Happy to help if you share the requirements. 

```python
from llmware.gguf_configs import GGUFConfigs
GGUFConfigs().set_config("custom_lib_path", "/path/to/your/custom/llama_cpp_backend")  

# ... and then load and run the model as usual - the GGUF model class will look at this config and load the llama.cpp found at the custom lib path.  
```

# Streaming GGUF

```python

""" This example illustrates how to use the stream method for GGUF models for fast streaming of inference,
especially for real-time chat interactions.

    Please note that the stream method has been implemented for GGUF models starting in llmware-0.2.13.  This will be
any model with GGUFGenerativeModel class, and generally includes models with names that end in "gguf".

    See also the chat UI example in the UI examples folder.

    We would recommend using a chat optimized model, and have included a representative list below.
"""


from llmware.models import ModelCatalog
from llmware.gguf_configs import GGUFConfigs

#   sets an absolute output maximum for the GGUF engine - normally set by default at 256
GGUFConfigs().set_config("max_output_tokens", 1000)

chat_models = ["phi-3-gguf",
               "llama-2-7b-chat-gguf",
               "llama-3-instruct-bartowski-gguf",
               "openhermes-mistral-7b-gguf",
               "zephyr-7b-gguf",
               "tiny-llama-chat-gguf"]

model_name = chat_models[0]

#   maximum output can be set optionally at any number up to the "max_output_tokens" set
model = ModelCatalog().load_model(model_name, max_output=500)

text_out = ""

token_count = 0

# prompt = "I am interested in gaining an understanding of the banking industry.  What topics should I research?"
prompt = "What are the benefits of small specialized LLMs?"

#   since model.stream provides a generator, then use as follows to consume the generator

for streamed_token in model.stream(prompt):

    text_out += streamed_token
    if text_out.strip():
        print(streamed_token, end="")

    token_count += 1

#   final output text and token count

print("\n\n***total text out***: ", text_out)
print("\n***total tokens***: ", token_count)
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

