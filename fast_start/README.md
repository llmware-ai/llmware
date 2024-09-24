

Fast Start: Learning llmware through examples  
===============

**Welcome to llmware!**    

llmware has two separate fast start modules, depending upon your objective and use case:

1. [**Agents**](https://www.github.com/llmware-ai/llmware/tree/main/fast_start/agents) - this structured set of examples will introduce you quickly to deploying small specialized language models - get started running models on your laptop, executing function calls, and building agent-based workflows in minutes.

2.  [**RAG**](https://www.github.com/llmware-ai/llmware/tree/main/fast_start/rag) - this is our original course that builds up each step in the process of building an AI-ready knowledge base, and connecting to the knowledge base with models.   It will cover models and agents, but in the process of building a wider RAG foundation in terms of parsing, text chunking, embedding, retrieval, and creating Libraries.  


Set up  

`pip3 install llmware` or `pip3 install 'llmware[full]'` or, if you prefer clone the github repo locally, e.g., `git clone git@github.com:llmware-ai/llmware.git`.  If you clone the repo, then we would recommend that you run the `welcome_to_llmware.sh` or `welcome_to_llmware_windows.sh` scripts to install all of the dependencies.    

Note: starting in llmware>=0.3.0, we offer two pip install options.  If you use the standard `pip3 install llmware`, then you will need to add a few additional pip3 installs in the RAG fast start to run examples 2 and 5 below, specifically:  

  `pip3 install torch`  
  `pip3 install transformers`  

Platforms:  
- Mac M1/M2/M3, Windows, Linux (Ubuntu 20 or Ubuntu 22 preferred)  
- RAM: 16 GB minimum  
- Python 3.9, 3.10, 3.11, 3.12 
- Pull the latest version of llmware == 0.3.0 (as of early June 2024)  
- Please note that we have updated the examples from the original versions, to use new features in llmware, so there may be minor differences with the videos, which are annotated in the comments in each example.    
  
There are 9 examples, designed to be used step-by-step, but each is self-contained,  
so you can feel free to jump into any of the examples, in any order, that you prefer.  

Each example has been designed to be "copy-paste" and RUN with lots of helpful comments and explanations embedded in the code samples.  

Please check out our [Fast Start Youtube tutorials](https://www.youtube.com/playlist?list=PL1-dn33KwsmD7SB9iSO6vx4ZLRAWea1DB) that walk through each example below.  

**RAG Course:**  

**Section I - Learning the Main Components**
1.  **Library** - parse, text chunk, and index to convert a "pile of files" into an AI-ready knowledge-base.  [Video](https://youtu.be/2xDefZ4oBOM?si=8vRCvqj0-HG3zc4c)  
  
2.  **Embeddings** - apply an embedding model to the Library, store vectors, and start enabling natural language queries.  [Video](https://youtu.be/xQEk6ohvfV0?si=B3X25ZsAZfW4AR_3)
   
3.  **Prompts** & **Model Catalog** - start running inferences and building prompts.  [Video](https://youtu.be/swiu4oBVfbA?si=0IVmLhiiYS3-pMIg)

**Section II - Connecting Knowledge with Prompts - 3 scenarios**  

4.  **RAG with Text Query** - start integrating documents into prompts.  [Video](https://youtu.be/6oALi67HP7U?si=pAbvio4ULXTIXKdL)
  
5.  **RAG with Semantic Query** - use natural language queries on documents and integrate with prompts.  [Video](https://youtu.be/XT4kIXA9H3Q?si=EBCAxVXBt5vgYY8s)
    
6.  **RAG with more complex retrieval** - start integrating more complex retrieval patterns.  [Video](https://youtu.be/G1Q6Ar8THbo?si=vIVAv35uXAcnaUJy)  

**Section III - Function Calls & Agents**  

7.  **Function Calls** - move beyond 'question-answer' prompting and start prompting with function calls.  

8.  **Agents** - the power of function calls is the ability to integrate model function calls as 'tools' available to an agent orchestrator.  [Video](https://youtu.be/cQfdaTcmBpY?si=pMWQj0qpPBVRmm34)  

9.  **Function Calls with Web Services** - one of the most exciting use cases is the ability to combine function calls with web services.   [Video](https://youtu.be/l0jzsg1_Ik0?si=ifwxVi_Z6I_hNtcf)  

After completing these 9 examples, you should have a good foundation and set of recipes to start 
exploring the other 100+ examples in the /examples folder, and build more sophisticated 
LLM-based applications.  

**Models**  
  - All of these examples are optimized for using local CPU-based models, primarily BLING, DRAGON and SLIM models.   
  - If you want to substitute for any other model in the catalog, it is generally as easy as 
    switching the model_name.  If the model requires API keys, we show in the examples how to pass those keys as an
    environment variable.  

**Collection Databases**  
  - Our parsers are optimized to index text chunks directly into a persistent data store.   
  - For Fast Start, we will use "sqlite" which is an embedded database, requiring no install  
  - For more scalable deployment, we would recommend either "mongo" or "postgres"  
  - Install instructions for "mongo" and "postgres" are provided in docker-compose files in the repository  

**Vector Databases**  
   - For Fast Start, we will use a no-install vector db (in Examples 2 and 5 specifically).  
   - There are 4 no-install options supported, but depending upon your enviroment, you may need to pip3 install the corresponding vector db python sdk, eg.:  
     
     - chromadb:  `pip3 install chromadb`  
     - milvus lite: `pip3 install pymilvus`  (Mac and Linux only)  
     - faiss: `pip3 install faiss`   
     - lancedb: `pip3 install lancedb`  
       
   - For more scalable deployment, we would recommend installing one of 9 supported vector databases, 
     including Milvus, PGVector (Postgres), Redis, Qdrant, Neo4j, Mongo-Atlas, Chroma, LanceDB, or Pinecone.   
   - Install instructions provided in "examples/Embedding" for specific db, as well as docker-compose scripts.  

**Local Private**
    - All of the processing will take place locally on your laptop.

*This is an ongoing initiative to provide easy-to-get-started tutorials - we welcome and encourage feedback, as well
as contributions with examples and other tips for helping others on their LLM application journeys!*  

**Let's get started!**


