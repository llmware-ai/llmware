
""" This Example shows a packaged 'document_summarizer' prompt using the slim-summary-tool. It shows a variety of
techniques to summarize documents generally larger than a LLM context window, and how to assemble multiple source
batches from the document, as well as using a 'query' and 'topic' to focus on specific segments of the document. """

import os

from llmware.prompts import Prompt
from llmware.setup import Setup


def test_summarize_document(example="jd salinger"):

    # pull a sample document (or substitute a file_path and file_name of your own)
    sample_files_path = Setup().load_sample_files(over_write=False)

    topic = None
    query = None
    fp = None
    fn = None

    if example not in ["jd salinger", "employment terms", "just the comp", "un resolutions"]:
        print ("not found example")
        return []

    if example == "jd salinger":
        fp = os.path.join(sample_files_path, "SmallLibrary")
        fn = "Jd-Salinger-Biography.docx"
        topic = "jd salinger"
        query = None

    if example == "employment terms":
        fp = os.path.join(sample_files_path, "Agreements")
        fn = "Athena EXECUTIVE EMPLOYMENT AGREEMENT.pdf"
        topic = "executive compensation terms"
        query = None

    if example == "just the comp":
        fp = os.path.join(sample_files_path, "Agreements")
        fn = "Athena EXECUTIVE EMPLOYMENT AGREEMENT.pdf"
        topic = "executive compensation terms"
        query = "base salary"

    if example == "un resolutions":
        fp = os.path.join(sample_files_path, "SmallLibrary")
        fn = "N2126108.pdf"
        # fn = "N2137825.pdf"
        topic = "key points"
        query = None

    # optional parameters:  'query' - will select among blocks with the query term
    #                       'topic' - will pass a topic/issue as the parameter to the model to 'focus' the summary
    #                       'max_batch_cap' - caps the number of batches sent to the model
    #                       'text_only' - returns just the summary text aggregated

    kp = Prompt().summarize_document_fc(fp, fn, topic=topic, query=query, text_only=True, max_batch_cap=15)

    print(f"\nDocument summary completed - {len(kp)} Points")
    for i, points in enumerate(kp):
        print(i, points)

    return 0


if __name__ == "__main__":

    print(f"\nExample: Summarize Documents\n")

    #   4 examples - ["jd salinger", "employment terms", "just the comp", "un resolutions"]
    #   -- "jd salinger" - summarizes key points about jd salinger from short biography document
    #   -- "employment terms" - summarizes the executive compensation terms across 15 page document
    #   -- "just the comp" - queries to find subset of document and then summarizes the key terms
    #   -- "un resolutions" - summarizes the un resolutions document

    summary_direct = test_summarize_document(example="employment terms")


