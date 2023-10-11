
import os

from llmware.prompts import Prompt

import logging

logging.basicConfig(level=logging.INFO)


def test_summarize_document():

    fp = "/path/to/files/"

    # sample file name from UN docs
    fn = "N2126108.pdf"
    # fn = "Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.docx"

    # note: when loading model, context window is automatically set based on model
    prompter = Prompt().load_model("claude-instant-v1")

    # note: set the expected output len in terms of tokens
    prompter.llm_max_output_len = 250

    # note: the process can potentially take 30-60 seconds, depending upon of documents
    #   --helpful to turn logging to INFO setting to see progress update

    # optional parameters:  'query' - will select among blocks with the query term
    #                       'key_issue' - will pass a question to the model to 'focus' the summary
    #                       'max_batch_cap' - caps the number of batches sent to the model
    #                       'text_only' - returns just the summary text aggregated

    summary = prompter.summarize_document(fp,fn,query=None, text_only=True, max_batch_cap=10, key_issue=None)

    print("update: output_text - ", summary)

    return summary


# test_summarize_document()


def test_summarize_document_from_library():

    from llmware.library import Library

    lib = Library().load_library("contract_lib_0928_0")

    prompter = Prompt().load_model("claude-instant-v1")
    prompter.llm_max_output_len = 300

    # note: will accept either a 'doc_id' parameter or a 'file_source' name
    summary = prompter.summarize_document_from_library(lib,doc_id=1)

    print("update: output_text - ", summary)

    return summary


# test_summarize_document_from_library()


def test_updated_model_catalog_lookup():

    # in ModelCatalog().load_model -> will pull the context_window parameter from the model card
    #   ... and automatically load into the model before passing back

    from llmware.models import ModelCatalog
    model_list = ModelCatalog().list_generative_models()

    for i, model in enumerate(model_list):

        if model["model_name"] != "HF-Generative":

            # model "max_total_len" = full context window
            my_model = ModelCatalog().load_model(model["model_name"])
            print("update: model context loaded - ", my_model.max_total_len, model["context_window"], model["model_name"])

            # prompter looks at the 'input_total_len' parameter, generally set at 50% of the max_total_len
            prompter = Prompt().load_model(model["model_name"])
            print("update: prompter context window = 50% - ", prompter.context_window_size)

    return 0


# test_updated_model_catalog_lookup()
