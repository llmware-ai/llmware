import os
import sys
from llmware.library import Library
from llmware.prompts import Prompt
from llmware.setup import Setup

sys.path.append(os.path.join(os.path.dirname(__file__),".."))
from utils import Logger

def test_summarize_document():

    # Setup library
    sample_files_path = Setup().load_sample_files()
    file_path = os.path.join(sample_files_path,"SmallLibrary")
    file_name = "N2137825.pdf"

    # note: when loading model, context window is automatically set based on model
    prompter = Prompt().load_model("claude-instant-v1")
    prompter.llm_max_output_len = 250

    # note: the process can potentially take 30-60 seconds, depending upon of documents
    #   --helpful to turn logging to INFO setting to see progress update

    # optional parameters:  'query' - will select among blocks with the query term
    #                       'key_issue' - will pass a question to the model to 'focus' the summary
    #                       'max_batch_cap' - caps the number of batches sent to the model
    #                       'text_only' - returns just the summary text aggregated
    summary = prompter.summarize_document(file_path,file_name,query=None, text_only=True, max_batch_cap=10, key_issue=None)
    Logger().log(f"\nDocument Summary:\n{summary}")
    assert (len(summary) > 0)
 

def test_summarize_document_from_library():

    library = Library().create_new_library("test_doc_summary")
    sample_files_path = Setup().load_sample_files()
    file_path = os.path.join(sample_files_path,"SmallLibrary")
    library.add_files(file_path)
  
    prompter = Prompt().load_model("claude-instant-v1")
    prompter.llm_max_output_len = 300

    # note: will accept either a 'doc_id' parameter or a 'file_source' name
    summary = prompter.summarize_document_from_library(library,doc_id=1)

    Logger().log(f"\nDocument (from Library) Summary:\n{summary}")
    assert (len(summary) > 0)