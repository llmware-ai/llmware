
""" This example illustrates the use of a reranker model to provide a fast, effective 'in-memory' semantic
similarity, replacing an explicit retrieval using either text or embedding from a vector db.

    This example uses a common pattern of trying to answer a specific factual question from a set of PDF documents.

    These are the key steps of the example:

    1.  Sample agreements are pulled from repo, cached locally, and then iterated.

    2.  Each PDF document (~10-15 pages) is parsed into text chunks in memory.
        -- this generates a list of dictionaries, with each dictionary entry consisting of the "text" and metadata

    3.  The reranker model takes as inference input both the query and the full set of text chunks.

    4.  The reranker model returns as output a sorted list of the (top) original text chunk dictionaries

    5.  The top text chunks are added as source to the prompt

    6.  Prompt_with_Sources run with the original query and the concatenated source to answer the question.


"""

import os

from llmware.parsers import Parser
from llmware.models import ModelCatalog
from llmware.prompts import Prompt
from llmware.setup import Setup


def rag_in_memory_with_reranker():

    """ Executes a rag process in memory using semantic reranker model and bling-phi-3-gguf to answer the question. """

    query = "What is the annual rate of the executive's base salary?"

    sample_files_path = Setup().load_sample_files(over_write=False)
    contracts_path = os.path.join(sample_files_path, "Agreements")

    files = os.listdir(contracts_path)

    #   will use two models for the example - reranker + a 'question-answer' rag llm
    reranker_model = ModelCatalog().load_model("jina-reranker-turbo")
    prompter = Prompt().load_model("bling-phi-3-gguf", temperature=0.0, sample=False)

    for i, doc in enumerate(files):

        if doc.endswith(".pdf"):

            print("\nPROCESSING: ", i, doc)

            parser_output = Parser().parse_one(contracts_path,doc,save_history=False)

            output = reranker_model.inference(query,parser_output,top_n=10, relevance_threshold=0.25)

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
