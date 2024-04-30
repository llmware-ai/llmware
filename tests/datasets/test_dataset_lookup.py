import os
import sys

from llmware.library import Library
from llmware.setup import Setup
from llmware.dataset_tools import Datasets
from logging import Logger

sys.path.append(os.path.join(os.path.dirname(__file__),".."))


def test_ds_lookup_by_name():

    library = Library().create_new_library("test_dataset_lookup")
    sample_files_path = Setup().load_sample_files()
    library.add_files(os.path.join(sample_files_path,"SmallLibrary"))

    ds = Datasets(library=library)

    # iterate thru all datasets in one shot
    for i, entry in enumerate(ds.dataset_available_types):
        ds_card = ds.get_dataset_card(entry)
        Logger().log(f"\n--------------------")
        Logger().log(f"{i+1}. {ds_card}")
        ds_dict = ds.build_ds_by_name(entry)
        Logger().log(f"\n{ds_dict}")
