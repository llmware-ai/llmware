
import os

from llmware.library import Library
from llmware.util import Datasets


def test_ds_lookup_by_name(my_test_library):

    lib = Library().load_library(my_test_library)

    ds = Datasets(library=lib)

    print("update: available dataset types: ", ds.dataset_available_types)

    # *** NOTE: changed optional parameter "prompt_wrapping" to "prompt_wrapper" to conform with Prompt Catalog ***

    # lookup dataset by name with new 'self-describing' dataset card
    for i, entry in enumerate(ds.dataset_available_types):
        ds_card = ds.get_dataset_card(entry)
        print("update: dataset card - ", i, ds_card)

    # build selected dataset by name
    ds_dict = ds.build_ds_by_name("build_text_ds")

    print("ds dict - ", ds_dict)

    # iterate thru all datasets in one shot
    for i, entry in enumerate(ds.dataset_available_types):

        # note: depending upon library/account set up - possible for empty datasets and/or potentially errors
        ds_dict = ds.build_ds_by_name(entry)

    return 0
