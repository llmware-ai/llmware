---
layout: default
title: Introduction by Examples
nav_order: 2
permalink: /examples
---
# Introduction by Examples
We introduce ``llmware`` through self-contained examples.


# Create your first library 
The code we use here is taken from our [example-1-create_first_library.py](https://github.com/llmware-ai/llmware/blob/main/fast_start/example-1-create_first_library.py), on some places, however, slightly modified.
{: .note}

In this introduction, we will walk through the steps of creating a **library**.
To create a ``library`` in ``llmware`` we have to instantiate a ``library`` object and call
the ``add_files`` method, which will parse the files, chunk up the text and also index it.
We will also download the samples files we provide, which can be used for any experimentation you
might want to do.




```python
from llmware.setup import Setup

sample_files_path = Setup().load_sample_files(over_write=False)
```

In ``llmware``, a **library** is a collection of unstructured data.
Currently, ``llmware`` supports *text* and *images*.
```python
from llmware.library import Library

library = Library().create_new_library('my_llmware_library')
```

``add_files`` supports pdf, pptx, docx, xlsx, csv, md, txt, json, wav, and zip, jpg, and png.
```python
library.add_files(ingestion_folder_path)
```


```python
updated_library_card = library.get_library_card()
doc_count = updated_library_card["documents"]
block_count = updated_library_card["blocks"]
```

```python
library_path = library.library_main_path
```


The result of a ``Query`` is a list of dictionaries, where one dictionary is one result.
A result dictionary has a wide range of useful keys.
A few important keys in the dictionary are *text*, *file_source*, *page_num*, *doc_ID*, *block_ID*, and
*matches*.
```python
query_results = Query(library).text_query('base salary', result_count=10)

for i, result in enumerate(query_results):
    text = result["text"]
    file_source = result["file_source"]
    page_number = result["page_num"]
    doc_id = result["doc_ID"]
    block_id = result["block_ID"]
    matches = result["matches"]
```

You can take a look at all the keys that are returned by calling ``keys()``.
```python
query_results[0].keys()
```
