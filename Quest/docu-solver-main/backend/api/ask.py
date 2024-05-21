from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from models.question import Question
from services.llm_service import get_llm_responses

router = APIRouter()


@router.post("/ask")
async def ask_question(question: Question):
    if question.question.strip() == "":
        raise HTTPException(status_code=400, detail="Question cannot be empty")


    llm_responses = get_llm_responses(question.question)

    return JSONResponse(content={"answer": llm_responses})
