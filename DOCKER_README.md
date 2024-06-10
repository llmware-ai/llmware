# DOCKER README

This is a guide on setting up a Linux environment with Docker and running LLMWare examples with different database systems.

---

## Python and Pip
Python should come installed with your Linux environment.

To install Pip, run the following:
```
sudo apt-get update
sudo apt-get -y install python3-pip
pip3 install --upgrade pip
```

---

## Docker and Docker Compose
The latest versions of Docker and Docker Comopse should be installed to be able to use the Docker Compose files in the LLMWare repository.

Instructions to install Docker: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04 (Steps 1-2)
Note: Step 1 is necessary, Step 2 is optional but we highly recommend it.

Instructions to install Docker Compose: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04 (Step 1)
Note: replace the URL in the `curl` command with the latest download from https://github.com/docker/compose/releases.

Check that Docker is running on your system:
```
sudo systemctl status docker
```

---

## Running Docker Compose files
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

---

## Test with Examples
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

---

## Stopping/Deleting Containers
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
