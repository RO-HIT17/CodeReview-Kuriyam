from fastapi import FastAPI, Request, Header , HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel

from service.review_service import handle_pr_review

import hmac, hashlib, os

load_dotenv()
app = FastAPI()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

def verify_signature(payload: bytes, signature: str):
    mac = hmac.new(WEBHOOK_SECRET.encode(), msg=payload, digestmod=hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, signature)

@app.post("/webhook")
async def github_webhook(request: Request, x_hub_signature_256: str = Header(None)):
    body = await request.body()

    if WEBHOOK_SECRET and not verify_signature(body, x_hub_signature_256):
        return {"error": "Invalid signature"}

    payload = await request.json()
    action = payload.get("action")
    event = payload.get("pull_request")
    
    if action == "opened" and event:
        pr_number = event["number"]
        repo = payload["repository"]["name"]
        owner = payload["repository"]["owner"]["login"]
        

        try:
            await handle_pr_review(owner, repo, pr_number)
            return {"status": "success", "message": "Review comments posted!"}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return {"ok": True}

class PRReviewRequest(BaseModel):
    owner: str
    repo: str
    pr_number: int

@app.post("/review-pr")
async def review_pr_route(payload: PRReviewRequest):
    try:
        await handle_pr_review(payload.owner, payload.repo, payload.pr_number)
        return {"status": "success", "message": "Review comments posted!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))