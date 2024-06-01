---
layout: default
title: Freqently Asked Questions
nav_order: 12
permalink: /faq
---
# Frequently Asked Questions (FAQ)


### How can I set the chunk size?
#### "I wnat to parse my documents into smaller chunks"
You can set the chunk size with the ``chunk_size`` parameter of the ``add_files`` method.

The ``add_files`` method from the ``Library`` class has a ``chunk_size`` parameter that controls the chunk size.
The method in addition has a parameter to control the maxium chunk size with ``max_chunk_size``.
These two parameters are passed on to the ``Parser`` class.
In the following example, we add the same files with different chunk sizes to the library ``chunk_size_example``.
```python
from pathlib import Path

from llmware.library import Library


path_to_my_library_files = Path('~/llmware_data/sample_files/Agreements')

my_library = Library().create_new_library(library_name='chunk_size_example')
my_library.add_files(input_folder_path=path_to_my_library_files, chunk_size=400)
my_library.add_files(input_folder_path=path_to_my_library_files, chunk_size=600)
```

### How can I set the embedding store?
#### "I want to use a specific embedding store"


### How can I set the data store?
#### "I want to use a specific data store"


### How can I retrieve more context?
#### "I want to retrieve more context from a query"


### How can I set the Large Language Model?
#### "I want to use a different LLM"

### How can I set the embedding model?
#### "I want to use a different embedding model"
