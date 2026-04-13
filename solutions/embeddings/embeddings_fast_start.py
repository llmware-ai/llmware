
""" This example shows the general recipe for creating an embedding.  This scenario uses ChromaDB in local
    file mode for no-install laptop deployment.

    NOTE: you may need to install separately:  pip3 install chromadb.

"""


import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup
from importlib import util
from llmware.configs import LLMWareConfig

if not util.find_spec("chromadb"):
    print("\nto run this example with chromadb, you need to install the chromadb python sdk:  pip3 install chromadb")


def embeddings_fast_start (library_name, vector_db="chromadb"):

    # Create and populate a library
    print (f"\nstep 1 - creating and populating library: {library_name}...")
    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files()
    library.add_files(input_folder_path=os.path.join(sample_files_path, "AgreementsLarge"))

    # To create vector embeddings you just need to specify the embedding model and the vector embedding DB
    # For examples of using HuggingFace and SentenceTransformer models, see those examples in this same folder

    embedding_model = "mini-lm-sbert"

    print (f"\n > Generating embedding vectors and storing in '{vector_db}'...")
    library.install_new_embedding(embedding_model_name=embedding_model, vector_db=vector_db)

    # Then when doing semantic queries, the most recent vector DB used for embeddings will be used.

    # We just find the best 3 hits for "Salary"
    q = Query(library)
    print (f"\n > Running a query for 'Salary'...")
    query_results = q.semantic_query(query="Salary", result_count=10, results_only=True)

    for i, entries in enumerate(query_results):

        # each query result is a dictionary with many useful keys

        text = entries["text"]
        document_source = entries["file_source"]
        page_num = entries["page_num"]
        vector_distance = entries["distance"]

        #  for display purposes only, we will only show the first 100 characters of the text
        if len(text) > 125:  text = text[0:125] + " ... "

        print("\nupdate: query results - {} - document - {} - page num - {} - distance - {} "
              .format( i, document_source, page_num, vector_distance))

        print("update: text sample - ", text)

    return query_results


if __name__ == "__main__":

    LLMWareConfig().set_active_db("sqlite")

    #   set to 'chromadb' local file storage for no-install fast start
    db = "chromadb"
    embeddings_fast_start("embedding_test_1", vector_db=db)


