
""" This example demonstrates evidence and fact checking capabilities in the Prompt class. """

import os

from llmware.prompts import Prompt
from llmware.setup import Setup
from llmware.configs import LLMWareConfig
from llmware.dataset_tools import Datasets


def contract_analysis_with_fact_checking (model_name):

    # Load the llmware sample files
    print (f"\n > Loading the llmware sample files...")
    sample_files_path = Setup().load_sample_files()
    contracts_path = os.path.join(sample_files_path,"Agreements")

    print (f"\n > Loading model {model_name}...")

    prompter = Prompt().load_model(model_name, temperature=0.0, sample=False)

    research = {"topic": "base salary", "prompt": "What is the executive's base salary?"}

    for i, contract in enumerate(os.listdir(contracts_path)):

        print("\nAnalyzing Contract - ", str(i+1), contract)
        print("Question: ", research["prompt"])

        # contract is parsed, text-chunked, and then filtered by "base salary'
        source = prompter.add_source_document(contracts_path, contract, query=research["topic"])

        # calling the LLM with 'source' information from the contract automatically packaged into the prompt
        responses = prompter.prompt_with_source(research["prompt"], prompt_name="default_with_context")
        
        # run several fact checks
        ev_numbers = prompter.evidence_check_numbers(responses)
        ev_sources = prompter.evidence_check_sources(responses)
        ev_stats = prompter.evidence_comparison_stats(responses)
        z = prompter.classify_not_found_response(responses, parse_response=True, evidence_match=True,ask_the_model=False)

        for r, response in enumerate(responses):
            print("LLM Response: ", response["llm_response"])
            print("Numbers: ",  ev_numbers[r]["fact_check"])
            print("Sources: ", ev_sources[r]["source_review"])
            print("Stats: ", ev_stats[r]["comparison_stats"])
            print("Not Found Check: ", z[r])

            # We're done with this contract, clear the source from the prompt
            prompter.clear_source_materials()

    # Save jsonl report to jsonl to /prompt_history folder
    print("\nPrompt state saved at: ", os.path.join(LLMWareConfig.get_prompt_path(),prompter.prompt_id))
    prompter.save_state()
    
    # Optional - builds a dataset from prompt history that is 'model-training-ready'
    ds = Datasets().build_gen_ds_from_prompt_history(prompt_wrapper="human_bot")

    return 0


if __name__ == "__main__":

    hf_model_list = ["llmware/bling-1b-0.1",
                     "llmware/bling-1.4b-0.1",
                     "llmware/bling-falcon-1b-0.1",
                     "llmware/bling-sheared-llama-1.3b-0.1",
                     "bling-phi-3-gguf"]

    model_name = hf_model_list[0]

    # to use a 3rd party model, select model_name, e.g., "gpt-4"
    #   --if model requires an api_key, then it must be set as an os.environ variable
    #   --see example on 'set_model_api_keys.py'

    contract_analysis_with_fact_checking(model_name)


