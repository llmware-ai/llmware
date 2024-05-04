
""" This example shows how to get started using the ModelCatalog to instantiate models and start running inferences.

    A core design principle of LLMWare is that all models should be accessible in the same way, with the
    underlying configuration details handled at lower levels of the implementation.   Our aspiration is that you
    should be able to substitute models in any pipeline/workflow at any point with minimal, if any, code change -
    and to be able to deploy heterogeneous combinations of local, private network and API-based models,
    with mix-qnd-match and full 'swqp-ability' at any time.

    While LLMWare supports OpenAI and other API-based models, we are "open-source-first" in our view and
    support of models, and all of our examples and classes/methods are optimized first to work with small, specialized
    open source models.   Our view is that essentially anything that can be done with large API models can be
    replicated with smaller fine-tuned models and well-designed data pipelines and workflows.

    We provide over 50+ LLMWare models that are all tested and designed for easy integration
    into LLMWare pipeline and workflows, but we are 100% committed to providing an open ecosystem and supporting
    the best in open source, including leading embedding models from Jina and Nomic, Llama-2, Llama-3, Mistral,
    Phi-3, Yi, DeciLM, StableLM, OpenHermes, Tiny Llama, RedPajama, Pythia, Sheared LLama, Huggingface Zephyr,
    SentenceTransformers and quantizations from The Bloke and Bartowski.  We also provide a full integration into GGUF,
    LLama.CPP and Whisper.CPP.

    It is easy to extend the ModelCatalog to include any of your favorite models from
    HuggingFace, Ollama, LMStudio, LLama.CPP, or llama-cpp-python.

    For open source models, we generally support both PyTorch (Huggingface) based models, as well as GGUF (LLama.CPP)
    quantized models.  For most use cases, we find that GGUF quantized versions are faster, take less memory
    and are generally as accurate, so we use GGUF-based models, aka "tools", in many of our examples.

    """

from llmware.models import ModelCatalog

all_models = ModelCatalog().list_all_models()

#   ~133 models in the catalog as of May 4, 2024 - and growing all the time!
print("\nAll Models")

for i, model in enumerate(all_models):
    print("models: ", i, model)

#   ~30 embedding models - including Nomic, Jina, leading sentence transformers, llmware industry-bert models
embedding_models = ModelCatalog().list_embedding_models()

"""
print("\nEmbedding Models")
for i, model in enumerate(embedding_models):
    print("embedding models: ", i, model)
"""

#   ~92 open source models
open_source_models = ModelCatalog().list_open_source_models()

"""
print("\nOpen Source Models")
for i, model in enumerate(open_source_models):
    print("open source models: ", i, model)
"""

#   Inference is Easy - same two lines every time
#   1.  load_model - use the model_name or display_name, and it will be looked up and instantiated
#   2.  inference -  all models support an inference method - call it to run a basic inference

model_name = "phi-3-gguf"
model = ModelCatalog().load_model(model_name)
response = model.inference("I am going to Paris.  What should I see?")

print(f"\ntest inference - {model_name} - response: ", response)

#   Check out other examples in Models, Prompts, SLIM-Agents Embeddings, and Use_Cases
#   -- configuration in loading model - temperature, sample, max_output
#   -- add models to the Catalog for easy invocation
#   -- integrating sources and building RAG workflows in Prompts
#   -- fact-checking and post-processing
#   -- using function-calls on small specialized models
#   -- agent based workflows
#   -- installing embeddings on a library collection


