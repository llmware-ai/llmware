# LLMSoundWare

## Overview

LLMSoundWare is a LLMWare + Streamlit web application that takes an audio file as input, transcribes it using LLMware models, and performs various analyses on the transcription. The app provides insights into sentiment, named entities, topics, categories, intents, emotions, and summaries extracted from the audio content. Additionally, it features an interactive chatbot powered by the Dragon model from LLMware, allowing users to ask questions about the audio and its analysis.

## Features

- **Audio Input:** Upload an audio file or record audio directly within the app.
- **Transcription:** Convert speech to text using LLMWare's WhisperCPP model.
- **Analysis:** Clean the transcription and analyze it for:
  - Sentiment 
  - Named Entities Recognition (NER)
  - Topics 
  - Categories 
  - Intent
  - Emotions 
  - Summary
- **Interactive Chatbot:** Chat with a Dragon model-powered assistant to inquire about the audio content and analysis results.
- Everything running locally (using Mac M1).

## LLMWare models used
- #### WhisperCPP (whisper-cpp-base-english) 
  - WhisperCPP is the implementation of Whisper packaged as a GGML deliverable. It is integrated as WhisperCPPModel in LLMware.
  - It is used for voice-to-text conversion.

- #### slim-sentiment-tool 
  - A 4_K_M quantized GGUF version of slim-sentiment, providing a small, fast inference implementation optimized for multi-model concurrent deployment.
  - It is used for Sentiment Analysis.

- #### slim-ner-tool 
  - A 4_K_M quantized GGUF version of slim-ner, providing a small, fast inference implementation optimized for multi-model concurrent deployment.
  - It is used for Named Entities Recognition.

- #### slim-topics-tool 
  - A 4_K_M quantized GGUF version of slim-topics, providing a small, fast inference implementation optimized for multi-model concurrent deployment.
  - It is used for Topic Identification.

- #### slim-category-tool 
  - A 4_K_M quantized GGUF version of slim-category, providing a small, fast inference implementation optimized for multi-model concurrent deployment.
  - It is used for Category Identification.

- #### slim-intent-tool 
  - A 4_K_M quantized GGUF version of slim-intent, providing a small, fast inference implementation optimized for multi-model concurrent deployment.
  - It is used for Intent Analysis.

- #### slim-emotions-tool 
  - A 4_K_M quantized GGUF version of slim-emotions, providing a small, fast inference implementation optimized for multi-model concurrent deployment.
  - It is used for Emotions Analysis.

- #### slim-summary-tool
  - A 4_K_M quantized GGUF version of slim-summary, providing a high-quality summarization of complex business documents with summary output structured as a Python list of key points.
  - It is used for Summarization.

- #### dragon-yi-answer-tool 
  - A quantized version of DRAGON Yi 6B, with 4_K_M GGUF quantization, providing a fast, small inference implementation for use on CPUs.
  - It is used for creating Chatbot experience.

## Video
Watch on [YouTube](https://youtu.be/RCZ4bzQrdAk)


https://github.com/AJ1904/llmsoundware/assets/49027490/53519bf4-90d7-48e7-b62b-56404598ef37


## Scenarios and Examples of Use

### 1. Business Meetings
#### Scenario:
A company records its business meetings to keep track of discussions, decisions, and action items.
#### Example:
- Upload the meeting audio file to LLMSoundWare.
- Transcribe the meeting discussion.
- Analyze the transcription to extract key topics, sentiments, and named entities.
- Use the chatbot to ask specific questions about decisions made or action items assigned during the meeting.

### 2. Customer Support
#### Scenario:
Customer support calls are recorded for quality assurance and training purposes.
#### Example:
- Upload a customer support call recording to LLMSoundWare.
- Transcribe the conversation between the support agent and the customer.
- Analyze the transcription to identify the sentiment, emotions, and intent of the customer.
- Use the chatbot to explore specific issues raised during the call and how they were addressed.

### 3. Educational Lectures
#### Scenario:
Students and educators want to transcribe and analyze lecture recordings for better understanding and revision.
#### Example:
- Upload a lecture audio file to LLMSoundWare.
- Transcribe the lecture content.
- Analyze the transcription to summarize key points, topics covered, and named entities mentioned.
- Use the chatbot to ask questions about specific concepts or topics discussed in the lecture.

### 4. Podcast Analysis
#### Scenario:
Podcast creators and listeners want to transcribe and analyze podcast episodes for content analysis and sharing insights.
#### Example:
- Upload a podcast episode to LLMSoundWare.
- Transcribe the podcast content.
- Analyze the transcription to identify topics, sentiments, and key points.
- Use the chatbot to discuss specific segments or themes covered in the podcast.

### 5. Legal Proceedings
#### Scenario:
Legal professionals need to transcribe and analyze court hearings or deposition recordings.
#### Example:
- Upload an audio recording of a court hearing to LLMSoundWare.
- Transcribe the legal proceedings.
- Analyze the transcription to extract named entities (e.g., names of people, organizations), topics, and emotions.
- Use the chatbot to ask about specific testimonies or legal arguments presented during the hearing.

## Packages & Tools
- LLMWare `pip install llmware`
- Streamlit `pip install streamlit `
- Streamlit audiorec `pip install strealit-audiorec`
- Plotly `pip install plotly`
- Matplotlib `pip install maltplotlib`
- Huggingface-hub `pip install huggingface-hub`
- Python

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/AJ1904/llmsoundware.git
   ```
2. Navigate to the project directory:
   ```sh
   cd llmsoundware
   ```
3. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit app:
   ```sh
   streamlit run llmsoundware.py
   ```
2. Open your web browser and go to `http://localhost:8501`.

## Example Usage

1. Upload an audio file or record audio.
2. Click "Process Audio" to transcribe and analyze the audio.
3. View the transcription and analysis results in the sidebar.
4. Use the chatbot to ask questions about the audio content and analysis.

## Troubleshoot
1. Ensure that you have installed LLMWare using pip.
2. Use Python version >=3.11
3. A lot of models are loaded into the memory. Out of memory issues might occur, so run in isolated environment.
4. Streamlit-audiorec is not part of streamlit, you should install it using pip.

## Code Structure

The main components of the app are:

### 1. Transcription and Analysis

- **Audio Processing:** Upload or record audio, and use the WhisperCPP model for transcription.
- **Analysis:** Clean the transcription and use LLMware models to extract insights.
- **Results Display:** Show the analysis results, including sentiment, NER, topics, categories, intents, emotions, and summaries.

### 2. Interactive Chatbot

- **Chat Interface:** Display chat messages and history.
- **Response Generation:** Use the Dragon model to generate responses based on user input and the audio transcription.

## Key Functions

### `process_audio(uploaded_file)`
Processes the uploaded audio file, generates a transcription using the WhisperCPP model, and returns the transcription and audio bytes.

### `analyze_transcription(transcription)`
Cleans the transcription and analyzes it using various LLMware models, returning the analysis results.

### `display_results()`
Displays the transcription and analysis results in the sidebar, including sentiment, NER, topics, categories, intents, emotions, and summaries.

### `create_gauge_chart(sentiment_score, width=400, height=300)`
Creates a gauge chart to visualize the sentiment score.

### `response_generator(query, text_sample="hello")`
Generates responses for the chatbot using the Dragon model, yielding words progressively for a typing effect.

### `main()`
The main function to set up and run the Streamlit app, including layout, audio processing, and chatbot functionality.


