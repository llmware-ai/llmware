# Test when a library has no blocks to embed, or when a null query is passed into a semantic search

import os
from llmware.library import Library
from llmware.retrieval import Query
import sys
sys.path.append(os.path.join(os.path.dirname(__file__),".."))
from utils import Logger

def test_no_blocks_faiss():
    library = Library().create_new_library("test_no_blocks_faiss")

    # Faiss
    embedding_summary = library.install_new_embedding(embedding_model_name="mini-lm-sbert",vector_db="faiss")
    Logger().log(f"\n  > Embedding Summary: {embedding_summary}")
    assert embedding_summary is not None
    
    query_results = Query(library).semantic_query(query="Salary", result_count=3, results_only=True)
    Logger().log(f"\n  > Query Results: {query_results}")
    assert query_results is not None

def test_no_blocks_milvus():
    library = Library().create_new_library("test_no_blocks_milvus")

    embedding_summary = library.install_new_embedding(embedding_model_name="mini-lm-sbert",vector_db="milvus")
    Logger().log(f"\n  > Embedding Summary: {embedding_summary}")
    assert embedding_summary is not None
    
    query_results = Query(library).semantic_query(query="Salary", result_count=3, results_only=True)
    Logger().log(f"\n  > Query Results: {query_results}")
    assert query_results is not None

def test_no_blocks_pinecone():
    library = Library().create_new_library("test_no_blocks_pinecone")

    embedding_summary = library.install_new_embedding(embedding_model_name="mini-lm-sbert",vector_db="pinecone")
    Logger().log(f"\n  > Embedding Summary: {embedding_summary}")
    assert embedding_summary is not None
    
    query_results = Query(library).semantic_query(query="Salary", result_count=3, results_only=True)
    Logger().log(f"\n  > Query Results: {query_results}")
    assert query_results is not None

def test_no_blocks_mongo_atlas():
    library = Library().create_new_library("test_no_blocks_atlas")

    embedding_summary = library.install_new_embedding(embedding_model_name="mini-lm-sbert",vector_db="mongo_atlas")
    Logger().log(f"\n  > Embedding Summary: {embedding_summary}")
    assert embedding_summary is not None
    
    query_results = Query(library).semantic_query(query="Salary", result_count=3, results_only=True)
    Logger().log(f"\n  > Query Results: {query_results}")
    assert query_results is not None
   
 