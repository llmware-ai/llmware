
from llmware.prompts import Prompt


def load_rag_benchmark_tester_ds():

    # pull 200 question rag benchmark test dataset from LLMWare HuggingFace repo
    from datasets import load_dataset

    ds_name = "llmware/rag_instruct_benchmark_tester"

    dataset = load_dataset(ds_name)

    print("update: loading RAG Benchmark test dataset - ", dataset)

    test_set = []
    for i, samples in enumerate(dataset["train"]):
        test_set.append(samples)

        # to view test set samples
        # print("rag benchmark dataset test samples: ", i, samples)

    return test_set


def run_test(model_name, prompt_list):

    print("\nupdate: Starting RAG Benchmark Inference Test - ", model_name)

    # pull DRAGON / BLING model directly from catalog, e.g., no from_hf=True
    prompter = Prompt().load_model(model_name)

    for i, entries in enumerate(prompt_list):

        prompt = entries["query"]
        context = entries["context"]

        response = prompter.prompt_main(prompt,context=context,prompt_name="default_with_context", temperature=0.3)

        print("\nupdate: model inference output - ", i, response["llm_response"])
        print("update: gold_answer              - ", i, entries["answer"])

        fc = prompter.evidence_check_numbers(response)
        sc = prompter.evidence_comparison_stats(response)
        sr = prompter.evidence_check_sources(response)

        print("\nFact-Checking Tools")

        for entries in fc:
            for f, facts in enumerate(entries["fact_check"]):
                print("update: fact check - ", f, facts)

        for entries in sc:
            print("update: comparison stats - ", entries["comparison_stats"])

        for entries in sr:
            for s, sources in enumerate(entries["source_review"]):
                print("update: sources - ", s, sources)

    return 0


if __name__ == "__main__":

    core_test_set = load_rag_benchmark_tester_ds()

    # fastest, smallest cpu model (also least accurate)
    cpu_model_name = "llmware/bling-1b-0.1"

    # one of the 7 gpu dragon models
    gpu_model_name = "llmware/dragon-mistral-7b-v0"

    output = run_test(cpu_model_name, core_test_set)
