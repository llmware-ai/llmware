

import os
import re
import time
import json
from werkzeug.utils import secure_filename

from llmware.models import ModelCatalog
from llmware.prompts import Prompt
from llmware.setup import Setup
from llmware.configs import LLMWareConfig


# SAMPLE SCRIPT #1 - Contract Analysis on Laptop, using BLING "CPU" model
#   -- easy to "swap" between HF model and GPT-4 or any other model for comparison
#   -- evaluate effectiveness of BLING models for basic contract analysis

def contract_analysis_on_laptop (model_name, from_hf=False):

    # my contracts folder path
    contracts_path = "/path/to/sample/agreement/exec_employment_agreements/"

    # query list
    query_list = {"executive employment agreement": "What are the name of the two parties?",
                  "base salary": "What is the executive's base salary?",
                  "governing law": "What is the governing law?"}

    if from_hf:
        # local cpu open source model
        prompter = Prompt().load_model(model_name,from_hf=True)
    else:
        # e.g., 'gpt-4'
        prompter = Prompt().load_model(model_name)

    for i, contract in enumerate(os.listdir(contracts_path)):

        print("\nAnalyzing contract: ", str(i+1), contract)

        for key, value in query_list.items():

            # contract is parsed, text-chunked, and then filtered by topic key
            source = prompter.add_source_document(contracts_path, contract, query=key)

            # calling the LLM with 'source' information from the contract automatically packaged into the prompt
            responses = prompter.prompt_with_source(value, prompt_name="just_the_facts", temperature=0.3)

            for r, response in enumerate(responses):
                print("LLM Response - ", key, re.sub("[\n]"," ", response["llm_response"]))

            # We're done with this contract, clear the source from the prompt
            prompter.clear_source_materials()

    # Save jsonl report to jsonl to /prompt_history folder
    print("\nupdate: prompt state saved at: ", os.path.join(LLMWareConfig.get_prompt_path(),prompter.prompt_id))

    prompter.save_state()

    return 0


# note:  stable-lm model will require hf config "trust_remote_code=True"
hf_model_list = ["llmware/bling-1b-0.1", "llmware/bling-1.4b-0.1", "llmware/bling-falcon-1b-0.1",
              "llmware/bling-sheared-llama-2.7b-0.1", "llmware/bling-sheared-llama-1.3b-0.1",
              "llmware/bling-red-pajamas-3b-0.1", "llmware/bling-stable-lm-3b-4e1t-0.1"]


# use huggingface local cpu model
bling_model = hf_model_list[0]

contract_analysis_on_laptop(bling_model, from_hf=True)

