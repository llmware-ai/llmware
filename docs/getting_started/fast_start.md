---
layout: default
title: Fast Start
parent: Getting Started
nav_order: 4
permalink: /getting_started/fast_start
---

Fast Start: Learning RAG with llmware through 6 examples 
---

**Welcome to llmware!**    

Fast Start is a structured series of 6 self-contained examples and accompanying videos that walk through the core foundational components of RAG with LLMWare.  
Set up  

`pip3 install llmware` or, if you prefer clone the github repo locally, e.g., `git clone git@github.com:llmware-ai/llmware.git
`.   

Platforms: 
- Mac M1/M2/M3, Windows, Linux (Ubuntu 20 or Ubuntu 22 preferred)  
- RAM: 16 GB minimum  
- Python 3.9, 3.10, 3.11, 3.12
- Pull the latest version of llmware == 0.2.14 (as of mid-May 2024)  
- Please note that we have updated the examples from the original versions, to use new features in llmware, so there may be minor differences with the videos, which are annotated in the comments in each example.    
  
There are 6 examples, designed to be used step-by-step, but each is self-contained,  
so you can feel free to jump into any of the examples, in any order, that you prefer.  

Each example has been designed to be "copy-paste" and RUN with lots of helpful comments and explanations embedded in the code samples.  

Please check out our [Fast Start Youtube tutorials](https://www.youtube.com/playlist?list=PL1-dn33KwsmD7SB9iSO6vx4ZLRAWea1DB) that walk through each example below.  

Examples:

**Section I - Learning the Main Components**
1.  **Library** - parse, text chunk, and index to convert a "pile of files" into an AI-ready knowledge-base.  [Video](https://youtu.be/2xDefZ4oBOM?si=8vRCvqj0-HG3zc4c)  
  
2.  **Embeddings** - apply an embedding model to the Library, store vectors, and start enabling natural language queries.  [Video](https://youtu.be/xQEk6ohvfV0?si=B3X25ZsAZfW4AR_3)
   
3.  **Prompts** & **Model Catalog** - start running inferences and building prompts.  [Video](https://youtu.be/swiu4oBVfbA?si=0IVmLhiiYS3-pMIg)

**Section II - Connecting Knowledge with Prompts - 3 scenarios**  

4.  **RAG with Text Query** - start integrating documents into prompts.  [Video](https://youtu.be/6oALi67HP7U?si=pAbvio4ULXTIXKdL)
  
5.  **RAG with Semantic Query** - use natural language queries on documents and integrate with prompts.  [Video](https://youtu.be/XT4kIXA9H3Q?si=EBCAxVXBt5vgYY8s)
    
6.  **RAG with more complex retrieval** - start integrating more complex retrieval patterns.  [Video](https://youtu.be/G1Q6Ar8THbo?si=vIVAv35uXAcnaUJy)  
   
After completing these 6 examples, you should have a good foundation and set of recipes to start 
exploring the other 100+ examples in the /examples folder, and build more sophisticated 
LLM-based applications.

**Models**  
  - All of these examples are optimized for using local CPU-based models, primarily BLING and DRAGON.
  - If you want to substitute for any other model in the catalog, it is generally as easy as 
    switching the model_name.  If the model requires API keys, we show in the examples how to pass those keys as an
    environment variable.

**Collection Databases**  
  - Our parsers are optimized to index text chunks directly into a persistent data store.   
  - For Fast Start, we will use "sqlite" which is an embedded database, requiring no install
  - For more scalable deployment, we would recommend either "mongo" or "postgres"
  - Install instructions for "mongo" and "postgres" are provided in docker-compose files in the repository

**Vector Databases**  
   - For Fast Start, we will use "chromadb" in persistent 'file' mode, requiring no install.  
   - Note: if you are using Python < 3.12, then please feel free to substitute for faiss (which was used in the videos).  
   - Note: depending upon how and when you installed llmware, you may need to `pip install chromadb`.  
   - For more scalable deployment, we would recommend installing one of 9 supported vector databases, 
     including Milvus, PGVector (Postgres), Redis, Qdrant, Neo4j, Mongo-Atlas, Chroma, LanceDB, or Pinecone.  
   - Install instructions provided in "examples/Embedding" for specific db, as well as docker-compose scripts.  

**Local Private**
    - All of the processing will take place locally on your laptop.

*This is an ongoing initiative to provide easy-to-get-started tutorials - we welcome and encourage feedback, as well
as contributions with examples and other tips for helping others on their LLM application journeys!*  

**Let's get started!**



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
