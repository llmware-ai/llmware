import plotly.graph_objects as go
from st_audiorec import st_audiorec
import streamlit as st
import streamlit.components.v1 as components
import os
from llmware.models import ModelCatalog
from llmware.gguf_configs import GGUFConfigs
from io import BytesIO
import tempfile
import re
from llmware.agents import LLMfx
import matplotlib.pyplot as plt
import gc
import random
import time

css='''
<style>
    section.main>div {
        padding-bottom: 1rem;
    }
    [data-testid="column"]>div>div {
        overflow: auto;
        height: 50vh;
    }

    div[data-testid="element-container"] iframe {
    max-width: 35vh;
    }

    [data-testid="stSidebar"]{
        min-width: 400px;
        max-width: 800px;
    }

</style>
'''
st.markdown(css, unsafe_allow_html=True)

# Initialize chat history and audio state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "audio_transcription" not in st.session_state:
    st.session_state.audio_transcription = ""

if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None

if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = {}

# Streamed response emulator
def response_generator(query, text_sample="hello"):
    response = dragon_model.inference(query, add_context=text_sample)
    answer = response["llm_response"]
    for word in answer.split():
        yield word + " "
        time.sleep(0.05)

# Load WhisperCPP model
whisper_base_english = "whisper-cpp-base-english"
model = ModelCatalog().load_model(whisper_base_english)

summary_model = ModelCatalog().load_model("slim-summary-tool")
dragon_model = ModelCatalog().load_model("dragon-yi-answer-tool") 

# Function to load LLMfx tools
@st.cache_resource
def create_llm_fx_instance():
    return LLMfx()

@st.cache_resource
def load_llm_tools(_llm_fx):
    # Explicitly trigger garbage collection
    gc.collect()
    with st.spinner("Loading intent tool..."):
        _llm_fx.load_tool("intent")
    with st.spinner("Loading category tool..."):
        _llm_fx.load_tool("category")
    with st.spinner("Loading sentiment tool..."):
        _llm_fx.load_tool("sentiment")
    with st.spinner("Loading emotions tool..."):
        _llm_fx.load_tool("emotions")
    with st.spinner("Loading topics tool..."):
        _llm_fx.load_tool("topics")
    return _llm_fx

# Create LLMfx instance and load tools
llm_fx = create_llm_fx_instance()
llm_fx = load_llm_tools(llm_fx)

# Function to process audio using WhisperCPP
def process_audio(uploaded_file):
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(uploaded_file.read())

    # Run inference
    response = model.inference(temp_file.name)

    # Extract transcription from response
    transcription = response["llm_response"]

    # Reset the file pointer of the uploaded file
    uploaded_file.seek(0)
    # Read uploaded file content as BytesIO object
    audio_bytes = BytesIO(uploaded_file.read())

    # Delete the temporary file
    os.unlink(temp_file.name)

    return transcription, audio_bytes

# Function to analyze transcription
def analyze_transcription(transcription):
    cleaned_transcription = re.sub(r'\[.*?\]', '', transcription)
    sentiment = llm_fx.sentiment(cleaned_transcription)
    ner = llm_fx.ner(cleaned_transcription)
    topic = llm_fx.topics(cleaned_transcription)
    category = llm_fx.category(cleaned_transcription)
    intent = llm_fx.intent(cleaned_transcription)
    emotions = llm_fx.emotions(cleaned_transcription)
    summary = summary_model.function_call(cleaned_transcription)
    
    return {
        "cleaned_transcription": cleaned_transcription,
        "sentiment": sentiment,
        "ner": ner,
        "topic": topic,
        "category": category,
        "intent": intent,
        "emotions": emotions,
        "summary": summary
    }

# Function to display the results of audio analysis
def display_results():
    results = st.session_state.analysis_results
    # Using "with" notation
    with st.sidebar:
        st.write("### Transcription")  
        st.text_area("Transcription", results["cleaned_transcription"], height=200, label_visibility="collapsed")
        st.write("### Overview")  
        display_function(results["topic"], 'topic', 'It looks like the audio is about')
        display_function(results["category"], 'category', 'The category of audio is')
        display_function(results["intent"], 'intent', 'The intent of the audio is')
        display_function(results["emotions"], 'emotions', 'The emotions in the audio are')
        create_gauge_chart(results["sentiment"])  
        display_summary(results["summary"])
        display_ner(results["ner"])
        
        

