
""" This example demonstrates running a benchmarks set of tests against llmware DRAGON models
    https://huggingface.co/collections/llmware/dragon-models-65552d7648093c3f6e35d1bf

        This example uses the RAG Benchmark test set, which can be pulled down from the LLMWare repository on
    Huggingface at: www.huggingface.co/llmware/rag_instruct_benchmark_tester, or by using the
     datasets library, which can be installed with:

     `pip3 install datasets`

"""

import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# The datasets package is not installed automatically by llmware
try:
    from datasets import load_dataset
except ImportError:
    raise ImportError ("This example requires the 'datasets' Python package. "
                       "You can install it with 'pip3 install datasets'")


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

    # Get the benchmark dataset
    test_dataset = load_rag_benchmark_tester_dataset()

    # BLING MODELS
    bling_models = ["llmware/bling-1b-0.1", "llmware/bling-1.4b-0.1", "llmware/bling-falcon-1b-0.1",
                    "llmware/bling-cerebras-1.3b-0.1", "llmware/bling-sheared-llama-1.3b-0.1",
                    "llmware/bling-sheared-llama-2.7b-0.1", "llmware/bling-red-pajamas-3b-0.1",
                    "llmware/bling-stable-lm-3b-4e1t-v0"]

    # DRAGON MODELS
    dragon_models = ['llmware/dragon-yi-6b-v0', 'llmware/dragon-red-pajama-7b-v0', 'llmware/dragon-stablelm-7b-v0',
                     'llmware/dragon-deci-6b-v0', 'llmware/dragon-mistral-7b-v0','llmware/dragon-falcon-7b-v0',
                     'llmware/dragon-llama-7b-v0']

    # Pick a model: if running on CPU/laptop, select from bling_models list
    model_name = dragon_models[0]
    output = run_test(model_name,test_dataset)
