---
layout: default
title: Components
nav_order: 3
has_children: true
description: llmware key architectural components, modules and classes
permalink: /components
---
# LLMWare Architecture
---

llmware is characterized by a logically integrated set of data pipelines involved in building LLM-based workflows, centered on two main sub-pipelines with high-level interfaces intended to provide an abstraction layer over individual 'end point' components to promote code re-use and the ability to easily 'swap' different components with minimal, if any, code change:  

**1.  Knowledge Ingestion** - "creating Gen Ai Food" - ingesting and organizing unstructured information from a wide range of data sources, including each of the major steps:  

    - Extracting and Parsing
    - Text Chunking
    - Indexing, Organizing and Storing
    - Embedding
    - Retrieval
    - Analytics and Reuse of Content  
    - Combining with SQL Table and Other Structured Content


   **Core LLMWare classes**:  **Library**, **Query** (retrieval module), **Parser**, **EmbeddingHandler** (embeddings module), **Graph**, **CustomTables** (resources module) and **Datasets** dataset_tools module).   
   
   In many cases, it is easy to get things done in LLMWare using only **Library** and **Query** - which provide convenient interfaces into parsing and embedding such that most use cases will not require calling those classes directly.  

   Supported document file types:  pdf, pptx, docx, xlsx, txt, csv, html, jsonl, json, tsv, jpg, jpeg, png, wav, zip, md, mp3, mp4, m4a  

   Key methods to know:  

        - Ingest anything  - `Library().add_files(input_folder_path="path/to/docs")`
   
        - Embed library    - `Library().install_new_embedding(embedding_model_name="your embedding model", vector_db="your vector db")`
   
        - Run Query        - `Query(library).query(query, query_type="semantic", result_count=20)`  
   
   Top examples to get started:  

   - [Parsing examples](https://www.github.com/llmware-ai/llmware/tree/main/examples/Parsing) - ~14 stand-alone parsing examples for all common document types, including options for parsing in memory, outputting to JSON, parsing custom configured CSV and JSON files, running OCR on embedded images found in documents, table extraction, image extraction, text chunking, zip files, and web sources.  
   - [Embedding examples](https://www.github.com/llmware-ai/llmware/tree/main/examples/Embedding) - ~15 stand-alone embedding examples to show how to use ~10 different vector databases and wide range of leading open source embedding models (including sentence transformers).  
   - [Retrieval examples](https://www.github.com/llmware-ai/llmware/tree/main/examples/Retrieval) - ~10 stand-alone examples illustrating different query and retrieval techniques - semantic queries, text queries, document filters, page filters, 'hybrid' queries, author search, using query state, and generating bibliographies.  
   - [Dataset examples](https://www.github.com/llmware-ai/llmware/tree/main/examples/Datasets) - ~5 stand-alone examples to show 'next steps' of how to leverage a Library to re-package content into various datasets and automated NLP analytics.  
   - [Fast start example #1-Parsing](https://www.github.com/llmware-ai/llmware/tree/main/fast_start/example-1-create_first_library.py) - shows the basics of parsing.  
   - [Fast start example #2-Embedding](https://www.github.com/llmware-ai/llmware/tree/main/fast_start/example-2-build_embeddings.py) - shows the basics of building embeddings.  
   - [CustomTable examples](https://www.github.com/llmware-ai/llmware/tree/main/Structured_Tables) - ~5 examples to start building structured tables that can be used in conjunction with LLM-based workflows.  


**2.  Model Prompting** - "Fun with LLMs" - the lifecycle of discovering, instantiating, and configuring an LLM-based model to execute an inference, including the ability to seamlessly prepare and integrate knowledge retrieval, and post-processing steps to validate accuracy, including:  
    
    - ModelCatalog - discover, load and manage configuration  
    - Inference
    - Function Calls  
    - Prompts  
    - Prompt with Sources
    - Fact Checking methods
    - Agent-based multi-step processes
    - Prompt History

   Core LLMWare classes:  **ModelCatalog** (models module), **Prompt**, **LLMfx** (agents module).
    
   Key methods to know:  

        - Discover Models - `ModelCatalog().list_all_models()`  

        - Load Model      - `model = ModelCatalog().load_model(model_name)`
        
        - Inference       - `response = model.inference(prompt, add_context=context)`  
        
        - Prompt          -  wraps the model class to provide easy source/retrieval management  
        
        - LLMfx           -  wraps the model class for function-calling SLIM models for agent processes  

   While ~17 individual model classes are exposed in the models module, for most use cases, we recommend working through the higher-level interface of ModelCatalog, as it promotes code re-use and the easy ability to swap models.  In many pipelines, even ModelCatalog is not required to be called directly, as the Prompt class (knowledge retrieval) and LLMfx (agents and function calls) class provide seamless workflow capabilities and are built on top of the ModelCatalog.  

   Top examples to get started:  
   - [Models examples](https://www.github.com/llmware-ai/llmware/tree/main/examples/Models) - ~20 examples showing a wide range of different model inferences and use cases, including the ability to integrate Ollama models, OpenChat (e.g., LMStudio) models, using LLama-3 and Phi-3, bringing your own models into the ModelCatalog, and configuring sampling settings.  
   - [Prompts examples](https://www.github.com/llmware-ai/llmware/tree/main/examples/Prompts) - ~5 examples that illustrate how to use Prompt as an integrated workflow for integrating knowledge sources, managing prompt history, and applying fact-checking.  
   - [SLIM-Agents examples](https://www.github.com/llmware-ai/llmware/tree/main/examples/SLIM-Agents) - ~20 examples showing how to build multi-model, multi-step Agent processes using locally-running SLIM function calling models.  
   - [Fast start example #3-Prompts and Models](https://www.github.com/llmware-ai/llmware/tree/main/fast_start/example-3-prompts_and_models.py) - getting started with model inference. 


In addition, to support these two key pipelines, LLMWare has a set of supporting and enabling classes and methods, including: 

    - resource module:  CollectionRetrieval, CollectionWriter, PromptState, QueryState, and ParserState - provides an abstraction layer on top of underlying database repositories and separate state mechanisms for major classes.   
    - gguf_configs module: GGUFConfigs 
    - model_configs module: global_model_repo_catalog_list, global_model_finetuning_prompt_wrappers_lookup, global_default_prompt_catalog  
    - util module:  Utilities  
    - setup module: Setup  
    - status module: Status
    - exceptions module: LLMWare Exceptions
    - web_services module: classes for Wikipedia, YFinance, and WebSite extraction  


**End-to-End Use Cases** - we publish and maintain a number of end-to-end use cases in [examples/Use_Cases](https://www.github.com/llmware-ai/llmware/tree/main/examples/Use_Cases)  



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

