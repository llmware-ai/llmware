
""" Global Default Configs for Models, Finetune Wrappers and Prompt Instructions Catalog.  These configs generally
 do not need to be accessed directly, but can be viewed and updated through ModelCatalog and PromptCatalog classes."""

global_model_repo_catalog_list = [

    # embedding models
    {"model_name": 'mini-lm-sbert', "display_name": "Sentence_Transformers (MPNet-Base)", "model_family": "LLMWareSemanticModel",
     "model_category": "embedding", "model_location": "llmware_repo", "embedding_dims": 384, "context_window":512,
     "link": "","custom_model_files": [], "custom_model_repo": ""},

    {"model_name": 'industry-bert-insurance', "display_name": "Insurance_LLMWare_Accelerator", "model_family": "LLMWareSemanticModel",
     "model_category": "embedding", "model_location": "llmware_repo", "embedding_dims": 768, "context_window":512,
     "link": "https://huggingface.co/llmware/industry-bert-insurance-v0.1", "custom_model_files":[],
     "custom_model_repo": ""},

    {"model_name": 'industry-bert-contracts', "display_name": "Contracts_LLMWare_Accelerator", "model_family": "LLMWareSemanticModel",
     "model_category": "embedding", "model_location": "llmware_repo", "embedding_dims": 768, "context_window":512,
     "link": "https://huggingface.co/llmware/industry-bert-contracts-v0.1", "custom_model_files":[],
     "custom_model_repo": ""},

    {"model_name": 'industry-bert-asset-management', "display_name": "Asset_Management_LLMWare_Accelerator",
     "model_family": "LLMWareSemanticModel", "model_category": "embedding", "model_location": "llmware_repo",
     "embedding_dims": 768, "context_window":512,
     "link": "https://huggingface.co/llmware/industry-bert-asset-management-v0.1", "custom_model_files":[],
     "custom_model_repo": ""},

    {"model_name": 'industry-bert-sec', "display_name": "SEC_LLMWare_Accelerator", "model_family": "LLMWareSemanticModel",
     "model_category": "embedding", "model_location": "llmware_repo", "embedding_dims": 768, "context_window":512,
     "link": "https://huggingface.co/llmware/industry-bert-sec-v0.1", "custom_model_files": [], "custom_model_repo": ""},

    # add open ai embeddings
    {"model_name": 'text-embedding-ada-002', "display_name": "OpenAI-Embedding", "model_family": "OpenAIEmbeddingModel",
     "model_category": "embedding", "model_location": "api", "context_window": 2048, "embedding_dims": 1536},

    # add cohere embeddings
    {"model_name": 'medium', "display_name": "Cohere-Medium-Embedding", "model_family": "CohereEmbeddingModel",
     "model_category": "embedding", "model_location": "api", "context_window": 2048, "embedding_dims": 4096},

    {"model_name": 'xlarge', "display_name": "Cohere-XLarge-Embedding", "model_family": "CohereEmbeddingModel",
     "model_category": "embedding", "model_location": "api", "context_window": 2048, "embedding_dims": 4096},

    # insert new cohere embedding model - v3 - announced first week of November 2023
    {"model_name": 'embed-english-v3.0', "display_name": "Cohere-English-v3", "model_family": "CohereEmbeddingModel",
     "model_category": "embedding", "model_location": "api",  "context_window": 2048, "embedding_dims": 1024},

    {"model_name": 'embed-multilingual-v3.0', "display_name": "Cohere-Multi-Lingual-v3", "model_family": "CohereEmbeddingModel",
     "model_category": "embedding", "model_location": "api", "context_window": 2048, "embedding_dims": 1024},

    {"model_name": 'embed-english-light-v3.0', "display_name": "Cohere-English-v3", "model_family": "CohereEmbeddingModel",
     "model_category": "embedding", "model_location": "api", "context_window": 2048, "embedding_dims": 384},

    {"model_name": 'embed-multilingual-light-v3.0', "display_name": "Cohere-English-v3",
     "model_family": "CohereEmbeddingModel", "model_category": "embedding", "model_location": "api",
     "context_window": 2048, "embedding_dims": 384},

    {"model_name": 'embed-english-v2.0', "display_name": "Cohere-English-v3",
     "model_family": "CohereEmbeddingModel", "model_category": "embedding", "model_location": "api",
     "context_window": 2048, "embedding_dims": 4096},

    {"model_name": 'embed-english-light-v2.0', "display_name": "Cohere-English-v3",
     "model_family": "CohereEmbeddingModel", "model_category": "embedding", "model_location": "api",
     "context_window": 2048, "embedding_dims": 1024},

    {"model_name": 'embed-multilingual-v2.0', "display_name": "Cohere-English-v3",
     "model_family": "CohereEmbeddingModel", "model_category": "embedding", "model_location": "api",
     "context_window": 2048, "embedding_dims": 768},
    # end - new cohere embeddings

    # add google embeddings - textembedding-gecko@001
    {"model_name": 'textembedding-gecko@latest', "display_name": "Google-Embedding", "model_family": "GoogleEmbeddingModel",
     "model_category": "embedding","model_location": "api", "context_window": 4000, "embedding_dims": 768},

    # generative-api models
    {"model_name": 'claude-v1', "display_name": "Anthropic Claude-v1", "model_family": "ClaudeModel",
     "model_category": "generative-api", "model_location": "api",  "context_window": 8000},
    {"model_name": 'claude-instant-v1', "display_name": "Anthropic Claude-Instant-v1", "model_family": "ClaudeModel",
     "model_category": "generative-api","model_location": "api", "context_window": 8000},
    {"model_name": 'command-medium-nightly', "display_name": "Cohere Command Medium", "model_family": "CohereGenModel",
     "model_category": "generative-api","model_location": "api", "context_window": 2048},
    {"model_name": 'command-xlarge-nightly', "display_name": "Cohere Command XLarge", "model_family": "CohereGenModel",
     "model_category": "generative-api","model_location": "api", "context_window": 2048},

    {"model_name": 'summarize-xlarge', "display_name": "Cohere Summarize Xlarge", "model_family": "CohereGenModel",
     "model_category":"generative-api","model_location": "api", "context_window": 2048},
    {"model_name": 'summarize-medium', "display_name": "Cohere Summarize Medium", "model_family": "CohereGenModel",
     "model_category":"generative-api","model_location": "api", "context_window": 2048},
    {"model_name": 'j2-jumbo-instruct', "display_name": "Jurassic-2-Jumbo-Instruct", "model_family": "JurassicModel",
     "model_category":"generative-api", "model_location": "api", "context_window": 2048},
    {"model_name": 'j2-grande-instruct', "display_name": "Jurassic-2-Grande-Instruct", "model_family": "JurassicModel",
     "model_category":"generative-api","model_location": "api", "context_window": 2048},
    {"model_name": 'text-bison@001', "display_name": "Google Palm", "model_family": "GoogleGenModel",
     "model_category": "generative-api","model_location": "api", "context_window": 8192},
    {"model_name": 'chat-bison@001', "display_name": "Google Chat", "model_family": "GoogleGenModel",
     "model_category": "generative-api","model_location": "api", "context_window": 8192},
    {"model_name": 'text-davinci-003', "display_name": "GPT3-Davinci", "model_family": "OpenAIGenModel",
     "model_category": "generative-api","model_location": "api", "context_window": 4096},
    {"model_name": 'text-curie-001', "display_name": "GPT3-Curie", "model_family": "OpenAIGenModel",
     "model_category": "generative-api","model_location": "api", "context_window": 2048},
    {"model_name": 'text-babbage-001', "display_name": "GPT3-Babbage", "model_family": "OpenAIGenModel",
     "model_category": "generative-api","model_location": "api", "context_window": 2048},
    {"model_name": 'text-ada-001', "display_name": "GPT3-Ada", "model_family": "OpenAIGenModel",
     "model_category": "generative-api","model_location": "api", "context_window": 2048},
    {"model_name": "gpt-3.5-turbo", "display_name": "ChatGPT", "model_family": "OpenAIGenModel",
     "model_category": "generative-api","model_location": "api", "context_window": 4000},

    # gpt-4 add
    {"model_name": "gpt-4", "display_name": "GPT-4", "model_family": "OpenAIGenModel",
     "model_category": "generative-api", "model_location": "api", "context_window": 8000},

    # gpt-3.5-turbo-instruct
    {"model_name": "gpt-3.5-turbo-instruct", "display_name": "GPT-3.5-Instruct", "model_family": "OpenAIGenModel",
     "model_category": "generative-api", "model_location": "api", "context_window": 4000},

    # new gpt-4 models announced in November 2023
    {"model_name": "gpt-4-1106-preview", "display_name": "GPT-4-Turbo", "model_family": "OpenAIGenModel",
     "model_category": "generative-api", "model_location": "api", "context_window": 128000},

    {"model_name": "gpt-3.5-turbo-1106", "display_name": "GPT-3.5-Turbo", "model_family": "OpenAIGenModel",
     "model_category": "generative-api", "model_location": "api", "context_window": 16385},
    # end - gpt-4 model update

    # generative AIB models - aib-read-gpt - "main model"
    {"model_name": "aib-read-gpt", "display_name": "AIB-READ-GPT", "model_family": "AIBReadGPTModel",
     "model_category": "generative-api", "model_location": "api", "context_window": 2048},

    # base supporting models and components
    {"model_name": "bert", "display_name": "Bert", "model_family": "BaseModel", "model_category": "base",
     "model_location": "llmware_repo"},
    {"model_name": "roberta", "display_name": "Roberta", "model_family": "BaseModel", "model_category": "base",
     "model_location": "llmware_repo"},
    {"model_name": "gpt2", "display_name": "GPT-2", "model_family": "BaseModel", "model_category": "base",
     "model_location": "llmware_repo"},

    # add api-based llmware custom model
    {"model_name": "llmware-inference-server", "display_name": "LLMWare-GPT", "model_family": "LLMWareModel",
     "model_category": "generative-api", "model_location": "api", "context_window": 2048},

    # core llmware bling open source models available in catalog directly
    {"model_name": "llmware/bling-1.4b-0.1", "display_name": "Bling-Pythia-1.4B", "model_family": "HFGenerativeModel",
     "model_category": "generative_local", "model_location": "hf_repo", "context_window": 2048,
     "instruction_following": False, "prompt_wrapper": "human_bot", "temperature": 0.3, "trailing_space":"",
     "link": "https://huggingface.co/llmware/bling-1.4b-0.1",
     "custom_model_files": [], "custom_model_repo": ""},

    {"model_name": "llmware/bling-1b-0.1", "display_name": "Bling-Pythia-1.0B", "model_family": "HFGenerativeModel",
     "model_category": "generative_local", "model_location": "hf_repo", "context_window": 2048,
     "instruction_following": False, "prompt_wrapper": "human_bot", "temperature": 0.3, "trailing_space": "",
     "link": "https://huggingface.co/llmware/bling-1b-0.1",
     "custom_model_files": [], "custom_model_repo": ""},

    {"model_name": "llmware/bling-falcon-1b-0.1", "display_name": "Bling-Falcon-1.3B", "model_family": "HFGenerativeModel",
     "model_category": "generative_local", "model_location": "hf_repo", "context_window": 2048,
     "instruction_following": False, "prompt_wrapper": "human_bot", "temperature": 0.3, "trailing_space": "",
     "link": "https://huggingface.co/llmware/bling-falcon-1b-0.1",
     "custom_model_files": [], "custom_model_repo": ""
     },

    {"model_name": "llmware/bling-sheared-llama-1.3b-0.1", "display_name": "Bling-Sheared-LLama-1.3B",
     "model_family": "HFGenerativeModel", "model_category": "generative_local", "model_location": "hf_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": "", "link": "https://huggingface.co/llmware/bling-sheared-llama-1.3b-0.1",
     "custom_model_files": [], "custom_model_repo": ""
     },

    {"model_name": "llmware/bling-red-pajamas-3b-0.1", "display_name": "Bling-Pythia-1.4B",
     "model_family": "HFGenerativeModel", "model_category": "generative_local", "model_location": "hf_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": "", "link": "https://huggingface.co/llmware/bling-red-pajamas-3b-0.1",
     "custom_model_files": [], "custom_model_repo": ""},

    {"model_name": "llmware/bling-sheared-llama-2.7b-0.1", "display_name": "Bling-Sheared-Llama-2.7B",
     "model_family": "HFGenerativeModel", "model_category": "generative_local", "model_location": "hf_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": "", "link": "https://huggingface.co/llmware/bling-sheared-llama-2.7b-0.1",
     "custom_model_files": [], "custom_model_repo": ""},

    {"model_name": "llmware/bling-stable-lm-3b-4e1t-v0", "display_name": "Bling-Stable-LM-3B",
     "model_family": "HFGenerativeModel", "model_category": "generative_local", "model_location": "hf_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": "", "link": "https://huggingface.co/llmware/bling-stable-lm-3b-4e1t-v0",
     "custom_model_files": [], "custom_model_repo": ""},

    {"model_name": "llmware/bling-cerebras-1.3b-0.1", "display_name": "Bling-Cerebras-1.3B",
     "model_family": "HFGenerativeModel", "model_category": "generative_local", "model_location": "hf_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": "", "link": "https://huggingface.co/llmware/bling-cerebras-1.3b-0.1",
     "custom_model_files": [], "custom_model_repo": ""},

    {"model_name": "llmware/bling-tiny-llama-v0", "display_name": "Bling-Tiny-Llama-v0",
     "model_family": "HFGenerativeModel", "model_category": "generative_local", "model_location": "hf_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": "", "link": "https://huggingface.co/llmware/bling-tiny-llama-v0",
     "custom_model_files": [], "custom_model_repo": ""},

    # create dragon models
    {"model_name": "llmware/dragon-yi-6b-v0", "display_name": "Dragon-Yi-6B",
     "model_family": "HFGenerativeModel", "model_category": "generative_local", "model_location": "hf_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": "\n", "link": "https://huggingface.co/llmware/dragon-yi-6b-v0",
     "custom_model_files": [], "custom_model_repo": ""},

    {"model_name": "llmware/dragon-stablelm-7b-v0", "display_name": "Dragon-StableLM-7B",
     "model_family": "HFGenerativeModel", "model_category": "generative_local", "model_location": "hf_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": "", "link": "https://huggingface.co/llmware/dragon-stablelm-7b-v0",
     "custom_model_files": [], "custom_model_repo": ""},

    {"model_name": "llmware/dragon-mistral-7b-v0", "display_name": "Dragon-Mistral-7B",
     "model_family": "HFGenerativeModel", "model_category": "generative_local", "model_location": "hf_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": "", "link": "https://huggingface.co/llmware/dragon-mistral-7b-v0",
     "custom_model_files": [], "custom_model_repo": ""},

    {"model_name": "llmware/dragon-red-pajama-7b-v0", "display_name": "Dragon-Red-Pajama-7B",
     "model_family": "HFGenerativeModel", "model_category": "generative_local", "model_location": "hf_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": "", "link": "https://huggingface.co/llmware/dragon-red-pajama-7b-v0",
     "custom_model_files": [], "custom_model_repo": ""},

    {"model_name": "llmware/dragon-deci-6b-v0", "display_name": "Dragon-Deci-6B",
     "model_family": "HFGenerativeModel", "model_category": "generative_local", "model_location": "hf_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": "", "link": "https://huggingface.co/llmware/dragon-deci-6b-v0",
     "custom_model_files": [], "custom_model_repo": ""},

    {"model_name": "llmware/dragon-falcon-7b-v0", "display_name": "Dragon-Falcon-7B",
     "model_family": "HFGenerativeModel", "model_category": "generative_local", "model_location": "hf_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": "", "link": "https://huggingface.co/llmware/dragon-falcon-7b-v0",
     "custom_model_files": [], "custom_model_repo": ""},

    {"model_name": "llmware/dragon-llama-7b-v0", "display_name": "Dragon-Llama-7B",
     "model_family": "HFGenerativeModel", "model_category": "generative_local", "model_location": "hf_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": "", "link": "https://huggingface.co/llmware/dragon-llama-7b-v0",
     "custom_model_files": [], "custom_model_repo": ""},

    {"model_name": "llmware/dragon-deci-7b-v0", "display_name": "Dragon-Deci-7B",
     "model_family": "HFGenerativeModel", "model_category": "generative_local", "model_location": "hf_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": "", "link": "https://huggingface.co/llmware/dragon-deci-7b-v0",
     "custom_model_files": [], "custom_model_repo": ""},

    # gguf models
    {"model_name": "llmware/dragon-mistral-7b-gguf", "display_name": "Dragon-Mistral-7B-GGUF",
     "model_family": "GGUFGenerativeModel", "model_category": "generative_local", "model_location": "llmware_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": "",
     "gguf_file": "dragon-mistral-7b-q4_k_m.gguf",
     "gguf_repo": "llmware/dragon-mistral-7b-v0",
     "link": "https://huggingface.co/llmware/dragon-mistral-7b-v0",
     "custom_model_files": ["dragon-mistral-7b-q4_k_m.gguf"], "custom_model_repo": "llmware/dragon-mistral-7b-v0"},

    {"model_name": "llmware/dragon-llama-7b-gguf", "display_name": "Dragon-Llama-7B-GGUF",
     "model_family": "GGUFGenerativeModel", "model_category": "generative_local", "model_location": "llmware_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": "",
     "gguf_file": "dragon-llama-7b-q4_k_m.gguf",
     "gguf_repo": "llmware/dragon-llama-7b-v0",
     "link": "https://huggingface.co/llmware/dragon-llama-7b-v0",
     "custom_model_files": ["dragon-llama-7b-q4_k_m.gguf"], "custom_model_repo": "llmware/dragon-llama-7b-v0"},

    {"model_name": "llmware/dragon-yi-6b-gguf", "display_name": "Dragon-Yi-6B-GGUF",
     "model_family": "GGUFGenerativeModel", "model_category": "generative_local", "model_location": "llmware_repo",
    "context_window": 2048, "instruction_following": False, "prompt_wrapper": "human_bot",
     "temperature": 0.3, "trailing_space": "\n",
     "gguf_file": "dragon-yi-6b-q4_k_m.gguf",
     "gguf_repo": "llmware/dragon-yi-6b-v0",
     "link": "https://huggingface.co/llmware/dragon-yi-6b-v0",
     "custom_model_files": ["dragon-yi-6b-q4_k_m.gguf"], "custom_model_repo": "llmware/dragon-yi-6b-v0"},

    # selected top HF open source chat models - gguf
    {"model_name": "TheBloke/Llama-2-7B-Chat-GGUF", "display_name": "Llama-2-7B-Chat-GGUF",
     "model_family": "GGUFGenerativeModel", "model_category": "generative_local", "model_location": "llmware_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "<INST>",
     "temperature": 0.3, "trailing_space": "",
     "gguf_file": "llama-2-7b-chat.Q4_K_M.gguf",
     "gguf_repo": "llmware/bonchon",
     "link": "https://huggingface.co/llmware/bonchon",
     "custom_model_files": ["llama-2-7b-chat.Q4_K_M.gguf"], "custom_model_repo": "llmware/bonchon"},

    {"model_name": "TheBloke/OpenHermes-2.5-Mistral-7B-GGUF", "display_name": "OpenHermes-Mistral-7B-GGUF",
     "model_family": "GGUFGenerativeModel", "model_category": "generative_local", "model_location": "llmware_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "chat_ml",
     "temperature": 0.3, "trailing_space": "",
     "gguf_file": "openhermes-2.5-mistral-7b.Q4_K_M.gguf",
     "gguf_repo": "llmware/bonchon",
     "link": "https://huggingface.co/llmware/bonchon",
     "custom_model_files": ["openhermes-2.5-mistral-7b.Q4_K_M.gguf"], "custom_model_repo": "llmware/bonchon"},

    {"model_name": "TheBloke/zephyr-7B-beta-GGUF", "display_name": "Zephyr-7B-GGUF",
     "model_family": "GGUFGenerativeModel", "model_category": "generative_local", "model_location": "llmware_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "hf_chat",
     "temperature": 0.3, "trailing_space": "",
     "gguf_file": "zephyr-7b-beta.Q4_K_M.gguf",
     "gguf_repo": "llmware/bonchon",
     "link": "https://huggingface.co/llmware/bonchon",
     "custom_model_files": ["zephyr-7b-beta.Q4_K_M.gguf"], "custom_model_repo": "llmware/bonchon"},

    {"model_name": "TheBloke/Starling-LM-7B-alpha-GGUF", "display_name": "Berkeley-Starling-7B-GGUF",
     "model_family": "GGUFGenerativeModel", "model_category": "generative_local", "model_location": "llmware_repo",
     "context_window": 2048, "instruction_following": False, "prompt_wrapper": "open_chat",
     "temperature": 0.3, "trailing_space": "",
     "gguf_file": "starling-lm-7b-alpha.Q4_K_M.gguf",
     "gguf_repo": "llmware/bonchon",
     "link": "https://huggingface.co/llmware/bonchon",
     "custom_model_files": ["starling-lm-7b-alpha.Q4_K_M.gguf"], "custom_model_repo": "llmware/bonchon"
     }
]

