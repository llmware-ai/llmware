import aiofiles
import requests
from PIL import Image
from global_vars import Var
from schemas import DocData
from utils import invoke_uid
from auth.auth import get_address
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from ai_functions.detector import predictTumor
from ai_functions.vision_ai import ask_ai

doc_router = APIRouter(prefix="/document", tags=["document"])


def get_response(prompt, context):
    res = requests.post('https://aecc-35-231-142-90.ngrok-free.app/chat',
                        json={'prompt': prompt, 'context': context})
    res = res.json()
    if not res:
        return False
    res = res.get('llm_response')
    return res


classifier_prompt = "Classify the image. 1 for MRI and 2 for not MRI, only send 1 or 2 without forming any sentences"
ocr_prompt = "Provide the summary from what u are seeing document it well"


@doc_router.post("/upload")
async def upload_file(file: UploadFile, prfid: str, address=Depends(get_address)):
    extension = file.filename.split('.')[-1]
    if extension not in ['jpg', 'png', 'jpeg']:
        raise HTTPException(status_code=400, detail="Invalid file type")
    file_name = invoke_uid(10) + '.' + extension
    async with aiofiles.open('assets/' + file_name, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    pillow_img = Image.open('assets/{}'.format(file_name))
    classification = ask_ai(pillow_img, classifier_prompt)
    classification = classification[0]
    if classification == '1':
        print('got 1')
        cancer_value = predictTumor('assets/{}'.format(file_name))
        if cancer_value:
            res = 'person was daignosed severe with brain tumor'
        else:
            res = 'person is healthy'
    else:
        res = ask_ai(pillow_img, ocr_prompt)
        print(res)
    doc_data = DocData(filename=file_name, inferences=res, address=address, prfid=prfid)

    await Var.db.add_document(doc_data)
    return {'filename': file_name}


@doc_router.post("/list_documents")
async def list_documents(prfid: str, address=Depends(get_address)):
    return await Var.db.get_documents(address, prfid)

@doc_router.post("/delete_document")
async def delete_document(filename: str, prfid: str, address=Depends(get_address)):
    return await Var.db.delete_document(address, prfid, filename)

