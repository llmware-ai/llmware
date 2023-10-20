# llmware
![Static Badge](https://img.shields.io/badge/python-3.9_%7C_3.10-blue?color=blue)
![PyPI - Version](https://img.shields.io/pypi/v/llmware?color=blue)

`llmware` is a unified, open, extensible framework for LLM-based application patterns including Retrieval Augmented Generation (RAG). This project provides a comprehensive set of tools that anyone can use – from beginner to the most sophisticated AI developer – to rapidly build industrial-grade enterprise LLM-based applications. 

With `llmware`, our goal is to contribute to and help catalize an open community around the new combination of open, extensible technologies being assembled to accomplish fact-based generative workflows.

## 🎯  Key features
`llmware` is an integrated framework comprised of four major components:

<details>
<summary><b><u>Retrieval</u>: Assemble fact-sets </b></summary>

- A comprehensive set of querying methods: semantic, text, and hybrid retrieval with integrated metadata.
- Ranking and filtering strategies to enable semantic search and rapid retrieval of information.
- Web scrapers, Wikipedia integration, and Yahoo Finance API integration as additional tools to assemble fact-sets for generation.
</details>


<details>    
<summary><b><u>Prompt</u>: Tools for sophisticated generative scenarios </b></summary>

- **Connect Models:** Open interface designed to support AI21, Ai Bloks READ-GPT, Anthropic, Cohere, HuggingFace Generative models, OpenAI.
- **Prepare Sources:** Tools for packaging and tracking a wide range of materials into model context window sizes. Sources include files, websites, audio, AWS Transcribe transcripts, Wikipedia and Yahoo Finance.  
- **Prompt Catalog:** Dynamically configurable prompts to experiment with multiple models without any change in the code.
- **Post Processing:** a full set of metadata and tools for evidence verification, classification of a response, and fact-checking.
- **Human in the Loop:** Ability to enable user ratings, feedback, and corrections of AI responses.
- **Auditability:** A flexible state mechanism to capture, track, analyze and audit the LLM prompt lifecycle  
</details>

<details>
<summary><b><u>Vector Embeddings</u>:  swappable embedding models and vector databases</b></summary>

- Custom trained sentence transformer embedding models and support for embedding models from Cohere, Google, HuggingFace Embedding models, and OpenAI.
- Mix-and-match among multiple options to find the right solution for any particular application.
- Out-of-the-box support for 3 vector databases - Milvus, FAISS, and Pinecone.
</details>
  
<details>
<summary><b><u>Parsing and Text Chunking</u>: Prepare your data for RAG</b></summary>
  
* Parsers for:  PDF, PowerPoint, Word, Excel, HTML, Text, WAV, AWS Transcribe transcripts.
* A complete set of text-chunking tools to separate information and associated metadata to a consistent block format.
</details>

#### 📚 Explore [additional llmware capabilities](https://github.com/llmware-ai/llmware/blob/main/examples/README.md) and 🎬 Check out these videos on how to quickly get started with RAG:
- [Fast Start to RAG with LLMWare Open Source Library](https://www.youtube.com/watch?v=0naqpH93eEU)
- [Use Retrieval Augmented Generation (RAG) without a Database](https://www.youtube.com/watch?v=tAGz6yR14lw)

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

### 3. 🔥 Start coding - Quick Start For RAG 🔥 
```python
# This example demonstrates Retrieval Augmented Retrieval (RAG):
import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.prompts import Prompt
from llmware.setup import Setup

# Update this value with your own API Key, either by setting the env var or editing it directly here:
openai_api_key = os.environ["OPENAI_API_KEY"]

# A self-contained end-to-end example of RAG
def end_to_end_rag():
    
    # Create a library called "Agreements", and load it with llmware sample files
    print (f"\n > Creating library 'Agreements'...")
    library = Library().create_new_library("Agreements")
    sample_files_path = Setup().load_sample_files()
    library.add_files(os.path.join(sample_files_path,"Agreements"))

    # Create vector embeddings for the library using the "industry-bert-contracts model and store them in Milvus
    print (f"\n > Generating vector embeddings using embedding model: 'industry-bert-contracts'...")
    library.install_new_embedding(embedding_model_name="industry-bert-contracts", vector_db="milvus")

    # Perform a semantic search against our library.  This will gather evidence to be used in the LLM prompt
    print (f"\n > Performing a semantic query...")
    os.environ["TOKENIZERS_PARALLELISM"] = "false" # Avoid a HuggingFace tokenizer warning
    query_results = Query(library).semantic_query("Termination", result_count=20)

    # Create a new prompter using the GPT-4 and add the query_results captured above
    prompt_text = "Summarize the termination provisions"
    print (f"\n > Prompting LLM with '{prompt_text}'")
    prompter = Prompt().load_model("gpt-4", api_key=openai_api_key)
    sources = prompter.add_source_query_results(query_results)

    # Prompt the LLM with the sources and a query string
    responses = prompter.prompt_with_source(prompt_text, prompt_name="summarize_with_bullets")
    for response in responses:
        print ("\n > LLM response\n" + response["llm_response"])
    
    # Finally, generate a CSV report that can be shared
    print (f"\n > Generating CSV report...")
    report_data = prompter.send_to_human_for_review()
    print ("File: " + report_data["report_fp"] + "\n")

end_to_end_rag()
```
#### Response from end-to-end RAG example

```
> python examples/rag.py

 > Creating library 'Agreements'...

 > Generating vector embeddings using embedding model: 'industry-bert-contracts'...

 > Performing a semantic query...

 > Prompting LLM with 'Summarize the termination provisions'

 > LLM response
- Employment period ends on the first occurrence of either the 6th anniversary of the effective date or a company sale.
- Early termination possible as outlined in sections 3.1 through 3.4.
- Employer can terminate executive's employment under section 3.1 anytime without cause, with at least 30 days' prior written notice.
- If notice is given, the executive is allowed to seek other employment during the notice period.

 > Generating CSV report...
File: /Users/llmware/llmware_data/prompt_history/interaction_report_Fri Sep 29 12:07:42 2023.csv
```
#### 📚 See additional [llmware examples](https://github.com/llmware-ai/llmware/blob/main/examples/README.md) for more code samples and ideas.


### 4. Accessing LLMs and setting-up API keys & secrets
To get started with a proprietary model, you need to provide your own API Keys.  If you don't yet have one, more information can be found at: [AI21](https://docs.ai21.com/docs/quickstart), [Ai Bloks](https://www.aibloks.com/contact-us), [Anthropic](https://docs.anthropic.com/claude/reference/getting-started-with-the-api),  [Cohere](https://cohere.com/), [Google](https://cloud.google.com/vertex-ai/docs/generative-ai/start/quickstarts/api-quickstart), [OpenAI](https://help.openai.com/en/collections/3675940-getting-started-with-openai-api).

API keys and secrets for models, aws, and pinecone can be set-up for use in environment variables or managed however you prefer. 

You can also access the `llmware` public model repository which includes out-of-the-box custom trained sentence transformer embedding models fine-tuned for the following industries: Insurance, Contracts, Asset Management, SEC. These domain specific models along with llmware's generative BLING model series ("Best Little Instruction-following No-GPU-required") are available at [llmware on Huggingface](https://huggingface.co/llmware). Explore using the model repository and the `llmware` Huggingface integration in [llmware examples](https://github.com/llmware-ai/llmware/blob/main/examples/README.md).


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

The llmware repo can be pulled locally to get access to all the examples, or to work directly with the llmware code

### Pull the repo locally

```bash
git clone git@github.com:llmware-ai/llmware.git
```
or download/extract a [zip of the llmware repository](https://github.com/llmware-ai/llmware/archive/refs/heads/main.zip)

### Other options for running llmware

<details>
<summary><b>Run llmware in a container </b></summary>
  
  ```bash
TODO insert command for pulling the container here
```
</details>

<details>
<summary><b>Run llmware natively </b></summary>

At the top level of the llmware repository run the following command:

```bash
pip install .
```

</details>

## ✨  Getting help or sharing your ideas with the community
Questions and discussions are welcome in our [github discussions](https://github.com/llmware-ai/llmware/discussions).

Interested in contributing to llmware? We welcome involvement from the community to extend and enhance the framework!  
- 💡 What's your favorite model or is there one you'd like to check out in your experiments? 
- 💡 Have you had success with a different embedding databases?
- 💡 Is there a prompt that shines in a RAG workflow?

Information on ways to participate can be found in our [Contributors Guide](https://github.com/llmware-ai/llmware/blob/main/CONTRIBUTING.md#contributing-to-llmware).  As with all aspects of this project, contributing is governed by our [Code of Conduct](https://github.com/llmware-ai/llmware/blob/main/CODE_OF_CONDUCT.md).

## 📣  Release notes and Change Log

**Supported OS's:**  
- MacOS
- Linux
- (Windows is a roadmap item)

**Supported Vector Databases:**
- Milvus
- FAISS
- Pinecone
- MongoDB Atlas Vector Search

**Prereqs:**  
- All Platforms: [python v3.9 - 3.10](https://www.python.org/about/gettingstarted/)
- Mac: [Homebrew](https://docs.brew.sh/Installation) is used to install the native dependencies
- Linux: 
  1. The pip package attempts to install the native dependencies. If it is run without root permission or a package manager other than Apt is used, you will need to manually install the following native packages: ```apt install -y libxml2 libpng-dev libmongoc-dev libzip4 tesseract-ocr poppler-utils```
  2. The llmware parsers optimize for speed by using large stack frames. If you receive a "Segmentation Fault" during a parsing operation, update the system's 'stack size' resource limit: ```ulimit -s 32768000```
  

**Optional:**
- [Docker](https://docs.docker.com/get-docker/) 

<details>
  <summary><b>Change Log</b></summary>

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

