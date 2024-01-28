
""""This example demonstrates:
      prompt_with_sources - powerful abstraction to integrate various knowledge sources into a prompt
"""


import os
from llmware.prompts import Prompt
from llmware.setup import Setup
from llmware.models import PromptCatalog
from llmware.library import Library
from llmware.retrieval import Query


def prompt_with_sources(model_name, library_name):

    print(f"Example - prompt_with_sources - attaching several different knowledge sources to a Prompt directly.")

    library = Library().create_new_library(library_name)

    sample_files_path = Setup().load_sample_files(over_write=False)

    ingestion_folder_path = os.path.join(sample_files_path, "Agreements")
    parsing_output = library.add_files(ingestion_folder_path)

    local_file = "Apollo EXECUTIVE EMPLOYMENT AGREEMENT.pdf"

    prompter = Prompt().load_model(model_name)

    sources2 = prompter.add_source_document(ingestion_folder_path, local_file, query="base salary")

    prompt = "What is the base salary amount?"
    prompt_instruction="default_with_context"
    response = prompter.prompt_with_source(prompt=prompt, prompt_name=prompt_instruction)[0]["llm_response"]
    print (f"- Context: {local_file}\n- Prompt: {prompt}\n- LLM Response:\n{response}")
    prompter.clear_source_materials()

    prompt = "Was Barack Obama the Prime Minister of Canada?"
    wiki_topic = "Barack Obama"
    prompt_instruction = "yes_no"
    sources3 = prompter.add_source_wikipedia(wiki_topic, article_count=1)
    response = prompter.prompt_with_source(prompt=prompt, prompt_name=prompt_instruction)[0]["llm_response"]
    print (f"- Context: {local_file}\n- Prompt: {prompt}\n- LLM Response:\n{response}")
    prompter.clear_source_materials()

    query_results = Query(library).text_query("base salary")
    prompt = "What is the annual rate of the base salary?"
    sources4 = prompter.add_source_query_results(query_results)
    response = prompter.prompt_with_source(prompt=prompt, prompt_name=prompt_instruction)[0]["llm_response"]
    print(f"- Context: {local_file}\n- Prompt: {prompt}\n- LLM Response:\n{response}")
    prompter.clear_source_materials()

    return 0


if __name__ == "__main__":

    #   to use API-based model for this example, set API keys in os.environ variable
    #   e.g., see example: set_model_api_keys.py
    #   e.g., os.environ["USER_MANAGED_OPENAI_API_KEY"] = "<insert-your-api-key>"

    #   this model is a placeholder which will run on local laptop - swap out for higher accuracy, larger models
    model_name = "llmware/bling-1b-0.1"

    library_name = "lib_prompt_with_sources_1"

    prompt_with_sources(model_name,library_name)

