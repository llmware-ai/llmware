from fastapi import APIRouter, File, UploadFile, HTTPException
from services.llm_service import ingest_and_index_files 
import os

router = APIRouter()

UPLOAD_DIRECTORY = "./uploaded_files"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@router.post("/upload-files")
async def upload_files(file: UploadFile = File(...)):
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in ["pdf"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)


    with open(file_location, "wb") as f:
        f.write(file.file.read())
        

    return {"info": f"file '{file.filename}' saved at '{file_location}'"}
