# Import required libraries
import azure.cognitiveservices.speech as speechsdk
import streamlit as st
from llmware.models import ModelCatalog
import requests
import os, re, time
from PIL import Image
from dotenv import load_dotenv
import base64

load_dotenv()

st.set_page_config(page_title='Gita Summarizer', page_icon = '🦚', initial_sidebar_state = 'auto')

LOGO_IMAGE = "logo.png"

st.markdown(
    """
    <style>
    .container {
        display: flex;
    }
    .logo-text {
        font-weight:700;
        font-size:50px ;
        color: #f9a01b ;
        margin-left:-15px;
        padding: 15px ;
    }
    .logo-img {
        float:right;
        width: 100px;
        height:100px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="container">
        <p class="logo-text">Gita Summarizer</p>
        <img class="logo-img" src="data:image/png;base64,{base64.b64encode(open(LOGO_IMAGE, "rb").read()).decode()}">
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("<p style='color: rgb(11 124 206); text-align: left; font-style: italic;'>Condense, Comprehend and Connect with Gita...</p>", unsafe_allow_html=True)        
st.markdown("<p style='color: rgb(17 166 144); text-align: left; font-style: italic;'>Ask queries related to Gita and get brief summarized text</p>", unsafe_allow_html=True)
# Get Azure Speech subscription key, service region, and token from environment variables
subscription_key = os.getenv("subscription_key")
service_region = os.getenv("service_region")
token=os.getenv("token")

# API endpoint for speech-to-text
url = f"https://{service_region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=en-US"

# Headers for the API request
headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Content-Type':'audio/wav',
  'Authorization': f'Bearer {token}'
}

with st.sidebar:
    with st.container():
        
        # Radio button to choose between real-time speech input and uploading an audio file
        option = st.radio("Choose an option:",("Real-time Speech Input", "Upload Audio File","Type in text"))
    
    st.markdown("----")
    
    with st.container():
        custom_css = """
        <style>
        .tech-stack {
            color: #007bff;
            font-weight: bold;
        }
        .key-points {
            color: #28a745;
        }
        .heading{
            font-size:20px;
        }
        </style>
        """
        st.markdown(custom_css, unsafe_allow_html=True)
        
        st.markdown("<p><strong class='heading'>Gita Summarizer</strong> is a <span class='tech-stack'>Streamlit</span> app utilizing <span class='tech-stack'>Azure Speech-to-Text</span> and <span class='tech-stack'>LLMWare</span> for extracting concise summaries from the Bhagavad Gita, ideal for insightful exploration of its teachings.</p>", unsafe_allow_html=True)

        st.markdown("<p>By condensing the profound teachings of the Bhagavad Gita into succinct summaries, the tool facilitates <span class='key-points'><i>easy comprehension</i></span> and <span class='key-points'><i>swift access</i></span> to its timeless wisdom.", unsafe_allow_html=True)

        st.markdown("This <span class='key-points'><i>summarization functionality</i></span> enhances the accessibility of the Bhagavad Gita, allowing users to grasp its key concepts quickly and effectively.</p>", unsafe_allow_html=True)
        
        styl = """
        <style>
            .text {
            position: fixed;
            bottom: 3rem;
            }
        </style>
        """
        st.markdown(styl, unsafe_allow_html=True)

        st.markdown("<p style='text-align: center; font-size: 1.2em; color: white;'>Jay Shri Krishna 🪈🦚🪶</p>", unsafe_allow_html=True)

                

# Function to summarize the transcribed text using LLMWare's SLIM-SUMMARY-TOOL
def summarize(text):
    with st.spinner("Unveiling Gita's Essence..."):
        model = ModelCatalog().load_model("slim-summary-tool",
                                    sample=False,
                                    temperature=0.0,
                                    max_output=200)

        test_script = ModelCatalog().get_test_script("slim-summary-tool")
        
        prompt=f"In the context of Gita, {text}"
        response = model.function_call(prompt,function="summarize",params=["data points (5)"])  
        r=response["llm_response"]
        print(r)
        filtered_responses = [re.sub(r'\b\d+\.\s*', '', response) for response in r]
        res=[]
        stop_sentences=["5 data points:", prompt.lower(), text]
        for i in filtered_responses:
            if i not in res and i.lower() not in stop_sentences:
                res.append(i)
        st.markdown("#### **Summarized text**")
        for i in res:
            st.markdown("- "+i)
        
if option=="Upload Audio File":
    
    st.markdown("#### **Upload an Audio file**")
    uploaded_file = st.file_uploader("", type="wav")
    
    if uploaded_file is not None:
        file_content = uploaded_file.read()    
        st.audio(file_content, format='audio/wav')
        
        # Sending audio file content to Azure Speech API for transcription
        with st.spinner("Fetching File content..."):
            response = requests.post(url, headers=headers, data=file_content)
        st.markdown("#### Transcription")        
        text=response.json()['DisplayText']    
        st.write(text)    
        
        # Summarizing the transcribed text on button click
        if st.button("Summarize"):            
            # st.write(summarize(text))  
            summarize(text)  
                
elif option=="Real-time Speech Input":
    
    st.markdown("#### **Real Time Audio Summarizer**")  
     
    # Function to capture real-time speech input and perform transcription
    def real_time_speech():
        speak=st.info("Speak into your microphone 🗣️...", icon="💡")
        # Speech configuration
        speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=service_region)
        speech_config.speech_recognition_language="en-US"
        
        # Audio configuration
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config,audio_config=audio_config)
        
        with st.spinner("Listening🧏🏻..."):
            speak.empty()
            result = speech_recognizer.recognize_once_async().get()
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                st.markdown("#### Transcription")
                st.write("{}".format(result.text))
                # st.write(summarize(result.text)) 
                summarize(result.text)  
                
                
            elif result.reason == speechsdk.ResultReason.NoMatch:
                st.error("No speech could be recognized")
                
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                st.error("Speech Recognition canceled: {}".format(cancellation_details.reason))
                
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    st.error("Error details: {}".format(cancellation_details.error_details))
                   
                    
    # Button to start real-time speech input                
    if st.button("Ready to Speak..."):
        real_time_speech()                       
                     
else:
    st.markdown("#### **Enter your questions about the Gita below 👇🏻..**")
    text=st.text_input('',value='')
    text=text.strip()
    if text!='':
        if len(text)<10:
            err=st.error("Query should be atleast 10 chars long")
            time.sleep(5)
            err.empty()
        else:
            if st.button("Get summary"):
                # st.write(summarize(text))
                summarize(text)  
            
    