
"""This example demonstrates what can be accomplished with llmware with no databases - all of these
#   examples run in-memory.  Note: for best results in some of the examples, you will need LLM API key.
"""

import json
import os
from llmware.parsers import Parser
from llmware.prompts import Prompt
from llmware.setup import Setup
from llmware.util import Datasets
from llmware.resources import PromptState
from llmware.models import PromptCatalog

# Iterate through and analyze the contracts in a folder 
def analyze_contracts_on_the_fly(model_name):

    # Load the llmware sample files
    print (f"\n > Loading the llmware sample files...")
    sample_files_path = Setup().load_sample_files()
    contracts_path = os.path.join(sample_files_path,"Agreements")

    # Create a Prompt instance)
    prompter = Prompt(save_state=True).load_model(model_name)
    
    # Iterate through contracts
    prompt_text = "What is the executive's annual base salary?"
    print (f"\n > Analyzing contracts with prompt: '{prompt_text}'")

    for i, contract in enumerate(os.listdir(contracts_path)):

        if contract != ".DS_Store":

            print (f"\n > Analyzing {contract}")

            # Add contract as a prompt source
            source = prompter.add_source_document(contracts_path, contract, query="base salary")

            # Prompt LLM and display response
            responses = prompter.prompt_with_source(prompt_text, prompt_name="number_or_none")
            for response in responses:
                print("LLM Response: " + response["llm_response"])

            # Fact check response and display result
            updated_responses = prompter.evidence_check_numbers(responses)
            for response in updated_responses:
                for fact_check in response["fact_check"]:
                    status = fact_check["status"]
                    text = fact_check["text"]
                    print(f"Fact Check: {status} -> {text}")

            # We're done with this contract, clear the source from the prompt
            prompter.clear_source_materials()

        # Save jsonl report to jsonl to /prompt_history folder
        prompter.save_state()

    return 0


# Use prompt history to easily create model-ready fine-tuning datasets 
def create_datasets_from_prompt_history(model_name):

    context = "Joe Biden is the 46th President of the United States.  He was born in Scranton, " \
              "Pennsylvania.  He served as Vice President from 2008 through 2016."

    # Create a Prompt
    prompter = Prompt(save_state=True).load_model(model_name)

    # Perform several prompts
    print (f"\n > Performing several prompts to populate the prompt state...")
    response = prompter.prompt_main(prompt="Who was the 46th president?", context=context)
    response = prompter.number_or_none(prompt="What year did Joe Biden start as vice president?", context=context)
    response = prompter.summarize_with_bullets(prompt="Who is Joe Biden?", context=context)

    # Create a Datasets object  
    datasets = Datasets()

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

    # Create dataset wrapped in "Chat GPT format" 
    print (f"\n > Creating a dataset from prompt history in HUMAN BOT format...")
    humanbot_dataset = datasets.build_gen_ds_from_prompt_history(prompt_wrapper="human_bot")
    print (f"\nThe dataset dict:\n{json.dumps(humanbot_dataset, indent=2)}")
    sample = datasets.get_dataset_sample(datasets.current_ds_name)
    print (f"\nRandom sample from the dataset:\n{json.dumps(sample, indent=2)}")

    return 0


# Parse files/content of various types
def parsing_with_no_library():

    # Load the llmware sample files
    print (f"\n > Loading the llmware sample files...")
    sample_files_path = Setup().load_sample_files()
   
    # Create a parser
    parser = Parser()

    # Parse PDF files
    print (f"\n > Parsing PDF files...")
    pdf_path = os.path.join(sample_files_path,"SmallLibrary")
    pdf_output = parser.parse_pdf(pdf_path, write_to_db=False, save_history=False)
    print(f"Running block count: {len(parser.parser_output)}")

    # Parse MS Office files
    print (f"\n > Parsing MS Office files...")
    office_path = os.path.join(sample_files_path,"SmallLibrary")
    office_output = parser.parse_office(office_path, write_to_db=False, save_history=False)
    print(f"Running block count: {len(parser.parser_output)}")

    # Parse website
    print (f"\n > Parsing Website...")
    website = "https://www.politico.com"
    website_output = parser.parse_website(website, write_to_db=False, save_history=False, get_links=False)
    print(f"Running block count: {len(parser.parser_output)}")

    # Parse AWS Transcribe transcripts
    print (f"\n > Parsing AWS Transcribe transcripts...")
    transcripts_path = os.path.join(sample_files_path,"AWS-Transcribe")
    transcripts_output = parser.parse_dialog(transcripts_path, write_to_db=False, save_history=False)
    print(f"Running block count: {len(parser.parser_output)}")

    # Save state
    print (f"\n > Saving parser state...")
    parser.save_state()
    parser_state_file = os.path.join(parser.parser_folder, "parser_job_" + parser.parser_job_id + ".jsonl")
    print(f"File: {parser_state_file}")

    return 0


