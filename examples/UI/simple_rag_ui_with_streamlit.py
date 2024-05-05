
""" This example shows how to build a simple RAG application with UI with Streamlit and LLMWare.

    Note: it requires a separate `pip install streamlit`, and to run the script, you should run from the
    command line with:

     `streamlit run using_with_streamlit_ui.py`

    For this example, we will be prompting against a set of Invoice documents, provided in the LLMWare
    sample files.

    If you would like to substitute longer documents then please look at the UI example:
        -- rag_ui_with_query_topic_with_streamlit.py

    as a framework to get started integrating a retrieval step before the prompt of the source

    For more information about Streamlit, check out their docs:  https://docs.streamlit.io/develop/tutorials

"""


import os
import streamlit as st

from llmware.prompts import Prompt
from llmware.setup import Setup

# st.set_page_config(layout="wide")


def simple_analyzer ():

    st.title("Simple RAG Analyzer")

    prompter = Prompt()

    sample_files_path = Setup().load_sample_files(over_write=False)
    doc_path = os.path.join(sample_files_path, "Invoices")

    files = os.listdir(doc_path)
    file_name = st.selectbox("Choose an Invoice", files)

    prompt_text = st.text_area("Question (hint: 'what is the total amount of the invoice?'")

    model_name = st.selectbox("Choose a model for answering questions", ["bling-phi-3-gguf",
                                                                         "bling-tiny-llama-1b",
                                                                         "bling-stablelm-3b-tool",
                                                                         "llama-3-instruct-bartowski-gguf",
                                                                         "dragon-llama-answer-tool"])

    if st.button("Run Analysis"):

        if file_name and prompt_text and model_name:

            prompter.load_model(model_name, temperature=0.0, sample=False)

            #   parse the PDF in memory and attach to the prompt
            sources = prompter.add_source_document(doc_path,file_name)

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

    simple_analyzer()
