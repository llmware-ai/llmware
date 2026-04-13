
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


def simple_chat_ui_app (model_name):

    st.title(f"Simple Chat with {model_name}")

    model = ModelCatalog().load_model(model_name, temperature=0.3, sample=True, max_output=250)

    # initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # accept user input
    prompt = st.chat_input("Say something")
    if prompt:

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            model_response = model.inference(prompt)

            # insert additional error checking / post-processing of output here
            bot_response = model_response["llm_response"]

            st.markdown(bot_response)

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

    return 0


if __name__ == "__main__":

    #   a few representative good chat models that can run locally
    #   note: will take a minute for the first time it is downloaded and cached locally

    chat_models = ["phi-3-gguf",
                   "llama-2-7b-chat-gguf",
                   "llama-3-instruct-bartowski-gguf",
                   "openhermes-mistral-7b-gguf",
                   "zephyr-7b-gguf"]

    model_name = chat_models[0]

    simple_chat_ui_app(model_name)



