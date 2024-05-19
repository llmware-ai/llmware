import os
import shutil
import pyttsx3
import streamlit as st
from llmware.exceptions import LibraryNotFoundException
from llmware.models import ModelCatalog
from llmware.gguf_configs import GGUFConfigs
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup
from llmware.configs import LLMWareConfig

# Initialize the TTS engine
engine = pyttsx3.init()

def get_available_voices():
    """Get the list of available voices"""
    voices = engine.getProperty('voices')
    voice_options = []
    for voice in voices:
        voice_options.append((voice.name, voice.id))
    return voice_options

def set_voice(voice_id):
    """Set the voice (optional)"""
    engine.setProperty('voice', voice_id)

def text_to_speech(text):
    """Convert text to speech"""
    print(f"Text-to-Speech: {text}")  # Debug message
    engine.say(text)
    engine.startLoop(False)
    engine.iterate()

def load_library(library_name, sample_folder):
    print(f"\nStep 1 - creating library {library_name}")
    library = Library().create_new_library(library_name)

    sample_files_path = Setup().load_sample_files(over_write=False)
    print(f"Step 2 - loading the llmware sample files and saving at: {sample_files_path}")

    ingestion_folder_path = os.path.join(sample_files_path, sample_folder)

    print(f"Step 3 - parsing and indexing files from {ingestion_folder_path}")

    parsing_output = library.add_files(ingestion_folder_path)

    print(f"Step 4 - completed parsing - {parsing_output}")

    updated_library_card = library.get_library_card()
    doc_count = updated_library_card["documents"]
    block_count = updated_library_card["blocks"]
    print(f"Step 5 - updated library card - documents - {doc_count} - blocks - {block_count} - {updated_library_card}")

    library_path = library.library_main_path

    print(f"Step 6 - library artifacts - including extracted images - saved at folder path - {library_path}")


    """Load the library"""
    return Library().load_library(library_name, sample_folder)

def query_library(library, query_text, result_count=10):
    """Query the library"""
    return Query(library).text_query(query_text, result_count=result_count)

def display_query_results(results):
    """Display query results"""
    for i, result in enumerate(results):
        text = result["text"]
        file_source = result["file_source"]
        page_number = result["page_num"]
        doc_id = result["doc_ID"]
        block_id = result["block_ID"]
        matches = result["matches"]
        st.write(f"Result {i+1}:")
        st.write(f"Text: {text}")
        st.write(f"File Source: {file_source}")
        st.write(f"Page Number: {page_number}")
        st.write(f"Document ID: {doc_id}")
        st.write(f"Block ID: {block_id}")
        st.write(f"Matches: {matches}")
        st.write("----")

def simple_chat_ui_app(model_name, voice_id, library_name, sample_folder):
    # Load the specified library
    print(f"\nStep 1 - creating library {library_name}")
    library = Library().create_new_library(library_name)

    sample_files_path = Setup().load_sample_files(over_write=False)
    print(f"Step 2 - loading the llmware sample files and saving at: {sample_files_path}")

    ingestion_folder_path = os.path.join(sample_files_path, sample_folder)

    print(f"Step 3 - parsing and indexing files from {ingestion_folder_path}")

    parsing_output = library.add_files(ingestion_folder_path)

    print(f"Step 4 - completed parsing - {parsing_output}")

    updated_library_card = library.get_library_card()
    doc_count = updated_library_card["documents"]
    block_count = updated_library_card["blocks"]
    print(f"Step 5 - updated library card - documents - {doc_count} - blocks - {block_count} - {updated_library_card}")

    library_path = library.library_main_path

    print(f"Step 6 - library artifacts - including extracted images - saved at folder path - {library_path}")

    # Set the selected voice
    set_voice(voice_id)

    st.title(f"Simple Chat with {model_name}")

    GGUFConfigs().set_config("max_output_tokens", 500)
    model = ModelCatalog().load_model(model_name, temperature=0.3, sample=True, max_output=450)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    st.subheader("Chat History")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    prompt = st.chat_input("Say something")
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Note that the st.write_stream method consumes a generator - so pass model.stream(prompt) directly
            bot_response = "".join([chunk for chunk in model.stream(prompt)])
            st.markdown(bot_response)

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

        # Convert bot response to speech
        text_to_speech(bot_response)

    # Query the library
    st.subheader("Library Query")
    query_text = st.text_input("Enter your query")
    if query_text:
        library = load_library(library_name, sample_folder)
        results = query_library(library, query_text)
        display_query_results(results)

    # File upload functionality
    st.subheader("Upload File")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])
    if uploaded_file is not None:
        file_details = {
            "filename": uploaded_file.name,
            "filetype": uploaded_file.type,
            "filesize": uploaded_file.size,
        }
        st.write(file_details)

        # Save the uploaded file to a temporary directory
        temp_dir = "temp_uploads"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("File uploaded successfully")

        # Create a directory containing the uploaded file
        temp_dir_with_file = os.path.join(temp_dir, "upload_dir")
        os.makedirs(temp_dir_with_file, exist_ok=True)
        shutil.copy(temp_file_path, temp_dir_with_file)

        # Add the uploaded file to the library
        with st.spinner("Processing file..."):
            library.add_files(temp_dir_with_file)
        st.success("File processed and added to the library")

if __name__ == "__main__":
    # Add custom CSS for styling
    st.markdown("""
        <style>
            .css-18e3th9 {
                background-color: #34EdW56;  /* Change background color */
            }
            .css-1d391kg {
                color: #fafafa;  /* Change text color */
            }
            .st-bx {
                color: #00FF00;  /* Change sidebar text color */
            }
            .css-1n76uvr {
                background-color: #333333;  /* Change header color */
            }
            .css-3mnurz {
                color: #ffffff;  /* Change input text color */
            }
            .st-cz {
                border-color: #00FF00;  /* Change border color */
            }
        </style>
        """, unsafe_allow_html=True)

    # Get available voices
    voice_options = get_available_voices()
    voice_names = [voice[0] for voice in voice_options]
    voice_ids = {voice[0]: voice[1] for voice in voice_options}

    # Streamlit sidebar for voice selection
    st.sidebar.title("Settings")
    st.sidebar.header("Voice Settings")
    selected_voice_name = st.sidebar.selectbox("Select Voice", voice_names)
    selected_voice_id = voice_ids[selected_voice_name]

    st.sidebar.header("Model Settings")
    # A few representative good chat models that can run locally
    chat_models = [
        "phi-3-gguf",
        "llama-2-7b-chat-gguf",
        "llama-3-instruct-bartowski-gguf",
        "openhermes-mistral-7b-gguf",
        "zephyr-7b-gguf",
        "tiny-llama-chat-gguf"
    ]
    model_name = st.sidebar.selectbox("Select Model", chat_models)

    # Set the library name
    library_name = "folder_library"

    simple_chat_ui_app(model_name, selected_voice_id, library_name, sample_folder="Accounts")