
"""This runs a benchmark test dataset against a series of prompts.  It can be used to test any model type for
    longer running series of prompts, as well as the fact-checking capability.

    This test uses the RAG Benchmark test set, which can be pulled down from the LLMWare repository on
    Huggingface at: www.huggingface.co/llmware/rag_instruct_benchmark_tester, or by using the
    datasets library, which can be installed with:

     `pip3 install datasets`
 """


import time
import random

from llmware.prompts import Prompt

# The datasets package is not installed automatically by llmware
try:
    from datasets import load_dataset
except ImportError:
    raise ImportError ("This test requires the 'datasets' Python package. "
                       "You can install it with 'pip3 install datasets'")



def load_rag_benchmark_tester_dataset():

    """ Loads benchmark dataset used in the prompt test. """

    dataset_name = "llmware/rag_instruct_benchmark_tester"
    print(f"\n > Loading RAG dataset '{dataset_name}'...")
    dataset = load_dataset(dataset_name)

    test_set = []
    for i, samples in enumerate(dataset["train"]):
        test_set.append(samples)

    return test_set


# Run the benchmark test
def test_prompt_rag_benchmark():

    test_dataset = load_rag_benchmark_tester_dataset()

    # SELECTED MODELS

    selected_test_models = ["llmware/bling-1b-0.1", "llmware/bling-1.4b-0.1",  "llmware/bling-falcon-1b-0.1",
                            "llmware/bling-tiny-llama-v0",
                            "bling-phi-3-gguf", "bling-answer-tool", "dragon-yi-answer-tool",
                            "dragon-llama-answer-tool", "dragon-mistral-answer-tool"]

    # randomly select one model from the list
    r = random.randint(0,len(selected_test_models)-1)

    model_name = selected_test_models[r]

    print(f"\n > Loading model '{model_name}'")
    prompter = Prompt().load_model(model_name)

    print(f"\n > Running RAG Benchmark Test against '{model_name}' - 200 questions")
    for i, entry in enumerate(test_dataset):

        start_time = time.time()

        prompt = entry["query"]
        context = entry["context"]
        response = prompter.prompt_main(prompt, context=context, prompt_name="default_with_context", temperature=0.3)

        assert response is not None

        # Print results
        time_taken = round(time.time() - start_time, 2)
        print("\n")
        print(f"{i + 1}. llm_response - {response['llm_response']}")
        print(f"{i + 1}. gold_answer - {entry['answer']}")
        print(f"{i + 1}. time_taken - {time_taken}")

        # Fact checking
        fc = prompter.evidence_check_numbers(response)
        sc = prompter.evidence_comparison_stats(response)
        sr = prompter.evidence_check_sources(response)

        for fc_entry in fc:
            for f, facts in enumerate(fc_entry["fact_check"]):
                print(f"{i + 1}. fact_check - {f} {facts}")

        for sc_entry in sc:
            print(f"{i + 1}. comparison_stats - {sc_entry['comparison_stats']}")

        for sr_entry in sr:
            for s, source in enumerate(sr_entry["source_review"]):
                print(f"{i + 1}. source - {s} {source}")

    return 0


