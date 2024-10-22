---
layout: default
title: Model Catalog  
parent: Components
nav_order: 2
description: overview of the major modules and classes of LLMWare  
permalink: /components/model_catalog
---
# Model Catalog:  
Access all models the same way with easy lookup, regardless of underlying implementation. 

- 150+ Models in Catalog with 50+ RAG-optimized BLING, DRAGON and Industry BERT models
- 18 SLIM function-calling small language models for Agent use cases  
- Full support for GGUF, HuggingFace, Sentence Transformers and major API-based models
- Easy to extend to add custom models - see examples

Generally, all models can be identified using either the `model_name` or `display_name`, which provides some flexibility 
to expose a more "UI friendly" name or an informal short-name for a commonly-used model.  

The default model list is implemented in the model_configs.py module, which is then generally accessed in the models.py module through 
the `ModelCatalog` class, which also provides the ability to add models of various types, over-write by loading a custom model catalog from json file, and 
other useful interfaces into the list of models.  

```python

from llmware.models import ModelCatalog
from llmware.prompts import Prompt

#   all models accessed through the ModelCatalog
models = ModelCatalog().list_all_models()

#   to use any model in the ModelCatalog - "load_model" method and pass the model_name parameter
my_model = ModelCatalog().load_model("llmware/bling-phi-3-gguf")
output = my_model.inference("what is the future of AI?", add_context="Here is the article to read")

#   to integrate model into a Prompt
prompter = Prompt().load_model("llmware/bling-tiny-llama-v0")
response = prompter.prompt_main("what is the future of AI?", context="Insert Sources of information")
```

#  ADD a Custom GGUF to the ModelCatalog  

```python
import time
import re
from llmware.models import ModelCatalog
from llmware.prompts import Prompt

#   Step 1 - register new gguf model - we will pick the popular LLama-2-13B-chat-GGUF

ModelCatalog().register_gguf_model(model_name="TheBloke/Llama-2-13B-chat-GGUF-Q2",
                                   gguf_model_repo="TheBloke/Llama-2-13B-chat-GGUF",
                                   gguf_model_file_name="llama-2-13b-chat.Q2_K.gguf",
                                   prompt_wrapper="my_version_inst")

#   Step 2- if the prompt_wrapper is a standard, e.g., Meta's <INST>, then no need to do anything else
#   -- however, if the model uses a custom prompt wrapper, then we need to define that too
#   -- in this case, we are going to create our "own version" of the Meta <INST> wrapper

ModelCatalog().register_new_finetune_wrapper("my_version_inst", main_start="<INST>", llm_start="</INST>")

#   Once we have completed these two steps, we are done - and can begin to use the model like any other

prompter = Prompt().load_model("TheBloke/Llama-2-13B-chat-GGUF-Q2")

question_list = ["I am interested in gaining an understanding of the banking industry. What topics should I research?",
                 "What are some tips for creating a successful business plan?",
                 "What are the best books to read for a class on American literature?"]


for i, entry in enumerate(question_list):

    start_time = time.time()
    print("\n")
    print(f"query - {i + 1} - {entry}")

    response = prompter.prompt_main(entry)

    # Print results
    time_taken = round(time.time() - start_time, 2)
    llm_response = re.sub("[\n\n]", "\n", response['llm_response'])
    print(f"llm_response - {i + 1} - {llm_response}")
    print(f"time_taken - {i + 1} - {time_taken}")
```

# ADD an Ollama Model

