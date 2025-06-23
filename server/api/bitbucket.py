# api/bitbucket.py

from fastapi import APIRouter, Request
from services.bitbucket_review import handle_bitbucket_pr_event

router = APIRouter()

@router.post("/bitbucket/webhook")
async def bitbucket_webhook(request: Request):
    payload = await request.json()
    return handle_bitbucket_pr_event(payload)
