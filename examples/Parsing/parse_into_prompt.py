
""" This example demonstrates how to parse a document 'in-flight' as part of a Prompt using "Prompt with Sources"

    1.  Load sample documents
    2.  Create a Prompt object
    3.  Load a locally-run BLING model (may take a few minutes to download the first time from HuggingFace)
    4.  Add Document as Source to Prompt
        -- this will automatically parse the source document, text chunk, and package into prompt context window
        -- optional query filter to narrow the list of text chunks packaged into the source
    5.  Invoke .prompt_with_sources method
        -- this will take the packaged source, and run inference on the LLM
"""


import os

from llmware.prompts import Prompt
from llmware.setup import Setup


def prompt_source (model_name):

    print(f"\nExample:  Parse and Filter Documents Directly in Prompt to LLM")

    #   load the llmware sample files
    print (f"\nstep 1 - loading the llmware sample files")
    sample_files_path = Setup().load_sample_files()
    contracts_path = os.path.join(sample_files_path,"Agreements")

    #   load bling model which will be used for the inference (will run on local laptop CPU)
    #   --note:  typically requires 16 GB laptop RAM
    print (f"step 2 - loading model {model_name}")

    #   create prompt object
    prompter = Prompt()
    prompter.load_model(model_name)

    #   this is the question that we will ask to each document
    research = {"topic": "base salary", "prompt": "What is the executive's base salary?"}

    for i, contract in enumerate(os.listdir(contracts_path)):

        #   (optional) safety check to exclude Mac-specific file artifact
        if contract != ".DS_Store":

            print("\nAnalyzing Contract - ", str( i +1), contract)
            print("Question: ", research["prompt"])

            # contract is parsed, text-chunked, and then filtered by "base salary'
            #   --note: query is optional - if no query, then entire document will be returned and added as source
            source = prompter.add_source_document(contracts_path, contract, query=research["topic"])

            # take a look at the created source
            print("Source created from document: ", source)

            # calling the LLM with 'source' information from the contract automatically packaged into the prompt
            responses = prompter.prompt_with_source(research["prompt"], prompt_name="default_with_context", temperature=0.3)

            for r, response in enumerate(responses):
                print("\nLLM Response: ", response["llm_response"])

            # We're done with this contract, clear the source from the prompt
            #   -- note: if looking to aggregate or keep 'running' source, then do not clear
            prompter.clear_source_materials()

    return 0


if __name__ == "__main__":

    model_name = "llmware/bling-1b-0.1"
    prompt_source(model_name)


