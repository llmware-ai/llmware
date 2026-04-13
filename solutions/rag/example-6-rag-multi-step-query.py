
"""     Fast Start Example #6 - RAG - Beyond the Basics

    This example builds upon examples #4 and #5 and demonstrates how to layer additional elements to
    improve the effectiveness of a RAG workflow over a larger set of documents-

    1.  Apply an initial filter across a batch of documents to identify a subset of documents of interest
    2.  Analyze the documents of interest to identify key provisions
    3.  Use fact-checking and post-processing to validate the accuracy of the LLM response
    4.  Write the output to JSON and CSV files for follow-up review and/or the next step in the workflow.

    For this example, we also recommend using a more sophisticated DRAGON model in GGUF format, which enables us
    to run 6-7B parameter models locally.

"""

import os

from llmware.setup import Setup
from llmware.library import Library
from llmware.prompts import Prompt, HumanInTheLoop
from llmware.retrieval import Query
from llmware.configs import LLMWareConfig


def msa_processing(library_name, llm_model_name):

    """ In this example, we will use the 'AgreementsLarge' sample files which consists of ~80 contracts.  We
    need to quickly identify the 'master service agreements' as we only want to analyze those contracts. """

    local_path = Setup().load_sample_files()
    agreements_path = os.path.join(local_path, "AgreementsLarge")

    #   create a library with all of the Agreements (~80 contracts)
    print(f"\nStarting:  Parsing 'AgreementsLarge' Folder")
    msa_lib = Library().create_new_library(library_name)
    msa_lib.add_files(agreements_path)

    #   find the "master service agreements" (MSA) - we know that 'master services agreement' will always
    #   be on the first page of the agreement, so we can use that as a good proxy for automatically filtering
    #   to our target set of documents

    print(f"\nCompleted Parsing - now, let's look for the 'master service agreements', e.g., 'msa'")

    q = Query(msa_lib)
    query = '"master services agreement"'
    results = q.text_search_by_page(query, page_num=1, results_only=False)

    #   results_only = False will return a dictionary with 4 keys:  {"query", "results", "doc_ID", "file_source"}
    msa_docs = results["file_source"]
    msa_doc_ids = results["doc_ID"]

    #   load prompt/llm locally
    prompter = Prompt().load_model(llm_model_name)

    print("update: identified the following msa doc id: ", msa_doc_ids)

    #   analyze each MSA - "query" & "llm prompt"
    for i, doc_id in enumerate(msa_doc_ids):

        print("\n")
        docs = msa_docs[i]
        if os.sep in docs:
            # handles difference in windows file formats vs. Mac/Linux
            docs = docs.split(os.sep)[-1]

        print (i+1, "Reviewing MSA - ", doc_id, docs)

        #   look for the termination provisions in each document
        doc_filter = {"doc_ID": [doc_id]}
        termination_provisions = q.text_query_with_document_filter("termination", doc_filter)

        #   package the provisions as a source to a prompt
        sources = prompter.add_source_query_results(termination_provisions)

        #   if you want to see more details about how the sources are packaged: uncomment this line-
        #   print("update: sources - ", sources)

        #   call the LLM and ask our question
        response = prompter.prompt_with_source("What is the notice for termination for convenience?")

        #   post processing fact checking
        stats = prompter.evidence_comparison_stats(response)
        ev_source = prompter.evidence_check_sources(response)

        for j, resp in enumerate(response):
            print("update: llm response - ", resp)
            print("update: compare with evidence- ", stats[j]["comparison_stats"])
            print("update: sources - ", ev_source[j]["source_review"])

        prompter.clear_source_materials()

    # Save jsonl report with full transaction history to /prompt_history folder
    print("\nupdate: Prompt state saved at: ", os.path.join(LLMWareConfig.get_prompt_path(),prompter.prompt_id))

    prompter.save_state()

    # Generate CSV report for easy Human review in Excel
    csv_output = HumanInTheLoop(prompter).export_current_interaction_to_csv()

    print("\nupdate: CSV output for human review - ", csv_output)

    return 0


if __name__ == "__main__":

    LLMWareConfig().set_active_db("sqlite")

    #   this is part of the DRAGON model series - RAG-fine-tuned fact-based Q&A model
    llm = "bling-phi-3-gguf"
    
    #   feel free to also try:  "dragon-yi-answer-tool" as a good substitute option

    m = msa_processing("example6_library", llm)

