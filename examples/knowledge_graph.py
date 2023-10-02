''' This example demonstrates creating and using knowledge graphs and document graphs
'''

import os
from llmware.library import Library
from llmware.setup import Setup
from llmware.util import Graph

# Create a library (if it doesn't already exist), add files to it
def create_and_populate_a_library(library_name):

    # Load the library or create and populate it if doesn't exist
    if Library().check_if_library_exists(library_name):
        # Load the library
        library = Library().load_library(library_name)
    else:
        print (f" > Creating library {library_name}...")
        # Create the library
        library = Library().create_new_library(library_name) 
        # Load the llmware sample file repository
        sample_files_path = Setup().load_sample_files()
        # Add files from the "SmallLibrary" folder to library
        library.add_files(os.path.join(sample_files_path,"SmallLibrary"))
    # Return the library
    return library

# Just a helper method to print large lists in the following methods more cleanly
def summarize_top_10(the_object):
    try:
        iterator = iter(the_object) 
    except TypeError:
        return the_object

    output = ""
    for i, item in enumerate(iterator):
        if i >= 10:
            return output
        output += (f"\n    - {item}")
    return output

# Building a knowledge graph is easy.
# It is an analytically intensive process and can take a few minutes for larger collections
def build_and_use_knowledge_graph (library):

    # Build the knowledge graph
    print (f" > Building knowledge graph for library '{library.library_name}'...")
    library.generate_knowledge_graph()

    # Knowledge graph artifacts are stored in the library's /nlp folder
    print (f" > Generated knowledge graph artifacts\nFrom: {library.nlp_path}:")
    for file_name in os.listdir(library.nlp_path):
        print (f"  - {file_name}")
   
    # Load Graph object with my_library
    graph = Graph(library)

    # Get the overall nlp stats
    print (f"\n > Knowledge graph - nlp stats")
    library_analytics = graph.get_library_data_stats()
    for key, value in library_analytics.items():
        if key not in ['graph_top']:
            if key in ['bigrams','mcw']:
                print(f"  - {key} (top 10 only):{summarize_top_10(value)}")
            else:
                print(f"  - {key}: {summarize_top_10(value)}")
  
    # Run a pseudo query against the knowledge graph to find related terms
    # These terms could be used to 'enhance' search query and weigh more heavily on related concepts
    query_term = 'united nations'
    print (f"\n > Knowledge graph - query for '{query_term}'")
    query_results = graph.kg_query(query_term)
    for key, value in query_results.items():
        print(f" - {key}: {value}")

    # Related bigrams
    print (f"\n > Knowledge graph - bigrams for '{query_term}'")
    bigrams = graph.kg_query_related_bigrams(query_term)
    for key, value in query_results.items():
        print(f" - {key}: {value}")
  
    # Query counts
    query_term_2 = "sustainable social development"
    print (f"\n > Knowledge graph - query counts for '{query_term_2}'")
    query_counts = graph.kg_query_counts(query_term_2)
    print(f" - {query_counts}")

    # Export for visualization
    print (f"\n > Knowledge graph - export for visualization for query '{query_term}'")
    red_nodes, nodes, edges = graph.export_graph_with_query_to_visualize(10, query_term)
    red_nodes = summarize_top_10(red_nodes)
    nodes = summarize_top_10(nodes)
    edges = summarize_top_10(edges)
    print(f" - Red Nodes: {(red_nodes)}\n - Nodes (top 10 only): {nodes}\n - Edges (top 10 only): {edges}")
 
    # Export whole graph for visualization
    print (f"\n > Knowledge graph - export for visualization for whole graph")
    nodes, edges = graph.export_graph_to_visualize(10)
    nodes = summarize_top_10(nodes)
    edges = summarize_top_10(edges)
    print(f" - Nodes (top 10 only): {nodes}\n - Edges (top 10 only): {edges}")

    # Build document graph
    print (f"\n > Building document graphs...")
    doc_graph = graph.doc_graph_builder()

    first_doc = doc_graph[0]

    print (f"\n > Document graph information for the 1st document in the library")
    for key, value in first_doc.items():
        if key in ['last_block_in_doc', 'first_block_in_doc', 'doc_ID']:
            print(f" - {key} : {value}")
            continue
        if key in ['context_table']:
            print(f" - {key} (top 3 only):")
            for i, item in enumerate(value):
                if (i >= 3):
                    continue
                print (f"    - {item}")

        else:
            print(f" - {key} (top 10 only):{summarize_top_10(value)}")


    # Assemble top blocks
    print (f"\n > Top blocks")
    block_output = graph.assemble_top_blocks(first_doc["block_scores"],first_doc["doc_ID"], max_samples=3)
    print (f"block_output:\n{block_output}")

library = create_and_populate_a_library("knowledge_graph")
build_and_use_knowledge_graph(library)
