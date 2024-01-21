
"""This example demonstrates what can be accomplished with llmware with no databases - all of these
#   examples run in-memory.  Note: for best results in some of the examples, you will need LLM API key.
"""

import json
import os
import time
from llmware.parsers import Parser
from llmware.prompts import Prompt
from llmware.setup import Setup
from llmware.util import PromptCatalog, Datasets
from llmware.resources import PromptState
import streamlit as st

@st.cache_resource
def load_llmware_model(model_name):
    # Load the llmware model
    print(f"\n > Loading the llmware model {model_name}...")
    
    return Prompt(save_state=True).load_model(model_name)

# Iterate through and analyze the contracts in a folder 
def analyze_contracts_on_the_fly(model_name, pdf_file, prompt_text):

    # Load the llmware sample files
    print (f"\n > Loading the llmware sample files...")
    sample_files_path = os.getcwd()
    contracts_path = os.path.join(sample_files_path,"Agreements")

    # Write odf fiel to local folder
    pdf_filename = pdf_file.name
    pdf_file_path = os.path.join(contracts_path, pdf_filename)
    with open(pdf_file_path, "wb") as pdf_file_out:
        pdf_file_out.write(pdf_file.read())

    st.write(f"\n > Loading the llmware model {model_name}...")
    prompter = load_llmware_model(model_name)
    
    print (f"\n > Analyzing contracts with prompt: '{prompt_text}'")
    st.write(f"\n > Analyzing contracts with prompt: '{prompt_text}'")

    start_time = time.time()

    for i, contract in enumerate(os.listdir(contracts_path)):

        if contract != ".DS_Store":

            print (f"\n > Analyzing {contract}")
            st.write(f"\n > Analyzing {contract}")

            # Add contract as a prompt source
            source = prompter.add_source_document(contracts_path, contract, query="proposal")

            # Prompt LLM and display response
            responses = prompter.prompt_with_source(prompt_text, prompt_name="number_or_none")
            for response in responses:
                print("LLM Response: " + response["llm_response"])
                st.write("LLM Response: " + response["llm_response"])


            # We're done with this contract, clear the source from the prompt
            prompter.clear_source_materials()

    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time
    print(f"\n > Inference time: {elapsed_time:.2f} seconds")
    st.write(f"\n > Inference time: {elapsed_time:.2f} seconds")

    return 0

if __name__ == "__main__":
    st.title("LLMWare PDF RAG App")
    # Model Dropdown
    model_name = st.selectbox("Choose an LLM model", ["llmware/bling-sheared-llama-1.3b-0.1", "llmware/bling-stable-lm-3b-4e1t-v0", "llmware/bling-sheared-llama-2.7b-0.1", "llmware/bling-falcon-1b-0.1", "llmware/bling-red-pajamas-3b-0.1", "llmware/bling-1b-0.1", "llmware/bling-cerebras-1.3b-0.1", "llmware/bling-1.4b-0.1", "llmware/bling-ner-to-json-v0", "llmware/bling-phi-1_5-v0", "llmware/bling-phi-2-v0", "llmware/bling-tiny-llama-v0"])

# PDF Upload
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# Prompt Text Field
    prompt_text = st.text_area("Enter your prompt text")

    if st.button("Run Analysis"):
        # Check if all inputs are provided
        if model_name and pdf_file and prompt_text:
            with st.spinner("Analyzing contracts..."):
                 #  simple RAG use case all in memory with local LLM
                analyze_contracts_on_the_fly(model_name, pdf_file, prompt_text)           
        else:
            st.warning("Please provide all required inputs before running the analysis.")
    
 

    


