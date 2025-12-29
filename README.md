# llmware

![Static Badge](https://img.shields.io/badge/python-3.9_%7C_3.10%7C_3.11%7C_3.12%7C_3.13-blue?color=blue)
![PyPI - Version](https://img.shields.io/pypi/v/llmware?color=blue)
![PyPI - Downloads](https://img.shields.io/pypi/dm/llmware?color=blue)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![OS](https://img.shields.io/badge/OS-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)
[![Discord](https://discord-live-members-count-badge.vercel.app/api/discord-members?guildId=1179245642770559067&label=discord%20members&color=5865F2)](https://discord.gg/bphreFK4NJ)
[![Documentation](https://github.com/llmware-ai/llmware/actions/workflows/pages.yml/badge.svg)](https://github.com/llmware-ai/llmware/actions/workflows/pages.yml)

**Unified framework for building enterprise RAG pipelines and Agent workflows using small, specialized models that run privately on your infrastructure.**

---

## 🚀 Start Here

**New to llmware?** Choose your path:

| I want to... | Start with... | Time needed |
|--------------|---------------|-------------|
| **Try RAG on my laptop** | [Quick Start RAG](#-quick-start-rag) | 5 minutes |
| **Build function-calling agents** | [Agent Fast Start](fast_start/agents/) | 10 minutes |
| **Learn the concepts** | [Core Concepts](#-core-concepts) | 15 minutes |
| **See real examples** | [Examples Gallery](#-examples--tutorials) | Browse |

**Quick Links:**
- [📺 YouTube Tutorials](https://www.youtube.com/@llmware) - Video guides and walkthroughs
- [💬 Discord Community](https://discord.gg/MhZn5Nc39h) - Get help and connect
- [🤗 Browse Models](https://www.huggingface.co/llmware) - 50+ specialized models
- [📖 Full Documentation](docs/) - Complete guides and API reference

---

## ⚡ Quick Start RAG

Get a complete RAG pipeline running locally in under 5 minutes:

**Step 1: Install**
```bash
pip install llmware
```

**Step 2: Run Your First RAG Query**
```python
from llmware.prompts import Prompt
from llmware.setup import Setup

# Download sample files and load a CPU-optimized model
sample_files = Setup().load_sample_files()
prompter = Prompt().load_model("bling-phi-3-gguf")

# Add a document and ask a question
source = prompter.add_source_document(sample_files, "Agreements/sample_contract.pdf")
response = prompter.prompt_with_source("What is the termination notice period?")

print(response[0]['llm_response'])
```

**Step 3: Try Different Setups**
```python
from llmware.configs import LLMWareConfig

# Fast start (no database setup required)
LLMWareConfig().set_active_db("sqlite")
LLMWareConfig().set_vector_db("chromadb")

# Production scale (requires Docker)
# See docs/deployment.md for setup instructions
```

**What just happened?** You parsed a PDF, created embeddings, retrieved relevant context, and generated an answer using a 3B parameter model running entirely on your CPU.

---

## 💡 Why llmware?

**Enterprise-Ready RAG & Agents:** llmware provides integrated components for the complete lifecycle of connecting knowledge sources to AI models, plus 50+ specialized models fine-tuned for enterprise tasks.

**Key Benefits:**
- **🔒 Private & Secure:** Run models locally or in your private cloud
- **💻 Laptop-Friendly:** Most examples work without GPU requirements  
- **🏢 Enterprise-Focused:** Built-in support for contracts, finance, OCR, and complex documents
- **🔧 Flexible Architecture:** Mix and match databases, models, and deployment options
- **📊 Production-Grade:** Scales from laptop prototypes to enterprise deployments

**What makes it different:** Unlike general-purpose frameworks, llmware combines purpose-built RAG infrastructure with specialized small models (1-9B parameters) that deliver enterprise-grade accuracy while running efficiently on standard hardware.

---

## 🧠 Core Concepts

Understanding these four concepts will help you work effectively with llmware:

**🗃️ Libraries:** Your knowledge containers that handle document parsing, text chunking, and embedding storage. Think of them as smart databases that understand your documents.

```python
from llmware.library import Library

lib = Library().create_new_library("contracts")
lib.add_files("/path/to/contracts/")  # Parses PDFs, Word, Excel, etc.
lib.install_new_embedding(embedding_model_name="mini-lm-sbert", vector_db="chromadb")
```

**🔍 Queries:** Powerful retrieval that combines text search, semantic similarity, and metadata filtering.

```python
from llmware.retrieval import Query

q = Query(lib)
results = q.semantic_query("termination clauses", result_count=5)
```

**💬 Prompts:** RAG orchestration that automatically assembles context from your queries and sends it to models.

```python
from llmware.prompts import Prompt

prompter = Prompt().load_model("bling-phi-3-gguf")
prompter.add_source_query_results(results)
response = prompter.prompt_with_source("Summarize the termination requirements")
```

**🤖 Agents:** Multi-step workflows using specialized SLIM models for tasks like extraction, sentiment analysis, and classification.

```python
from llmware.agents import LLMfx

agent = LLMfx()
agent.load_work("Tesla stock fell 8% after missing earnings...")
agent.load_tool("sentiment")
agent.load_tool("extract")
agent.sentiment()
agent.extract(params=["company", "stock_change"])
```

---

## 🎯 Key Features

<details>
<summary><b>📚 Universal Document Processing</b></summary>

Parse 15+ file formats with automatic text chunking, table extraction, and metadata management.

```python
from llmware.library import Library

# Handles PDF, DOCX, XLSX, PPTX, TXT, CSV, MD, JSON, HTML, images, audio
lib = Library().create_new_library("knowledge_base")
lib.add_files("/mixed_documents/")  # Automatic format detection and parsing

# Rich metadata and content extraction
lib_card = Library().get_library_card("knowledge_base")
print(f"Processed {lib_card['documents']} documents, {lib_card['text_chunks']} chunks")
```
</details>

<details>
<summary><b>🔍 Advanced Retrieval</b></summary>

Combine text search, semantic similarity, and hybrid approaches with sophisticated filtering.

```python
from llmware.retrieval import Query

q = Query(lib)

# Multiple query types
text_results = q.text_query("confidentiality", result_count=10)
semantic_results = q.semantic_query("data protection clauses", result_count=5)
filtered_results = q.text_query_with_document_filter(
    "termination", 
    {"file_name": "employment_contract.pdf"}
)
```
</details>

<details>
<summary><b>🤖 Specialized Model Families</b></summary>

Access 50+ models optimized for enterprise tasks, from 1B CPU-friendly models to 9B production-grade models.

- **SLIM Models:** Function-calling tools (sentiment, extract, topics, boolean, text2sql)
- **BLING Models:** 1-3B RAG-optimized models for laptops  
- **DRAGON Models:** 6-9B production-grade RAG models
- **Industry BERT:** Domain-specific embeddings (legal, finance, insurance)

```python
from llmware.models import ModelCatalog

# Get all SLIM function-calling models
ModelCatalog().get_llm_toolkit()

# Test a specific tool
ModelCatalog().tool_test_run("slim-sentiment-tool")
```
</details>

<details>
<summary><b>💾 Flexible Data Architecture</b></summary>

Mix and match text databases and vector stores based on your needs.

```python
from llmware.configs import LLMWareConfig

# Development setup (no servers required)
LLMWareConfig().set_active_db("sqlite")
LLMWareConfig().set_vector_db("chromadb")

# Production setup
LLMWareConfig().set_active_db("postgres") 
LLMWareConfig().set_vector_db("milvus")
```

**Supported Options:**
- **Text DBs:** SQLite, MongoDB, Postgres
- **Vector DBs:** ChromaDB, Milvus, PGVector, Qdrant, Redis, FAISS, LanceDB, Pinecone
</details>

---

## 📚 Examples & Tutorials

**🎬 Video Tutorials** (5-10 minutes each)
- [RAG with BLING on your laptop](https://www.youtube.com/watch?v=JjgqOZ2v5oU)
- [Getting Started with SLIM Agents](https://youtu.be/aWZFrTDmMPc)
- [Document Summarization](https://youtu.be/Ps3W-P9A1m8)

**📋 Popular Examples**

| Use Case | Code | Description |
|----------|------|-------------|
| **Contract Analysis** | [contract_analysis.py](examples/Use_Cases/contract_analysis_on_laptop_with_bling_models.py) | Extract key terms from legal documents |
| **Financial Research** | [web_services_slim_fx.py](examples/Use_Cases/web_services_slim_fx.py) | Multi-model agents for financial analysis |
| **Document Q&A** | [bling_fast_start.py](examples/Models/bling_fast_start.py) | Question-answering on business documents |
| **Voice Analysis** | [parsing_great_speeches.py](examples/Use_Cases/parsing_great_speeches.py) | Transcribe and analyze audio files |

**📂 Browse by Category**
- [Getting Started Examples](examples/Getting_Started/) - Basic workflows and setup
- [SLIM Agents](examples/SLIM-Agents/) - Function calling and multi-model workflows  
- [RAG Workflows](examples/Prompts/) - Advanced retrieval and prompting
- [Model Examples](examples/Models/) - Working with different model types

**🚀 Fast Start Series**
Complete tutorial series covering RAG basics to advanced agent workflows: [fast_start/](fast_start/)

---

## 🗂️ Data Store Setup

**Quick Start (No Installation)**
```bash
pip install llmware
# Uses SQLite + ChromaDB automatically
```

**Production Scale**
```bash
# Download Docker Compose for MongoDB + Milvus
curl -o docker-compose.yaml https://raw.githubusercontent.com/llmware-ai/llmware/main/docker-compose.yaml
docker compose up -d
```

**Other Options:** See [docs/deployment.md](docs/deployment.md) for Postgres, Redis, Qdrant, and other database configurations.

---

## 🛠️ Advanced Topics

For production deployments, optimization, and advanced use cases:

- **📊 [Model Benchmarks & Performance](docs/benchmarks.md)** - Accuracy comparisons and optimization guides
- **🚀 [Deployment Guide](docs/deployment.md)** - Production setup, Docker, and scaling
- **🔧 [API Reference](docs/api/)** - Complete technical documentation  
- **📄 [Release Notes](CHANGELOG.md)** - Version history and migration guides
- **📋 [White Papers](docs/whitepapers/)** - Technical deep dives and research

---

## 🤝 Community & Support

**Get Help:**
- [💬 Discord](https://discord.gg/MhZn5Nc39h) - Real-time community support
- [💡 GitHub Discussions](https://github.com/llmware-ai/llmware/discussions) - Q&A and feature requests
- [📺 YouTube](https://www.youtube.com/@llmware) - Tutorials and demos

**Contribute:**
- [🤝 Contributing Guide](repo_docs/CONTRIBUTING.md) - How to contribute code, docs, or examples
- [📜 Code of Conduct](repo_docs/CODE_OF_CONDUCT.md) - Community guidelines

**Latest Release:** v0.4.0 - Enhanced GGUF/ONNX support, Windows ARM64, streamlined dependencies. [See full changelog](CHANGELOG.md)

---

## 🚀 What's Next?

1. **Try the Quick Start** above to get your first RAG pipeline running
2. **Explore Examples** in the [examples/](examples/) directory  
3. **Join the Community** on [Discord](https://discord.gg/MhZn5Nc39h)
4. **Check out Advanced Topics** in [docs/](docs/) when you're ready to scale

**Ready to build?** llmware makes enterprise AI accessible, private, and powerful. Start with a simple example and scale to production when you're ready.

---

<p align="center">
  <strong>Built with intention by the llmware team</strong><br>
  <a href="https://discord.gg/MhZn5Nc39h">Discord</a> •
  <a href="https://www.youtube.com/@llmware">YouTube</a> •
  <a href="https://www.huggingface.co/llmware">Hugging Face</a> •
  <a href="https://github.com/llmware-ai/llmware">GitHub</a>
</p>
