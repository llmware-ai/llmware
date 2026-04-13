
""" This example shows a complex multi-part research analysis.  In this example, we will:

    1.  Build a "research" library.
    2.  Query the research library to identify topics of interest.
    3.  Create an agent with several analytical tools: sentiment, emotions, topic, entities analysis
    4.  Pass the results of our query to the agent to conduct multifaceted analysis.
    5.  Apply a top-level filter ('sentiment') on the results from the query
    6.  For any of the passages with negative sentiment, we will run a follow-up set of analyses.
    7.  Finally, we will assemble the follow-up analysis into a list of detailed reports.
"""

import os
import shutil

from llmware.agents import LLMfx
from llmware.library import Library
from llmware.retrieval import Query
from llmware.configs import LLMWareConfig
from llmware.setup import Setup


def multistep_analysis():

    """ In this example, our objective is to research Microsoft history and rivalry in the 1980s with IBM. """

    #   step 1 - assemble source documents and create library

    print("update: Starting example - agent-multistep-analysis")

    #   note:  lines 38-49 attempt to automatically pull sample document into local path
    #   depending upon permissions in your environment, you may need to set up directly
    #   if you pull down the samples files with Setup().load_sample_files(), in the Books folder,
    #   you will find the source: "Bill-Gates-Biography.pdf"
    #   if you have pulled sample documents in the past, then to update to latest: set over_write=True

    print("update: Loading sample files")

    sample_files_path = Setup().load_sample_files(over_write=False)
    bill_gates_bio = "Bill-Gates-Biography.pdf"
    path_to_bill_gates_bio = os.path.join(sample_files_path, "Books", bill_gates_bio)

    microsoft_folder = os.path.join(LLMWareConfig().get_tmp_path(), "example_microsoft")

    print("update: attempting to create source input folder at path: ", microsoft_folder)

    if not os.path.exists(microsoft_folder):
        os.mkdir(microsoft_folder)
        os.chmod(microsoft_folder, 0o777)
        shutil.copy(path_to_bill_gates_bio,os.path.join(microsoft_folder, bill_gates_bio))

    #   create library
    print("update: creating library and parsing source document")

    LLMWareConfig().set_active_db("sqlite")
    my_lib = Library().create_new_library("microsoft_history_0210_1")
    my_lib.add_files(microsoft_folder)

    #   run our first query - "ibm"
    query = "ibm"
    search_results = Query(my_lib).text_query(query)
    print(f"update: executing query to filter to key passages - {query} - results found - {len(search_results)}")

    #   create an agent and load several tools that we will be using
    agent = LLMfx()
    agent.load_tool_list(["sentiment", "emotions", "topic", "tags", "ner", "answer"])

    #   load the search results into the agent's work queue
    agent.load_work(search_results)

    while True:

        agent.sentiment()

        if not agent.increment_work_iteration():
            break

    #   analyze sections where the sentiment on ibm was negative
    follow_up_list = agent.follow_up_list(key="sentiment", value="negative")

    for job_index in follow_up_list:

        # follow-up 'deep dive' on selected text that references ibm negatively
        agent.set_work_iteration(job_index)
        agent.exec_multitool_function_call(["tags", "emotions", "topics", "ner"])
        agent.answer("What is a brief summary?", key="summary")

    my_report = agent.show_report(follow_up_list)

    activity_summary = agent.activity_summary()

    for entries in my_report:
        print("my report entries: ", entries)

    return my_report


if __name__ == "__main__":

    multistep_analysis()


