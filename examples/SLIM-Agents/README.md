 🚀 Start Building Multi-Model Agents Locally on a Laptop 🚀  
===============

**What is a SLIM?**    

**SLIMs** are **S**tructured **L**anguage **I**nstruction **M**odels, which are small, specialized 1B parameter LLMs, 
finetuned to generate structured outputs (Python dictionaries, JSON and SQL) that can be handled programmatically, and 
stacked together in multi-step, multi-model Agent workflows - all running on a local CPU.  

**Check out the Intro videos**  
[SLIMS Intro Video](https://www.youtube.com/watch?v=cQfdaTcmBpY)  

There are 10 SLIM models, each delivered in two packages - a Pytorch/Huggingface FP16 model, and a  
quantized "tool" designed for fast inference on a CPU, using LLMWare's embedded GGUF inference engine.  In most cases, 
we would recommend that you start with the "tools" version of the models.

**Getting Started**

We have several ready-to-run examples in this repository:  

| Example                                                                                                                                             | Detail                                                                       |
|-----------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| 1.   Getting Started with SLIM Models ([code](slims-getting-started.py) / [video](https://www.youtube.com/watch?v=cQfdaTcmBpY) | Install the models and run hello world tests to see the models in action.    |
| 2.   Getting Started with Function-Calling Agent ([code](agent-llmfx-getting-started.py) / [video]())                                   | Generate a Structured Report with LLMfx                                      |                                                                                                                                              |   
| 3.   Multi-step Complex Analysis with Agent ([code](agent-multistep-analysis.py))                                                       | Delivering Complex Research Analysis with SLIM Agents                        |                                                                                                                               |  
| 4.   Document Clustering ([code](document-clustering.py) / [video](https://www.youtube.com/watch?v=Bncvggy6m5Q))                    | Multi-faceted automated document analysis with Topics, Tags and NER          |  
| 5.   Two-Step NER Retrieval ([code](ner-retrieval.py) / [video](https://www.youtube.com/watch?v=Cf-07GBZT68&t=2s))                          | Using NER to extract name, and then using as basis for retrieval.            |                                                                                                                                        | 
| 6.   Using Sentiment Analysis ([code](sentiment-analysis.py) / [video](https://www.youtube.com/watch?v=8aV5p3tErP0)) | Using sentiment analysis on earnings transcripts and a 'if...then' condition |
| 7.   Text2SQL - Intro ([code](text2sql-getting-started.py))                                                                             | Getting Started with SLIM-SQL-TOOL and Basic Text2SQL Inference              |                                                                                                                   |
| 8.   Text2SQL - E2E ([code](text2sql-end-to-end-2.py))                                                                                  | End-to-End Natural Langugage Query to SQL DB Query                           |                                                                                                                     |
| 9.   Text2SQL - MultiStep ([code](text2sql-multistep-example-3.py))                                                                     | Extract a customer name using NER and use in a Text2SQL query                |


For information on all of the SLIM models, check out [LLMWare SLIM Model Collection](https://www.huggingface.co/llmware/).  

**Models List**  
If you would like more information about any of the SLIM models, please check out their model card:  
- ner - extract named entities  - [slim-ner](https://www.huggingface.co/llmware/slim-ner) & [slim-ner-tool](https://www.huggingface.co/llmware/slim-ner-tool)
- sentiment - evaluate sentiment - [slim-sentiment](https://www.huggingface.co/slim-sentiment) & [slim-sentiment-tool](https://www.huggingface.co/llmware/slim-sentiment-tool)    
- topics - generate topic - [slim-topics](https://www.huggingface.co/slim-topics) & [slim-topics-tool](https://www.huggingface.co/llmware/slim-topics-tool)  
- ratings - apply 1 (low) - 5 (high) rating - [slim-ratings](https://www.huggingface.co/slim-ratings) & [slim-ratings-tool](https://www.huggingface.co/llmware/slim-ratings-tool)  
- emotions - assess emotions - [slim-emotions](https://www.huggingface.co/slim-emotions) & [slim-emotions-tool](https://www.huggingface.co/llmware/slim-emotions-tool)  
- tags - auto-generate list of tags - [slim-tags](https://www.huggingface.co/slim-tags) & [slim-tags-tool](https://www.huggingface.co/llmware/slim-tags-tool)  
- intent - identify intent - [slim-intent](https://www.huggingface.co/slim-intent) & [slim-intent-tool](https://www.huggingface.co/llmware/slim-intent-tool)  
- category - high-level category - [slim-category](https://www.huggingface.co/slim-category) & [slim-category-tool](https://wwww.huggingface.co/llmware/slim-category-tool)
- nli - assess if evidence supports conclusion - [slim-nli](https://www.huggingface.co/slim-nli) & [slim-nli-tool](https://www.huggingface.co/llmware/slim-nli-tool)  
- sql - convert text into sql - [slim-sql](https://www.huggingface.co/slim-sql) & [slim-sql-tool](https://www.huggingface.co/llmware/slim-sql-tool)  

You may also want to check out these quantized 'answer' tools, which work well in conjunction with SLIMs for question-answer and summarization:  
- bling-answer-tool - 1b quantized RAG model - [bling-answer-tool](https://www.huggingface.co/llmware/bling-answer-tool)  
- dragon-yi-answer-tool - 6b quantized RAG model - [dragon-yi-answer-tool](https://www.huggingface.co/llmware/dragon-yi-answer-tool)  
- dragon-mistral-answer-tool - 7b quantized RAG model - [dragon-mistral-answer-tool](https://www.huggingface.co/llmware/dragon-mistral-answer-tool)  
- dragon-llama-answer-tool - 7b quantized RAG model - [dragon-llama-answer-tool](https://www.huggingface.co/llmware/dragon-llama-answer-tool)  


**Set up**  
No special setup for SLIMs is required other than to install llmware >=0.2.2, e.g., `pip3 install llmware`.  

**Platforms:**   
- Mac M1, Mac x86, Windows, Linux (Ubuntu 22 preferred)  
- RAM: 16 GB minimum 
- Python 3.9, 3.10, 3.11 (note: not supported on 3.12 yet)
- llmware >= 0.2.2 version
  

### **Let's get started!  🚀**


