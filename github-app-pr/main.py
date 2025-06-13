from fastapi import FastAPI, Request, Header
import hmac, hashlib, os
from app.utils import comment_on_pr, get_pr_diff, generate_review_comment
from dotenv import load_dotenv
from app.github_auth import get_installation_token
from app.inline_test import post_inline_comment
from pydantic import BaseModel
from app.review_service import handle_pr_review
from fastapi import HTTPException
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

        try:
            await handle_pr_review(owner, repo, pr_number)
            return {"status": "success", "message": "Review comments posted!"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return {"ok": True}

@app.post("/test-pr")
async def test_pr():
    print("🔥 Called /test-pr endpoint")

    pr_number = 14
    repo = "CodeReview-Kuriyam"
    owner = "RO-HIT17"
    repo_full_name = f"{owner}/{repo}"

    diff_text = await get_pr_diff(repo_full_name, pr_number)
    review_comment = await generate_review_comment(diff_text)
    await comment_on_pr(pr_number, repo, owner, review_comment)

    return {"status": "Test comment sent"}

@app.post("/test-inline-comment")
async def test_inline_comment(request: Request):
    data = await request.json()
    
    owner = data["owner"]
    repo = data["repo"]
    pr_number = data["pr_number"]
    file_path = data["file_path"]
    line = data["line"]
    comment = data["comment"]
    
    
    token = await get_installation_token()

    status_code, res = await post_inline_comment(
        owner, repo, pr_number, token, file_path, comment, line
    )
    return {"status": status_code, "response": res}


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