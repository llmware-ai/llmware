---
layout: default
title: Library 
parent: Components
nav_order: 7
description: overview of the major modules and classes of LLMWare  
permalink: /components/library
---
# Library:  ingest, organize and index a collection of knowledge at scale - Parse, Text Chunk and Embed.  
---

Library is the main organizing construct for unstructured information in LLMWare.   Users can create one large library with all types of different content, or
can create multiple libraries with each library comprising a specific logical collection of information on a
particular subject matter, project/case/deal, or even different accounts/users/departments.

Each Library consists of the following components:

1. Collection on a Database - this is the core of the Library, and is created through parsing of documents, which
are then automatically chunked and indexed in a text collection database.  This is the basis for retrieval,
and the collection that will be used as the basis for tracking any number of vector embeddings that can be
attached to a library collection.

2. File archives - found in the llmware_data path, within Accounts, there is a folder structure for each Library.
All file-based artifacts for the Library are organized in these folders, including copies of all files added in
the library (very useful for retrieval-based applications), images extracted and indexed from the source
documents, as well as derived artifacts such as nlp and knowledge graph and datasets.

3. Library Catalog - each Library is registered in the LibraryCatalog table, with a unique library_card that has
the key attributes and statistics of the Library.

When a Library object is passed to the Parser, the parser will automatically route all information into the
Library structure.

The Library also exposes convenience methods to easily install embeddings on a library, including tracking of
incremental progress.

To parse into a Library, there is the very useful convenience methods, "add_files" which will invoke the Parser,
collate and route the files within a selected folder path, check for duplicate files, execute the parsing,
text chunking and insertion into the database, and update all of the Library state automatically.

Libraries are the main index constructs that are used in executing a Query.   Pass the library object when
constructing the Query object, and then all retrievals (text, semantic and hybrid) will be executed against
the content in that Library only.


```python

from llmware.library import Library

#   to parse and text chunk a set of documents (pdf, pptx, docx, xlsx, txt, csv, md, json/jsonl, wav, png, jpg, html)  

#   step 1 - create a library, which is the 'knowledge-base container' construct
#          - libraries have both text collection (DB) resources, and file resources (e.g., llmware_data/accounts/{library_name})
#          - embeddings and queries are run against a library

lib = Library().create_new_library("my_library")

#    step 2 - add_files is the universal ingestion function - point it at a local file folder with mixed file types
#           - files will be routed by file extension to the correct parser, parsed, text chunked and indexed in text collection DB

lib.add_files("/folder/path/to/my/files")

#   to install an embedding on a library - pick an embedding model and vector_db
lib.install_new_embedding(embedding_model_name="mini-lm-sbert", vector_db="milvus", batch_size=500)

#   to add a second embedding to the same library (mix-and-match models + vector db)  
lib.install_new_embedding(embedding_model_name="industry-bert-sec", vector_db="chromadb", batch_size=100)

#   easy to create multiple libraries for different projects and groups

finance_lib = Library().create_new_library("finance_q4_2023")
finance_lib.add_files("/finance_folder/")

hr_lib = Library().create_new_library("hr_policies")
hr_lib.add_files("/hr_folder/")

#    pull library card with key metadata - documents, text chunks, images, tables, embedding record
lib_card = Library().get_library_card("my_library")

#   see all libraries
all_my_libs = Library().get_all_library_cards()

```


Need help or have questions?
============================

Check out the [llmware videos](https://www.youtube.com/@llmware) and [GitHub repository](https://github.com/llmware-ai/llmware).

Reach out to us on [GitHub Discussions](https://github.com/llmware-ai/llmware/discussions).


# About the project

`llmware` is &copy; 2023-{{ "now" | date: "%Y" }} by [AI Bloks](https://www.aibloks.com/home).

## Contributing
Please first discuss any change you want to make publicly, for example on GitHub via raising an [issue](https://github.com/llmware-ai/llmware/issues) or starting a [new discussion](https://github.com/llmware-ai/llmware/discussions).
You can also write an email or start a discussion on our Discrod channel.
Read more about becoming a contributor in the [GitHub repo](https://github.com/llmware-ai/llmware/blob/main/CONTRIBUTING.md).

## Code of conduct
We welcome everyone into the ``llmware`` community.
[View our Code of Conduct](https://github.com/llmware-ai/llmware/blob/main/CODE_OF_CONDUCT.md) in our GitHub repository.

## ``llmware`` and [AI Bloks](https://www.aibloks.com/home)
``llmware`` is an open source project from [AI Bloks](https://www.aibloks.com/home) - the company behind ``llmware``.
The company offers a Software as a Service (SaaS) Retrieval Augmented Generation (RAG) service.
[AI Bloks](https://www.aibloks.com/home) was founded by [Namee Oberst](https://www.linkedin.com/in/nameeoberst/) and [Darren Oberst](https://www.linkedin.com/in/darren-oberst-34a4b54/) in Oktober 2022.

## License

`llmware` is distributed by an [Apache-2.0 license](https://github.com/llmware-ai/llmware/blob/main/LICENSE).

## Thank you to the contributors of ``llmware``!
<ul class="list-style-none">
{% for contributor in site.github.contributors %}
  <li class="d-inline-block mr-1">
     <a href="{{ contributor.html_url }}">
        <img src="{{ contributor.avatar_url }}" width="32" height="32" alt="{{ contributor.login }}">
    </a>
  </li>
{% endfor %}
</ul>


---
<ul class="list-style-none">
    <li class="d-inline-block mr-1">
        <a href="https://discord.gg/MhZn5Nc39h"><span><i class="fa-brands fa-discord"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://www.youtube.com/@llmware"><span><i class="fa-brands fa-youtube"></i></span></a>
    </li>
   <li class="d-inline-block mr-1">
    <a href="https://huggingface.co/llmware"><span> <img src="https://huggingface.co/front/assets/huggingface_logo-noborder.svg" alt="Hugging Face" class="hugging-face-logo"/> </span></a>
     </li>
    <li class="d-inline-block mr-1">
        <a href="https://www.linkedin.com/company/aibloks/"><span><i class="fa-brands fa-linkedin"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://twitter.com/AiBloks"><span><i class="fa-brands fa-square-x-twitter"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://www.instagram.com/aibloks/"><span><i class="fa-brands fa-instagram"></i></span></a>
    </li>
</ul>
---

