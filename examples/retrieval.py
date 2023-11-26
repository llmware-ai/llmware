''' This example demonstrates the various ways to retrieve data from libraries:
      1. Basic retrieval
      2. Retrieval with filters
      3. Bulk retrieval
      4. Retrieval State and Export
 '''

import os
from llmware.configs import LLMWareConfig
from llmware.library import Library
from llmware.resources import LibraryCatalog
from llmware.retrieval import Query
from llmware.setup import Setup
from sentence_transformers import SentenceTransformer

# Create a library (if it doesn't already exist), add files to it and generate vector embeddings which enables semantic query
def create_and_populate_a_library(library_name):

    print (f" > Creating and populating a library: {library_name}")
    # Load the library or create and populate it if doesn't exist
    if Library().check_if_library_exists(library_name):
        # Load the library
        library = Library().load_library(library_name)
        # Load an embedding model and create vector embeddings for the library 
        library.install_new_embedding(from_sentence_transformer=True, embedding_model_name=embedding_model_name, model=embedding_model, vector_db="milvus")
 
    else:
        # Create the library
        library = Library().create_new_library(library_name) 
        # Load the llmware sample file repository
        sample_files_path = Setup().load_sample_files()
        # Add files from the "SmallLibrary" folder to library
        library.add_files(os.path.join(sample_files_path,"SmallLibrary"))
        # Load an embedding model and create vector embeddings for the library 
        library.install_new_embedding(from_sentence_transformer=True, embedding_model_name=embedding_model_name, model=embedding_model, vector_db="milvus")
    # Return the library
    return library

# A retrieval returns a query_result dict that contains information about the query including the "results" 
def perform_basic_text_retrieval(library, query_text):

    # Create a Query instance
    query = Query(library)
    # Set the keys that should be returned 
    query.query_result_return_keys = ["file_source", "page_num", "text"]
    # Perform a simple query
    query_results = query.query(query_text)
    # Get the top result:
    top_result = query_results[0]
    # Print the file, page_num and text from from the first result
    file_source = top_result["file_source"]
    page_number = top_result["page_num"]
    result_text = top_result["text"]
    print (f"\n> Top result for '{query_text}': {file_source} (page {page_number}):\nText:{result_text}")

# A retrieval returns a query_result dict that contains information about the query including the "results"
def perform_text_retrieval_by_author(library, query_text, author):

    # Create a Query instance
    query = Query(library)
    # Set the keys that should be returned 
    query.query_result_return_keys = ["file_source", "page_num", "text", "author_or_speaker"]
    # Perform a text query by author
    query_results = query.text_query_by_author_or_speaker(query_text, author)
    # Get the top result:
    top_result = query_results[0]
    # Print the file, page_num, text and author from from the first result
    file_source = top_result["file_source"]
    page_num = top_result["page_num"]
    text = top_result["text"]
    author = top_result["author_or_speaker"]
    print (f"\n> Top result for '{query_text}': {file_source} (page {page_num}), Author: {author}:\nText:{text}")

# A bibliography is the lsit of documents and their pages referenced in a set of query results. 
# The format is: [{'Gaia EXECUTIVE EMPLOYMENT AGREEMENT.pdf': [3, 5, 2, 4, 1]}]
def get_bibliography_from_query_results(library, query_text):

    # Create a Query instance
    query = Query(library)
    # Perform a simple query
    query_results = query.query(query_text, result_count=20)
    # Get a bibliography
    biblio = query.bibliography_builder_from_qr(query_results=query_results)
    # Print out the bibliography
    print (f"\n> Bibliography for '{query_text}':\n{biblio}")

# If a particular result is interesting, you can widen the context window to retrieve more text before and/or after
def focus_on_and_expand_result(library, query_text):

    # Create a Query instance
    query = Query(library)
    # Perform a simple query
    query_results = query.query(query_text, result_count=20)
    # Capture the third result
    interesting_result = query_results[2]
    # Pull a 500 character window from before the result
    result_before = query.expand_text_result_before(interesting_result,window_size=500)
    # Pull a 100 character window from after the result
    result_after = query.expand_text_result_after(interesting_result, window_size=100)
    # Print the original result and the expanded result
    original_result_text = interesting_result["text"]
    expanded_result_text = result_before["expanded_text"] + original_result_text + result_after["expanded_text"]
    print (f"\n> Expanding a result context window'")
    print (f"\nOriginal result: {original_result_text}")
    print (f"\nExpanded Result: {expanded_result_text}")

# A very powerful form of retrieval involves document filters.  Once a 'document filter' is created, it can be 
# applied to query further only in that document set
# For example:You could set up a document filter to get all documents that mention a topic like 'Artificial Intelligence'
# and then within that subset of documents, look for details on leading researchers.
def perform_retrieval_with_document_filters(library, doc_filter_text, query_text):

    # Create a Query instance
    query = Query(library,from_sentence_transformer=True,embedding_model_name=embedding_model_name, embedding_model=embedding_model)
    # Create a document filter using exact (text) search mode
    doc_filter = query.document_filter(doc_filter_text, query_mode="text", exact_mode=True)
    # Perform a semantic query with the document filter
    semantic_results = query.semantic_query_with_document_filter(query_text, doc_filter, result_count=3)
    # Print the text from the results
    print (f"\n> Retrieval with a document filter'")
    for i, result in enumerate(semantic_results):
        result_text = result["text"]
        print (f"\n{1}. {result_text}")


