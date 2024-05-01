
""" This example demonstrates creating and using knowledge graphs and document graphs """

import os
from llmware.library import Library
from llmware.setup import Setup
from llmware.graph import Graph
from llmware.configs import LLMWareConfig


def build_and_use_knowledge_graph (library_name):

    #   note: steps 1-3 are repeated in several examples and create a basic library with document sources
    #   -- if you have already created a library, then skip to step 4

    # step 1 - Create library which is the main 'organizing construct' in llmware
    print ("\nupdate: Step 1 - Creating library: {}".format(library_name))

    library = Library().create_new_library(library_name)

    # step 2 - Pull down the sample files from S3 through the .load_sample_files() command
    #   --note: if you need to refresh the sample files, set 'over_write=True'
    print ("update: Step 2 - Downloading Sample Files")

    sample_files_path = Setup().load_sample_files(over_write=False)

    #   step 3 - point ".add_files" method to the folder of documents that was just created
    #   this method parses all of the documents, text chunks, and captures in MongoDB

    print("update: Step 3 - Parsing and Text Indexing Files")

    library.add_files(input_folder_path=os.path.join(sample_files_path, "UN-Resolutions-500"))

    #
    #   ***         KNOWLEDGE GRAPH METHODS START HERE      ***
    #
    #   step 4 - Build the Knowledge Graph from Library
    #

    # Build the knowledge graph
    print (f"update: Step 4 - Building knowledge graph for library '{library.library_name}'...")
    library.generate_knowledge_graph()

    # Knowledge graph artifacts are stored in the library's /nlp folder
    print (f" > Generated knowledge graph artifacts\nFrom: {library.nlp_path}:")
    for file_name in os.listdir(library.nlp_path):
        print (f"  - {file_name}")
   
    #   step 5 - Load Graph object with my_library
    graph = Graph(library)

    # Get the overall nlp stats
    print (f"\n > Knowledge graph - nlp stats")
    library_analytics = graph.get_library_data_stats()

    print("update: library analytics - ", library_analytics)

    # Run a pseudo query against the knowledge graph to find related terms
    # These terms could be used to 'enhance' search query and weigh more heavily on related concepts
    query_term = 'united nations'
    print (f"\nKnowledge graph - query for '{query_term}'")
    query_results = graph.kg_query(query_term)
    for key, value in query_results.items():
        print(f" - {key}: {value}")

    # Related bigrams
    print (f"\nKnowledge graph - bigrams for '{query_term}'")
    bigrams = graph.kg_query_related_bigrams(query_term)
    print(f"{bigrams}")

    # Query counts
    query_term_2 = "sustainable social development"
    print (f"\n > Knowledge graph - query counts for '{query_term_2}'")
    query_counts = graph.kg_query_counts(query_term_2)
    print(f" - {query_counts}")

    # Export for visualization
    print (f"\n > Knowledge graph - export for visualization for query '{query_term}'")
    red_nodes, nodes, edges = graph.export_graph_with_query_to_visualize(20, query_term)
    print ("nodes for export - ", red_nodes, nodes, edges)

    # Export whole graph for visualization
    print (f"\n > Knowledge graph - export for visualization for whole graph")
    nodes, edges = graph.export_graph_to_visualize(10)
    print("nodes for export - ", nodes, edges)

    return 0


if __name__ == "__main__":

    LLMWareConfig().set_active_db("sqlite")

    build_and_use_knowledge_graph("kg_test_99_610")
