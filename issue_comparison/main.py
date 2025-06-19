from fastapi import FastAPI, Request, Header , HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
import httpx
from middleware.github_auth import get_installation_token
from service.review_service import handle_pr_review
import requests
import hmac, hashlib, os
class CheckPRRequest(BaseModel):
    owner: str
    repo: str
    pr_number: int
    issue_number: int
    
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
 
GITHUB_TOKEN = "ghs_DJwVDDibYMBHBe8xDpHtHKPB4raWBO2Ed8Ea"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama:7b"

OWNER = "RO-HIT17"
REPO = "CodeReview-Kuriyam"
PR_NUMBER = 31
ISSUE_NUMBER = 30

@app.post("/check-and-comment")
async def check_and_comment():
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    timeout = httpx.Timeout(30.0, connect=10.0)  # 30 sec total, 10 sec connect timeout

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            print("➡️ Fetching PR diff...")
            diff_resp = await client.get(
                f"https://api.github.com/repos/{OWNER}/{REPO}/pulls/{PR_NUMBER}",
                headers={**headers, "Accept": "application/vnd.github.v3.diff"}
            )
            print("✅ PR diff fetched.")
            if diff_resp.status_code != 200:
                print(f"❌ PR diff fetch failed: {diff_resp.text}")
                raise HTTPException(status_code=diff_resp.status_code, detail="Failed to fetch PR diff")
            pr_diff = diff_resp.text

            print("➡️ Fetching issue description...")
            issue_resp = await client.get(
                f"https://api.github.com/repos/{OWNER}/{REPO}/issues/{ISSUE_NUMBER}",
                headers=headers
            )
            print("✅ Issue description fetched.")
            if issue_resp.status_code != 200:
                print(f"❌ Issue fetch failed: {issue_resp.text}")
                raise HTTPException(status_code=issue_resp.status_code, detail="Failed to fetch issue description")
            issue_body = issue_resp.json().get("body", "")

            print("➡️ Sending prompt to CodeLlama...")
            prompt = (
                "You are a code reviewer.\n"
                "Given the following GitHub issue and PR diff, determine if the PR addresses the issue.\n"
                "Respond with YES if fully addressed, else explain why not.\n\n"
                f"Issue:\n{issue_body}\n\nPR Diff:\n{pr_diff}"
            )
            llama_payload = {
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            }

            res = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    })
            print("✅ CodeLlama response received.")
            llama_output = res.json().get("response", "").strip()

            if True:
                print("📝 Posting review comment to PR...")
                comment_payload = {
                    "body": f"🔍 **Review Check**:\n\nThis PR  address the issue #{ISSUE_NUMBER}.\n\n\n{llama_output}"
                }
                comment_resp = await client.post(
                    f"https://api.github.com/repos/{OWNER}/{REPO}/issues/{PR_NUMBER}/comments",
                    json=comment_payload,
                    headers=headers
                )
                if comment_resp.status_code != 201:
                    print(f"❌ Failed to post PR comment: {comment_resp.text}")
                    raise HTTPException(status_code=comment_resp.status_code, detail="Failed to post PR comment")
                print("✅ Comment posted to PR.")

            return {"status": "done", "llama_output": llama_output}
        
        except Exception as e:
            print("🔥 Exception occurred:", str(e))
            raise HTTPException(status_code=500, detail=str(e))