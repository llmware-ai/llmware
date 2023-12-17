# llmware
![Static Badge](https://img.shields.io/badge/python-3.9_%7C_3.10%7C_3.11-blue?color=blue)
![PyPI - Version](https://img.shields.io/pypi/v/llmware?color=blue)

`llmware` is a unified, open, extensible framework for LLM-based application patterns including Retrieval Augmented Generation (RAG). This project provides a comprehensive set of tools that anyone can use – from beginner to the most sophisticated AI developer – to rapidly build industrial-grade enterprise LLM-based applications with specific focus on leveraging open source models, small specialized LLMs, and delivering end-to-end private cloud LLM-based applications.  _Key differentiators include: first-tier integration of 20+ RAG-optimized open source models between 1B-7B parameters (BLING and DRAGON); scalable ingestion and embedding of documents and integration of sources into Prompts; and tools for source citation for Q & A, fact checking, and other guardrails for model hallucination_.

With `llmware`, our goal is to contribute to and help catalyze an open community around the new combination of open, extensible technologies being assembled to accomplish fact-based generative workflows.

## 🎯  Key features
`llmware` is an integrated framework comprised of four major components:

<details>
<summary><b><u>Retrieval</u>: Assemble and Query knowledge base </b></summary>

- **High-performance document parsers** to rapidly ingest, text chunk and ingest common document types.
- **Comprehensive intuitive querying methods**: semantic, text, and hybrid retrieval with integrated metadata.
- **Ranking and filtering strategies** to enable semantic search and rapid retrieval of information.
- **Web scrapers, Wikipedia integration, and Yahoo Finance API** integration as additional tools to assemble fact-sets for generation.
</details>


<details>    
<summary><b><u>Prompt</u>: Simple, Unified Abstraction across 50+ Models</b></summary>

- **Connect Models:** Simple high-level interface with flexible Model Catalog and support for 50+ models out of the box, with focus on open source generative and embedding models, along with all of the leading commercial LLMs.
- **Prompts with Sources:** Powerful abstraction to easily package a wide range of materials into model context window sizes. Sources include files, websites, audio, AWS Transcribe transcripts, Wikipedia and Yahoo Finance.  
- **Prompt Catalog:** Dynamically configurable prompts to experiment with multiple models without any change in the code.
- **Post Processing:** a full set of metadata and tools for evidence verification, classification of a response, and fact-checking.
- **Human in the Loop:** Ability to enable user ratings, feedback, and corrections of AI responses.
- **Auditability:** A flexible state mechanism to capture, track, analyze and audit the LLM prompt lifecycle. 
</details>

<details>
<summary><b><u>Vector Embeddings</u>:  swappable embedding models and vector databases</b></summary>

- **Industry Bert**: provide out-of-the-box industry finetuned open source Sentence Transformers.
- **Wide Model Support**: Custom trained HuggingFace, sentence transformer embedding models and support for leading commercial models.
- **Mix-and-match** among multiple options to find the right solution for any particular application.
- **Out-of-the-box** support for 4 vector databases - Milvus, FAISS, Pinecone and Mongo Atlas.
</details>
  
<details>
<summary><b><u>Parsing and Text Chunking</u>: Scalable Ingestion </b></summary>
  
* Integrated High-Speed Parsers for:  PDF, PowerPoint, Word, Excel, HTML, Text, WAV, AWS Transcribe transcripts.
* A complete set of text-chunking tools to separate information and associated metadata to a consistent block format.
</details>

#### 📚 Explore [additional llmware capabilities](https://github.com/llmware-ai/llmware/blob/main/examples/README.md) and 🎬 Check out these videos on how to quickly get started with RAG:
- [Use small LLMs for RAG for Contract Analysis (feat. LLMWare)](https://www.youtube.com/watch?v=8aV5p3tErP0)
- [Invoice Processing with LLMware](https://www.youtube.com/watch?v=VHZSaBBG-Bo&t=10s)
- [Ingest PDFs at Scale](https://www.youtube.com/watch?v=O0adUfrrxi8&t=10s)
- [Evaluate LLMs for RAG with LLMWare](https://www.youtube.com/watch?v=s0KWqYg5Buk&t=105s)
- [Fast Start to RAG with LLMWare Open Source Library](https://www.youtube.com/watch?v=0naqpH93eEU)
- [Use Retrieval Augmented Generation (RAG) without a Database](https://www.youtube.com/watch?v=tAGz6yR14lw)
- [RAG using CPU-based (No-GPU required) Hugging Face Models with LLMWare on your laptop](https://www.youtube.com/watch?v=JjgqOZ2v5oU)
- [Pop up LLMWare Inference Server](https://www.youtube.com/watch?v=qiEmLnSRDUA&t=20s)
- [DRAGON-7B-Models](https://www.youtube.com/watch?v=d_u7VaKu6Qk&t=37s)
- 
## 🌱 Getting Started

### 1. Install llmware:

```bash
pip install llmware
```
or 
```bash
python3 -m pip install llmware
```
See [Working with llmware](#%EF%B8%8F-working-with-the-llmware-github-repository) for other options to get up and running.

### 2. MongoDB and Milvus

MongoDB and Milvus are optional and used to provide production-grade database and vector embedding capabilities. The fastest way to get started is to use the provided Docker Compose file which takes care of running them both:
```bash
curl -o docker-compose.yaml https://raw.githubusercontent.com/llmware-ai/llmware/main/docker-compose.yaml
```
and then run the containers:
```bash
docker compose up -d
```
Not ready to install MongoDB or Milvus?  Check out what you can do without them in our [examples section](https://github.com/llmware-ai/llmware/blob/main/examples/README.md#using-llmware-without-mongodb-or-an-embedding-database).

See [Running MongoDB and Milvus](#%EF%B8%8F-alternate-options-for-running-mongodb-and-milvus) for other options to get up and running with these optional dependencies.

### 3. 🔥 Start coding - Quick Start for RAG 🔥 
```python
# This example illustrates a simple contract analysis using a small RAG-optimized LLM running locally:

import os
import re
from llmware.prompts import Prompt, HumanInTheLoop
from llmware.setup import Setup
from llmware.configs import LLMWareConfig

def contract_analysis_on_laptop (model_name):

    # Load the llmware sample files
    print (f"\n > Loading the llmware sample files...")
    sample_files_path = Setup().load_sample_files()
    contracts_path = os.path.join(sample_files_path,"Agreements")
 
    # query list
    query_list = {"executive employment agreement": "What are the name of the two parties?",
                  "base salary": "What is the executive's base salary?",
                  "governing law": "What is the governing law?"}

    print (f"\n > Loading model {model_name}...")

    prompter = Prompt().load_model(model_name)

    for i, contract in enumerate(os.listdir(contracts_path)):

        #   excluding Mac file artifact
        if contract != ".DS_Store":

            print("\nAnalyzing contract: ", str(i+1), contract)

            print("LLM Responses:")
            for key, value in query_list.items():

                # contract is parsed, text-chunked, and then filtered by topic key
                source = prompter.add_source_document(contracts_path, contract, query=key)

                # calling the LLM with 'source' information from the contract automatically packaged into the prompt
                responses = prompter.prompt_with_source(value, prompt_name="just_the_facts", temperature=0.3)

                for r, response in enumerate(responses):
                    print(key, ":", re.sub("[\n]"," ", response["llm_response"]).strip())

                # We're done with this contract, clear the source from the prompt
                prompter.clear_source_materials()

    # Save jsonl report to jsonl to /prompt_history folder
    print("\nPrompt state saved at: ", os.path.join(LLMWareConfig.get_prompt_path(),prompter.prompt_id))
    prompter.save_state()

    # Save csv report that includes the model, response, prompt, and evidence for human-in-the-loop review
    csv_output = HumanInTheLoop(prompter).export_current_interaction_to_csv()
    print("csv output saved at:  ", csv_output)


if __name__ == "__main__":

    # use local cpu model - smallest, fastest (use larger BLING models for higher accuracy)
    model = "llmware/bling-1b-0.1"

    contract_analysis_on_laptop(model)

```

#### 📚 See 50+ [llmware examples](https://github.com/llmware-ai/llmware/blob/main/examples/README.md) for more RAG examples and other code samples and ideas.


### 4. Accessing LLMs and setting-up API keys & secrets

To use LLMWare, you do not need to use any proprietary LLM - we would encourage you to experiment with (BLING)[https://huggingface.co/llmware], (DRAGON)[https://huggingface.co/llmware], (Industry-BERT)[https://huggingface.co/llmware], the GGUF examples, along with bringing in your favorite models from HuggingFace and Sentence Transformers. 

If you would like to use a proprietary model, you will need to provide your own API Keys.   API keys and secrets for models, aws, and pinecone can be set-up for use in environment variables or managed however you prefer. 

## 🔹 Alternate options for running MongoDB and Milvus

There are several options for getting MongoDB running
<details>
<summary><b>🐳  A. Run mongo container with docker </b></summary>
  
  ```bash
docker run -d -p 27017:27017  -v mongodb-volume:/data/db --name=mongodb mongo:latest
```
</details>

<details>
<summary><b>🐳  B. Run container with docker compose </b></summary>
  
 Create a _docker-compose.yaml_ file with the content: 
```yaml
version: "3"

services:
  mongodb:
    container_name: mongodb
    image: 'mongo:latest'
    volumes:
      - mongodb-volume:/data/db
    ports:
      - '27017:27017'

volumes:
    llmware-mongodb:
      driver: local
```
and then run:
```bash
docker compose up
```
</details>

<details>
<summary><b>📖  C. Install MongoDB natively </b></summary>
  
See the [Official MongoDB Installation Guide](https://www.mongodb.com/docs/manual/installation/)

</details>

<details>
<summary><b>🔗  D. Connect to an existing MongoDB deployment </b></summary>
  
You can connect to an existing MongoDB deployment by setting the connection string to the environment variable, ```COLLECTION_DB_URI```.  See the example script, [Using Mongo Atlas](https://github.com/llmware-ai/llmware/blob/main/examples/using_mongo_atlas.py), for detailed information on how to use Mongo Atlas as the NoSQL and/or Vector Database for `llmware`.  

Additional information on finding and formatting connection strings can be found in the [MongoDB Connection Strings Documentation](https://www.mongodb.com/docs/manual/reference/connection-string/).


</details>

## ✍️ Working with the llmware Github repository

The llmware repo can be pulled locally to get access to all the examples, or to work directly with the latest version of the llmware code.

### Pull the repo locally

```bash
git clone git@github.com:llmware-ai/llmware.git
```
or download/extract a [zip of the llmware repository](https://github.com/llmware-ai/llmware/archive/refs/heads/main.zip)

### Run llmware natively 

Update the local copy of the repository:

```bash
git pull
```
Download the shared llmware native libraries and dependencies by running the load_native_libraries.sh script. This pulls the right wheel for your platform and extracts the llmware native libraries and dependencies into the proper place in the local repository.   
 
```bash
./scripts/dev/load_native_libraries.sh
```

At the top level of the llmware repository run the following command:

```bash
pip install .
```

## ✨  Getting help or sharing your ideas with the community
Questions and discussions are welcome in our [github discussions](https://github.com/llmware-ai/llmware/discussions).

Interested in contributing to llmware? We welcome involvement from the community to extend and enhance the framework!  
- 💡 What's your favorite model or is there one you'd like to check out in your experiments? 
- 💡 Have you had success with a different embedding databases?
- 💡 Is there a prompt that shines in a RAG workflow?

Information on ways to participate can be found in our [Contributors Guide](https://github.com/llmware-ai/llmware/blob/main/CONTRIBUTING.md#contributing-to-llmware).  As with all aspects of this project, contributing is governed by our [Code of Conduct](https://github.com/llmware-ai/llmware/blob/main/CODE_OF_CONDUCT.md).

## 📣  Release notes and Change Log

**Latest Updates - 17 Dec 2023: llmware v0.1.12**
  - dragon-deci-7b added to catalog - RAG-finetuned model on high-performance new 7B model base from Deci
  - New GGUFGenerativeModel class for easy integration of GGUF Models
  - Adding prebuilt llama_cpp / ctransformer shared libraries for 'out of the box' use on Mac M1, Mac x86, Linux x86 and Windows
  - 3 DRAGON models packaged as Q4_K_M GGUF models for CPU laptop use (dragon-mistral-7b, dragon-llama-7b, dragon-yi-6b)
  - 4 leading open source chat models added to default catalog with Q4_K_M with support for specific chat prompt wrappers
  
**Supported Operating Systems:**  
- MacOS
- Linux
- Windows

**Supported Vector Databases:**
- Milvus
- FAISS
- Pinecone
- MongoDB Atlas Vector Search

**Prereqs:**  
- All Platforms: [Python v3.9 - 3.11](https://www.python.org/about/gettingstarted/)
- To enable the OCR parsing capabilities, install [Tesseract v5.3.3](https://tesseract-ocr.github.io/tessdoc/Installation.html) and [Poppler v23.10.0](https://poppler.freedesktop.org/) native packages.  
     
**Optional:**
- [Docker](https://docs.docker.com/get-docker/) 

**Known issues:**
- A segmentation fault can occur when parsing if the native package for mongo-c-driver is 1.25 or above.  To address this issue, install the latest version of llmware or downgrade mongo-c-driver to v1.24.4.

<details>
  <summary><b>🚧 Change Log</b></summary>

- **17 Dec 2023: llmware v0.1.12**
  - dragon-deci-7b added to catalog - RAG-finetuned model on high-performance new 7B model base from Deci
  - New GGUFGenerativeModel class for easy integration of GGUF Models
  - Adding prebuilt llama_cpp / ctransformer shared libraries for Mac M1, Mac x86, Linux x86 and Windows
  - 3 DRAGON models packaged as Q4_K_M GGUF models for CPU laptop use (dragon-mistral-7b, dragon-llama-7b, dragon-yi-6b)
  - 4 leading open source chat models added to default catalog with Q4_K_M
  
- **8 Dec 2023: llmware v0.1.11**
  - New fast start examples for high volume Document Ingestion and Embeddings with Milvus.
  - New LLMWare 'Pop up' Inference Server model class and example script.
  - New Invoice Processing example for RAG.
  - Improved Windows stack management to support parsing larger documents.
  - Enhancing debugging log output mode options for PDF and Office parsers.

- **30 Nov 2023: llmware v0.1.10**
  - Windows added as a supported operating system.
  - Further enhancements to native code for stack management. 
  - Minor defect fixes.

- **24 Nov 2023: llmware v0.1.9**
  - Markdown (.md) files are now parsed and treated as text files.
  - PDF and Office parser stack optimizations which should avoid the need to set ulimit -s.
  - New llmware_models_fast_start.py example that allows discovery and selection of all llmware HuggingFace models.
  - Native dependencies (shared libraries and dependencies) now included in repo to faciliate local development.
  - Updates to the Status class to support PDF and Office document parsing status updates.
  - Minor defect fixes including image block handling in library exports.

- **17 Nov 2023: llmware v0.1.8**
  - Enhanced generation performance by allowing each model to specific the trailing space parameter.
  - Improved handling for eos_token_id for llama2 and mistral.
  - Improved support for Hugging Face dynamic loading
  - New examples with the new llmware DRAGON models.
    
- **14 Nov 2023: llmware v0.1.7**
  - Moved to Python Wheel package format for PyPi distribution to provide seamless installation of native dependencies on all supported platforms.  
  - ModelCatalog enhancements:
    - OpenAI update to include newly announced ‘turbo’ 4 and 3.5 models.
    - Cohere embedding v3 update to include new Cohere embedding models.
    - BLING models as out-of-the-box registered options in the catalog. They can be instantiated like any other model, even without the “hf=True” flag.
    - Ability to register new model names, within existing model classes, with the register method in ModelCatalog.
  - Prompt enhancements:
    - “evidence_metadata” added to prompt_main output dictionaries allowing prompt_main responses to be plug into the evidence and fact-checking steps without modification.
    - API key can now be passed directly in a prompt.load_model(model_name, api_key = “[my-api-key]”)
  - LLMWareInference Server - Initial delivery:
    - New Class for LLMWareModel which is a wrapper on a custom HF-style API-based model.    
    - LLMWareInferenceServer is a new class that can be instantiated on a remote (GPU) server to create a testing API-server that can be integrated into any Prompt workflow.    
 
- **03 Nov 2023: llmware v0.1.6**
  - Updated packaging to require mongo-c-driver 1.24.4 to temporarily workaround segmentation fault with mongo-c-driver 1.25.
  - Updates in python code needed in anticipation of future Windows support.  

- **27 Oct 2023: llmware v0.1.5**
  - Four new example scripts focused on RAG workflows with small, fine-tuned instruct models that run on a laptop (`llmware` [BLING](https://huggingface.co/llmware) models).
  - Expanded options for setting temperature inside a prompt class.
  - Improvement in post processing of Hugging Face model generation.
  - Streamlined loading of Hugging Face generative models into prompts.
  - Initial delivery of a central status class: read/write of embedding status with a consistent interface for callers.
  - Enhanced in-memory dictionary search support for multi-key queries.
  - Removed trailing space in human-bot wrapping to improve generation quality in some fine-tuned models.
  - Minor defect fixes, updated test scripts, and version update for Werkzeug to address [dependency security alert](https://github.com/llmware-ai/llmware/security/dependabot/2).
- **20 Oct 2023: llmware v0.1.4**
  - GPU support for Hugging Face models.
  - Defect fixes and additional test scripts.
- **13 Oct 2023: llmware v0.1.3**
  - MongoDB Atlas Vector Search support.
  - Support for authentication using a MongoDB connection string.
  - Document summarization methods.
  - Improvements in capturing the model context window automatically and passing changes in the expected output length.  
  - Dataset card and description with lookup by name.
  - Processing time added to model inference usage dictionary.
  - Additional test scripts, examples, and defect fixes.
- **06 Oct 2023: llmware v0.1.1**
  - Added test scripts to the github repository for regression testing.
  - Minor defect fixes and version update of Pillow to address [dependency security alert](https://github.com/llmware-ai/llmware/security/dependabot/1).
- **02 Oct 2023: llmware v0.1.0**  🔥 Initial release of llmware to open source!! 🔥


</details>

