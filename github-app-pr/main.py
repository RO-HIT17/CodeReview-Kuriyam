from fastapi import FastAPI, Request, Header
import hmac, hashlib, os
from app.utils import comment_on_pr, get_pr_diff, generate_review_comment
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
        repo_full_name = payload["repository"]["full_name"]

        # ✅ Fetch PR diff
        diff_text = await get_pr_diff(repo_full_name, pr_number)
        
        # 🧠 Send to Ollama for review
        review_comment = await generate_review_comment(diff_text)

        # 💬 Post review comment on PR
        await comment_on_pr(pr_number, repo, owner, review_comment)

    return {"ok": True}

@app.post("/test-pr")
async def test_pr():
    print("🔥 Called /test-pr endpoint")

    pr_number = 14
    repo = "CodeReview-Kuriyam"
    owner = "RO-HIT17"
    repo_full_name = f"{owner}/{repo}"

    # Test flow
    diff_text = await get_pr_diff(repo_full_name, pr_number)
    review_comment = await generate_review_comment(diff_text)
    await comment_on_pr(pr_number, repo, owner, review_comment)

    return {"status": "Test comment sent"}
