''' This example demonstrates:
    1. Creating your first library
    2. Adding some files to it
    3. Generating vector embeddings and storing them in Milvus 
    4. Doing a semantic query
'''

import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup
from llmware.status import Status

library_name="getting_started"

print (f"\n > Creating library {library_name}...")
library = Library().create_new_library(library_name)

print (f"\n > Loading the llmware Sample Files...")
sample_files_path = Setup().load_sample_files()

print (f"\n > Adding some files to the library...")
library.add_files(input_folder_path=os.path.join(sample_files_path, "SmallLibrary"))

print (f"\n > Generating embedding vectors (using the 'mini-lm-sbert' model) and storing them (using 'Milvus')...")
Status(library.account_name).tail_embedding_status(library.library_name, "mini-lm-sbert")
library.install_new_embedding(embedding_model_name="mini-lm-sbert", vector_db="milvus")

print (f"\n > Running a query for 'Salary'...")
query_results = Query(library).semantic_query(query="Salary", result_count=3, results_only=True)
print (query_results)
print (f"\n\nHits for 'Salary' in {library_name}:\n")
for query_result in query_results:
    print("File: " +  query_result["file_source"] + " (Page " + str(query_result["page_num"]) + "):\n" + query_result["text"] + "\n")
