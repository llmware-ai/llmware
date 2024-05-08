
"""This example demonstrates running a benchmarks set of tests against llmware DRAGON models
    https://huggingface.co/collections/llmware/dragon-models-65552d7648093c3f6e35d1bf
    The model loading and interaction is handled with the llmware Prompt class which provides additional
    capabilities like evidence checking

        This example uses the RAG Benchmark test set, which can be pulled down from the LLMWare repository on
    Huggingface at: www.huggingface.co/llmware/rag_instruct_benchmark_tester, or by using the
     datasets library, which can be installed with:

     `pip3 install datasets`

"""

import time
from llmware.prompts import Prompt

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
def run_test(model_name, prompt_list):

    print(f"\n > Loading model '{model_name}'") 
    prompter = Prompt().load_model(model_name)

    print(f"\n > Running RAG Benchmark Test against '{model_name}' - 200 questions")
    for i, entry in enumerate(prompt_list):

        start_time = time.time()

        prompt = entry["query"]
        context = entry["context"]
        response = prompter.prompt_main(prompt,context=context,prompt_name="default_with_context", temperature=0.3)

        # Print results
        time_taken = round(time.time() - start_time, 2)
        print("\n")
        print(f"{i+1}. llm_response - {response['llm_response']}")
        print(f"{i+1}. gold_answer - {entry['answer']}")
        print(f"{i+1}. time_taken - {time_taken}")

        # Fact checking
        fc = prompter.evidence_check_numbers(response)
        sc = prompter.evidence_comparison_stats(response)
        sr = prompter.evidence_check_sources(response)
        for fc_entry in fc:
            for f, facts in enumerate(fc_entry["fact_check"]):
                print(f"{i+1}. fact_check - {f} {facts}")

        for sc_entry in sc:
            print(f"{i+1}. comparison_stats - {sc_entry['comparison_stats']}")
       
        for sr_entry in sr:
            for s, source in enumerate(sr_entry["source_review"]):
                print(f"{i+1}. source - {s} {source}")

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

    # Pick a model - note: if running on laptop/CPU, select a bling model
    model_name = dragon_models[0]
    output = run_test(model_name, test_dataset)

