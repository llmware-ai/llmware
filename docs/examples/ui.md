---
layout: default
title: UI
parent: Examples
nav_order: 8
description: overview of the major modules and classes of LLMWare  
permalink: /examples/ui
---
# UI - Introduction by Examples
We introduce ``llmware`` through self-contained examples.

**UI Scenarios**    

We provide several 'UI' examples that show how to use LLMWare in a complex recipe combining different elements to accomplish a specific objective.   While each example is still high-level, it is shared in the spirit of providing a high-level framework 'starting point' that can be developed in more detail for a variety of common use cases.  All of these examples use small, specialized models, running locally - 'Small, but Mighty' !  


1.  [**GGUF Streaming Chatbot**](https://www.github.com/llmware-ai/llmware/tree/main/examples/UI/gguf_streaming_chatbot.py)  

    - Locally deployed chatbot using leading open source chat models, including Phi-3-GGUF
    - Uses Streamlit
    - Core simple framework of ~20 lines using llmware and Streamlit

2.  [**Simple RAG UI with Streamlit**](https://www.github.com/llmware-ai/llmware/tree/main/examples/UI/simple_rag_ui_with_streamlit.py)  

    - Simple RAG UI 

3.  [**RAG UI with Query Topic with Streamlit**](https://www.github.com/llmware-ai/llmware/tree/main/examples/UI/rag_ui_with_query_topic_with_streamlit.py)  

    - UI demonstrating UI with query topic in RAG scenario

4.  [**Using Streamlit Chat UI**](https://www.github.com/llmware-ai/llmware/tree/main/examples/UI/using_streamlit_chat_ui.py)

    - Basic Streamlit Chat UI 


For more examples, see the [UI examples]((https://www.github.com/llmware-ai/llmware/tree/main/examples/UI/) in the main repo.   

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

