
"""This example demonstrates basic use of Prompts to start running inference in LLMWare workflows"""

import json
import os
from llmware.library import Library
from llmware.prompts import Prompt
from llmware.retrieval import Query
from llmware.setup import Setup
from llmware.util import PromptState, Datasets


# Demonstrate interacting with the prompts in a variety of ways
def prompt_operations(llm_model):

    # Create a new prompter with state persistence
    prompter = Prompt(save_state=True)

    # Capture the prompt_id (which can be used later to reload state)
    prompt_id = prompter.prompt_id

    # Load the model
    prompter.load_model(llm_model)

    # Define a list of prompts
    prompts = [
        {"query": "How old is Bob?", "context": "John is 43 years old.  Bob is 27 years old."},
        {"query": "When did COVID start?", "context": "COVID started in March of 2020 in most of the world."},
        {"query": "What is the current stock price?", "context": "The stock is trading at $26 today."},
        {"query": "When is the big game?", "context": "The big game will be played on November 14, 2023."},
        {"query": "What is the CFO's salary?", "context": "The CFO has a salary of $285,000."},
        {"query": "What grade is Michael in school?", "context": "Michael is starting 11th grade."}
        ]

    # Iterate through the prompt which will save each response dict in in the prompt_state    
    print (f"> Sending a series of prompts to {llm_model}...")

    for i, prompt in enumerate(prompts):
        print ("  - " + prompt["query"])
        response = prompter.prompt_main(prompt["query"],context=prompt["context"],register_trx=True)

        print(f"  -  LLM Responses: {response}")

    # Print how many interactions are now in the prompt history
    interaction_history = prompter.interaction_history
    print (f"> Prompt Interaction History now contains {len(interaction_history)} interactions")
    
    # Use the dialog_tracker to regenerate the conversation with the LLM
    print (f"> Reconstructed Dialog")
    dialog_history = prompter.dialog_tracker
    for i, conversation_turn in enumerate(dialog_history):
        print("  - ", i, "[user]: ", conversation_turn["user"])
        print("  - ", i, "[ bot]: ", conversation_turn["bot"])

    # Saving and clean the prompt state
    prompter.save_state()
    prompter.clear_history()

    # Print the number of interactions
    interaction_history = prompter.interaction_history
    print (f"> Prompt history has been cleared")
    print (f"> Prompt Interaction History now contains {len(interaction_history)} interactions")

    # Reload the prompt state using the prompt_id and print again the number of interactions
    prompter.load_state(prompt_id)
    interaction_history = prompter.interaction_history
    print (f"> The previous prompt state has been re-loaded")
    print (f"> Prompt Interaction History now contains {len(interaction_history)} interactions")

    # Generate a Promppt transaction report
    prompt_transaction_report = PromptState().generate_interaction_report([prompt_id])
    print (f"> A prompt transaction report has been generated: {prompt_transaction_report}")

    return 0


def prompt_with_sources_basic(model_name):

    print(f"Example - prompt_with_sources - attaching a file as a 'source' directly in a Prompt.")

    #   pulls down the sample files, including a specific agreement file
    sample_files_path = Setup().load_sample_files(over_write=False)
    fp = os.path.join(sample_files_path, "Agreements")

    local_file = "Apollo EXECUTIVE EMPLOYMENT AGREEMENT.pdf"

    prompter = Prompt().load_model(model_name)

    #   .add_source_document will do the following:
    #       1.  parse the file (any supported document type)
    #       2.  apply an optional query filter to reduce the text chunks to only those matching the query
    #       3.  batch according to the model context window, and make available for any future inferences

    sources = prompter.add_source_document(fp, local_file, query="base salary")

    prompt = "What is the base salary amount?"
    prompt_instruction = "default_with_context"
    response = prompter.prompt_with_source(prompt=prompt, prompt_name=prompt_instruction)

    print(f"LLM Response - {response}")

    response_display = response[0]["llm_response"]
    print (f"- Context: {local_file}\n- Prompt: {prompt}\n- LLM Response:\n{response_display}")

    prompter.clear_source_materials()

    return 0


if __name__ == "__main__":

    #   to use openai or anthropic, update with your own api keys
    os.environ["USER_MANAGED_OPENAI_API_KEY"] = "<insert-your-key>"
    os.environ["USER_MANAGED_ANTHROPIC_API_KEY"] = "<insert-your-key>"

    # if you don't have an API key available, you can use any of the BLING models and run locally
    #   e.g., llm_model = "llmware/bling-1b-0.1"

    model_name = "llmware/bling-1b-0.1"

    print(f"\nExample 1 - basic prompt options - packaging prompt, running inference and getting results\n")
    prompt_operations(model_name)

    print(f"\nExample 2 - intro to prompt_with_sources - adding a document source to a prompt\n")
    prompt_with_sources_basic(model_name)