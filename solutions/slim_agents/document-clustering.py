
"""This example demonstrates the use of LLM function calls to perform document clustering and
    automated classification of different parts of a document.  """

from llmware.parsers import Parser
from llmware.agents import LLMfx
from llmware.setup import Setup

import os


def document_clustering_example ():

    samples_fp = Setup().load_sample_files(over_write=True)
    agreements_fp = os.path.join(samples_fp, "Agreements")
    agreement_files = os.listdir(agreements_fp)

    if len(agreement_files) == 0:
        print("something went wrong")
        return -1

    # parsing the first file (could be random) found in the os.listdir in the Agreements sample folder
    contract_chunks = Parser().parse_one_pdf(agreements_fp,agreement_files[0])

    #   create a LLMfx object
    agent = LLMfx()

    #   there are ~65-70 contract_chunks in ~15 page contract - feel free to slice (faster demo), or the whole thing
    agent.load_work(contract_chunks[0:5])

    agent.load_tool_list(["topics","tags", "ner"])

    while True:
        agent.exec_multitool_function_call(["topics", "tags","ner"])

        if not agent.increment_work_iteration():
            break

    agent.show_report()

    agent.activity_summary()

    # uncomment this to see a full view of all of the responses
    """
    for i, entries in enumerate(agent.response_list):
        print("response_list: ", i, entries)
    """

    return agent.response_list


if __name__ == "__main__":

    analysis= document_clustering_example()