""" Fine-tuning Prompt Wrappers - virtually all instruct fine-tuned models will have a special 'prompt wrapper' 
that is an artifact from fine-tuning and needs to be applied consistently to lead to the expected model behavior.   
There are a number of common formats captured in the default catalog, but can be extended through ModelCatalog.   
When constructing the prompt, this wrapper will be applied automatically. """

global_model_finetuning_prompt_wrappers_lookup = {

        #   each wrapper can consist of up to 5 elements to represent common segments of the prompt
        #   1.  optional - "system_start" and "system_stop"
        #   2.  required - "main_start" and "main_stop"
        #   3.  required - "start_llm_response"

        "human_bot": {"main_start": "<human>: ", "main_stop": "\n", "start_llm_response": "<bot>:"},

        "<INST>": {"main_start": "<INST>", "main_stop": "</INST>", "start_llm_response": ""},

        "hf_chat": {"system_start": "<|im_start|>system\n", "system_stop": "<|im_end|>\n",
                    "main_start": "<|im_start|>user", "main_stop": "<|im_end|>\n",
                    "start_llm_response": "<|im_start|>assistant"},

        "open_chat": {"main_start": "GPT4 User: ", "main_stop": "<|endofturn|>",
                      "start_llm_response": "GPT4 Assistant:"},

        "alpaca": {"main_start": "### Instruction: ", "main_stop": "\n",
                   "start_llm_response": "### Response: "},

        "chat_ml": {"system_start": "<|im_start|>system", "system_stop":"<|im_end|>\n",
                    "main_start":"<|im_start|>user", "main_stop":"<|im_end|>\n",
                    "start_llm_response":"<|im_start|>assistant"}
        }


