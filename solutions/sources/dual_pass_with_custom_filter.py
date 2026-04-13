import os
from llmware.library import Library
from llmware.setup import Setup
from llmware.status import Status
from llmware.retrieval import Query

def create_unr500_sample_library(library_name):
    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files(over_write=False)
    ingestion_folder_path = os.path.join(sample_files_path, "UN-Resolutions-500")
    parsing_output = library.add_files(ingestion_folder_path)
    return library

def parse_and_generate_vector_embeddings(library_name, input_folder_path):
    # Configuration for embeddings
    embedding_model = "mini-lm-sbert"
    vector_db = "milvus"

    # Create a new library or load if it exists
    print(f"\nCreating or loading library: {library_name}")
    library = Library().load_library(library_name)

    if not library:
        print(f"Error: Failed to create or load library '{library_name}'")
        return

    # Parse and text index files
    print("Parsing and Text Indexing Files")
    if not os.path.exists(input_folder_path):
        print(f"Error: Input folder path '{input_folder_path}' does not exist.")
        return

    num_files_added = library.add_files(input_folder_path=input_folder_path)
    print(f"Number of files added for indexing: {num_files_added}")

    # Generate embeddings
    print(f"Generating Embeddings in {vector_db} db with Model {embedding_model}")
    embedding_status = library.install_new_embedding(embedding_model_name=embedding_model, vector_db=vector_db)
    if not embedding_status:
        print(f"Error: Embedding generation failed for model '{embedding_model}' with vector db '{vector_db}'")
        return

    # Check the embedding status
    update = Status().get_embedding_status(library_name, embedding_model)
    print("Embeddings Complete - Status check at end of embedding: ", update)


def perform_dual_pass_query(library, query_text, result_count=20, primary="text", custom_filter=None, desired_match_status=None):
    print(f"\nPerforming dual pass query: '{query_text}'")

    q = Query(library)

    # Perform the query with the custom filter
    dual_pass_results = q.dual_pass_query(query_text, result_count=result_count, primary=primary, custom_filter=custom_filter)

    # Filter results based on match status if desired_match_status is specified
    if desired_match_status:
        dual_pass_results = [result for result in dual_pass_results if result.get('match_status') == desired_match_status]

    for i, result in enumerate(dual_pass_results):
        print(f"Result {i+1}:")
        print(f"    Doc ID: {result.get('doc_ID')}")
        print(f"    Block ID: {result.get('block_ID')}")
        print(f"    Page Num: {result.get('page_num')}")
        print(f"    Text Snippet: {result.get('text')}")
        print(f"    File Source: {result.get('file_source')}")
        print(f"    Match Status: {result.get('match_status')}")
        print("----")

    return dual_pass_results

if __name__ == "__main__":
    
    library_name = "un_resolutions500"     
    query_text = "what weapons will cause an arms race?"  # Replace with your query text

    # Custom filter definition
    custom_filter = {
        "author_or_speaker": "ETPU FrontDesk1",
        "file_type": "pdf",
        "content_type": "image"
        # Add more filters as needed
    }

    # Assuming library is already created and vector embeddings are generated
    library = Library().load_library(library_name)

    # Perform a dual pass query on the library with custom filter
    dual_pass_results = perform_dual_pass_query(library, query_text, custom_filter=custom_filter)

    # If you want to filter by match_status, pass the desired status like "matched" in the function call
    # dual_pass_results = perform_dual_pass_query(library, query_text, custom_filter=custom_filter, desired_match_status="matched")
