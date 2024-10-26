---
layout: default
title: Agents 
parent: Components
nav_order: 4
description: overview of the major modules and classes of LLMWare  
permalink: /components/agents
---
# Agents
---

Agents with Function Calls and SLIM Models 🔥 

llmware has been designed to enable Agent and LLM-based function calls using small language models designed for local and private 
deployment and the ability to leverage open source models to conduct complex RAG and knowledge-based workflow automation.  

The key elements in llmware:  

 - **SLIM models** - 18 function-calling small language models, optimized for a specific extraction, classification, generation, or 
summarization activity, and generate python dictionaries and lists as output.  

- **LLMfx class** - enables a wide range of agent-based processes.  

Here is an example to get started: 

```python

from llmware.agents import LLMfx

text = ("Tesla stock fell 8% in premarket trading after reporting fourth-quarter revenue and profit that "
        "missed analysts’ estimates. The electric vehicle company also warned that vehicle volume growth in "
        "2024 'may be notably lower' than last year’s growth rate. Automotive revenue, meanwhile, increased "
        "just 1% from a year earlier, partly because the EVs were selling for less than they had in the past. "
        "Tesla implemented steep price cuts in the second half of the year around the world. In a Wednesday "
        "presentation, the company warned investors that it’s 'currently between two major growth waves.'")

#   create an agent using LLMfx class
agent = LLMfx()

#   load text to process
agent.load_work(text)

#   load 'models' as 'tools' to be used in analysis process
agent.load_tool("sentiment")
agent.load_tool("extract")
agent.load_tool("topics")
agent.load_tool("boolean")

#   run function calls using different tools
agent.sentiment()
agent.topics()
agent.extract(params=["company"])
agent.extract(params=["automotive revenue growth"])
agent.xsum()
agent.boolean(params=["is 2024 growth expected to be strong? (explain)"])

#   at end of processing, show the report that was automatically aggregated by key
report = agent.show_report()

#   displays a summary of the activity in the process
activity_summary = agent.activity_summary()

#   list of the responses gathered
for i, entries in enumerate(agent.response_list):
    print("update: response analysis: ", i, entries)

output = {"report": report, "activity_summary": activity_summary, "journal": agent.journal}  

```


Need help or have questions?
============================

Check out the [llmware videos](https://www.youtube.com/@llmware) and [GitHub repository](https://github.com/llmware-ai/llmware).

Reach out to us on [GitHub Discussions](https://github.com/llmware-ai/llmware/discussions).


# About the project

`llmware` is &copy; 2023-{{ "now" | date: "%Y" }} by [AI Bloks](https://www.aibloks.com/home).

## Contributing
Please first discuss any change you want to make publicly, for example on GitHub via raising an [issue](https://github.com/llmware-ai/llmware/issues) or starting a [new discussion](https://github.com/llmware-ai/llmware/discussions).
You can also write an email or start a discussion on our Discord channel.
Read more about becoming a contributor in the [GitHub repo](https://github.com/llmware-ai/llmware/blob/main/CONTRIBUTING.md).

## Code of conduct
We welcome everyone into the ``llmware`` community.
[View our Code of Conduct](https://github.com/llmware-ai/llmware/blob/main/CODE_OF_CONDUCT.md) in our GitHub repository.

## ``llmware`` and [AI Bloks](https://www.aibloks.com/home)
``llmware`` is an open source project from [AI Bloks](https://www.aibloks.com/home) - the company behind ``llmware``.
The company offers a Software as a Service (SaaS) Retrieval Augmented Generation (RAG) service.
[AI Bloks](https://www.aibloks.com/home) was founded by [Namee Oberst](https://www.linkedin.com/in/nameeoberst/) and [Darren Oberst](https://www.linkedin.com/in/darren-oberst-34a4b54/) in October 2022.

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

