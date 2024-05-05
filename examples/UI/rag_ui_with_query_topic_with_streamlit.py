
""" This example shows how to build a simple UI RAG application for longer documents in which a retrieval query step
    is required to build a context from selected text chunks in the document.

    This example is build with a Streamlit UI. To run, it requires a separate `pip install streamlit`, and
    to execute the script, you should run from the command line with:

     `streamlit run using_with_streamlit_ui.py`

    For more information about Streamlit, check out their docs:  https://docs.streamlit.io/develop/tutorials

    To build out the application, you would replace the very simple 'text search' mechanism used below with
    techniques outlined in examples in Embeddings and Retrieval.

"""


import os
import streamlit as st

from llmware.prompts import Prompt
from llmware.setup import Setup

# st.set_page_config(layout="wide")


def simple_analyzer_with_topic_query ():

    st.title("Simple RAG Analyzer with Focusing Query")

    prompter = Prompt()

    sample_files_path = Setup().load_sample_files(over_write=False)
    doc_path = os.path.join(sample_files_path, "Agreements")

    files = os.listdir(doc_path)
    file_name = st.selectbox("Choose an Agreement", files)

    #   ** topic_query ** = this is a proxy for a more complex focusing retrieval strategy to target only a
    #   specific part of the document, rather then the whole document
    #   in this case, this will run a 'text match' search against the topic query to reduce the
    #   text chunks reviewed in trying to answer the question

    topic_query = st.text_area("Filtering Topic (hint: 'vacation')")

    #   ** prompt_text ** - this is the question that will be passed to the LLM
    prompt_text = st.text_area("Question (hint: 'how many vacation days will the executive receive'")

    model_name = st.selectbox("Choose a model for answering questions", ["bling-phi-3-gguf",
                                                                         "bling-tiny-llama-1b",
                                                                         "bling-stablelm-3b-tool",
                                                                         "llama-3-instruct-bartowski-gguf",
                                                                         "dragon-llama-answer-tool"])

    if st.button("Run Analysis"):

        if file_name and prompt_text and model_name:

            prompter.load_model(model_name, temperature=0.0, sample=False)

            #   parse the PDF in memory and attach to the prompt
            if not topic_query:
                sources = prompter.add_source_document(doc_path,file_name)
            else:
                # this is where we use the topic_query to filter the parsed document
                sources = prompter.add_source_document(doc_path,file_name, query=topic_query)

            #   run the inference with the source
            response = prompter.prompt_with_source(prompt_text)

            #   fact checks
            fc = prompter.evidence_check_numbers(response)
            cs = prompter.evidence_check_sources(response)

            if len(response) > 0:
                if "llm_response" in response[0]:
                    response = response[0]["llm_response"]

                    st.write(f"Answer: {response}")

                    if len(fc) > 0:
                        if "fact_check" in fc[0]:
                            fc_out = fc[0]["fact_check"]
                            st.write(f"Numbers Check: {fc_out}")

                    if len(cs) > 0:
                        if "source_review" in cs[0]:
                            sr_out = cs[0]["source_review"]
                            st.write(f"Source review: {sr_out}")


if __name__ == "__main__":

    simple_analyzer_with_topic_query()
