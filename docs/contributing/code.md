---
layout: default
title: Code contributions
parent: Contributing
nav_order: 1
permalink: /contributing/code
---
# Contributing code
One way to contribute to ``llmware`` is by contributing to the code base.

We briefly describe some of the important modules of ``llmware`` next, so you can more easily navigate the code base.
You may also take a look at our [fast start series from YouTube](https://www.youtube.com/playlist?list=PL1-dn33KwsmD7SB9iSO6vx4ZLRAWea1DB).

## Core modules

### Library
<iframe width="560" height="315" src="https://www.youtube.com/embed/2xDefZ4oBOM?si=IAHkxpQkFwnWyYTL" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
The *library* module implements the classes **Library** and **LibraryCatalog**.
The **Library** class implements the *library* concept.
A *library* is a collection of documents, where a document can be PDF, an image, or an office document.
It is responsible for parsing, text chunking, and indexing.
In other words, it does the heavy lifting of adding content.
In the following, we shortly describe the functions for adding documents to the library.

```python
add_file(
    self,
    file_path):
```
This method adds one document of any supported type to the library.

```python
add_files(
    self,
    input_folder_path=None,
    encoding="utf-8",
    chunk_size=400,
    get_images=True,get_tables=True,
    smart_chunking=2,
    max_chunk_size=600,
    table_grid=True,
    get_header_text=True,
    table_strategy=1,
    strip_header=False,
    verbose_level=2,
    copy_files_to_library=True):
```
This method adds the documents of one folder to the library.

```python
add_website(
    self,
    url,
    get_links=True,
    max_links=5):
```
This method adds a website, and links from the website, to the library.

```python
add_wiki(
    self,
    topic_list,
    target_results=10):
```
This method adds a wikipedia article to the library.

```python
add_dialogs(
    self,
    input_folder=None):
```
This method adds an AWS dialog transcript to the library.

```python
add_image(
    self,
    input_folder=None):
```
This method adds images to the libary.

```python
add_pdf_by_ocr(
    self,
    input_folder=None):
```
This method adds scanned PDFs to the library.

```python
add_pdf(
    self,
    input_folder=None):
```
This method adds PDFs to the library.

```python
add_office(
    self,
    input_folder=None):
```
This method adds office documents to the library.

### Embeddings
<iframe width="560" height="315" src="https://www.youtube.com/embed/xQEk6ohvfV0?si=GAPle5gVdVPkYKWv" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
An *embedding* is a vector store and an embedding model.
It is responsible for applying an embedding model to a library, storing the embeddings in a vector store, and providing access to the embeddings with natural language queries.
We briefly describe the common methods offered by all vector stores below.

```python
def create_new_embedding(
    self,
    doc_ids=None,
    batch_size=500):
```
This method creates the embeddings and adds them to the vector store.

```python
def search_index(
    self,
    query_embedding_vector,
    sample_count=10):
```
This method searches the vector store given the query vector.

```python
def delete_index(self):
```
This method deletes the created vector store index.


### Prompts
<iframe width="560" height="315" src="https://www.youtube.com/embed/swiu4oBVfbA?si=rKbgO3USADCqICqr" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
A *prompt* is an input to model.
The prompt is used by the model to generate the response.
One important use case is that users want to augment a prompt, or a series of prompts, with additional information.
Next, we describe methods for augmenting a prompt with additional information.

```python
def add_source_new_query(
    self,
    library,
    query=None,
    query_type="semantic",
    result_count=10):
```
This method adds the results of the ``query`` to the prompt.

```python
def add_source_query_results(
    self,
    query_results):
```
This method adds previous results from a query as a source to the prompt.

```python
def add_source_library(
    self,
    library_name):
```
This method adds an entire library to the prompt.
We recommend that you only use this when the library is sufficiently small.

```python
def add_source_wikipedia(
    self,
    topic,
    article_count=3,
    query=None):
```
This method adds wikipedia articles to the prompt based on the provided ``topic``.

```python
def add_source_yahoo_finance(
    self,
    ticker=None,
    key_list=None):
```
This method adds a Yahoo finance ticker to the prompt.

```python
def add_source_knowledge_graph(
    self,
    library,
    query):
```
This method adds the summary output elements from a knowledge graph based on the provided ``query``.
Please note that this method is experimental, i.e. unstable, and is subject to change dramatically in each new version.

```python
def add_source_website(
    self,
    url,
    query=None):
```
This method adds the website pointed to by the ``url`` to the prompt.

```python
def add_source_document(
    self,
    input_fp,
    input_fn,
    query=None):
```
This method adds a document, or documents, of any supported type to the prompt.
If documents are added, then the ``query`` parameter can be used to filter the documents.

```python
def add_source_last_interaction_step(
    self):
```
This method adds the last interaction to the prompt.
The use case for this is to enable interactive dialog, i.e. chatting.

### Model Catalog
A *model catalog* is a collection of models.
In the following, we briefly describe the methods for adding new models to the catalog.

```python
def register_new_hf_generative_model(
    self,
    hf_model_name=None,
    context_window=2048,
    prompt_wrapper="<INST>",
    display_name=None,
    temperature=0.3,
    trailing_space="",
    link=""):
```
This method adds a new generative model from hugging face.
Users can therefore add models from hugging face that are unsupported currently.

```python
def register_sentence_transformer_model(
    self,
    model_name,
    embedding_dims,
    context_window,
    display_name=None,
    link=""):
```
This method adds a new sentence transformer.

```python
def register_gguf_model(
    self,
    model_name,
    gguf_model_repo,
    gguf_model_file_name,
    prompt_wrapper=None,
    eos_token_id=0,
    display_name=None,
    trailing_space="",
    temperature=0.3,
    context_window=2048,
    instruction_following=True):
```
This method adds a new GGUF model.

```python
def register_open_chat_model(
    cls,
    model_name,
    api_base=None,
    model_type="chat",
    display_name=None,
    context_window=4096,
    instruction_following=True,
    prompt_wrapper="",
    temperature=0.5):
```
This method adds any chat model that is available through a web API, e.g. a chat model that is available locally
via localhost.

```python
def register_ollama_model(
    cls,
    model_name,
    host="localhost",
    port=11434,
    model_type="chat",
    raw=False,
    stream=False,
    display_name=None,
    context_window=4096,
    instruction_following=True,
    prompt_wrapper="",
    temperature=0.5):
```
This method adds an OLLama model that is available through a web API.
The method is similar to the ``register_open_chat_model`` method above.

### Categories of code contributions

#### New or Enhancement to existing Features
You want to submit a code contribution that adds a new feature or enhances an existing one?
Then the best way to start is by opening a discussion in our [GitHub discussions](https://github.com/llmware-ai/llmware/discussions).
Please do this before you work on it, so you do not put effort into it just to realise after submission that
it will not be merged.

#### Bugs
If you encounter a bug, you can

- File an issue about the bug.
- Provide a self-contained minimal example that reproduces the bug, which is extremely important.
- Provide possible solutions for the bug.
- Submit a pull a request to fix the bug.

We encourage you to read [How to create a Minimal, Reproducible Example](https://stackoverflow.com/help/minimal-reproducible-example) from the Stackoverflow helpcenter, and the tag description of [self-container](https://stackoverflow.com/tags/self-contained/info), also from Stackoverflow.
