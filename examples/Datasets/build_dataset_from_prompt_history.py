
"""This example shows how to automatically build an 'instruct' dataset from prompt state history"""

import json
import os
from llmware.prompts import Prompt
from llmware.dataset_tools import Datasets
from llmware.configs import LLMWareConfig


# Use prompt history to easily create model-ready fine-tuning datasets
def create_datasets_from_prompt_history(model_name):

    context = "Joe Biden is the 46th President of the United States.  He was born in Scranton, " \
              "Pennsylvania.  He served as Vice President from 2008 through 2016."

    # Create a Prompt
    prompter = Prompt(save_state=True)
    prompter.load_model(model_name)

    # Perform several prompts
    print (f"\n > Performing several prompts to populate the prompt state...")

    response = prompter.prompt_main("Who was the 46th president?", context=context,
                                    register_trx=True)

    response = prompter.prompt_main(prompt="What year did Joe Biden start as vice president?", context=context,
                                    register_trx=True)

    response = prompter.prompt_main(prompt="Who is Joe Biden?", context=context, register_trx=True)

    for i, entries in enumerate(prompter.interaction_history):
        print("update: interaction prompt history created: ", i, entries)

    prompter.save_state()

    # Create a Datasets object
    datasets = Datasets(testing_split=0.0, validation_split=0.0)

    # Create dataset wrapped in "Alpaca format"
    print (f"\n > Creating a dataset from prompt history in ALPACA format...")
    alpaca_dataset = datasets.build_gen_ds_from_prompt_history(prompt_wrapper="alpaca")
    print (f"\nThe dataset dict:\n{json.dumps(alpaca_dataset, indent=2)}")
    sample = datasets.get_dataset_sample(datasets.current_ds_name)
    print (f"\nRandom sample from the dataset:\n{json.dumps(sample, indent=2)}")

    # Create dataset wrapped in "Chat GPT format"
    print (f"\n > Creating a dataset from prompt history in CHAT GPT format...")
    chatgpt_dataset = datasets.build_gen_ds_from_prompt_history(prompt_wrapper="chat_gpt")
    print (f"\nThe dataset dict:\n{json.dumps(chatgpt_dataset, indent=2)}")
    sample = datasets.get_dataset_sample(datasets.current_ds_name)
    print (f"\nRandom sample from the dataset:\n{json.dumps(sample, indent=2)}")

    # Create dataset wrapped in "human_bot format"
    print (f"\n > Creating a dataset from prompt history in HUMAN BOT format...")
    humanbot_dataset = datasets.build_gen_ds_from_prompt_history(prompt_wrapper="human_bot")
    print (f"\nThe dataset dict:\n{json.dumps(humanbot_dataset, indent=2)}")
    sample = datasets.get_dataset_sample(datasets.current_ds_name)
    print (f"\nRandom sample from the dataset:\n{json.dumps(sample, indent=2)}")

    return 0


if __name__ == "__main__":

    LLMWareConfig().set_active_db("sqlite")

    model_name = "llmware/bling-1b-0.1"

    create_datasets_from_prompt_history(model_name)