```python

from llmware.models import ModelCatalog

#   Step 1 - register your Ollama models in llmware ModelCatalog
#   -- these two lines will register: llama2 and mistral models
#   -- note: assumes that you have previously cached and installed both of these models with ollama locally

#   register llama2
ModelCatalog().register_ollama_model(model_name="llama2",model_type="chat",host="localhost",port=11434)

#   register mistral - note: if you are using ollama defaults, then OK to register with ollama model name only
ModelCatalog().register_ollama_model(model_name="mistral")

#   optional - confirm that model was registered
my_new_model_card = ModelCatalog().lookup_model_card("llama2")
print("\nupdate: confirming - new ollama model card - ", my_new_model_card)

#   Step 2 - start using the Ollama model like any other model in llmware

print("\nupdate: calling ollama llama 2 model ...")

model = ModelCatalog().load_model("llama2")
response = model.inference("why is the sky blue?")

print("update: example #1 - ollama llama 2 response - ", response)

#   Tip: if you are loading 'llama2' chat model from Ollama, note that it is already included in
#   the llmware model catalog under a different name, "TheBloke/Llama-2-7B-Chat-GGUF"
#   the llmware model name maps to the original HuggingFace repository, and is a nod to "TheBloke" who has
#   led the popularization of GGUF - and is responsible for creating most of the GGUF model versions.
#   --llmware uses the "Q4_K_M" model by default, while Ollama generally prefers "Q4_0"

print("\nupdate: calling Llama-2-7B-Chat-GGUF in llmware catalog ...")

model = ModelCatalog().load_model("TheBloke/Llama-2-7B-Chat-GGUF")
response = model.inference("why is the sky blue?")

print("update: example #1 - [compare] - llmware / Llama-2-7B-Chat-GGUF response - ", response)

#   Now, let's try the Ollama Mistral model with a context passage

model2 = ModelCatalog().load_model("mistral")

context_passage= ("NASA’s rover Perseverance has gathered data confirming the existence of ancient lake "
                  "sediments deposited by water that once filled a giant basin on Mars called Jerezo Crater, "
                  "according to a study published on Friday.  The findings from ground-penetrating radar "
                  "observations conducted by the robotic rover substantiate previous orbital imagery and "
                  "other data leading scientists to theorize that portions of Mars were once covered in water "
                  "and may have harbored microbial life.  The research, led by teams from the University of "
                  "California at Los Angeles (UCLA) and the University of Oslo, was published in the "
                  "journal Science Advances. It was based on subsurface scans taken by the car-sized, six-wheeled "
                  "rover over several months of 2022 as it made its way across the Martian surface from the "
                  "crater floor onto an adjacent expanse of braided, sedimentary-like features resembling, "
                  "from orbit, the river deltas found on Earth.")

response = model2.inference("What are the top 3 points?", add_context=context_passage)

print("\nupdate: calling ollama mistral model ...")

print("update: example #2 - ollama mistral response - ", response)

#   Step 3 - using the ollama discovery API - optional

discovery = model2.discover_models()
print("\nupdate: example #3 - checking ollama model manifest list: ", discovery)

if len(discovery) > 0:
    # note: assumes tht you have at least one model registered in ollama -otherwise, may throw error
    for i, models in enumerate(discovery["models"]):
        print("ollama models: ", i, models)
```

# Add a LM Studio Model

```python
from llmware.models import ModelCatalog
from llmware.prompts import Prompt


#   one step process:  add the open chat model to the Model Registry
#   key params:
#       model_name      =   "my_open_chat_model1"
#       api_base        =   uri_path to the proposed endpoint
#       prompt_wrapper  =   alpaca | <INST> | chat_ml | hf_chat | human_bot
#                           <INST>      ->  Llama2-Chat
#                           hf_chat     ->  Zephyr-Mistral
#                           chat_ml     ->  OpenHermes - Mistral
#                           human_bot   ->  Dragon models
#       model_type      =   "chat" (alternative:  "completion")

ModelCatalog().register_open_chat_model("my_open_chat_model1",
                                        api_base="http://localhost:1234/v1",
                                        prompt_wrapper="<INST>",
                                        model_type="chat")

#   once registered, you can invoke like any other model in llmware

prompter = Prompt().load_model("my_open_chat_model1")
response = prompter.prompt_main("What is the future of AI?")


#   you can (optionally) register multiple open chat models with different api_base and model attributes

ModelCatalog().register_open_chat_model("my_open_chat_model2",
                                        api_base="http://localhost:5678/v1",
                                        prompt_wrapper="hf_chat",
                                        model_type="chat")
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

