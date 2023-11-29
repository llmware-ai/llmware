''' This example demonstrates running RAG Instruct benchmark test datasets for any model:
      - load two "RAG" test datasets from Huggingface
      - load model locally, and run inferences
      - output is saved as json report
'''
import os
import time
import json


from werkzeug.utils import secure_filename
from llmware.prompts import Prompt

try:
    from datasets import load_dataset
except ImportError:
    raise ImportError (
        "This example requires classes from the 'datasets' Python package. " 
        "You can install it with 'pip install datasets'"
    )

def rag_instruct_tester(model_name, from_hf=False, save_path=None):

    dataset1_name = "llmware/rag_instruct_test_dataset_0.1"
    dataset2_name = "llmware/rag_instruct_test_dataset2_financial_0.1"

    # load first dataset - pull from huggingface repo
    print(f"\n > Loading Dataset: {dataset1_name}...")
    ds1 = load_dataset(dataset1_name)["test"]

    # load second dataset - pull from huggingface repo
    print(f"\n > Loading Dataset: {dataset2_name}...")
    ds2 = load_dataset(dataset2_name)["test"]

    # initiate Prompt object and load selected model
    print(f"\n > Loading Model: {model_name}...")
    prompter = Prompt().load_model(model_name, from_hf=from_hf)

    total_response_output = []
    t1 = time.time()

    # iterate thru both test datasets (100 samples X 2 = 200 total)
    test_ds = [ds1, ds2]

    print(f"\n > Starting Test for Model: {model_name}...")

    for ds in test_ds:

        for i, entries in enumerate(ds):

            output = prompter.prompt_main(entries["query"],context=entries["context"],
                                          prompt_name="default_with_context",temperature=0.3)

            print(f"\nTest #{i+1}")
            print(f"Query:        {entries['query']}")
            print(f"LLM response: {output['llm_response']}")
            print(f"Gold answer:  {entries['answer']}")
            print(f"Usage:        {output['usage']}")

            core_output = {"number": i,
                           "llm_response": output["llm_response"],
                           "gold_answer": entries["answer"],
                           "prompt": entries["query"],
                           "context": entries["context"],
                           "usage": output["usage"]}

            total_response_output.append(core_output)

    t2 = time.time()

    print(f"\nTotal processing time: {t2-t1} seconds")

    if save_path:
        fn = secure_filename(model_name) + "_rag_instruct_test.jsonl"
        f_out = open(os.path.join(save_path, fn), "w", encoding='utf-8')

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
