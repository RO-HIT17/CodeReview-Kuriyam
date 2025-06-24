from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import json, os, httpx
from core.config import BITBUCKET_APP_PASSWORD, BITBUCKET_USERNAME

router = APIRouter()

@router.get("/atlassian-connect.json")
async def serve_manifest():
    with open("atlassian-connect.json", "r") as f:
        manifest = json.load(f)
    return JSONResponse(content=manifest)


async def post_bitbucket_general_comment(comments_url: str, message: str):
    payload = {
        "content": {"raw": message}
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            comments_url,
            auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD),
            headers={"Content-Type": "application/json"},
            json=payload
        )

    if response.status_code in (200, 201):
        print("[✅] Bitbucket comment posted")
    else:
        print(f"[❌] Failed to comment: {response.status_code}, {response.text}")
        raise HTTPException(status_code=500, detail="Bitbucket comment failed")

# Webhook handler
@router.post("/webhook")
async def bitbucket_webhook(request: Request):
    headers = request.headers
    event = headers.get("X-Event-Key")
    payload = await request.json()

    if event != "pullrequest:created":
        return {"message": "Event ignored"}

    try:
        payload = payload.get("data", payload)  # unwrap if necessary
        pr = payload["pullrequest"]
        pr_id = pr["id"]
        comments_url = pr["links"]["comments"]["href"]
        repo_full_name = pr["destination"]["repository"]["full_name"]

        message = f"👋 Thanks for opening PR #{pr_id} in `{repo_full_name}`! Our bot will review this soon."

        await post_bitbucket_general_comment(comments_url, message)

        return {"status": "comment posted"}

    except Exception as e:
        print("[ERROR]", e)
        raise HTTPException(status_code=500, detail="Webhook processing failed")
