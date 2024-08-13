
"""This example demonstrates running a benchmarks set of tests against any llmware model in HuggingFace
    https://huggingface.co/llmware

    Usage: You can pass in a model name:
        python llmware_model_fast_start.py llmware/bling-1b-0.1
    If you do not specify a model you will be prompted to pick one

    This example uses the RAG Benchmark test set, which can be pulled down from the LLMWare repository on
    Huggingface at: www.huggingface.co/llmware/rag_instruct_benchmark_tester, or by using the
     datasets library, which can be installed with:

     `pip3 install datasets`

"""

import re
import sys
import time
import torch
from huggingface_hub import hf_api, ModelCard
from transformers import AutoModelForCausalLM, AutoTokenizer

# The datasets package is not installed automatically by llmware
try:
    from datasets import load_dataset
except ImportError:
    raise ImportError ("This example requires the 'datasets' Python package. "
                       "You can install it with 'pip3 install datasets'")


# Query HuggingFace and get the llmware models.  Return the the components of a table: headers and data
def get_llmware_models():
    table_headers=['','MODEL','DETAILS']
    table_data=[]

    models = hf_api.list_models(author="llmware")
    sorted_models = sorted(models, key=lambda x: x.id)
    
    for i, model in enumerate(sorted_models):
        model_card_content = ModelCard.load(model.id).content
        match = re.search(r"Model type:\*\* (.+?)\n", model_card_content)  # Get type from a line like this:  - **Model type:** GPTNeoX instruct-trained decoder
        model_type = ""
        if match:
            model_type = match.group(1).strip()
        model_details = f"{model_type} ({model.downloads} downloads)"
        table_data.append([i+1, model.id, model_details])

    return table_headers, table_data


def print_llmware_models():

    table_headers, table_data = get_llmware_models()

    print(table_headers[0], "\t\t", table_headers[1], "\t\t", table_headers[2])
    for row in table_data:
        print(row[0], "\t\t", row[1], "\t\t", row[2])


def prompt_user_for_model_selection(prompt=None):

    table_headers, table_data = get_llmware_models()

    print(table_headers[0], "\t\t", table_headers[1], "\t\t", table_headers[2])
    for row in table_data:
        print(row[0], "\t\t", row[1], "\t\t", row[2])

    num_models = len(table_data)

    if prompt is None:
        prompt = f"\nSelect a model (1-{num_models}): "
    while True:
        try:
            user_input = input(prompt)
            user_integer = int(user_input)
            if user_integer not in range(1,num_models+1):
                continue        
            return table_data[user_integer-1][1]
        except ValueError:
            print("That's not an integer. Please try again.")
    return None


# Pull a 200 question RAG benchmark test dataset from llmware HuggingFace repo
def load_rag_benchmark_tester_dataset():

    dataset_name = "llmware/rag_instruct_benchmark_tester"
    print(f"\n > Loading RAG dataset '{dataset_name}'...")
    dataset = load_dataset(dataset_name)

    test_set = []
    for i, samples in enumerate(dataset["train"]):
        test_set.append(samples)

    return test_set


# Run the benchmark test
def run_test(model_name, test_dataset):
 
    # Load the model and tokenizer
    print(f"\n > Loading model '{model_name}'") 
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if torch.cuda.is_available():
        model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True, torch_dtype="auto")
    else:
        model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
    model.to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    print(f"\n > Running RAG Benchmark Test against '{model_name}' - 200 questions")  
    # Run each test
    for i, entry in enumerate(test_dataset):

        start_time = time.time()

        # Create and tokenize a prompt
        # Note: in our testing, the dragon-yi model performs better with a trailing "\n" at end of prompt
        new_prompt = "<human>: " + entry["context"] + "\n" + entry["query"] + "\n" + "<bot>:" + "\n"
        inputs = tokenizer(new_prompt, return_tensors="pt")
        start_of_output = len(inputs.input_ids[0])

        # Call model.generate()
        #  Note: temperature: set at 0.3 for consistency of output
        #        max_new_tokens: set at 100 - may prematurely stop a few of the summaries
        outputs = model.generate(
            inputs.input_ids.to(device),
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=True,
            temperature=0.3,
            max_new_tokens=100,
            )

        output_only = tokenizer.decode(outputs[0][start_of_output:],skip_special_tokens=True)

        # quick/optional post-processing clean-up of potential fine-tuning artifacts

        eot = output_only.find("<|endoftext|>")
        if eot > -1:
            output_only = output_only[:eot]

        bot = output_only.find("<bot>:")
        if bot > -1:
            output_only = output_only[bot+len("<bot>:"):]

        # Print results
        time_taken = round(time.time() - start_time, 2)
        print("\n")
        print(f"{i+1}. llm_response - {output_only}")
        print(f"{i+1}. gold_answer - {entry['answer']}")
        print(f"{i+1}. time_taken - {time_taken}")

    return 0


if __name__ == "__main__":

    # Prompt user to get model if not passed in as an argument
    if len(sys.argv) > 1:
        selected_model = sys.argv[1]
    else:
        selected_model = prompt_user_for_model_selection()
    test_dataset = load_rag_benchmark_tester_dataset()
    output = run_test(selected_model,test_dataset)
