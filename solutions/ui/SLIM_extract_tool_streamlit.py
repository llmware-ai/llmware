""" This example provides a basic framework to build a Chatbot UI interface in conjunction with LLMWare
    using Streamlit Chat UI.

    To run this example requires an install of Streamlit, e.g., `pip3 install streamlit`

    To execute the script, run from the command line with:  `streamlit run using_with_streamlit_ui.py`

    Also, please note that the first time you run with a new model, the model will be downloaded and cached locally,
    so expect a delay on the 'first run' which will be much faster on every successive run.

    All components of the chatbot will be running locally, so the speed will be determined greatly by the
    CPU/GPU capacities of your machine.

    We have set the max_output at 250 tokens - for faster, set lower ...

    For more information on the Streamlit Chat UI,
    see https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps


"""

import streamlit as st
from llmware.models import ModelCatalog

# Title of the Streamlit app
st.title("SLIM Extract Tool LLMWARE")

# Text input for the text to analyze
text_to_analyze = st.text_area("Enter the text to analyze:", "\"Good Will Hunting,\" a 1997 film directed by Gus Van Sant, tells the story of a young janitor at MIT who has a hidden talent for mathematics and undergoes therapy to confront his troubled past.")

# Text input for the queries
queries_input = st.text_area("Enter your queries (comma separated):", "Director, Film Name")

# Convert the input queries to a list
queries_list = [query.strip() for query in queries_input.split(',')]

# Button to run the analysis
if st.button("Analyze"):
    # Load the model
    model = ModelCatalog().load_model("slim-extract-tool", sample=False, temperature=0.0, max_output=250)
    
    # Initialize the output dictionary
    output_dict = {}

    # Loop through the queries and call the model with the entire text for each query
    for j, query in enumerate(queries_list):
        st.write(f"Query {j+1}: {query}")
        response = model.function_call(text_to_analyze, function="extract", params=[query])
        output_dict.update(response["llm_response"])
        #if not response["llm_response"]:
           # st.write("No response")
       # st.write("Extract response: ", response["llm_response"])

    # Display the response on the screen
    st.write("Output Dictionary:")
    st.json(output_dict)