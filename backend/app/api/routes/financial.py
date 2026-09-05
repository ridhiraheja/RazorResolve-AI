"""
Financial Chat router — provides educational stock analysis, comparisons, and financial metric Q&A.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.financial_analysis import analyze_financial_message

router = APIRouter(prefix="/financial", tags=["financial-chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def financial_chat(req: ChatRequest):
    """
    Process natural language financial questions, stock analysis requests,
    or company comparisons.
    """
    if not req.message or not req.message.strip():
        raise HTTPException(400, "Message cannot be empty")

    try:
        res = analyze_financial_message(req.message)
        return res
    except Exception as e:
        raise HTTPException(500, f"Error processing financial analysis: {str(e)}")
