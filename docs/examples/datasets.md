---
layout: default
title: Datasets
parent: Examples
nav_order: 10
description: overview of the major modules and classes of LLMWare  
permalink: /examples/datasets
---
# Datasets - Introduction by Examples

llmware provides powerful capabilities to transform raw unstructured information into various model-ready datasets.  

```python

import os
import json

from llmware.library import Library
from llmware.setup import Setup
from llmware.dataset_tools import Datasets
from llmware.retrieval import Query

def build_and_use_dataset(library_name):

    # Setup a library and build a knowledge graph.  Datasets will use the data in the knowledge graph
    print (f"\n > Creating library {library_name}...")
    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files()
    library.add_files(os.path.join(sample_files_path,"SmallLibrary"))
    library.generate_knowledge_graph()

    # Create a Datasets object from library
    datasets = Datasets(library)

    # Build a basic dataset useful for industry domain adaptation for fine-tuning embedding models
    print (f"\n > Building basic text dataset...")

    basic_embedding_dataset = datasets.build_text_ds(min_tokens=500, max_tokens=1000)
    dataset_location = os.path.join(library.dataset_path, basic_embedding_dataset["ds_id"])

    print (f"\n > Dataset:")
    print (f"(Files referenced below are found in {dataset_location})")

    print (f"\n{json.dumps(basic_embedding_dataset, indent=2)}")
    sample = datasets.get_dataset_sample(datasets.current_ds_name)

    print (f"\nRandom sample from the dataset:\n{json.dumps(sample, indent=2)}")
    
    # Other Dataset Generation and Usage Examples:

    # Build a simple self-supervised generative dataset- extracts text and splits into 'text' & 'completion'
    # Several generative "prompt_wrappers" are available - chat_gpt | alpaca | 
    basic_generative_completion_dataset = datasets.build_gen_ds_targeted_text_completion(prompt_wrapper="alpaca")
    
    # Build a generative self-supervised training sets created by pairing 'header_text' with 'text'
    xsum_generative_completion_dataset = datasets.build_gen_ds_headline_text_xsum(prompt_wrapper="human_bot")
    topic_prompter_dataset = datasets.build_gen_ds_headline_topic_prompter(prompt_wrapper="chat_gpt")
    
    # Filter a library by a key term as part of building the dataset
    filtered_dataset = datasets.build_text_ds(query="agreement", filter_dict={"master_index":1})
    
    # Pass a set of query results to create a dataset from those results only
    query_results = Query(library=library).query("africa")
    query_filtered_dataset = datasets.build_text_ds(min_tokens=250,max_tokens=600, qr=query_results)

    return 0
```

For more examples, see the [datasets example]((https://www.github.com/llmware-ai/llmware/tree/main/examples/Datasets/) in the main repo.   


Check back often - we are updating these examples regularly - and many of these examples have companion videos as well.  


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

