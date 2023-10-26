
import os
import time
import json
from werkzeug.utils import secure_filename

from llmware.models import ModelCatalog
from llmware.prompts import Prompt
from llmware.setup import Setup
from llmware.configs import LLMWareConfig
from llmware.util import Datasets


def contract_analysis_w_fact_checking (model_name, from_hf=False):

    # my contracts folder path
    contracts_path = "/local/path/to/samples/agreements/executive_employment_agreements/"

    if from_hf:
        # local cpu open source model
        prompter = Prompt().load_model(model_name,from_hf=True)
    else:
        # e.g., 'gpt-4'
        prompter = Prompt().load_model(model_name)

    # low temperature setting for RAG retrieval
    # prompter.llm_model.temperature = 0.3

    research = {"topic": "base salary", "prompt": "What is the executive's base salary?"}

    for i, contract in enumerate(os.listdir(contracts_path)):

        print("\nAnalyzing Contract - ", str(i+1), contract)
        print("Question: ", research["prompt"])

        # contract is parsed, text-chunked, and then filtered by "base salary'
        source = prompter.add_source_document(contracts_path, contract, query=research["topic"])

        # calling the LLM with 'source' information from the contract automatically packaged into the prompt
        responses = prompter.prompt_with_source(research["prompt"], prompt_name="just_the_facts", temperature=0.3)

        # review_output = prompter.quality_check_reviewer(responses)

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
    print("\nupdate: prompt state saved at: ", os.path.join(LLMWareConfig.get_prompt_path(),prompter.prompt_id))

    prompter.save_state()
    
    # Optional - builds a dataset from prompt history that is 'model-training-ready'
    ds = Datasets().build_gen_ds_from_prompt_history(prompt_wrapper="human_bot")

    return 0


# note: stable-lm model requires "trust_remote_code=True"
hf_model_list = ["llmware/bling-1b-0.1", "llmware/bling-1.4b-0.1", "llmware/bling-falcon-1b-0.1",
              "llmware/bling-sheared-llama-2.7b-0.1", "llmware/bling-sheared-llama-1.3b-0.1",
              "llmware/bling-red-pajamas-3b-0.1", "llmware/bling-stable-lm-3b-4e1t-0.1"]

# to use gpt-4
# contract_analysis_on_laptop("gpt-4")

# to use huggingface local cpu model
contract_analysis_w_fact_checking(hf_model_list[0], from_hf=True)

