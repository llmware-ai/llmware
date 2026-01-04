
""" onnx reranker model - this example shows how to use onnx reranker model -
    it is modeled directly off other reranker example in the repository -

    please note that you should import onnxruntime to run this example, e.g.,

    -- `pip install onnxruntime`

"""

import os

from llmware.parsers import Parser
from llmware.models import ModelCatalog
from llmware.prompts import Prompt
from llmware.setup import Setup

# models: jina-reranker-tiny-onnx, jina-reranker-turbo-onnx


def rag_in_memory_with_reranker():

    """ Executes a rag process in memory using semantic reranker model and bling-phi-3-gguf to answer the question. """

    query = "What is the annual rate of the executive's base salary?"

    sample_files_path = Setup().load_sample_files(over_write=False)
    contracts_path = os.path.join(sample_files_path, "Agreements")

    files = os.listdir(contracts_path)

    #   will use two models for the example - reranker + a 'question-answer' rag llm

    # use onnx reranker model
    reranker_model = ModelCatalog().load_model("jina-reranker-turbo-onnx")

    # use small gguf model - can substitute
    prompter = Prompt().load_model("bling-answer-tool", temperature=0.0, sample=False)

    for i, doc in enumerate(files):

        if doc.endswith(".pdf"):

            print("\nPROCESSING: ", i, doc)

            parser_output = Parser().parse_one(contracts_path,doc,save_history=False)

            output = reranker_model.rank(query,parser_output,top_n=10, relevance_threshold=0.25)

            use_top = 3
            if len(output) > use_top:
                output = output[0:use_top]

            for i, results in enumerate(output):
                print("semantic ranking results: ", i, results["rerank_score"], results["text"])

            sources = prompter.add_source_query_results(output)
            responses = prompter.prompt_with_source(query,prompt_name="default_with_context")

            for i, resp in enumerate(responses):
                print("\nllm answers: ", i, resp)

            prompter.clear_source_materials()

    return 0


if __name__ == "__main__":

    rag_in_memory_with_reranker()
