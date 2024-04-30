
""" This example demonstrates creating and using datasets
    1. Datasets suitable for fine tuning embedding models
    2. Completion and other types of datasets
    3. Generating datasets from all data in a library or with filtered data
    4. Creating datasets from AWS Transcribe transcripts
"""

import json
import os
from llmware.dataset_tools import Datasets
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup
from llmware.configs import LLMWareConfig


def build_and_use_dataset(library_name):

    # Setup a library and build a knowledge graph.  Datasets will use the data in the knowledge graph
    print (f"\n > Creating library {library_name}...")
    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files()
    library.add_files(os.path.join(sample_files_path,"SmallLibrary"))
    library.generate_knowledge_graph()

    # Create a Datasets object from library
    datasets = Datasets(library)

    # Build a basic dataset useful for industry domain adaptation for fine-tuning embedding models
    print (f"\n > Building basic text dataset...")

    basic_embedding_dataset = datasets.build_text_ds(min_tokens=500, max_tokens=1000)
    dataset_location = os.path.join(library.dataset_path, basic_embedding_dataset["ds_id"])

    print (f"\n > Dataset:")
    print (f"(Files referenced below are found in {dataset_location})")

    print (f"\n{json.dumps(basic_embedding_dataset, indent=2)}")
    sample = datasets.get_dataset_sample(datasets.current_ds_name)

    print (f"\nRandom sample from the dataset:\n{json.dumps(sample, indent=2)}")
    
    # Other Dataset Generation and Usage Examples:

    # Build a simple self-supervised generative dataset- extracts text and splits into 'text' & 'completion'
    # Several generative "prompt_wrappers" are available - chat_gpt | alpaca | 
    basic_generative_completion_dataset = datasets.build_gen_ds_targeted_text_completion(prompt_wrapper="alpaca")
    
    # Build a generative self-supervised training sets created by pairing 'header_text' with 'text'
    xsum_generative_completion_dataset = datasets.build_gen_ds_headline_text_xsum(prompt_wrapper="human_bot")
    topic_prompter_dataset = datasets.build_gen_ds_headline_topic_prompter(prompt_wrapper="chat_gpt")
    
    # Filter a library by a key term as part of building the dataset
    filtered_dataset = datasets.build_text_ds(query="agreement", filter_dict={"master_index":1})
    
    # Pass a set of query results to create a dataset from those results only
    query_results = Query(library=library).query("africa")
    query_filtered_dataset = datasets.build_text_ds(min_tokens=250,max_tokens=600, qr=query_results)

    return 0


if __name__ == "__main__":

    LLMWareConfig().set_active_db("sqlite")

    build_and_use_dataset("test_txt_datasets_0")
