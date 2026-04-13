
"""This example demonstrates a basic contract analysis workflow run entirely on on a laptop
    using a new Bling-Phi-3 RAG-finetuned small specialized instruct model.
"""

import os
import re
from llmware.prompts import Prompt, HumanInTheLoop
from llmware.setup import Setup
from llmware.configs import LLMWareConfig


def contract_analysis_on_laptop (model_name):

    # Load the llmware sample files
    print (f"\n > Loading the llmware sample files...")
    sample_files_path = Setup().load_sample_files()
    contracts_path = os.path.join(sample_files_path,"Agreements")
 
    # query list
    query_list = {"executive employment agreement": "What are the name of the two parties?",
                  "base salary": "What is the executive's base salary?",
                  "vacation": "How many vacation days will the executive receive?"}

    print (f"\n > Loading model {model_name}...")

    prompter = Prompt().load_model(model_name, temperature=0.0, sample=False)

    for i, contract in enumerate(os.listdir(contracts_path)):

        # exclude potential mac os created file artifact in folder path
        if contract != ".DS_Store":
            
            print("\nAnalyzing contract: ", str(i+1), contract)

            print("LLM Responses:")
            
            for key, value in query_list.items():

                # contract is parsed, text-chunked, and then filtered by topic key
                source = prompter.add_source_document(contracts_path, contract, query=key)

                # calling the LLM with 'source' information from the contract automatically packaged into the prompt
                responses = prompter.prompt_with_source(value, prompt_name="default_with_context")

                for r, response in enumerate(responses):
                    print(key, ":", re.sub("[\n]"," ", response["llm_response"]).strip())

                # We're done with this contract, clear the source from the prompt
                prompter.clear_source_materials()

    # Save jsonl report to jsonl to /prompt_history folder
    print("\nPrompt state saved at: ", os.path.join(LLMWareConfig.get_prompt_path(),prompter.prompt_id))
    prompter.save_state()

    #Save csv report that includes the model, response, prompt, and evidence for human-in-the-loop review
    csv_output = HumanInTheLoop(prompter).export_current_interaction_to_csv()
    print("csv output - ", csv_output)


if __name__ == "__main__":

    #   use new bling phi-3 model quantized and running on local cpu
    model = "bling-phi-3-gguf"

    contract_analysis_on_laptop(model)

