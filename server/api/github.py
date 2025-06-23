# api/github.py

from fastapi import APIRouter, Request
from services.github_review import handle_github_pr_event

router = APIRouter()

@router.post("/github/webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    response = await handle_github_pr_event(payload)
    return {"status": "processed", "details": response}
