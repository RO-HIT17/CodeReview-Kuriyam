from fastapi import APIRouter, Request
from app.services.github import fetch_pr_diff
from app.services.reviewer import review_with_model
import asyncio

router = APIRouter()

@router.post("/webhook")
async def webhook_handler(request: Request):
    payload = await request.json()

    if payload.get("action") == "opened" and "pull_request" in payload:
        pr = payload["pull_request"]
        repo = payload["repository"]

        owner = repo["owner"]["login"]
        repo_name = repo["name"]
        pr_number = pr["number"]

        diff = await fetch_pr_diff(owner, repo_name, pr_number)
        review = await review_with_model(diff)

        # Optional: post back to PR
        print(f"\n--- Review Suggestion ---\n{review}")

    return {"status": "ok"}
