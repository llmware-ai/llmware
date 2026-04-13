
""" This example shows an end-to-end processing of Master Services Agreements (MSAs) - including the parsing and
text chunking of the documents with document filtering to rapidly identify the "MSA" agreements from a large
batch of contract documents, using queries to extract source materials, using a locally-running GPU to review and
answer the key questions, with evidence checking, and output for final human review.

    The example uses a quantized 6B parameter model running on a local machine.

    Note: this example tracks the example #6 in the Fast Start.

"""

import os

from llmware.setup import Setup
from llmware.library import Library
from llmware.prompts import Prompt, HumanInTheLoop
from llmware.retrieval import Query
from llmware.configs import LLMWareConfig


def msa_processing():

    local_path = Setup().load_sample_files()
    agreements_path = os.path.join(local_path, "AgreementsLarge")

    #   create a library with all of the Agreements (~80 contracts)
    msa_lib = Library().create_new_library("msa_lib503_635")
    msa_lib.add_files(agreements_path)

    #   find the "master service agreements" (MSA)
    q = Query(msa_lib)
    query = "master services agreement"
    results = q.text_search_by_page(query, page_num=1, results_only=False)

    #   results_only = False will return a dictionary with 4 keys:  {"query", "results", "doc_ID", "file_source"}
    msa_docs = results["file_source"]

    #   load prompt/llm locally
    model_name = "llmware/dragon-yi-6b-gguf"
    prompter = Prompt().load_model(model_name)

    #   analyze each MSA - "query" & "llm prompt"
    for i, docs in enumerate(msa_docs):

        print("\n")
        print (i+1, "Reviewing MSA - ", docs)

        #   look for the termination provisions in each document
        doc_filter = {"file_source": [docs]}
        termination_provisions = q.text_query_with_document_filter("termination", doc_filter)

        #   package the provisions as a source to a prompt
        sources = prompter.add_source_query_results(termination_provisions)

        print("update: sources - ", sources)

        #   call the LLM and ask our question
        response = prompter.prompt_with_source("What is the notice for termination for convenience?")

        #   post processing fact checking
        stats = prompter.evidence_comparison_stats(response)
        ev_source = prompter.evidence_check_sources(response)

        for i, resp in enumerate(response):
            print("update: llm response - ", resp)
            print("update: compare with evidence- ", stats[i]["comparison_stats"])
            print("update: sources - ", ev_source[i]["source_review"])

        prompter.clear_source_materials()

    # Save jsonl report with full transaction history to /prompt_history folder
    print("\nupdate: prompt state saved at: ", os.path.join(LLMWareConfig.get_prompt_path(),prompter.prompt_id))

    prompter.save_state()

    # Generate CSV report for easy Human review in Excel
    csv_output = HumanInTheLoop(prompter).export_current_interaction_to_csv()

    print("\nupdate: csv output for human review - ", csv_output)

    return 0


if __name__ == "__main__":

    m = msa_processing()
