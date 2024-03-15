---
layout: default
title: Home | llmware
nav_order: 1
description: llmware is an integrated framework with over 50+ models in Hugging Face for quickly developing LLM-based applications including Retrieval Augmented Generation (RAG) and Multi-Step Orchestration of Agent Workflows.
permalink: /
---
# Welcome to fasttrees

`llmware` is an integrated framework with over 50+ models in Hugging Face for quickly developing LLM-based applications including Retrieval Augmented Generation (RAG) and Multi-Step Orchestration of Agent Workflows.
{: .fs-6 .fw-300 }

[Install llmware](#install-llmware){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[View llmware on GitHub](https://github.com/llmware-ai/llmware/tree/main){: .btn .fs-5 .mb-4 .mb-md-0 }
[Open an Issue on GitHub](https://github.com/llmware-ai/llmware/issues){: .btn .fs-5 .mb-4 .mb-md-0 }


# Install llmware 

You can easily install `llmware` via `pip`.

```bash
pip install llmware 
```

# When to use llmware 

llmware and it's models focus on making it easy to integrate open source small specialized models and connecting enterprise knowledge safely and securely.


# Usage

```python
from llmware.models import ModelCatalog

# get all SLIM models, delivered as small, fast quantized tools
ModelCatalog().get_llm_toolkit()

# see the model in action with test script included
ModelCatalog().tool_test_run("slim-sentiment-tool") 
```

# About the project

`llmware` is &copy; 2023-{{ "now" | date: "%Y" }} [AI Bloks](https://www.aibloks.com/home).

## License

`llmware` is diributed by an [Apache-2.0 license](https://github.com/llmware-ai/llmware/blob/main/LICENSE).
