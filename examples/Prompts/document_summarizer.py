
"""This Example shows a packaged 'document_summarizer' prompt
#   1.  Example # 1 - summarizing a document directly from a file path and file name
#   2.  Example # 2 - select a filename from a library to summarize
#   3.  Note:  plug in any supported LLM at the bottom of the script
"""

import os

from llmware.prompts import Prompt
from llmware.setup import Setup


def test_summarize_document(model_name):

    # pull a sample document (or substitute a file_path and file_name of your own)
    sample_files_path = Setup().load_sample_files(over_write=False)
    fp = os.path.join(sample_files_path, "SmallLibrary")

    # sample file name from small library
    # fn = "N2126108.pdf"
    # fn = "N2137825.pdf"
    fn = "Jd-Salinger-Biography.docx"

    # note: when loading model, context window is automatically set based on model
    prompter = Prompt().load_model(model_name)

    # note: set the expected output len in terms of tokens
    prompter.llm_max_output_len = 250

    # note: the process can potentially take 30-60 seconds, depending upon of documents
    #   --helpful to turn logging to INFO setting to see progress update

    # optional parameters:  'query' - will select among blocks with the query term
    #                       'key_issue' - will pass a question to the model to 'focus' the summary
    #                       'max_batch_cap' - caps the number of batches sent to the model
    #                       'text_only' - returns just the summary text aggregated

    summary = prompter.summarize_document(fp,fn,query=None, text_only=True, max_batch_cap=10, key_issue=None)

    print("update: summary output_text - ", summary)

    return summary


def test_summarize_document_from_library(model_name):

    from llmware.library import Library
    lib = Library().create_new_library("lib_small_doc_summarizer_1")
    sample_files_path = Setup().load_sample_files(over_write=False)
    ingestion_folder_path = os.path.join(sample_files_path, "SmallLibrary")
    parsing_output = lib.add_files(ingestion_folder_path)
    fn = "N2126108.pdf"

    prompter = Prompt().load_model(model_name)
    prompter.llm_max_output_len = 300

    # note: will accept either a 'doc_id' parameter or a 'file_source' name
    summary = prompter.summarize_document_from_library(lib,filename=fn)

    print("update: summary - output_text - ", summary)

    return summary


if __name__ == "__main__":

    #   Update these values with your own API Keys by setting os.environ vars:
    #
    #   to use OPENAI (e.g., 'gpt-3.5-turbo' or 'gpt-4')
    #       os.environ["USER_MANAGED_OPENAI_API_KEY"] = "<insert-your-key>"
    #       llm_model = "gpt-3.5-turbo"
    #
    #   to use Anthropic (e.g., "claude-instant-v1")
    #       os.environ["USER_MANAGED_ANTHROPIC_API_KEY"] = "<insert-your-key>"
    #

    #   note: summarization results will be better with larger models - using 1b here as example for quick run
    llm_model = "llmware/bling-1b-0.1"

    print(f"\nExample: Summarize Documents\n")

    #   example 1 - pass a filepath and filename, and it will be summarized directly
    summary_direct = test_summarize_document(llm_model)

    #   example 2 - create library, identify a filename from the library, and it will be summarized
    summary_library = test_summarize_document_from_library(llm_model)



