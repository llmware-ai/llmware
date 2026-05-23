import os
import time
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from llmware.parsers import Parser
from llmware.configs import LLMWareConfig
from dotenv import load_dotenv
from groq import Groq
import json

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("groq_api"))

# Initialize the FastAPI router
router = APIRouter()

# Define the folder where uploaded PDFs will be stored
UPLOAD_FOLDER = "assignment_folder"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists

# Define the API endpoint for uploading and processing the PDF
@router.post("/upload-and-process-pdf")
async def upload_and_process_pdf(
    file: UploadFile = File(...),
    query: str = Form(...),  # Query to pass to Groq
):
    """
    API endpoint to upload a PDF file, extract text from it, and query Groq.

    Parameters:
        file (UploadFile): PDF file to be uploaded and processed.
        query (str): Query to be used with Groq.

    Returns:
        dict: Extracted text from the PDF and the response from Groq.
    """
    try:
        # Save the uploaded PDF to the UPLOAD_FOLDER
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        print(f"File uploaded to: {file_path}")

        # Initialize LLMWare database
        LLMWareConfig().set_active_db("sqlite")

        # Initialize the parser
        parser = Parser()

        # Process the uploaded PDF using OCR
        t0 = time.time()
        print(f"Processing file: {file.filename}")

        parser_output = parser.parse_one_pdf_by_ocr_images(UPLOAD_FOLDER, file.filename, save_history=True)

        if parser_output:
            extracted_text = "\n\n".join(block["text"] for block in parser_output if "text" in block)
            print(f"Completed parsing {file.filename} in {time.time() - t0:.2f} seconds. Blocks created: {len(parser_output)}")
        else:
            extracted_text = "No text could be extracted from the PDF."

        # Delete the processed PDF
        os.remove(file_path)
        print(f"Deleted file: {file.filename}")

        # Pass extracted text and query to Groq for processing
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Extracted text: {extracted_text}\n\nQuery: {query}"}
            ],
            model="llama3-8b-8192",
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=False,
        )

        # Extract the response from Groq
        groq_response = chat_completion.choices[0].message.content

        # Return the extracted text and Groq's response
        return JSONResponse(
            content={
                "filename": file.filename,
                "extracted_text": extracted_text,
                "query": query,
                "groq_response": groq_response.replace("\n", "").replace("\t", "").replace('\"', ""),
            },
            status_code=200,
        )

    except Exception as e:
        # Handle errors during processing
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")