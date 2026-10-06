import os
import time
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from llmware.parsers import Parser
from llmware.configs import LLMWareConfig
from llmware.models import ModelCatalog
from dotenv import load_dotenv
from groq import Groq
import json



load_dotenv()

client = Groq(api_key=os.getenv("groq_api"))

# Initialize the FastAPI router
router = APIRouter()

# Define the folder where uploaded PDFs will be stored
UPLOAD_FOLDER = "assignment_folder"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists
# Register the Ollama model (you can register multiple models similarly)




@router.post("/upload-and-process-pdf")
async def upload_and_process_pdf(
    file: UploadFile = File(...),
    teacher_answer: str = Form(...)
):
    """
    API endpoint to upload a PDF file, process it using OCR, and delete the file afterward.
    Also accepts the teacher's answer as input.

    Parameters:
        file (UploadFile): PDF file to be uploaded and processed.
        teacher_answer (str): Teacher's answer as a text input.

    Returns:
        dict: Extracted text from the PDF and the teacher's answer.
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

        example = {"mark": 100}
        # Send a request to the Groq LLM for grading
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a teacher who excels in grading assignments."
                },
                {
                    "role": "user",
                    "content": (f"""
                                I will give you two texts: one by the student and the other by the teacher (correct answer). 
                                Refer to both and give the student a mark out of 100.\n\n
                                Student's answer: {extracted_text}\n\n
                                Teacher's reference: {teacher_answer}
                                return  only integer mark out of 100 example: {json.dumps(example)} no other text 
                                """
                                ),
                }
            ],
            model="llama-3.1-70b-versatile",
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=False,
        )

        # Extract the response
        graded_response = chat_completion.choices[0].message.content


        # Return the extracted text along with the teacher's answer
        return JSONResponse(
            content={
                "filename": file.filename,
                "extracted_text": extracted_text,
                "teacher_answer": teacher_answer,
                "mark"  : json.loads(graded_response.replace('\"', '"')),
            },
            status_code=200,
        )

    except Exception as e:
        # Handle errors during processing
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")