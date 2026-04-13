
"""This example demonstrates how to parse a PDF document 'in-line' and integrate in memory directly into a
Prompt as a source of evidence for an LLM inference. """

import os
from llmware.prompts import Prompt
from llmware.setup import Setup


def prompt_with_sources (model_name):

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

    model_name = "llmware/bling-1b-0.1"

    print(f"\nExample - intro to prompt_with_sources - adding a document source to a prompt\n")

    prompt_with_sources (model_name)

