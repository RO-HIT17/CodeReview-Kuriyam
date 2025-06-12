from fastapi import FastAPI, Request, Header
import hmac, hashlib, os
from app.utils import comment_on_pr
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

    if WEBHOOK_SECRET and not verify_signature(body, x_hub_signature_256):
        return {"error": "Invalid signature"}

    payload = await request.json()
    action = payload.get("action")
    event = payload.get("pull_request")
    
    if action == "opened" and event:
        pr_number = event["number"]
        repo = payload["repository"]["name"]
        owner = payload["repository"]["owner"]["login"]

        await comment_on_pr(pr_number, repo, owner, "👋 Thanks for opening this PR! We'll review it shortly.")
    
    return {"ok": True}

@app.post("/test-pr")
async def test_pr():
    print("🔥 Called /test-pr endpoint")

    pr_number = 11
    repo = "CodeReview-Kuriyam"
    owner = "RO-HIT17"

    await comment_on_pr(
        pr_number=pr_number,
        repo=repo,
        owner=owner,
        message="✅ Test comment from /test-pr endpoint"
    )

    return {"status": "Test comment sent"}
