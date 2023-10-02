''' This example demonstrates creating vector embeddings (used for doing semantic queries)
      Note: Pinecone is not used in the example below as it requires an API key.  If you have a Pinecone account, you can set these two variables:
         os.environ.get("USER_MANAGED_PINECONE_API_KEY") = <your-pinecone-api-key>
         os.environ.get("USER_MANAGED_PINECONE_ENVIRONMENT") = <your-pinecone-environment> (for example "gcp-starter")
'''
import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup

# Generate vector embeddings and store then in each of Milvus, FAISS
# This is only to demonstrate how to work with the various embedding DBs.  Typically, you'd pick just one
def generate_vector_embeddings(library_name):  

    # Create and populate a library
    print (f"\n > Creating a and populating library: {library_name}...")
    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files()
    library.add_files(input_folder_path=os.path.join(sample_files_path, "SmallLibrary"))

    # To create vector embeddings you just need to specify the embedding model and the vector embedding DB
    # For examples of using HuggingFace and SentenceTransformer models, see those examples in this same folder
    vector_dbs = ["milvus", "faiss"]
    embedding_model = "mini-lm-sbert"
    for vector_db in vector_dbs:
        print (f"\n > Generating embedding vectors and storing in '{vector_db}'...")
        library.install_new_embedding(embedding_model_name=embedding_model, vector_db=vector_db)

    # Then when doing semantic queries, the most recent vector DB used for embeddings will be used.
    # We just find the best 3 hits for "Salary"
    query = Query(library,embedding_model_name=embedding_model)
    print (f"\n > Running a query for 'Salary'...")
    query_results = Query(library).semantic_query(query="Salary", result_count=3, results_only=True)
    print (query_results) 
    print (f"\n\nHits for 'Salary' in '{library_name}':\n")
    for query_result in query_results:
        print("File: " +  query_result["file_source"] + " (Page " + str(query_result["page_num"]) + "):\n" + query_result["text"] + "\n")

generate_vector_embeddings("embedding_tests")

