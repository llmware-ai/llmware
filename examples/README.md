# Getting started with `llmware`

| Example     |  Detail      |
|-------------|--------------|
| 1.   Getting Started ([code](getting_started.py)) | Create and populate your first library, prepare the library for semantic search with vector embeddings, and run a semantic search. |
| 2.   Working with LLMs ([code](working_with_llms.py)) | Connect to your favorite LLM and perform basic prompts. |
| 3.   LLM Prompts ([code](llm_prompts.py)) | Prompt LLMs with various sources, explore the out-of-the-box Prompt Catalog, and use different prompt styles.|
| 4.   Retrieval ([code](retrieval.py)) | Explore the breadth of retrieval capabilities and persisting, loading and saving retrieval history.|
| 5.   RAG Quick Start ([code](rag.py) / [video](https://www.youtube.com/watch?v=0naqpH93eEU)) | End-to-end RAG scenario in less than 15 lines of code.|
| 6.   BLING models ([code](bling_fast_start.py) / [video](https://www.youtube.com/watch?v=JjgqOZ2v5oU))   | Explore `llmware`'s BLING model series ("Best Little Instruction-following No-GPU-required").  See how they perform in common RAG scenarios - question-answering, key-value extraction, and basic summarization.   |
| 7.   RAG with BLING ([code](bling_rag.py)) | Experiment with RAG scenarios using `llmware`'s BLING ~1B parameter GPT model running on your laptop.   |
| 8.   RAG benchmark testing ([code](bling_rag_benchmark_tests.py)) | Run RAG instruct benchmark tests against the `llmware` BLING models to find the best one for your RAG workflow.  |
| 9.   RAG "on the fly" ([code](working_without_a_database.py)) |  Analyze a set of documents using RAG _without_ a database or vector embeddings. |
| 10.  Fact Checking ([code](bling_evidence_checking.py))  | Explore the full set of evidence methods in this example script that analyzes a set of contracts. |
| 11.  Hallucination Guardrails |  Fact checking model responses with the `analyze_contracts_on_the_fly` ([code](working_without_a_database.py)), a variety of fact checking techniques with the `prompt_fact_checking` ([code](working_with_prompts.py)), human in the loop interaction reports with the `send_to_human_for_review` ([code](rag.py)).  |
| 12.  Working with Prompts ([code](working_with_prompts.py)) |  Inspection of Prompt history which is useful in AI Audit scenarios.| 
| 13.  Parsing ([code](parsing.py)) | Ingest at scale into library and ‘at runtime' into any Prompt.|
| 14.  Embedding ([code](embedding.py)) | Simple access to multiple embedding models and vector DBs (“mix and match”). |
| 15.  Hugging Face Integration ([code](huggingface_integration.py)) | How to bring your favorite HF model into llmware seamlessly.  Customize a generative model with weights from a custom fine-tuned model. |
| 16.  Knowledge Graph ([code](knowledge_graph.py)) | Generate scalable, statistical NLP artifacts - knowledge graphs & document graphs.  |
| 17.  Working with Datasets ([code](working_with_datasets.py)) | Dataset generation streamlined for fine-tuning generative and embedding models and formats such as Alpaca, ChatGPT, Human-Bot.  |
| 18.  Working without Databases ([code](working_without_a_database.py) / [video](https://www.youtube.com/watch?v=tAGz6yR14lw))| Parse, Prompt and generate Datasets from Prompt history without installing MongoDB or a vector database.|
| 19.  Working with Libraries ([code](working_with_libraries.py)) | Explore all Library operations. |
| 20.  Using MongoDB Atlas ([code](using_mongo_atlas.py) / [video](https://www.youtube.com/watch?v=scGMcVk7mws))  | Demonstrates using MongoDB Atlas as `llmware`'s NoSQL datastore and Atlas Vector Search for vector embeddings.|


# Using `llmware` without a database
You can do some interesting things using `llmware` without a database or vector embeddings.  Parsing can be done in memory and outputted to text or json. Prompts can be crafted with sources from files, Wikipedia or the Yahoo Finance API.  The **Working without Databases** ([code](working_without_a_database.py) / [video](https://www.youtube.com/watch?v=tAGz6yR14lw)), [LLM Prompts](llm_prompts.py), and [Parsing](parsing.py) examples show scenarios that can be accomplished and throughout the examples are specific methods that do not require MongoDB or embeddings.  

# `llmware` BLING Models
The `llmware` public model repository has out-of-the-box custom trained sentence transformer embedding models fine-tuned for the following industries:  Insurance, Contracts, Asset Management, SEC. These domain specific models along with `llmware`'s generative BLING model series ("Best Little Instruction-following No-GPU-required") are available at [llmware on Hugging Face](https://huggingface.co/llmware). Explore their use in the [Embedding](embedding.py), [Hugging Face Integration](huggingface_integration.py),[`llmware` BLING model](bling_fast_start.py), [RAG with BLING](bling_rag.py), and [RAG benchmark testing](bling_rag_benchmark_tests.py) examples.

# Additional llmware capabilities
- Create knowledge graphs with a high-powered and fast C-based co-occurrence table matrix builder, the output of which can feed NLP statistics as well as potentially graph databases.  Explore the [Knowledge Graph](knowledge_graph.py) example.

- Generate datasets for fine-tuning both generative and embedding models.  `llmware` uses sophisticated data-crafting strategies, and leveraging the data captured throughout the system.  Explore the [Datasets](working_with_datasets.py) example.  
  
- Library is the simple, flexible, unifying construct in `llmware` to assemble and normalize parsed text chunks, and is linked to both a text search index, and an open platform of embedding models and vector databases. Explore the [Working with Libraries](working_with_libraries.py) example.

- The `llmware` parsers follow a consistent 27 key metadata dictionary, so that you can extract the same information from a PDF as a PowerPoint or Text file. The parsers generally extract images, tables, and all available document metadata.  There is a complete set of text chunking tools to parse a batch of documents (across multiple formats) and chunk and store in consistent format in a document store.  Explore the [Parsing](parsing.py) example.

- All data artifacts are published in standard formats – json, txt files, pytorch_model.bin files, and fully portable and exportable to any platform. 

