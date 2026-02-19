import os
import shutil
from llmware.library import Library
from llmware.retrieval import Query

def setup_environment(docs_folder):
    """Ensure docs folder exists and contains test files"""
    os.makedirs(docs_folder, exist_ok=True)
    
    test_file = os.path.join(docs_folder, "test_neet.txt")
    if not os.path.exists(test_file):
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("NEET stands for National Eligibility cum Entrance Test. "
                   "It is India's medical entrance examination for undergraduate programs.")
        print(f"Created test file: {test_file}")

def create_fresh_library(library_name):
    """Create a completely clean library"""
    # Delete if exists
    if Library().check_if_library_exists(library_name):
        Library().delete_library(library_name)
    
    # Manual cleanup
    lib_path = os.path.join(os.path.expanduser("~"), "llmware", "libraries", library_name)
    if os.path.exists(lib_path):
        shutil.rmtree(lib_path)
    
    # Create new
    return Library().create_new_library(library_name)

def process_documents(library, docs_folder):
    """Add and process documents with clear feedback"""
    print("\nProcessing documents:")
    doc_files = [f for f in os.listdir(docs_folder) 
                if f.endswith(('.pdf', '.docx', '.txt', '.pptx', '.md'))]
    
    for doc in doc_files:
        print(f"- Found: {doc}")
    
    # Process documents (v0.4.1 compatible)
    result = library.add_files(input_folder_path=docs_folder,
                             chunk_size=400)
    
    library.generate_knowledge_graph()
    print("\nDocuments processed successfully!")

def query_documents(library):
    """Interactive query interface"""
    print("\nReady for queries. Try asking about:")
    print("- NEET exam")
    print("- Medical entrance")
    print("- What NEET stands for")
    
    while True:
        query = input("\nYour question (or 'quit'): ").strip()
        if query.lower() in ('quit', 'exit'):
            break
        
        results = Query(library).text_query(query, result_count=2)
        
        if results:
            print(f"\nFound {len(results)} results:")
            for i, res in enumerate(results, 1):
                print(f"\n{i}. From {res['file_source']}:")
                print(res['text'][:300].replace('\n', ' ') + "...")
        else:
            print("\nNo results found. Try rephrasing or check document content.")

if __name__ == "__main__":
    # Configuration - matches your exact paths
    DOCS_FOLDER = r"C:\Users\rites\llmware\examples\Retrieval\docs"
    LIB_NAME = "neet_library"
    
    print("NEET Document QA System (llmware v0.4.1)")
    print(f"Using documents from: {DOCS_FOLDER}")
    
    # Setup environment
    setup_environment(DOCS_FOLDER)
    
    # Create fresh library
    lib = create_fresh_library(LIB_NAME)
    
    # Process documents
    process_documents(lib, DOCS_FOLDER)
    
    # Start query session
    query_documents(lib)