# Sometimes you want to retrieve all data so you can further process it yourself
def perform_bulk_retrieval(library):
 
    # Create a Query instance
    query = Query(library)
    # Create a list of keys of interest. This can be omitted if you want all keys
    key_dict = ["file_source", "text", "page_num", "author_or_speaker"]
    # Get the whole libary. The returns a list of all blocks
    all_blocks = query.get_whole_library(selected_keys=key_dict)
    print (f"\n> Bulk retrieval Retrieval'")
    print (f"\n{len(all_blocks)} blocks were retrieved")

# A dual pass retrieval combines semantic + text query
def perform_dual_pass_retrieval(library, query_text):

    # Create a Query instance configured for semantic search
    query = Query(library,from_sentence_transformer=True,embedding_model_name=embedding_model_name, embedding_model=embedding_model)
    # Do a dual_pass_query
    hybrid_qr_results = query.dual_pass_query(query_text,result_count=20, primary="semantic")
    num_of_results = len(hybrid_qr_results)
    print (f"\n> Dual Pass Retrieval'")
    print (f"\n{num_of_results} were found")

# Demonstrate some methods involved with persisting and loading Query state as well as export
def retreival_state_and_export(library):

    # Create a Query instance with history peristence
    query = Query(library, save_history=True)
    # Capture the query_id
    query_id = query.query_id
    # Run a series of queries
    query_results = query.text_query("sustainable development", result_count=20)
    query_results = query.text_query("africa", result_count=26)
    query_results = query.text_query("pandemic risk", result_count=15)
    # Save state
    query.save_query_state()
    # Generate Retrieval Report.  The report will be stored in the llmware_data/query_history folder
    csv_file = query.generate_csv_report()
    csv_file_path = os.path.join(LLMWareConfig().get_query_path(), csv_file)
    print (f"\n> Retrieval State and Export'")
    print (f"\nExport for query id '{query_id}': {csv_file_path}")
    
    # Additionally here is how can clear state and reload based on a query_id:
    query.clear_query_state()
    query.load_query_state(query_id)

# Demonstrate the methods and capabilities available for doing filtered retrieval
# Note: This method is not meant to be run as-is.
def retrieval_filter_options(library):

    # Create a Query instance
    query = Query(library)
    # Basic filters by block fields
    filter_dict = {"content_type": "text", "author_or_speaker": "Margaret Smith"}
    query_results = query.text_query_with_custom_filter("human rights", filter_dict, result_count=20)

    # Document filters
    doc_id_list = [0,1,5,13,22,135]
    query_results = query.text_query_with_document_filter("human rights", doc_id_list)

    # Page Lookup - especially useful when looking for data on a notable or known page in your documents, e.g., the first page
    page_list = [1,6]
    query_results = query.page_lookup(page_list=page_list,doc_id_list=doc_id_list,text_only=True)

    # Predefined filters
    query_results_with_images = query.image_query("africa")
    query_results_with_tables = query.table_query("revenue")
    query_results_by_page = query.text_search_by_page("recitals", page_num=1)
    query_results_from_filter = query.text_query_by_author_or_speaker("company stock price", "John Smith")
    query_results_docs_only = query.document_filter("tesla stock",exact_mode=True, result_count=50)

    # Timestamp filters
    first_date = "2005-05-10"
    last_datae = "2023-12-31"
    query_results_time_window = query.filter_by_time_stamp(query_reults, first_date=first_date, last_date=last_date)

# Demonstrate the methods and capabilities available when doing semantic queries
# Note: This method is not meant to be run as-is.
def semantic_retrieval_strategies(library):

    # Create a Query instance configured for semantic search
    query = Query(library,from_sentence_transformer=True,embedding_model_name=embedding_model_name, embedding_model=embedding_model)

    # Use semantic embeddings to 're-rank' query results
    text_query_results = query.text_query("stock trends", result_count=30)
    reranked_results = query.apply_semantic_ranking(text_query_results,"stock trends")

    # Use semantic embedding space directly by passing 'text block' directly, rather than a query
    one_block = reranked_results["results"][0]
    direct_embedding_results = query.similar_blocks_embedding(one_block, result_count=30, embedding_distance_threshold=1.5)

    # Augment text query with semantic
    text_query_results = query.text_query("stock trends", result_count=30)
    augmented_qr = query.augment_qr(texts_query_results,"stock trends",augment_query="semantic")


# Embedding model used for the examples below
embedding_model_name = "all-MiniLM-L6-v1"
print (f"Loading embedding model: '{embedding_model_name}'")
embedding_model = SentenceTransformer(embedding_model_name)

library = create_and_populate_a_library(library_name="retrieval_tests")
perform_basic_text_retrieval(library=library, query_text='salary')
perform_text_retrieval_by_author(library=library, query_text='United Nations', author='Andrea Chambers')
get_bibliography_from_query_results(library=library, query_text='salary')
focus_on_and_expand_result(library=library, query_text='salary')
perform_retrieval_with_document_filters(library=library, doc_filter_text="Agreement", query_text='Agreement')
perform_bulk_retrieval(library)
perform_dual_pass_retrieval(library=library, query_text='africa')
retreival_state_and_export(library)
