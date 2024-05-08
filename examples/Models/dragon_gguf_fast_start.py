
"""This example demonstrates running a 7B RAG-instruct fine-tuned DRAGON model locally on a laptop.

    This example uses the RAG Benchmark test set, which can be pulled down from the LLMWare repository on
    Huggingface at: www.huggingface.co/llmware/rag_instruct_benchmark_tester, or by using the
     datasets library, which can be installed with:

     `pip3 install datasets`

"""


import time
from llmware.prompts import Prompt
from llmware.exceptions import LLMWareException
from importlib import util
if not util.find_spec("datasets"):
    raise LLMWareException(message="\nto run this example, you need to install HuggingFace datasets:  "
                                    "`pip3 install datasets`")

try:
    from datasets import load_dataset
except:
    raise LLMWareException(message="Exception: datasets not found and required for example.")


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
        response = prompter.prompt_main(prompt, context=context, prompt_name="default_with_context", temperature=0.3)

        # Print results
        time_taken = round(time.time() - start_time, 2)
        print("\n")
        print(f"{i + 1}. llm_response - {response['llm_response']}")
        print(f"{i + 1}. gold_answer - {entry['answer']}")
        print(f"{i + 1}. time_taken - {time_taken}")

    return 0


if __name__ == "__main__":

    ds = load_rag_benchmark_tester_dataset()

    #   Supported Q4_K_M GGUF Dragon Models:
    #       -- llmware/dragon-yi-6b-gguf
    #       -- llmware/dragon-mistral-7b-gguf
    #       -- llmware/dragon-llama-7b-gguf

    model_name = "llmware/dragon-yi-6b-gguf"

    output = run_test(model_name,ds)
