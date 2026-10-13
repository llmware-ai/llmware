import streamlit as st
from pathlib import Path
import google.generativeai as genai
from google_api_key import google_api_key
from llmware.models import ModelCatalog

# Configure Google API Key
genai.configure(api_key=google_api_key)

# Streamlit App Setup
st.set_page_config(page_title="Scan AI", layout="wide")
st.title("Scan AI")
st.subheader("Upload medical images to get precise, AI-driven diagnoses for improved healthcare decisions.")

# File upload widget
file_uploaded = st.file_uploader('Upload the image for Analysis', type=['png', 'jpg', 'jpeg'])

# Set up the Gemini model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

system_prompts = [
    """
    You are a domain expert in medical image analysis. You are tasked with 
    examining medical images for a renowned hospital.
    Your expertise will help in identifying or 
    discovering any anomalies, diseases, conditions or
    any health issues that might be present in the image.
    """
]

model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

# Upload button and submission logic
if file_uploaded:
    st.image(file_uploaded, width=200, caption='Uploaded Image')

    submit = st.button("Generate Analysis")

    if submit:
        image_data = file_uploaded.getvalue()
        image_parts = [{"mime_type": "image/jpg", "data": image_data}]
        prompt_parts = [image_parts[0], system_prompts[0]]

        # Generate response from Gemini model
        response = model.generate_content(prompt_parts)
        
        if response:
            st.title('Detailed Analysis Based on the Uploaded Image')
            st.write(response.text)

            # Now integrate llmware model to summarize the response
            # Initialize llmware model for summarization
            llm_model = ModelCatalog().load_model(selected_model="slim-summary-tool", sample=False, temperature=0.0, max_output=200)

            # Call llmware model to summarize the analysis response
            summary_response = llm_model.function_call(response.text, function="summarize", params=["summary points (5)"])

            # Assuming summary_response is a dictionary with a key "llm_response" containing a list of points
            if "llm_response" in summary_response:
                st.title('Summary of the Analysis')
                # Loop through the summary response list and display each point
                for i, point in enumerate(summary_response["llm_response"]):
                    st.write(f"{i+1}. {point}")
            else:
                st.write("No summary available.")
