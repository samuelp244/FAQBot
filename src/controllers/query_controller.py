from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.query_service import QueryService

router = APIRouter(tags=["query"])
query_service = QueryService()

class QuestionRequest(BaseModel):
    question: str

@router.post("/ask/")
async def ask_question(request: QuestionRequest):
    """Query the FAQ system with a question"""
    try:
        response = await query_service.generate_answer(request.question)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
