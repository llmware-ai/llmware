from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import PyPDF2
from llmware.models import ModelCatalog
import os
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_pdfs"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def extract_text(file_path, page_no):
    try:
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            if 0 <= page_no < len(pdf_reader.pages):
                page = pdf_reader.pages[page_no]
                return page.extract_text()
            else:
                return None
    except FileNotFoundError:
        return None

def summarize_text(text):
    if text is not None:
        slim_model = ModelCatalog().load_model("slim-summary-tool")
        response = slim_model.function_call(text, params=["key points (3)"], function="summarize")
        return response["llm_response"]
    else:
        return "Invalid text"

def classify_tags(text):
    if text is not None:
        slim_model = ModelCatalog().load_model("slim-tags-tool")
        response = slim_model.function_call(text, params=["tags"], function="classify")
        return response["llm_response"]
    else:
        return "Invalid text"

def identify_topic(text):
    if text is not None:
        slim_model = ModelCatalog().load_model("slim-topics-tool")
        response = slim_model.function_call(text, params=["topics"], function="classify")
        return response["llm_response"]
    else:
        return "Invalid text"

def get_answer(text, question):
    if text is not None:
        questions='"'+ question+ "(explain)"+ '"'
        slim_model = ModelCatalog().load_model("slim-boolean-tool")
        response = slim_model.function_call(text, params=[questions], function="boolean")
        return response["llm_response"]
    else:
        return "Invalid text"

@app.post("/process_pdf/")
async def process_pdf(
    function_name: str = Form(...),
    page_no: int = Form(...),
    question: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    # Save the uploaded file
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    with open(file_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        pdf_pages = len(pdf_reader.pages)

    # Extract text from the specified page
    text = extract_text(file_path, page_no)
    if text is None:
        os.remove(file_path)  # Clean up the file
        raise HTTPException(status_code=404, detail="PDF or page not found")

    # Process the function call
    match function_name:
        case "get_summary":
            result = summarize_text(text)
        case "get_tags":
            result = classify_tags(text)
        case "get_topic":
            result = identify_topic(text)
        case "get_answer":
            if question is None:
                if file_path:
                    os.remove(file_path)  # Clean up the file
                raise HTTPException(status_code=400, detail=" Question not found!")
            result = get_answer(text, question)
        case _:
            if file_path:
                os.remove(file_path)  # Clean up the file
            raise HTTPException(status_code=400, detail="Invalid name")

    os.remove(file_path)  # Clean up the file
    return JSONResponse(content={"result": result, "totalpages": pdf_pages})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

