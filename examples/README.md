# Top New Examples 

Looking for the Fast Start tutorial series? [Click here](./fast_start/)  
Looking for SLIM Models?  [Click here](SLIM-Agents/)  

| Example                                                                                                                    | Detail                                                                                                                                                                                                                          |
|----------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1.   BLING models fast start ([code](Models/bling_fast_start.py) / [video](https://www.youtube.com/watch?v=JjgqOZ2v5oU)    | Explore `llmware`'s BLING model series ("Best Little Instruction-following No-GPU-required").  See how they perform in common RAG scenarios - question-answering, key-value extraction, and basic summarization.                |
| 2.   DRAGON GGUF Models ([code](Models/dragon_gguf_fast_start.py) / [video](https://www.youtube.com/watch?v=BI1RlaIJcsc&t=130s) | State-of-the-Art 7B RAG GGUF Models.                                                                                                                                                                                            |   
| 3.   Using Custom GGUF Models([code](Models/using-custom-gguf-models.py) / [video](https://www.youtube.com/watch?v=9wXJgld7Yow) | Building RAG with any GGUF model                                                                                                                                                                                                |  
| 4.   Multiple Embeddings with PG Vector ([code](Embedding/using_multiple_embeddings.py) / [video](https://www.youtube.com/watch?v=Bncvggy6m5Q) | Comparing Multiple Embedding Models using Postgres / PG Vector                                                                                                                                                                  |  
| 5.   Master Service Agreement Analysis with DRAGON ([code](Models/msa_processing.py) / [video](https://www.youtube.com/watch?v=Cf-07GBZT68&t=2s) | Analyzing MSAs using DRAGON YI 6B Model.                                                                                                                                                                                        | 
| 6.   RAG with BLING ([code](RAG/contract_analysis_on_laptop_with_bling_models.py) / [video](https://www.youtube.com/watch?v=8aV5p3tErP0) | Using contract analysis as an example, experiment with RAG for complex document analysis and text extraction using `llmware`'s BLING ~1B parameter GPT model running on your laptop.                                            |
| 7.   Parse and Embed with Milvus([code](Embedding/docs2vecs_with_milvus_un_resolutions)                                    | End-to-end example for Parsing, Embedding and Querying 500 pdf documents     |                                                                                                                                                   |
| 8.   Streamlit Example ([code](Getting_Started/ui_without_a_database.py)  | Upload pdfs, and run inference on llmware BLING models.                                                                                                                                                                                                                                             |
| 9.   Integrating LM Studio ([code](Models/using-open-chat-models.py) / [video](https://www.youtube.com/watch?v=h2FDjUyvsKE&t=101s)            | Integrating LM Studio Models with LLMWare                                                                                                                                                                                       |                                                                                                                                       
| 10.  Prompts With Sources ([code](Prompts/prompt_with_sources.py))                                                                            | Attach wide range of knowledge sources directly into Prompts.                                                                                                                                                                   
| 11.  DRAGON RAG benchmark testing with llmware ([code](Models/dragon_rag_benchmark_tests_llmware.py))                                         | Run RAG instruct benchmark tests against the `llmware` DRAGON models to find the best one for your RAG workflow. This example uses the llmware Prompt API which provides additional capabilities such as evidence/fact checking |
| 12.  Fact Checking ([code](Prompts/fact_checking.py))                                                                                         | Explore the full set of evidence methods in this example script that analyzes a set of contracts.                                                                                                                               |
| 13.  Using 7B GGUF Chat Models ([code](Models/chat_models_gguf_fast_start.py)) | Using 4 state of the art 7B chat models in minutes running locally                                                                                                                                                              |
| 14.  Hybrid Retrieval - Semantic + Text ([code](Retrieval/dual_pass_with_custom_filter.py)) | Using 'dual pass' retrieval to combine best of semantic and text search                                                                                                                                                         |

# Using SQLite and No-Install Vector DB options - `llmware` Fast Start  
- LLMWare is an enterprise-grade data pipeline and requires the use of a database.  For a quick start, with no installation, we provide SQLite instance, as well 
as no-install vector db options, including ChromaDB, LanceDB and FAISS.

#  Fast Start Tutorials
- Please also see the fast_start repository for an end-to-end set of 6 tutorials with code.  

# `llmware` Open Source Models
The `llmware` public model repository has 4 model collections:
- **SLIM model series:** small, specialized models fine-tuned for function calling and multi-step, multi-model Agent workflows.  
- **DRAGON model series:**  Production-grade RAG-optimized 6-7B parameter models - "Delivering RAG on ..." the leading foundation base models.
- **BLING model series:**  Small CPU-based RAG-optimized, instruct-following 1B-3B parameter models.
- **Industry BERT models:**  out-of-the-box custom trained sentence transformer embedding models fine-tuned for the following industries:  Insurance, Contracts, Asset Management, SEC.

These models collections are available at [`llmware` on Hugging Face](https://huggingface.co/llmware). 

