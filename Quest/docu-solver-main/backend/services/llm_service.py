from llmware.library import Library
from llmware.retrieval import Query
from llmware.configs import LLMWareConfig

# Configure LLMWare
LLMWareConfig().set_active_db("sqlite")
LLMWareConfig().set_vector_db("chromadb")

# Initialize the library name for creating a new library in llmware
library_name = "docsolver"
library = Library().create_new_library(library_name)

# Ingest and index files
def ingest_and_index_files(folder_path: str):
    # print(f"Parsing and indexing files from {folder_path}")
    parsing_output = library.add_files(
        input_folder_path=folder_path,
        chunk_size=200,
        max_chunk_size=250,
        smart_chunking=2,
        strip_header=True,
        encoding="utf-8",
        get_images=False,
        get_tables=False,
        get_header_text=False
    )
    # print(f"Completed parsing - {parsing_output}")

    updated_library_card = library.get_library_card()
    doc_count = updated_library_card["documents"]
    block_count = updated_library_card["blocks"]
    # print(f"Updated library card - documents: {doc_count}, blocks: {block_count}, {updated_library_card}")

    library_path = library.library_main_path
    print(f"Library artifacts, including extracted images, saved at folder path: {library_path}")



# Get responses from LLM
def get_llm_responses(query: str, result_count: int = 5) -> list:
    ingest_and_index_files("./uploaded_files")
    print(query)
    query_results = Query(library).text_query(query, result_count=result_count)


    query = [f"{result['text']}\n" for result in query_results]
    print(query)
    return query
