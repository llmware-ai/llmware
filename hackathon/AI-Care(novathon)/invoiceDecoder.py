from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
from llmware.models import ModelCatalog  # Import llmware model

# Load environment variables
load_dotenv()  # take environment variables from .env

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get response from Gemini model
def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, image[0], prompt])
    return response.text

# Function to process uploaded image
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Initialize the Streamlit app
st.set_page_config(page_title="Invoice Decoder")
st.title("Invoice Decoder")
st.subheader("Transforms invoices into readable text, simplifying billing across multiple languages.")
input = st.text_input("Input Prompt: ", key="input")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
image = ""   

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

submit = st.button("Execute Prompt")

input_prompt = """
               You are an expert in understanding invoices.
               You will receive input images as invoices & 
               you will have to answer questions based on the input image.
               """

# If the submit button is clicked
if submit:
    image_data = input_image_setup(uploaded_file)
    # Get response from Gemini model
    response = get_gemini_response(input_prompt, image_data, input)
    
    # Display the Gemini response (detailed analysis of the invoice)
    st.subheader("The Response from Gemini Model")
    st.write(response)
    
    # Now, integrate the llmware model to summarize the response
    # Initialize llmware model for summarization
    llm_model = ModelCatalog().load_model(selected_model="slim-summary-tool", sample=False, temperature=0.0, max_output=200)
    
    # Call llmware model to summarize the response from Gemini model
    summary_response = llm_model.function_call(response, function="summarize", params=["summary points (5)"])
    
    # Assuming the summary response is a list of points in the "llm_response"
    if "llm_response" in summary_response:
        st.subheader("Summary of the Invoice")
        # Loop through the summary response list and display each point
        for i, point in enumerate(summary_response["llm_response"]):
            st.write(f"{i + 1}. {point}")
    else:
        st.write("No summary available.")