""" Global default prompt catalog consists of a set of prebuilt useful prompt instructions across a wide range
of models.   Unlike prompt_wrappers, which tend to be an attribute of the model, the prompt catalog can be invoked
on a 'prompt-by-prompt' basis to drive different behavior from a model.   Note:  not all models will support
 very complex open-ended instructions or respond in a consistent manner. """

global_default_prompt_catalog = [

    {"prompt_name": "just_the_facts",
     "prompt_description": "Closed Context - read passage, answer question, stick to the facts.",
     "run_order": ["blurb1", "$context", "blurb2", "$query", "instruction"],
     "blurb1": "Please read the following text: ",
     "blurb2": " Please answer the question: ",
     "instruction": "In providing the answer, please only use facts contained in the text.",
     "system_message": "You are a helpful assistant who speaks with facts and no wasted words.",
     "user_vars": {}},

    {"prompt_name": "answer_or_not_found",
     "prompt_description": "Closed Context - read passage, answer question, provide 'Not Found' if no answer in text.",
     "run_order": ["blurb1", "$context", "blurb2", "$query", "instruction"],
     "blurb1": "Please read the following text: ",
     "blurb2": " Please answer the question: ",
     "instruction": "Please only use facts in the text.  If the text does not provide the answer, then please "
                    "respond with: {{not_found_response}}",
     "system_message": "You are a helpful assistant who speaks with facts and no wasted words.",
     "user_vars": {"not_found_response": "'Not Found.'"}},

    {"prompt_name": "number_or_none",
     "prompt_description": "Closed Context - read passage, answer question, provide 'Not Found' if no answer in text.",
     "run_order": ["blurb1", "$context", "blurb2", "$query","instruction"],
     "blurb1" : "Please read the following text: ",
     "blurb2" : " Please answer the question: ",
     "instruction": "Please provide a specific number as an answer from the text.  "
                    "If the text does not provide a specific numerical answer, then please respond "
                    "with: {{not_found_response}}",
     "system_message": "You are a helpful assistant who speaks with facts and no wasted words.",
     "user_vars": {"not_found_response": "'Not Found.'"}},

    {"prompt_name": "summarize_with_bullets",
     "prompt_description": "Basic summarization with open ended number of bullet points.",
     "run_order": ["blurb1", "$context", "instruction"],
     "blurb1": "Please read the following text: ",
     "instruction": "Please summarize with bulletpoints.",
     "system_message": "You are a helpful assistant who speaks with facts and no wasted words.",
     "user_vars": {}},

    {"prompt_name": "summarize_with_numbered_bullets",
     "prompt_description": "Summarization with specified number of bullet points.",
     "run_order": ["blurb1", "$context", "instruction"],
     "blurb1": "Please read the following text: ",
     "instruction": "Please summarize the text with approximately {{number_of_bulletpoints}} numbered bulletpoints.",
     "system_message": "You are a helpful assistant who speaks with facts and no wasted words.",
     "user_vars": {"number_of_bulletpoints": 5}},

    {"prompt_name": "xsummary",
     "prompt_description": "Xtreme summarization with specified number of words.",
     "run_order": ["blurb1", "$context", "instruction"],
     "blurb1": "Please read the following text: ",
     "instruction": "Please summarize the text in no more than {{number_of_words}} words.",
     "system_message": "You are a helpful assistant who speaks with facts and no wasted words.",
     "user_vars": {"number_of_words": 25}},

    {"prompt_name": "completion",
     "prompt_description": "Open context text generation to complete starting point provided in prompt.",
     "run_order": ["blurb1", "$query", "instruction"],
     "blurb1": "Here is the starting point of a longer text: ",
     "instruction": "Please complete this text in the style provided in the text.",
     "system_message": "You are a helpful assistant who is a good creative writer.",
     "user_vars": {}},

    {"prompt_name": "dialog_summary",
     "prompt_description": "General summarization of a conversation text with specified number of bullet points.",
     "run_order": ["blurb1", "$context", "instruction"],
     "blurb1": "Please read the following discussion between two parties: ",
     "instruction": "Please summarize the key points from the conversation using less "
                    "than {{number_of_bulletpoints}} bulletpoints.",
     "system_message": "You are a helpful assistant.",
     "user_vars": {"number_of_bulletpoints": 10}},

    {"prompt_name": "not_found_classifier",
     "prompt_description": "Not Found Response classifier - used to ask a model to classify a particular response "
                           "as 'not found' - very useful in RAG applications.",
     "run_order": ["blurb1", "blurb2", "$context", "instruction"],
     "blurb1": "Here are several examples of a 'not found' response: "
               "Not Found \n"
               "The text does not provide an answer. \n"
               "The answer is not clear. \n"
               "Sorry, I could not find a definitive answer. \n"
               "The answer is not provided in the information given. \n"
               "The text does not specify the answer to this question. \n",
     "blurb2": "Here is a new example: ",
     "instruction": "Please respond 'Yes' or 'No' if this new example is a 'Not Found' response.",
     "system_message": "You are a helpful assistant.",
     "user_vars": {}},

    {"prompt_name": "top_level_select",
     "prompt_description": "Select the best answer among choices provided.",
     "run_order": ["blurb1", "$query", "blurb2","$context", "instruction"],
     "blurb1": "We are trying to answer the following question: ",
     "blurb2": "Which of the following selections best answers the question?",
     "instruction": "Please respond with the best answer among these selections.  "
                    "If more than one answer is useful, please summarize with bulletpoints.",
     "system_message": "You are a helpful assistant who speaks with facts and no wasted words.",
     "user_vars": {}},

    {"prompt_name": "answer_question_in_role",
     "prompt_description": "Answer a question with a specific role or point of view.",
     "run_order": ["blurb1", "$context", "blurb2", "$query", "instruction"],
     "blurb1": "Please read the following text: ",
     "blurb2": "Please answer the following question: ",
     "instruction": "In providing an answer to the question, please assume the perspective of a {{role}} and "
                    "write in that style.",
     "system_message": "You are a helpful assistant.",
     "user_vars": {"role": "business analyst"}},

    {"prompt_name": "editor_in_role",
     "prompt_description": "Edit a passage with a specific role or point of view.",
     "run_order": ["blurb1", "$context", "instruction"],
     "blurb1": "Please read the following text: ",
     "instruction": "Our task is to edit and improve the language of the text from the perspective of a business analyst.",
     "system_message": "You are a helpful editor and writer who reads text and improves the writing.",
     "user_vars": {"role": "business analyst"}},

    {"prompt_name": "yes_no",
     "prompt_description": "Answer a question with 'Yes' or 'No'.",
     "run_order": ["blurb1", "$context", "blurb2", "$query", "instruction"],
     "blurb1": "Please read the following text: ",
     "blurb2": "Based on these materials, please answer the question: ",
     "instruction": "Please answer this question with 'Yes' or 'No'.  If the text does not provide an answer,"
                    "then please respond with 'Not Found.'",
     "system_message": "You are a helpful assistant who speaks with facts and no wasted words.",
     "user_vars": {}},

    {"prompt_name": "multiple_choice",
     "prompt_description": "Answer a question using a set of pre-defined choices provided.",
     "run_order": ["blurb1", "$context", "blurb2", "$query", "instruction"],
     "blurb1": "Please read the following text: ",
     "blurb2": "Based on these materials, please answer the question: ",
     "instruction": "Please select from the choices provided.  If the text does not provide an answer,"
                    "then please respond with 'Not Found.'",
     "system_message": "You are a helpful assistant who speaks with facts and no wasted words."},

    {"prompt_name": "default_with_context",
     "prompt_description": "Default simple prompt when a question and context are passed.",
     "run_order": ["blurb1", "$context", "blurb2", "$query"],
     "blurb1": "Please read the following text: ",
     "blurb2": "Based on this text, please answer the question: ",
     "instruction": "",
     "system_message": "You are a helpful assistant who speaks with facts and no wasted words."},

    {"prompt_name": "default_no_context",
     "prompt_description": "Default simple prompt when only a question is passed.",
     "run_order": ["blurb1","$query"],
     "blurb1": "Please discuss the following: ",
     # "blurb2": "Based on this text, please answer the question: ",
     "instruction": "",
     "system_message": "You are a helpful assistant who likes to answer questions."},

    {"prompt_name": "summarize_with_bullets_w_query",
     "prompt_description": "Summarization of a text with a specific question being posed.",
     "run_order": ["blurb1", "$context", "blurb2","$query","instruction"],
     "blurb1": "Please read the following text: ",
     "blurb2": "Please read the following question: ",
     "instruction": "Please summarize with bulletpoints an analysis of the question.",
     "system_message": "You are a helpful assistant who speaks with facts and no wasted words."},

    {"prompt_name": "summarize_with_references_w_query",
     "prompt_description": "Summarization with text with guidance to provide reference to specific "
                           "information in the text passage.",
     "run_order": ["blurb1", "$context", "blurb2", "$query", "instruction"],
     "blurb1": "Please read the following text: ",
     "blurb2": "Please read the following question: ",
     "instruction": "Please provide an analysis of the question using information and specific clauses "
                    "in the text.",
     "system_message": "You are a helpful assistant who speaks with facts and no wasted words."},

    {"prompt_name": "write_poem",
     "prompt_description": "Write a poem prompt - note: results may vary greatly by model.",
     "run_order": ["instruction", "$query"],
     "instruction": "Please write a poem using the following prompt: ",
     "system_message": "You are a helpful assistant who is a creative writer and can rhyme words easily."},

    {"prompt_name": "ten_words",
     "prompt_description": "Xtreme summarization to answer question from a text in 10 words of less.",
     "run_order": ["instruction", "$query", "$context"],
     "blurb1": "Please read the following text: ",
     "blurb2": "Please read the following question: ",
     "instruction": "In no more than ten words, please give concise answer to the following question, using the "
                    "text as evidence to support",
     "system_message": "You are a helpful assistant who speaks with facts and no wasted words."},

    {"prompt_name": "explain_child",
     "prompt_description": "Standard simplified answer prompt - note: results may vary greatly by model.",
     "run_order": ["instruction", "$query", "$context"],
     "instruction": "Please explain to a child the following question using the provided text: ",
     "system_message": "You are a helpful assistant."},

    {"prompt_name": "make_joke",
     "prompt_description": "Standard joke prompt - note:  results may vary greatly by model.",
     "run_order": ["instruction", "$query"],
     "instruction": "Please be funny and tell a joke on the subject of: ",
     "system_message": "You are a helpful assistant with a good sense of humor."},

    {"prompt_name": "tell_story",
     "prompt_description": "Standard tell a story prompt - note: results may vary greatly by model.",
     "run_order": ["instruction", "$query"],
     "instruction": "Please write the start of a story on the topic of: ",
     "system_message": "You are a helpful assistant."},

    {"prompt_name": "write_headline",
     "prompt_description": "Generate a headline from a question and context.",
     "run_order": ["instruction", "$query", "$context"],
     "instruction": "Please write the headline only in a few words in capitalization to answer the question below, "
                    "using the materials provided. ",
     "system_message": "You are a helpful assistant."},

    {"prompt_name": "facts_only",
     "prompt_description": "Basic 'facts only' Q&A prompt.",
     "run_order": ["blurb1", "$context", "blurb2", "$query", "instruction"],
     "blurb1": "Please use the following materials- ",
     "blurb2": "Please answer the following question - ",
     "instruction": "In answering the question, please only use information contained in the provided materials.",
     "system_message": "You are a helpful assistant."},

    {"prompt_name": "top_bulletpoints",
     "prompt_description": "Summarization with question and answer in 5 bullet points.",
     "run_order": ["blurb1", "$context", "blurb2", "$query", "instruction"],
     "blurb1": "Please read the text below -  ",
     "blurb2": "Please read the following question - ",
     "instruction": "Please answer the question using the text, and write no more than 5 bulletpoints.",
     "system_message": "You are a helpful assistant."},

    {"prompt_name": "report_title",
     "prompt_description": "Generate title of report given context passage.",
     "run_order": ["instruction", "$context"],
     "instruction": "Please write the title to a report with the following information:  ",
     "system_message": "You are a helpful assistant."},

    {"prompt_name": "marketing_slogan",
     "prompt_description": "Generate marketing style slogan given context passage.",
     "run_order": ["blurb1", "$context", "blurb2", "$query", "instruction"],
     "blurb1": "Please read the following materials- ",
     "blurb2": "Please answer the following question - ",
     "instruction": "Please write a marketing slogan for the following offering using the following information as "
                    "background source materials.",
     "system_message": "You are a helpful assistant."},

    {"prompt_name": "top_level_summary",
     "prompt_description": "Summarization prompt intended for 'second-level' summaries of materials.",
     "run_order": ["blurb1", "$context", "blurb2", "$query", "instruction"],
     "blurb1": "Please read the following materials- ",
     "blurb2": "Please answer the following question - ",
     "instruction": "In answering the question, please write no more than five bulletpoints, and reference the most "
                    "important facts in the source materials.",
     "system_message": "You are a helpful assistant."},

]