# Parse an entire folder to json (import all supported file types)
def parse_all_to_json():

    # Load the llmware sample files
    print (f"\n > Loading the llmware sample files...")
    sample_files_path = Setup().load_sample_files()
    input_folder = os.path.join(sample_files_path,"SmallLibrary")

    # Create a parser
    parser = Parser()
    
    # Parse entire folder to json
    print (f"\n > Parsing folder: {input_folder}...")
    blocks  = parser.ingest_to_json(input_folder)
    print (f"Total Blocks: {len(parser.parser_output)}")
    print (f"Files Parsed:")
    for processed_file in blocks["processed_files"]:
        print(f"  - {processed_file}")

    return 0


# Try out all prompt instruction types
def try_all_prompt_instructions(model_name):

    test_sample = "Joseph Robinette Biden Jr. (  BY-dən; born November 20, 1942) is an American politician " \
                  "who is the 46th and current president of the United States. A member of the Democratic Party, " \
                  "he previously served as the 47th vice president from 2009 to 2017 under President Barack Obama " \
                  "and represented Delaware in the United States Senate from 1973 to 2009.  Born in Scranton, " \
                  "Pennsylvania, Biden moved with his family to Delaware in 1953. He studied at the University of " \
                  "Delaware before earning his law degree from Syracuse University.  He was elected to the New Castle " \
                  "County Council in 1970 and to the U.S. Senate in 1972. As a senator, Biden drafted and led the " \
                  "effort to pass the Violent Crime Control and Law Enforcement Act and the Violence Against Women " \
                  "Act; and oversaw six U.S. Supreme Court confirmation hearings, including the contentious hearings " \
                  "for Robert Bork and Clarence Thomas. Biden ran unsuccessfully for the Democratic presidential " \
                  "nomination in 1988 and 2008. In 2008, Barack Obama chose Biden as his running mate, and Biden " \
                  "was a close counselor to Obama during his two terms as vice president.In the 2020 presidential " \
                  "election, Biden and his running mate, Kamala Harris, defeated incumbents Donald Trump and " \
                  "Mike Pence. Taking office at age 78, Biden is the oldest president in U.S. history, the " \
                  "first to have a female vice president, and the first from Delaware. In 2021, he signed a " \
                  "bipartisan infrastructure bill, as well as a $1.9 trillion economic stimulus package in " \
                  "response to the COVID-19 pandemic and subsequent recession."

    test_sample_short = "Joe Biden is the 46th President of the United States.  He was born in Scranton, " \
                        "Pennsylvania.  He served as Vice President from 2008 through 2016."

    # Create a prompt
    prompter = Prompt(save_state=True).load_model(model_name)

    # Iterate through all prompt instructions and display the responses for the same prompt question
    prompt_question = "Who is Joe Biden?"
    print (f"\n > Running all available prompt instructions with provided context and asking '{prompt_question}'")
    for i, prompt in enumerate(PromptCatalog().list_all_prompts()):
        response = prompter.prompt_from_catalog(prompt_question, context=test_sample, prompt_name=prompt)["llm_response"]
        print(f"\n{i+1}. {prompt}\n{response}")

    return 0


