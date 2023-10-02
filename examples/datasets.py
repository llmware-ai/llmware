''' This example demonstrates creating and using datasets
    1. Datasets suitable for fine tuning embedding models
    2. Completion and other types of datasets
    3. Generating datasets from all data in a library or with filtered data
    4. Creating datasets from AWS Transcribe transcripts
'''
import json
import os
from llmware.util import Datasets
from llmware.library import Library
from llmware.retrieval import Query
from llmware.parsers import Parser
from llmware.setup import Setup

def build_and_use_dataset(library_name):

    # Setup a library and build a knowledge graph.  Datasets will use the data in the knowledge graph
    print (f"\n > Creating library {library_name}...")
    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files()
    library.add_files(os.path.join(sample_files_path,"SmallLibrary"))
    library.generate_knowledge_graph()

    # Create a Datasets object
    datasets = Datasets(library)

    # Build a basic dataset useful for industry domain adaptation for finetuning embedding models
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
    basic_generative_completion_dataset= datasets.build_gen_ds_targeted_text_completion(prompt_wrapping="alpaca")
    
    # Build a generative self-supervised training sets created by pairing 'header_text' with 'text'
    xsum_generative_completion_dataset = datasets.build_gen_ds_headline_text_xsum(prompt_wrapping="human_bot")
    topic_prompter_dataset = datasets.build_gen_ds_headline_topic_prompter(prompt_wrapping="chat_gpt")
    
    # Filter a library by a key term as part of building the dataset
    filtered_dataset = datasets.build_text_ds(query="agreement", filter_dict={"master_index":1})
    
    # Pass a set of query results to create a dataset from those results only
    query_results = Query(library=library).query("africa")
    query_filtered_dataaset = datasets.build_text_ds(min_tokens=250,max_tokens=600, qr=query_results)
        
    # Images with text dataset
    images_with_text_dataset = datasets.build_visual_ds_image_labels()

    
def build_aws_transcribe_datasets(library_name):

    # Setup a library and build a knowledge graph.  Datasets will use the data in the knowledge graph
    print (f"\n > Creating library {library_name}...")
    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files()
    library.add_dialogs(os.path.join(sample_files_path,"AWS-Transcribe"))
    library.generate_knowledge_graph()

    # Create a Datasets object
    datasets = Datasets(library)

    # Build generative conversation dataset 
    print (f"\n > Building generative conversation dataset...")
    generative_conversation_dataset = datasets.build_gen_dialog_ds(prompt_wrapping="human_bot",human_first=True)
    dataset_location = os.path.join(library.dataset_path, generative_conversation_dataset["ds_id"])
    print (f"\n > Dataset:")
    print (f"(Files referenced below are found in {dataset_location})")
    print (f"\n{json.dumps(generative_conversation_dataset, indent=2)}")
    sample = datasets.get_dataset_sample(datasets.current_ds_name)
    print (f"\nRandom sample from the dataset:\n{json.dumps(sample, indent=2)}")

    # Other Dataset Generation and Usage Examples:
    
    # Build generative model fine-tuning dataset from llm prompt state history
    # supports 3 popular formats - alpaca, chatgpt, and 'human_bot'
    generative_curated_dataset = datasets.build_gen_ds_from_prompt_history(prompt_wrapping="alpaca")

build_and_use_dataset("test_txt_datasets")
build_aws_transcribe_datasets("aws_transcribe_datasets")