
"""
#   This example shows how easily a core text dataset for domain adaptation can be created.
#   The dataset is packaged as JSONL files with each row representing a training sample, and is automatically split
#   into train / test / validation datasets. A manifest.json file describes the dataset artifacts in the archive.
#   This dataset is designed primarily for fine-tuning semantic embedding models using a contrastive distortion
#   technique, such as TSDAE or DECLUTR, but the dataset is generally "model-ready" for most "language model"
#   unsupervised tasks.

#   Note: this dataset is not intended for instruct-training -> see other examples for building instruct/dialog datasets
"""

import os

from llmware.library import Library
from llmware.dataset_tools import Datasets
from llmware.setup import Setup
from llmware.configs import LLMWareConfig


def build_embedding_finetuning_dataset(library_name):

    # step 1 - create new library
    lib = Library().create_new_library(library_name)

    # step 2 - pull sample documents (or point to your own)
    sample_file_path = Setup().load_sample_files(over_write=False)
    fin_docs_path = os.path.join(sample_file_path, "FinDocs")

    # step 3 - parse, text chunk and index files that will be used to create the dataset
    parsing_output = lib.add_files(fin_docs_path)

    print("update: completed parsing - ", parsing_output)

    # step 4 - create dataset
    ds = Datasets(library=lib, testing_split=0.10, validation_split=0.10)
    ds_output = ds.build_text_ds(min_tokens=100, max_tokens=500)
    print("update: completed building dataset - ", ds_output)
    print("update: dataset will be found in this path - ", lib.dataset_path)

    return ds_output


if __name__ == "__main__":

    LLMWareConfig().set_active_db("sqlite")

    my_lib_name = "financial_docs_library"
    output = build_embedding_finetuning_dataset(my_lib_name)
