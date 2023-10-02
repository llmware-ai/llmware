# Getting started with llmware

| Example     |  Detail      |
--------------|--------------|
| 1.  Getting Started ([code](getting_started.py)) | Create and populate your first library, prepare the library for semantic search with vector embeddings, and run a semantic search. |
| 2.  Working with LLMs ([code](working_with_llms.py)) | Connect to your favorite LLM and perform basic prompts. |
| 3.  LLM Prompts ([code](llm_prompts.py)) | Prompt LLMs with various sources, explore the out-of-the-box Prompt Catalog, and use different prompt styles.|
| 4.  Retrieval ([code](retrieval.py)) | Explore the breadth of retrieval capabilities and persisting, loading and saving retrieval history.|
| 5.  RAG ([code](rag.py)) | Integrate Prompts and Retrieval using various information Sources to accomplish Retrieval Augmented Generation (RAG).|
| 6.  Working with Prompts ([code](working_with_prompts.py)) |  Inspection of Prompt history which is useful in AI Audit scenarios.| 
| 7.  Parsing ([code](parsing.py)) | Ingest at scale into library and ‘at runtime' into any Prompt.|
| 8.  Embedding ([code](embedding.py)) | Simple access to multiple embedding models and vector DBs (“mix and match”). |
| 9.  Huggingface Integration ([code](huggingface_integration.py)) | How to bring your favorite HF model into llmware seamlessly.  Customize a generative model with weights from a custom fine-tuned model. |
| 10.  `llmware` BLING model ([code](llmware_bling.py)) | Experiement with RAG scenarios using ~1B parameter GPT models that can run on your laptop.  BLING models are fine-tuned for common RAG scenarios, specifically: question-answering, key-value extraction, and basic summarization.   | 
| 11.  Knowledge Graph ([code](knowledge_graph.py)) | Generate scalable, statistical NLP artifacts - knowledge graphs & document graphs.  |
| 12.  Datasets ([code](datasets.py)) | Dataset generation streamlined for fine-tuning generative and embedding models and formats such as Alpaca, ChatGPT, Human-Bot.  |
| 13. Working without Databases ([code](working_without_a_database.py))| Parse, Prompt and generate Datasets from Prompt history without installing MongoDB or a vector database.|
| 14.  Working with Libraries ([code](working_with_libraries.py)) | Explore all Library operations. |

# Using llmware without MongoDB or an embedding database
You can do some interesting things using `llmware` without a database or vector embeddings.  Parsing can be done in memory and outputted to text or json. Prompts can be crafted with sources from files, Wikipedia or the Yahoo Finance API.  The [Working without a Database](working_without_a_database.py), [LLM Prompts](llm_prompts.py), and [Parsing](parsing.py) examples show scenarios that can be accomplished and through out the examples are specific methods that do not require MongoDB or embeddings.  

# Additional llmware capabilities
- The `llmware` public model repository with out-of-the-box custom trained sentence transformer embedding models fine-tuned for the following industries:  Insurance, Contracts, Asset Management, SEC. These domain specific models along with `llmware`'s generative BLING model series ("Best Little Instruction-following No-GPU-required") are available at [llmware on Huggingface](https://huggingface.co/llmware). Explore their use in the [Embedding](embedding.py), [Huggingface Integration](huggingface_integration.py), and [`llmware` BLING model](llmware_bling.py) examples.  

- Create knowledge graphs with a high-powered and fast C-based co-occurrence table matrix builder, the output of which can feed NLP statistics as well as potentially graph databases.  Explore the [Knowledge Graph](knowledge_graph.py) example.

- Generate datasets for fine-tuning both generative and embedding models.  llmware uses sophisticated data-crafting strategies, and leveraging the data captured throughout the system.  Explore the [Datasets](datasets.py) example.  
  
- Library is the simple, flexible, unifying construct in llmware to assemble and normalize parsed text chunks, and is linked to both a text search index, and an open platform of embedding models and vector databases. Explore the [Working with Libraries](working_with_libraries.py) example.

- The llmware parsers follow a consistent 27 key metadata dictionary, so that you can extract the same information from a PDF as a PowerPoint or Text file. The parsers generally extract images, tables, and all available document metadata.  There is a complete set of text chunking tools to parse a batch of documents (across multiple formats) and chunk and store in consistent format in a document store.  Explore the [Parsing](parsing.py) example.

- All data artifacts are published in standard formats – json, txt files, pytorch_model.bin files, and fully portable and exportable to any platform. 

