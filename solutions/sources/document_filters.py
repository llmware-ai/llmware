
"""
This 'getting started' example demonstrates how to use basic text retrieval with the Query class
      1. Create a sample library
      2. Run a basic text query
      3. View the results
"""

import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup
from llmware.configs import LLMWareConfig

#   A very powerful form of retrieval involves document filters.  Once a 'document filter' is created, it can be
#   applied to query further only in that document set
#   For example:You could set up a document filter to get all documents that mention
#   a topic like 'Artificial Intelligence'
#   and then within that subset of documents, look for details on leading researchers.


def create_agreements_embeddings_sample_library(library_name):

    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files(over_write=False)
    ingestion_folder_path = os.path.join(sample_files_path, "Agreements")
    parsing_output = library.add_files(ingestion_folder_path)

    library.install_new_embedding(embedding_model_name="mini-lm-sbert", vector_db="chromadb")

    return library


def perform_retrieval_with_document_filters(library, doc_filter_text, query_text):

    print(f"Example - using a Document Filter with Semantic Search")

    #   create a Query instance
    query = Query(library)

    #   create a document filter using exact (text) search mode
    doc_filter = query.document_filter(doc_filter_text, query_mode="text", exact_mode=True)

    #   the document filter narrows the library to only documents with the target filter_text
    print("\ndocument filter: ", doc_filter)

    #   perform a semantic query with the document filter -> results will be limited to the documents in the filter
    semantic_results = query.semantic_query_with_document_filter(query_text, doc_filter)

    #   display the text from the results
    print (f"\nRetrieval with a document filter'")
    for i, result in enumerate(semantic_results):
        result_text = result["text"]
        print (f"Results - {i} - file_source - {result['file_source']} - {result['distance']}"
               f" - {result['text']}")

    return 0


if __name__ == "__main__":

    LLMWareConfig().set_active_db("sqlite")

    lib = create_agreements_embeddings_sample_library("lib_doc_filter_1")

    #   this will run a two-step query
    #   step 1  - look in the entire library for documents with the executive's name 'leto apollo'
    #   step 2  - using that document filter, pass to a semantic query, and retrieve specific text chunks
    #             from the selected documents with 'base salary'

    perform_retrieval_with_document_filters(library=lib, doc_filter_text="leto apollo", query_text='base salary')


