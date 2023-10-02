''' This example demonstrates using llmware's bling model: https://huggingface.co/llmware/bling-1.4b-0.1
    BLING ("Best Little Instruction-following No-GPU-required") models are fine-tuned with distilled high-quality custom instruct datasets.
    They are targeted at a specific subset of instruct tasks with the objective of providing a high-quality Instruct model that is 'inference-ready' 
    on a CPU laptop even without using any advanced quantization optimizations.
'''

import os
import torch
from llmware.configs import LLMWareConfig
from llmware.prompts import Prompt
from llmware.models import ModelCatalog

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
except ImportError:
    raise ImportError (
        "This example requires classes from the 'transformers' Python package" 
        "You can install it with 'pip install transformers'"
    )

# Bling models published to date:
bling_models = ['llmware/bling-1b-0.1','llmware/bling-1.4b-0.1']

def use_llmware_bling():

    # Load a llmware BLING model from HuggingFace
    hf_model_name = "llmware/bling-1.4b-0.1"
    print (f"\n > Loading model '{hf_model_name}'from HuggingFace...")
    custom_hf_model = AutoModelForCausalLM.from_pretrained(hf_model_name)
    hf_tokenizer = AutoTokenizer.from_pretrained(hf_model_name)

    # Bring the model into llmware
    bling_model = ModelCatalog().load_hf_generative_model(custom_hf_model, hf_tokenizer, 
                                                          instruction_following=False, prompt_wrapper="human_bot")

    # Setup a varity of test prompts with contexts
    prompt_list = [

        {"query":   "What is the CEO's salary?",
        "context":  "The CEO has a salary of $350,000.  The CFO has a salary of $285,000."},

        {"query":   "What is the stock price on Thursday?",
        "context":  "The stock was trading at $33 on Thursday, and is now trading at $36 on Friday."},

        {"query":   "What is Bob's age?",
        "context":  "John is 32 years old.   Margaret is 46 years old.   Bob is 61 years old."},

        {"query":   "What is the company's address?",
        "context":  "The company's headquarters are located at: 555 California Street, San Francisco, California 94123."},

        {"query":   "When was Biden inaugurated?",
        "context":  "Joe Biden's tenure as the 46th president of the United States began with "
                    "his inauguration on January 20, 2021. Biden, a Democrat from Delaware who "
                    "previously served as vice president under Barack Obama, "
                    "took office following his victory in the 2020 presidential election over "
                    "Republican incumbent president Donald Trump. Upon his inauguration, he "
                    "became the oldest president in American history."},

        {"query":   "Who was Biden's opponent in the 2020 presidential election?",
        "context":  "Joe Biden's tenure as the 46th president of the United States began with "
                    "his inauguration on January 20, 2021. Biden, a Democrat from Delaware who "
                    "previously served as vice president under Barack Obama, "
                    "took office following his victory in the 2020 presidential election over "
                    "Republican incumbent president and opponent Donald Trump. Upon his inauguration, he "
                    "became the oldest president in American history."},

        {"query":   "What is a list of the top summary points?",
        "context":  "Joe Biden's tenure as the 46th president of the United States began with "
                    "his inauguration on January 20, 2021. Biden, a Democrat from Delaware who "
                    "previously served as vice president under Barack Obama, "
                    "took office following his victory in the 2020 presidential election over "
                    "Republican incumbent president Donald Trump. Upon his inauguration, he "
                    "became the oldest president in American history."},

        {"query":   "Who refused to acknowledge Biden as the winner of the election?",
        "context":  "Though Biden was generally acknowledged as the winner, "
                    "General Services Administration head Emily W. Murphy "
                    "initially refused to begin the transition to the president-elect, "
                    "thereby denying funds and office space to his team. "
                    "On November 23, after Michigan certified its results, Murphy "
                    "issued the letter of ascertainment, granting the Biden transition "
                    "team access to federal funds and resources for an orderly transition. "
                    "Two days after becoming the projected winner of the 2020 election, "
                    "Biden announced the formation of a task force to advise him on the "
                    "COVID-19 pandemic during the transition, co-chaired by former "
                    "Surgeon General Vivek Murthy, former FDA commissioner David A. Kessler, "
                    "and Yale University's Marcella Nunez-Smith.On January 5, 2021, "
                    "the Democratic Party won control of the United States Senate, "
                    "effective January 20, as a result of electoral victories in "
                    "Georgia by Jon Ossoff in a runoff election for a six-year term "
                    "and Raphael Warnock in a special runoff election for a two-year term. "
                    "President-elect Biden had supported and campaigned for both "
                    "candidates prior to the runoff elections on January 5.On January 6, "
                    "a mob of thousands of Trump supporters violently stormed the Capitol "
                    "in the hope of overturning Biden's election, forcing Congress to "
                    "evacuate during the counting of the Electoral College votes. More "
                    "than 26,000 National Guard members were deployed to the capital "
                    "for the inauguration, with thousands remaining into the spring. "},

        {"query":   "What is the name of the Company?",
        "context":  "THIS EXECUTIVE EMPLOYMENT AGREEMENT (this “Agreement”) is entered "
                    "into this 2nd day of April, 2012, by and between Aphrodite Apollo "
                    "(“Executive”) and TestCo Software, Inc. (the “Company” or “Employer”), "
                    "and shall become effective upon Executive’s commencement of employment "
                    "(the “Effective Date”) which is expected to commence on April 16, 2012. "
                    "The Company and Executive agree that unless Executive has commenced "
                    "employment with the Company as of April 16, 2012 (or such later date as "
                    "agreed by each of the Company and Executive) this Agreement shall be "
                    "null and void and of no further effect."},

        {"query":   "What are the names of the two parties?",
        "context":  "THIS EXECUTIVE EMPLOYMENT AGREEMENT (this “Agreement”) is entered "
                    "into this 2nd day of April, 2012, by and between Aphrodite Apollo "
                    "(“Executive”) and TestCo Software, Inc. (the “Company” or “Employer”), "
                    "and shall become effective upon Executive’s commencement of employment "
                    "(the “Effective Date”) which is expected to commence on April 16, 2012. "
                    "The Company and Executive agree that unless Executive has commenced "
                    "employment with the Company as of April 16, 2012 (or such later date as "
                    "agreed by each of the Company and Executive) this Agreement shall be "
                    "null and void and of no further effect."},

        {"query":   "When will employment start?",
        "context":  "THIS EXECUTIVE EMPLOYMENT AGREEMENT (this “Agreement”) is entered "
                    "into this 2nd day of April, 2012, by and between Aphrodite Apollo "
                    "(“Executive”) and TestCo Software, Inc. (the “Company” or “Employer”), "
                    "and shall become effective upon Executive’s commencement of employment "
                    "(the “Effective Date”) which is expected to commence on April 16, 2012. "
                    "The Company and Executive agree that unless Executive has commenced "
                    "employment with the Company as of April 16, 2012 (or such later date as "
                    "agreed by each of the Company and Executive) this Agreement shall be "
                    "null and void and of no further effect."}
    ]

    # Iterate through all the prompts and interact with the model
    for i, entries in enumerate(prompt_list):
        prompt = entries["query"]
        context = entries["context"]
        output = bling_model.inference(prompt, add_context=context, add_prompt_engineering=True)["llm_response"]
        print(f"\nPrompt: {prompt}\nResponse:\n{output.strip()}")
     
    # You can also integrate the model into an llmware Prompt
    prompt = "What is my age?"
    context = "I am 33 years old"
    prompter = Prompt(llm_model=custom_hf_model, tokenizer=hf_tokenizer, from_hf=True)
    output = prompter.prompt_main(prompt, context=context)["llm_response"]
    print(f"\nPrompt: {prompt}\nResponse:\n{output.strip()}")

use_llmware_bling()
