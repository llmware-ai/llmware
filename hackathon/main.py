from fastapi import FastAPI, UploadFile
from ocr import ocr_answer_sheet
from embeddings import generate_embeddings, store_embeddings, retrieve_similar_content, evaluate_answer, generate_report
from feedback import generate_feedback
from llmware.configs import LLMWareConfig
import pinecone

# Initialize FastAPI app
app = FastAPI()

# Initialize Pinecone and LLMWare clients
pinecone.init(api_key="pcsk_4W8J2V_9PxDugonc2vKaa9dBynY4uS9kro38JNnjo1zgSLCdpMQLeGzvmMfmm4ynWios6F", environment="us-west1-gcp")
index = pinecone.Index("exam-eval")

@app.post("/upload")
async def upload_file(file: UploadFile):
    # OCR extraction of student answers
    text = ocr_answer_sheet(file.file)
    
    # Assuming you have a predefined answer key
    answer_key = {
        # Question ID: Answer Text (Use your actual answer key here)
    }

    # Process answers and generate the report
    report = generate_report(text, answer_key)

    return {"report": report}
