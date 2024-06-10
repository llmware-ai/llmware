---
layout: default
title: Introduction by Examples 
parent: Examples
nav_order: 9
permalink: /examples/getting_started
---
# Introduction by Examples
We introduce ``llmware`` through self-contained examples.


# Your first library and query

{: .note }
> The code here is a modified version from [example-1-create_first_library.py](https://github.com/llmware-ai/llmware/blob/main/fast_start/example-1-create_first_library.py).
> The adjustments are made to ease understanding for this post.

In this introduction, we will walk through the steps of creating a **library**.
To create a ``library`` in ``llmware`` we have to instantiate a ``library`` object and call
the ``add_files`` method, which will parse the files, chunk up the text and also index it.
We will also download the samples files we provide, which can be used for any experimentation you
might want to do.


**Configuring llmware**

Before we get started, we can influence the configuration of ``llmware``.
For example, we can decide on which **text collection** data base to use, and on the logging level.
By default, ``llmware`` uses MongoDB as the text collection data base and has a ``debug_mode`` level
of ``0``.
This means that by default, ``llmware`` will show the status manager and print errors.
The status manager is useful for large parsing jobs.
In this ``library`` introduction, we will change the text collection data base as well as the ``debug_mode``.
As the text collection data base, we will choose ``sqlite``.
And we will change the ``debug_mode`` to ``2``, which will show the file name that is being parsed, i.e. a file-by-file progress.
```python
from llmware.configs import LLMWareConfig

LLMWareConfig().set_active_db("sqlite")
LLMWareConfig().set_config("debug_mode", 2)
```

**Downloading sample files**

We start by downloading the sample files we need.
``llmware`` provides a set of sample files which we use throughout our examples.
The following code snippet downloads these sample files, and in doing so creates the directories
*Agreements*, *Invoices*, *UN-Resolutions-500*, *SmallLibrary*, *FinDocs*, and *AgreementsLarge*.
If you want to get the newest version of the sample files, you can set ``over_write=True``.
However, we encourage you to try it out with your own files once you are comfortable enough with ``llmware``.
```python
from llmware.setup import Setup

sample_files_path = Setup().load_sample_files(over_write=False)
```
``sample_files_path`` is the path where the files are stores.
Assume that your use name is ``foo``, then on Linux the path would be ``'/home/foo/llmware_data/sample_files'.``


**Creating a library**

Now that we have data, we can start to create our library.
In ``llmware``, a **library** is a collection of unstructured data.
Currently, ``llmware`` supports *text* and *images*.
The following code creates an empty ``library`` with the name ``my_llmware_library``.
```python
from llmware.library import Library

library = Library().create_new_library('my_llmware_library')
```

**Adding files to a library**

Now that we have created a ``library``, we are ready to *add files* to it.
Currently, the ``add_files`` method supports pdf, pptx, docx, xlsx, csv, md, txt, json, wav, and zip, jpg, and png.
The method will automatically choose the correct parser, based on the file extension.
```python
library.add_files('/home/foo/llmware_data/sample_files/Agreements')
```

**The library card**

A ``library`` keeps inventory of its files, similar to a good librarian.
We do this with a *library card*.
At the moment of this writing, a library card has the keys _id, library_name, embedding, knowledge_graph, unique_doc_id, documents, blocks, images, pages, tables, and account_name.
```python
updated_library_card = library.get_library_card()
doc_count = updated_library_card["documents"]
block_count = updated_library_card["blocks"]
library_card.keys()
```

You can also get where the library is stored via the ``library_main_path`` attribute.
Again, assuming your user name is *foo* and you are on a Linux system, then the ``library_path`` is ``'/home/foo/llmware_data/accounts/llmware/my_lib'``.
```python
library.library_main_path
```

**Querying a library**

Finally, we are ready to execute a query against our library.
Remember that the text is indexed automatically when we add it to the library.
The result of a ``Query`` is a list of dictionaries, where one dictionary is one result.
A result dictionary has a wide range of useful keys.
A few important keys in the dictionary are *text*, *file_source*, *page_num*, *doc_ID*, *block_ID*, and
*matches*.
In the following, we query the library for the base salary, return the first ten results, and
iterate over the results.
```python
query_results = Query(library).text_query('base salary', result_count=10)

for query_result in query_results:
    text = query_result["text"]
    file_source = query_result["file_source"]
    page_number = query_result["page_num"]
    doc_id = query_result["doc_ID"]
    block_id = query_result["block_ID"]
    matches = query_result["matches"]
```

You can take a look at all the keys that are returned by calling ``keys()``.
```python
query_results[0].keys()
```
