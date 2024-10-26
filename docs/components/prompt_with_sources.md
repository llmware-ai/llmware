---
layout: default
title: Prompt with Sources
parent: Components
nav_order: 10
description: overview of the major modules and classes of LLMWare  
permalink: /components/prompt_with_sources
---
# Prompt with Sources
---
Prompt with Sources: the easiest way to combine knowledge retrieval with a LLM inference, and provides several high-level useful methods to 
easily integrate a retrieval/query/parsing step into a prompt to be used as a source for running an inference on a model.  

This is best illustrated with a simple example:

```python

from llmware.prompts import Prompt

#   build a prompt and attach a model
prompter = Prompt().load_model("llmware/bling-tiny-llama-v0")

#   add_source_document method: accepts any supported document type, parses the file, and creates text chunks
#   if a query is passed, then it will run a quick in-memory filtering search against the text chunks
#   the text chunks are packaged into sources with all of the accompanying metadata from the file, and made 
#   available automatically in batches to be used in prompting -

source = prompter.add_source_document("/folder/to/one/doc/", "filename", query="fast query")

#   to run inference with 'prompt with sources' -> source will be automatically added to the prompt
responses = prompter.prompt_with_source("my query")

#   depending upon the size of the source (and batching relative to the model context window, there may be more than 
#   a single inference run, so unpack potentially multiple responses

for i, response in enumerate(responses):
    print("response: ", i, response)
```

# FACT CHECKING  

Using prompt_with_source also provides integrated fact-checking methods that use the packaged source information to validate key 
elements from the llm_response

```python
from llmware.prompts import Prompt

prompter = Prompt().load_model("bling-answer-tool", temperature=0.0, sample=False)

# contract is parsed, text-chunked, and then filtered by "base salary'
source = prompter.add_source_document("/local/folder/path", "my_document.pdf", query="exact filter query")

# calling the LLM with 'source' information from the contract automatically packaged into the prompt
responses = prompter.prompt_with_source("my question to the document", prompt_name="default_with_context")
    
# run several fact checks

#   checks for numbers match
ev_numbers = prompter.evidence_check_numbers(responses)

#   looks for statistical overlap to identify potential sources for the llm response
ev_sources = prompter.evidence_check_sources(responses)

#   builds set of comparison stats between the llm_response and the sources
ev_stats = prompter.evidence_comparison_stats(responses)

#   identifies if a response is a "not found" response
z = prompter.classify_not_found_response(responses, parse_response=True, evidence_match=True,ask_the_model=False)

for r, response in enumerate(responses):
    print("LLM Response: ", response["llm_response"])
    print("Numbers: ",  ev_numbers[r]["fact_check"])
    print("Sources: ", ev_sources[r]["source_review"])
    print("Stats: ", ev_stats[r]["comparison_stats"])
    print("Not Found Check: ", z[r])
```

In addition to `add_source_document`, the Prompt class implements the following other methods to easily integrate sources into prompts:  

# Add Source - Query Results - Two Options 

```python

from llmware.prompts import Prompt
from llmware.retrieval import Query
from llmware.library import Library

#   build a prompt
prompter = Prompt().load_model("llmware/bling-tiny-llama-v0")

#   Option A - run query and then add query_results to the prompt
my_lib = Library().load_library("my_library")
results = Query(my_lib).query("my query")

source2 = prompter.add_source_query_results(results)

#   Option B - run a new query against a library and load directly into a prompt
source3 = prompter.add_source_new_query(my_lib, query="my new query", query_type="semantic", result_count=15)

```

# Add Other Sources

```python

from llmware.prompts import Prompt

#   build a prompt
prompter = Prompt().load_model("llmware/bling-tiny-llama-v0")

#   add wikipedia articles as a source
wiki_source = prompter.add_source_wikipedia("topic", article_count=5, query="filter among retrieved articles")  

#   add a website as a source
website_source = prompter.add_source_website("my_url", query="filter among website")

#   add an entire library (should be small, e.g., just a couple of documents)
source = prompter.add_source_library("my_library")

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

