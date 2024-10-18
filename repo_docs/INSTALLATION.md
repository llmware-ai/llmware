## ✍️ Working with the llmware Github repository  

The llmware repo can be pulled locally to get access to all the examples, or to work directly with the latest version of the llmware code.  

```bash
git clone git@github.com:llmware-ai/llmware.git
```  

We have provided a **welcome_to_llmware** automation script in the root of the repository folder.  After cloning:  
- On Windows command line:  `.\welcome_to_llmware_windows.sh`  
- On Mac / Linux command line:  `sh ./welcome_to_llmware.sh`  

Alternatively, if you prefer to complete setup without the welcome automation script, then the next steps include:  

1.  **install requirements.txt** - inside the /llmware path - e.g., ```pip3 install -r llmware/requirements.txt```  

2.  **install requirements_extras.txt** - inside the /llmware path - e.g., ```pip3 install -r llmware/requirements_extras.txt```  (Depending upon your use case, you may not need all or any of these installs, but some of these will be used in the examples.)  

3.  **run examples** - copy one or more of the example .py files into the root project path.   (We have seen several IDEs that will attempt to run interactively from the nested /example path, and then not have access to the /llmware module - the easy fix is to just copy the example you want to run into the root path).  

4.  **install vector db** - no-install vector db options include milvus lite, chromadb, faiss and lancedb - which do not require a server install, but do require that you install the python sdk library for that vector db, e.g., `pip3 install pymilvus`, or `pip3 install chromadb`.  If you look in [examples/Embedding](https://github.com/llmware-ai/llmware/tree/main/examples/Embedding), you will see examples for getting started with various vector DB, and in the root of the repo, you will see easy-to-get-started docker compose scripts for installing milvus, postgres/pgvector, mongo, qdrant, neo4j, and redis.  

5.  Pytorch 2.3 note:  we have seen recently issues with Pytorch==2.3 on some platforms - if you run into any issues, we have seen that uninstalling Pytorch and downleveling to Pytorch==2.1 usually solves the problem.  

6.  Numpy 2.0 note: we have seen issues with numpy 2.0 with many libraries not yet supporting.  Our pip install setup will accept numpy 2.0 (to avoid pip conflicts), but if you pull from repo, we restrict to <2.   If you run into issues with numpy, we have found that they can be fixed by downgrading numpy to <2, e.g., 1.26.4.  To use WhisperCPP, you should downlevel to numpy <2.  
