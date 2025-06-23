# api/feedback.py

from fastapi import APIRouter, Request
from feedback.store import store_feedback_vote

router = APIRouter()

@router.post("/feedback")
async def feedback_endpoint(request: Request):
    data = await request.json()
    store_feedback_vote(data)
    return {"status": "feedback recorded"}