# Function to create a gauge chart
def create_gauge_chart(sentiment_score, width=400, height=300):
    # Define sentiment colors
    colors = {'negative': 'red', 'neutral': 'yellow', 'positive': 'green'}

    # Extract sentiment and confidence score
    sentiment = sentiment_score['llm_response']['sentiment'][0]
    confidence_score = sentiment_score['confidence_score']
    color = colors.get(sentiment, 'gray')

    # Convert confidence score to percentage
    confidence_percentage = confidence_score * 100

    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = confidence_percentage,
        title = {'text': f"Sentiment : {sentiment.capitalize()}"},
        number = {'suffix': "%"},  # Display value as percentage
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 75], 'color': "gray"},
                {'range': [75, 100], 'color': "darkgray"}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 50}
        }),
        layout=dict(width=width, height=height)
        )
    # Add sentiment value as annotation
    fig.add_annotation(
        x=0.5,
        y=0.4,
        text="",
        showarrow=False,
        font=dict(
            family="Arial",
            size=14,
            color="black"
        )
    )
    st.plotly_chart(fig)

# Function to display various outputs with confidence score
def display_function(output, typee, description):
    value = output['llm_response'][typee][0]
    confidence_score = output['confidence_score'] 
    badge_color = get_badge_color(confidence_score)
    confidence_score = confidence_score * 100
    badge_style = f"background-color: {badge_color}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;"
    badge_text = f"{value.capitalize()}"

    st.markdown(f'{description} <span style="{badge_style}">{badge_text}</span>. I am {confidence_score:.2f}% confident!', unsafe_allow_html=True)

def display_summary(output):
    summaries = output.get('llm_response', [])
    if not summaries:
        return
    
    st.write("### Interesting Points")
    
    for summary in summaries:
        st.write(f"- {summary}")


    
# Function to display Named Entities Recognition (NER) output
def display_ner(ner_output):
    # Extract relevant information
    persons = ', '.join(ner_output['llm_response'].get('people', []))
    organizations = ', '.join(ner_output['llm_response'].get('organization', []))
    places = ', '.join(ner_output['llm_response'].get('place', []))
    misc = ', '.join(ner_output['llm_response'].get('misc', []))
    
    st.write(f"### Named Entities Recognition (NER)")
    st.write(f"**Persons:** {persons if persons else 'None'}")
    st.write(f"**Organizations:** {organizations if organizations else 'None'}")
    st.write(f"**Places:** {places if places else 'None'}")
    st.write(f"**Others:** {misc if misc else 'None'}")

# Function to get badge color based on confidence score
def get_badge_color(confidence_score):
    if confidence_score >= 0.8:
        return "green"
    elif confidence_score >= 0.5:
        return "orange"
    else:
        return "red"

# Main function to run the Streamlit app
def main():
    # Set up the title and description
    st.title("LLMSoundWare")
    st.write("Upload an audio file to transcribe and analyze. You can also record audio using the microphone.")

    # Create two columns
    col1, col2 = st.columns(2)

    # Left column for audio processing
    with col1:
        # Upload sound file
        uploaded_file = st.file_uploader("Upload audio file", type=["wav", "m4a", "mp3"], label_visibility="collapsed")

        wav_audio_data = st_audiorec()

    if wav_audio_data is not None:
        st.audio(wav_audio_data, format='audio/wav')
        # Create a BytesIO object from recorded audio data
        recorded_audio_bytes = BytesIO(wav_audio_data)

        # Process recorded audio
        if st.button("Process Recorded Audio"):
            transcription, audio_bytes = process_audio(recorded_audio_bytes)
            st.session_state.audio_transcription = transcription
            st.session_state.audio_bytes = audio_bytes
            st.session_state.analysis_results = analyze_transcription(transcription)
            # display_results()

    # Button to start processing
    if uploaded_file:
        st.audio(uploaded_file, format='audio/wav')
        if st.button("Process Audio"):
            # Perform audio processing
            transcription, audio_bytes = process_audio(uploaded_file)
            st.session_state.audio_transcription = transcription
            st.session_state.audio_bytes = audio_bytes
            st.session_state.analysis_results = analyze_transcription(transcription)
            #display_results()

    # Display transcription and analysis if available
    if st.session_state.audio_transcription:
        display_results()

    # Right column for chat assistant
    with col2:
        st.write("Chat with the Dragon")
        # Display chat messages from history on app rerun
        st.markdown("###### Chat History")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        # Accept user input
        st.markdown("###### Current Prompt")
        if prompt := st.chat_input("You can ask me about the content :D"):
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Generate and display assistant response
            with st.chat_message("assistant"):
                response = ''.join(response_generator(prompt, st.session_state.audio_transcription))
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})



if __name__ == "__main__":
    main()
