
import os
import time
import json
from werkzeug.utils import secure_filename

from llmware.prompts import Prompt


#   SAMPLE SCRIPT - run RAG Instruct benchmark test datasets for any model
#   -- load two "RAG" test datasets from Huggingface
#   -- load model locally, and run inferences
#   -- output saved as json report

def rag_instruct_tester(model_name, from_hf=False, save_path=None):

    # huggingface datasets import -> fetches the rag_instruct datasets
    from datasets import load_dataset

    # load first dataset - pull from huggingface repo
    rag_instruct_tester_ds1 = "llmware/rag_instruct_test_dataset_0.1"
    print("update: loading test dataset 1 - ", rag_instruct_tester_ds1)
    ds1 = load_dataset(rag_instruct_tester_ds1)["test"]

    # load second dataset - pull from huggingface repo
    rag_instruct_tester_ds2 = "llmware/rag_instruct_test_dataset2_financial_0.1"
    print("update: loading test dataset 2 - ", rag_instruct_tester_ds2)
    ds2 = load_dataset(rag_instruct_tester_ds2)["test"]

    # initiate Prompt object and load selected model
    prompter = Prompt().load_model(model_name, from_hf=from_hf)

    total_response_output = []

    t1 = time.time()

    # iterate thru both test datasets (100 samples X 2 = 200 total)
    test_ds = [ds1, ds2]

    print("\nStarting Test for Model: ", model_name)

    for ds in test_ds:

        for i, entries in enumerate(ds):

            output = prompter.prompt_main(entries["query"],context=entries["context"],prompt_name="default_with_context",
                                          temperature=0.3)

            print("\n")
            print("update: test - {} -    ".format(str(i)), entries["query"])
            print("update: LLM response:  ", output["llm_response"])
            print("update: Gold answer:   ", entries["answer"])
            print("update: Usage:         ", output["usage"])

            core_output = {"number": i,
                           "llm_response": output["llm_response"],
                           "gold_answer": entries["answer"],
                           "prompt": entries["query"],
                           "context": entries["context"],
                           "usage": output["usage"]}

            total_response_output.append(core_output)

    t2 = time.time()

    print("update: total processing time: ", t2-t1)

    if save_path:
        fn = secure_filename(model_name) + "_rag_instruct_test.jsonl"
        f_out = open(os.path.join(save_path, fn), "w")

        for entry in total_response_output:
            jsonl_row = json.dumps(entry)
            f_out.write(jsonl_row)
            f_out.write("\n")

        f_out.close()

    return total_response_output


# designed for bling models - but can used with any LLM to evaluate on common RAG tasks

hf_model_list = ["llmware/bling-1b-0.1", "llmware/bling-1.4b-0.1", "llmware/bling-falcon-1b-0.1",
              "llmware/bling-sheared-llama-2.7b-0.1", "llmware/bling-sheared-llama-1.3b-0.1",
              "llmware/bling-red-pajamas-3b-0.1", "llmware/bling-stable-lm-3b-4e1t-0.1"]

model_name = "llmware/bling-sheared-llama-1.3b-0.1"

rag_instruct_tester(model_name, from_hf=True, save_path="/local/save/path/")
