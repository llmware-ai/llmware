---
layout: default
title: Vector Databases 
parent: Components
nav_order: 11
description: overview of the major modules and classes of LLMWare  
permalink: /components/vector_databases
---
# Vector Databases
---

llmware supports the following vector databases:  

  - Milvus and Milvus-Lite  - `milvus`  
  - Postgres (PG Vector)   - `postgres`  
  - Qdrant - `qdrant`  
  - ChromaDB - `chromadb`  
  - Redis - `redis`  
  - Neo4j - `neo4j`  
  - LanceDB - `lancedb`  
  - FAISS - `faiss`  
  - Mongo-Atlas - `mongo-atlas`  
  - Pinecone  - `pinecone`  

In llmware, unstructured content is ingested and organized into a Library, and then embeddings are created against the
Library object, and usually, handled by implicitly through the Library method `.install_new_embedding`.  

All embedding models are implemented through the embeddings.py module, and the `EmbeddingHandler` class, which routes 
the embedding process to the vector db specific handler and provides a common set of utility functions.   
In most cases, it is not necessarily to explicitly call the vector db class.   

The design is intended to promote code re-use and to make it easy to experiment with different endpoint vector databases 
without significant code changes, as well as to leverage the Library as the core organizing construct.  

#  Select Vector DB
To select a vector database in llmware is generally done is one of two ways:  

1. Explicit Setting - `LLMWareConfig().set_vector_db("postgres")`  

2. Pass the name of the vector database at the time of installing the embeddings:  

    `library.install_new_embedding(embedding_model_name=embedding_model, vector_db='milvus',batch_size=100)`

#  Install Vector DB  

No-install options:  chromadb, lancedb, faiss, and milvus-lite  

API-based options:  mongo-atlas, pinecone

Install server options:  

Generally, we have found that Docker (and Docker-Compose) are the easiest and most consistent ways to install vector 
db across different platforms.   

1.  milvus - we provide a docker-compose script in the main repository root folder path, which installs mongodb as well.

```bash 
curl -o docker-compose.yaml https://raw.githubusercontent.com/llmware-ai/llmware/main/docker-compose_mongo_milvus.yaml
docker compose up -d
```  

2.  qdrant  

```bash
curl -o docker-compose.yaml https://raw.githubusercontent.com/llmware-ai/llmware/main/docker-compose-qdrant.yaml
docker compose up -d  
```  

3. postgres and pgvector  

```bash
curl -o docker-compose.yaml https://raw.githubusercontent.com/llmware-ai/llmware/main/docker-compose-pgvector.yaml
docker compose up -d  
```  

4.  redis
```bash
# scripts to deploy other options
curl -o docker-compose.yaml https://raw.githubusercontent.com/llmware-ai/llmware/main/docker-compose-redis-stack.yaml
```

5.  neo4j

```bash
curl -o docker-compose.yaml https://raw.githubusercontent.com/llmware-ai/llmware/main/docker-compose-neo4j.yaml
docker compose up -d  
```  

# Configure Vector DB  

To configure a vector database in llmware, we provide configuration objects in the `configs.py` module to adjust 
authentication, port/host information, and other common configurations.   To use the configuration, the pattern is 
as follows through simple `get_config` and `set_config` methods:    

```python
from llmware.configs import MilvusConfig
MilvusConfig().set_config("lite", True)

from llmware.configs import ChromaDBConfig
current_config = ChromaDBConfig().get_config("persistent_path")  
ChromaDBConfig().set_config("persistent_path", "/new/local/path")
```

Configuration objects are provided for the following vector DB:  `MilvusConfig`, `ChromaDBConfig`, `QdrantConfig`, 
`Neo4jConfig`, `LanceDBConfig`, `PineConeConfig`, `MongoConfig`, `PostgresConfig`.  

For 'out-of-the-box' testing and development, for most use cases, you will not need to change these configs.  

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