# Use specific methods to invoke various prompt instructions
def use_specific_prompt_instructions(model_name):

    test_sample = "Joseph Robinette Biden Jr. (  BY-dən; born November 20, 1942) is an American politician " \
                  "who is the 46th and current president of the United States. A member of the Democratic Party, " \
                  "he previously served as the 47th vice president from 2009 to 2017 under President Barack Obama " \
                  "and represented Delaware in the United States Senate from 1973 to 2009.  Born in Scranton, " \
                  "Pennsylvania, Biden moved with his family to Delaware in 1953. He studied at the University of " \
                  "Delaware before earning his law degree from Syracuse University.  He was elected to the New Castle " \
                  "County Council in 1970 and to the U.S. Senate in 1972. As a senator, Biden drafted and led the " \
                  "effort to pass the Violent Crime Control and Law Enforcement Act and the Violence Against Women " \
                  "Act; and oversaw six U.S. Supreme Court confirmation hearings, including the contentious hearings " \
                  "for Robert Bork and Clarence Thomas. Biden ran unsuccessfully for the Democratic presidential " \
                  "nomination in 1988 and 2008. In 2008, Barack Obama chose Biden as his running mate, and Biden " \
                  "was a close counselor to Obama during his two terms as vice president.In the 2020 presidential " \
                  "election, Biden and his running mate, Kamala Harris, defeated incumbents Donald Trump and " \
                  "Mike Pence. Taking office at age 78, Biden is the oldest president in U.S. history, the " \
                  "first to have a female vice president, and the first from Delaware. In 2021, he signed a " \
                  "bipartisan infrastructure bill, as well as a $1.9 trillion economic stimulus package in " \
                  "response to the COVID-19 pandemic and subsequent recession."

    test_sample_short = "Joe Biden is the 46th President of the United States.  He was born in Scranton, " \
                        "Pennsylvania.  He served as Vice President from 2008 through 2016."

    # Create a prompt
    prompter = Prompt(save_state=True).load_model(model_name)

    print (f"\n > Running specific prompt instructions")

    # yes_no
    response = prompter.yes_or_no("Was Joe Biden born in Michigan?",test_sample_short)
    print("\nyes/no\n" + response["llm_response"])

    # summarize with bullets
    response = prompter.summarize_with_bullets("Who is Joe Biden?", test_sample, number_of_bullets=9)
    print("\nnumbered bullets\n" + response["llm_response"])

    # multiple choice
    prompt = "Where was Joe Biden born?"
    choice_list = ["Scranton, Pennsylvania", "Detroit, Michigan", "Cleveland, Ohio", "None of the Above"]
    response = prompter.multiple_choice(prompt,test_sample_short, choice_list)
    print("\nmultiple choice\n" + response["llm_response"])

    # xsummary
    response = prompter.xsummary(test_sample,number_of_words=20)
    print("\nxsummary\n" + response["llm_response"])
 
    # number_or_none
    prompt = "What is the stock price?"
    context = "The stock price is currently $15.50"
    response = prompter.number_or_none(prompt,context=context)
    print("\nnumber_or_none\n" + response["llm_response"])
 
    # completion
    response = prompter.completion("In the dark of the night, the man heard a noise and ...", temperature=1.0,
                                   target_len=200)
    print("\ncompletion\n" + response["llm_response"])

    # title generator
    response = prompter.title_generator_from_source("who is joe biden?", context=test_sample,title_only=True)
    print("\ntitle generator\n" + response)

    return 0


# Add your own custom prompt
def create_custom_prompt(model_name):

    test_sample_short = "Joe Biden is the 46th President of the United States.  He was born in Scranton, " \
                        "Pennsylvania.  He served as Vice President from 2008 through 2016."

    # Run Order List - How to construct the prompt
    run_order_list = ["blurb1", "$context", "blurb2", "$query", "instruction"]

    # Dictionary to use for the prompt
    my_prompt_dict = {"blurb1": "Please use the following materials- ",
                      "blurb2": "Please answer the following question - ",
                      "instruction": "In answering the question, please mention 'Lucy told you that'.",
                      "system_message": "You are a helpful assistant."}

    print (f"\n > Prompting LLM with a custom prompt (to add in the response that 'Lucy' was the source of the answer)")
    
    # Add the new custom prompt
    prompt_catalog = PromptCatalog()
    prompt_catalog.add_custom_prompt_card("my_prompt",run_order_list,my_prompt_dict)
 
    # Create a new prompt
    prompter = Prompt(save_state=True,prompt_catalog=prompt_catalog).load_model(model_name)

    # Prompt the LLM
    response = prompter.prompt_from_catalog("Where was Joe Biden born?",context=test_sample_short, prompt_name="my_prompt")
    print("\nLLM Response:\n" + response["llm_response"])


if __name__ == "__main__":

    #   to use openai or anthropic, update with your own api keys
    os.environ["USER_MANAGED_OPENAI_API_KEY"] = "<insert-your-key>"
    os.environ["USER_MANAGED_ANTHROPIC_API_KEY"] = "<insert-your-key>"

    #   for these first set of examples, feel free to use any model, including a local bling model

    model_name = "llmware/bling-1b-0.1"

    #   simple RAG use case all in memory with local LLM
    analyze_contracts_on_the_fly(model_name)

    #   creates dataset from prompt history
    create_datasets_from_prompt_history(model_name)

    #   parsing documents in memory
    parsing_with_no_library()

    #   parsing and exporting to json file
    parse_all_to_json()

    #   for the last set of examples, we would recommend using OpenAI, Anthropic or Google models for best results

    #   feel free to replace with any other model
    model_name = "gpt-3.5-turbo"

    #   shows the various prompt instructions in the prompt catalog and how to use
    try_all_prompt_instructions(model_name)

    #   shows specific prompt instructions
    use_specific_prompt_instructions(model_name)

    #   shows how to create and register a custom prompt in the prompt catalog
    create_custom_prompt(model_name)

