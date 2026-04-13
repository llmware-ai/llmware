
""" This example shows how to build a local chatbot prototype using llmware and Streamlit.  The example shows
how to use several GGUF chat models in the LLMWare catalog, along with using the model.stream method which
provides a real time generator for displaying the bot response in real-time.

    This is purposefully super simple script (but surprisingly fun) to provide the core of the recipe.

    The Streamlit code below is derived from Streamlit tutorials available at:
    https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps

    If you are new to using Steamlit, to run this example:

    1.  pip3 install streamlit

    2.  to run, go to the command line:  streamlit run "path/to/gguf_streaming_chatbot.py"

"""

import streamlit as st
from llmware.models import ModelCatalog
from llmware.gguf_configs import GGUFConfigs

GGUFConfigs().set_config("max_output_tokens", 500)


def simple_chat_ui_app (model_name):

    st.title(f"Simple Chat with {model_name}")

    model = ModelCatalog().load_model(model_name, temperature=0.3, sample=True, max_output=450)

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

            #   note that the st.write_stream method consumes a generator - so pass model.stream(prompt) directly
            bot_response = st.write_stream(model.stream(prompt))

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
                   "zephyr-7b-gguf",
                   "tiny-llama-chat-gguf"]

    model_name = chat_models[0]

    simple_chat_ui_app(model_name)



