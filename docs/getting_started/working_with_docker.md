---
layout: default
title: Working with Docker
parent: Getting Started
nav_order: 6
permalink: /getting_started/working_with_docker
---

# Working with Docker Scripts 

This section is a short guide on setting up a Linux environment with Docker and running LLMWare examples with different database systems.

## 1. Python and Pip
Python should come installed with your Linux environment.

To install Pip, run the following:
```
sudo apt-get update
sudo apt-get -y install python3-pip
pip3 install --upgrade pip
```

## 2. Docker and Docker Compose
The latest versions of Docker and Docker Comopse should be installed to be able to use the Docker Compose files in the LLMWare repository.

Instructions to install Docker: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04 (Steps 1-2)
Note: Step 1 is necessary, Step 2 is optional but we highly recommend it.

Instructions to install Docker Compose: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04 (Step 1)
Note: replace the URL in the `curl` command with the latest download from https://github.com/docker/compose/releases.

Check that Docker is running on your system:
```
sudo systemctl status docker
```

## 3. Running Docker Compose files
`cd` into the repository and ensure that you can see files of the format `docker-compose-database-name.yaml`.

To run a Compose file:
```
docker-compose -f docker-compose-database-name.yaml up -d
```

Check that the container is running:
```
docker ps
```
Note: this will list only the the containers that are currently running, add the `-a` flag (`docker ps -a`) to list all containers (even those that are stopped).

## 4. Test with Examples
The Compose files currently support 6 database systems:
- Mongo
- Postgres/PG Vector
- Neo4j
- Milvus
- Qdrant
- Redis

Note: PG Vector is an alias for Postgres and is used for vector embeddings.

1. Mongo and Postgres are used as the active database to store library text collections.
2. PG Vector, Neo4j, Milvus, Qdrant and Redis are used as the vector database to store vector embeddings.

To test that the containers are working as intended, you can modify an example provided in the LLMWare repository. The simplest example to do this is `fast_start/example-2-build_embeddings.py`.

Open the file in an editor.
1. Change the argument passed in as the active database on line 128 to an appropriate active database (Mongo or Postgres).
2. Change the argument passed in as the vector database on line 138 to an appropriate vector database (PG Vector, Neo4j, Milvus, Qdrant or Redis).

Run the example with these changes, and you should see updates in the terminal indicating that the embeddings are being generated correctly.

Note: It is possible that you will see an error:
```
llmware.exceptions.EmbeddingModelNotFoundException: Embedding model for 'example2_library' could not be located
```
In this case, use a unique name for the library name passed in on line 147.

## 5. Stopping/Deleting Containers
To stop a container, run:
```
docker stop container_ID_OR_container_name
```

To delete a container, run:
```
docker rm container_ID_OR_container_name
```

Note: passing in either the ID or the name will work.

To find the ID or name of a container, run:
```
docker ps -a
```

---

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
