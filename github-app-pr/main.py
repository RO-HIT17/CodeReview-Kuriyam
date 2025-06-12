from fastapi import FastAPI, Request, Header
import hmac
import hashlib
import os
from handlers import comment_on_pr
from dotenv import load_dotenv

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

    # Signature verification (optional)
    if WEBHOOK_SECRET and not verify_signature(body, x_hub_signature_256):
        return {"error": "Invalid signature"}

    payload = await request.json()
    action = payload.get("action")
    event = payload.get("pull_request")
    
    if action == "opened" and event:
        pr_number = event["number"]
        repo = payload["repository"]["name"]
        owner = payload["repository"]["owner"]["login"]

        # Comment on PR
        await comment_on_pr(pr_number, repo, owner, "👋 Thanks for opening this PR! We'll review it shortly.")
    
    return {"ok": True}
