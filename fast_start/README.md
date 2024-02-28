

Fast Start: Learning RAG with llmware through 6 examples 
===============

**Welcome to llmware!**    

Set up  

`pip3 install llmware` or, if you prefer clone the github repo locally, e.g., `git clone git@github.com:llmware-ai/llmware.git
`.   

Platforms: 
- Mac M1, Mac x86, Windows, Linux (Ubuntu 22 preferred)  
- RAM: 16 GB minimum 
- Python 3.9, 3.10, 3.11 (note: not supported on 3.12 yet)
- Use llmware >= 0.2.0 version  
- Latest version of llmware is 0.2.4 (as of end of February 2024)
  
There are 6 examples, designed to be used step-by-step, but each is self-contained, 
so you can feel free to jump into any of the examples, in any order, that you prefer.  

Each example has been designed to be "copy-paste" and RUN with lots of helpful comments and explanations embedded in the code samples.

Examples:

**Section I - Learning the Main Components**
1.  **Library** - parse, text chunk, and index to convert a "pile of files" into an AI-ready knowledge-base.  

2.  **Embeddings** - apply an embedding model to the Library, store vectors, and start enabling natural language queries.  

3.  **Prompts** & **Model Catalog** - start running inferences and building prompts.

**Section II - Connecting Knowledge with Prompts - 3 scenarios**  

4.  **RAG with Text Query** - start integrating documents into prompts.  

5.  **RAG with Semantic Query** - use natural language queries on documents and integrate with prompts.
 
6.  **RAG with more complex retrieval** - start integrating more complex retrieval patterns.

After completing these 6 examples, you should have a good foundation and set of recipes to start 
exploring the other 50+ examples in the /examples folder, and build more sophisticated 
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
   - For Fast Start, we will use "faiss" which is an embedded vector store, requiring no install
   - For more scalable deployment, we would recommend installing one of 7 supported vector databases, 
     including Milvus, PGVector (Postgres), Redis, Qdrant, Neo4j, Mongo-Atlas or Pinecone.  
   - Install instructions provided in "examples/Embedding" for specific db, as well as docker-compose scripts.

**Local Private**
    - All of the processing will take place locally on your laptop.

*This is an ongoing initiative to provide easy-to-get-started tutorials - we welcome and encourage feedback, as well
as contributions with examples and other tips for helping others on their LLM application journeys!*  

**Let's get started!**


