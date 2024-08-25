
""" This example shows how to run the RAG benchmark test against a selected model in the Model Catalog, and
generate a json test report. """

import os
import json
import time

from llmware.prompts import Prompt
from llmware.configs import LLMWareConfig

from datasets import load_dataset


def load_rag_benchmark_tester_dataset():

    """ Pulls the standard 200 question RAG benchmark test from llmware Huggingface repository.  """

    dataset_name = "llmware/rag_instruct_benchmark_tester"
    print(f"\n > Loading RAG dataset '{dataset_name}'...")
    dataset = load_dataset(dataset_name)

    test_set = []
    for i, samples in enumerate(dataset["train"]):
        test_set.append(samples)

    return test_set


def model_test_run_general(model_name, prompt_list, save_fp=None, test_name_base=None):

    #   use llmware_path if no path provided

    if not save_fp:
        save_fp = LLMWareConfig().get_llmware_path()

    if not test_name_base:
        test_name_base = model_name

    # run direct inference on model
    print("\nupdate: Starting Generative Instruct Custom Fine-tuned Test")

    t1 = time.time()

    prompter = Prompt().load_model(model_name, temperature=0.0, sample=False, max_output=100)

    total_response_output = []
    answer_sheet = []

    for i, entries in enumerate(prompt_list):

        prompt = entries["query"]
        context = entries["context"]
        answer = ""

        if "answer" in entries:
            answer = entries["answer"]

        output = prompter.prompt_main(prompt,context=context,prompt_name="default_with_context")

        print("\nupdate: model inference output - ", i, output["llm_response"])
        print("update: gold_answer              - ", i, answer)

        core_output = {"number": i,
                       "llm_response": output["llm_response"],
                       "gold_answer": answer,
                       "prompt": prompt,
                       "usage": output["usage"]}

        answer_only = {"number": i, "llm_response": output["llm_response"],
                       "gold_answer": answer}

        total_response_output.append(core_output)
        answer_sheet.append(answer_only)

    t2 = time.time()

    print("update: total processing time: ", t2-t1)

    test_fn = test_name_base + "_core_rag_test.jsonl"
    f_out = open(os.path.join(save_fp, test_fn), "w")

    for entry in total_response_output:
        jsonl_row = json.dumps(entry)
        f_out.write(jsonl_row)
        f_out.write("\n")

    f_out.close()

    answer_sheet_fn = test_name_base + "_answer_sheet.jsonl"
    f_out = open(os.path.join(save_fp, answer_sheet_fn), "w")

    for entry in answer_sheet:
        jsonl_row = json.dumps(entry)
        f_out.write(jsonl_row)
        f_out.write("\n")

    f_out.close()

    return total_response_output


if __name__ == "__main__":

    model_name = "bling-phi-3.5-gguf"

    core_test_set = load_rag_benchmark_tester_dataset()

    output = model_test_run_general(model_name, core_test_set)
