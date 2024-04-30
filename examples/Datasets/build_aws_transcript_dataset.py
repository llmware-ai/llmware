
""" This example demonstrates how to create a dataset from AWS Transcripts
    1. Parse AWS JSON Transcripts
    2. Build Dialog Dataset
"""

import json
import os
from llmware.dataset_tools import Datasets
from llmware.library import Library
from llmware.setup import Setup
from llmware.configs import LLMWareConfig


def build_aws_transcribe_datasets(library_name):

    # Setup a library and build a knowledge graph.  Datasets will use the data in the knowledge graph
    print (f"\n > Creating library {library_name}...")
    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files()
    library.add_dialogs(os.path.join(sample_files_path ,"AWS-Transcribe"))
    library.generate_knowledge_graph()

    # Create a Datasets object
    datasets = Datasets(library)

    # Build generative conversation dataset
    print (f"\n > Building generative conversation dataset...")
    generative_conversation_dataset = datasets.build_gen_dialog_ds(prompt_wrapper="human_bot", human_first=True)
    dataset_location = os.path.join(library.dataset_path, generative_conversation_dataset["ds_id"])
    print (f"\n > Dataset:")
    print (f"(Files referenced below are found in {dataset_location})")
    print (f"\n{json.dumps(generative_conversation_dataset, indent=2)}")
    sample = datasets.get_dataset_sample(datasets.current_ds_name)
    print (f"\nRandom sample from the dataset:\n{json.dumps(sample, indent=2)}")

    return 0


if __name__ == "__main__":

    LLMWareConfig().set_active_db("sqlite")

    build_aws_transcribe_datasets("aws_transcripts_lib_1")
