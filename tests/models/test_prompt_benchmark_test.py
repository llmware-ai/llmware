"""This runs a benchmark test dataset against a series of prompts.  It can be used to test any model type for
longer running series of prompts, as well as the fact-checking capability.

This test uses the RAG Benchmark test set, which can be pulled down from the LLMWare repository on
Huggingface at: www.huggingface.co/llmware/rag_instruct_benchmark_tester, or by using the
datasets library, which can be installed with:

 `pip3 install datasets`
"""

import time
import random
import logging
import numpy as np
import matplotlib.pyplot as plt
from llmware.prompts import Prompt

# The datasets package is not installed automatically by llmware
try:
    from datasets import load_dataset
except ImportError:
    raise ImportError("This test requires the 'datasets' Python package. "
                      "You can install it with 'pip3 install datasets'")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_rag_benchmark_tester_dataset():
    """Loads benchmark dataset used in the prompt test."""
    dataset_name = "llmware/rag_instruct_benchmark_tester"
    logging.info(f"Loading RAG dataset '{dataset_name}'...")
    dataset = load_dataset(dataset_name)

    test_set = []
    for i, samples in enumerate(dataset["train"]):
        test_set.append(samples)

    return test_set

def load_models(models):
    """Load a list of models dynamically."""
    for model in models:
        try:
            logging.info(f"Loading model '{model}'")
            yield Prompt().load_model(model)
        except Exception as e:
            logging.error(f"Failed to load model '{model}': {e}")

def test_prompt_rag_benchmark(selected_test_models):
    test_dataset = load_rag_benchmark_tester_dataset()

    # Randomly select one model from the list
    r = random.randint(0, len(selected_test_models) - 1)
    model_name = selected_test_models[r]

    logging.info(f"Selected model: {model_name}")
    prompter = next(load_models([model_name]))

    logging.info(f"Running RAG Benchmark Test against '{model_name}' - 200 questions")
    results = []
    for i, entry in enumerate(test_dataset):
        try:
            start_time = time.time()

            prompt = entry["query"]
            context = entry["context"]
            response = prompter.prompt_main(prompt, context=context, prompt_name="default_with_context", temperature=0.3)

            assert response is not None

            # Print results
            time_taken = round(time.time() - start_time, 2)
            logging.info(f"{i + 1}. llm_response - {response['llm_response']}")
            logging.info(f"{i + 1}. gold_answer - {entry['answer']}")
            logging.info(f"{i + 1}. time_taken - {time_taken}")

            # Fact checking
            fc = prompter.evidence_check_numbers(response)
            sc = prompter.evidence_comparison_stats(response)
            sr = prompter.evidence_check_sources(response)

            for fc_entry in fc:
                for f, facts in enumerate(fc_entry["fact_check"]):
                    logging.info(f"{i + 1}. fact_check - {f} {facts}")

            for sc_entry in sc:
                logging.info(f"{i + 1}. comparison_stats - {sc_entry['comparison_stats']}")

            for sr_entry in sr:
                for s, source in enumerate(sr_entry["source_review"]):
                    logging.info(f"{i + 1}. source - {s} {source}")

            results.append({
                "llm_response": response["llm_response"],
                "gold_answer": entry["answer"],
                "time_taken": time_taken,
                "fact_check": fc,
                "comparison_stats": sc,
                "source_review": sr
            })

        except Exception as e:
            logging.error(f"Error processing entry {i}: {e}")

    # Performance metrics
    total_time = sum(result["time_taken"] for result in results)
    average_time = total_time / len(results) if results else 0
    logging.info(f"Total time taken: {total_time} seconds")
    logging.info(f"Average time per question: {average_time} seconds")

    # Visualization
    time_taken_list = [result["time_taken"] for result in results]
    plt.plot(range(1, len(time_taken_list) + 1), time_taken_list, marker='o')
    plt.xlabel('Question Number')
    plt.ylabel('Time Taken (seconds)')
    plt.title('Time Taken per Question')
    plt.show()

    return results

# Example usage
if __name__ == "__main__":
    selected_test_models = [
        "llmware/bling-1b-0.1", "llmware/bling-1.4b-0.1", "llmware/bling-falcon-1b-0.1",
        "llmware/bling-tiny-llama-v0", "bling-phi-3-gguf", "bling-answer-tool",
        "dragon-yi-answer-tool", "dragon-llama-answer-tool", "dragon-mistral-answer-tool"
    ]
    test_prompt_rag_benchmark(selected_test_models)
