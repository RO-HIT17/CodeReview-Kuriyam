from fastapi import FastAPI, Request, Header, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
import httpx
import requests
import hmac, hashlib, os, re

from middleware.github_auth import get_installation_token
from service.review_service import handle_pr_review

load_dotenv()
app = FastAPI()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama:7b"

def verify_signature(payload: bytes, signature: str):
    mac = hmac.new(WEBHOOK_SECRET.encode(), msg=payload, digestmod=hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, signature)

def extract_issue_number(text: str) -> str | None:
    if not text:
        return None
    print("🔍 Scanning text for issue reference...")
    match = re.search(r'#(\d+)', text)
    if match:
        issue_num = match.group(1)
        print(f"✅ Found issue number: #{issue_num}")
        return issue_num
    print("⚠️ No issue reference found in this text.")
    return None

@app.post("/webhook")
async def github_webhook(request: Request, x_hub_signature_256: str = Header(None)):
    body = await request.body()
    GITHUB_TOKEN = await get_installation_token()

    if WEBHOOK_SECRET and not verify_signature(body, x_hub_signature_256):
        print("❌ Signature verification failed.")
        return {"error": "Invalid signature"}

    payload = await request.json()
    action = payload.get("action")
    event = payload.get("pull_request")

    print(f"📩 Received webhook - action: {action}")

    if action == "opened" and event:
        pr_number = event["number"]
        repo = payload["repository"]["name"]
        owner = payload["repository"]["owner"]["login"]

        print(f"➡️ PR opened: #{pr_number} in {owner}/{repo}")

        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

        timeout = httpx.Timeout(30.0, connect=10.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                print("➡️ Fetching PR diff...")
                diff_resp = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}",
                    headers={**headers, "Accept": "application/vnd.github.v3.diff"}
                )
                if diff_resp.status_code != 200:
                    print(f"❌ Failed to fetch PR diff: {diff_resp.text}")
                    raise HTTPException(status_code=diff_resp.status_code, detail="Failed to fetch PR diff")
                pr_diff = diff_resp.text
                print("✅ PR diff fetched.")

                # Try to extract issue number from PR body, title, and commit messages
                print("🔎 Attempting to extract linked issue...")
                pr_body = event.get("body", "")
                pr_title = event.get("title", "")
                issue_number = extract_issue_number(pr_body) or extract_issue_number(pr_title)

                # If still not found, check commit messages
                if not issue_number:
                    print("➡️ Checking commits in the PR...")
                    commits_resp = await client.get(
                        f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits",
                        headers=headers
                    )
                    if commits_resp.status_code == 200:
                        commits = commits_resp.json()
                        for commit in commits:
                            message = commit.get("commit", {}).get("message", "")
                            issue_number = extract_issue_number(message)
                            if issue_number:
                                break
                    else:
                        print(f"⚠️ Could not fetch commits: {commits_resp.text}")

                if not issue_number:
                    print("⚠️ No linked issue found in PR body, title, or commits.")
                    return {"status": "skipped", "message": "No issue linked in PR body, title, or commits"}

                print(f"➡️ Fetching issue #{issue_number}...")
                issue_resp = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}",
                    headers=headers
                )
                if issue_resp.status_code != 200:
                    print(f"❌ Failed to fetch issue: {issue_resp.text}")
                    raise HTTPException(status_code=issue_resp.status_code, detail="Failed to fetch issue")
                issue_body = issue_resp.json().get("body", "")
                print("✅ Issue fetched.")

                print("➡️ Sending prompt to CodeLlama...")
                prompt = (
                    "You are a code reviewer.\n"
                    "Given the following GitHub issue and PR diff, determine if the PR addresses the issue.\n"
                    "Respond with YES if fully addressed, else explain why not.\n\n"
                    f"Issue:\n{issue_body}\n\nPR Diff:\n{pr_diff}"
                )

                res = requests.post(OLLAMA_URL, json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False
                })
                llama_output = res.json().get("response", "").strip()
                print("✅ LLM response received.")

                comment_payload = {
                    "body": f"🔍 **Review Check**:\n\nThis PR tries to address issue #{issue_number}.\n\n{llama_output}"
                }

                print("➡️ Posting comment to PR...")
                comment_resp = await client.post(
                    f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments",
                    json=comment_payload,
                    headers=headers
                )
                if comment_resp.status_code != 201:
                    print(f"❌ Failed to post comment: {comment_resp.text}")
                    raise HTTPException(status_code=comment_resp.status_code, detail="Failed to post PR comment")

                print("✅ Review comment posted.")
                return {"status": "success", "llama_output": llama_output}

            except Exception as e:
                print("🔥 Exception occurred:", str(e))
                raise HTTPException(status_code=500, detail=str(e))

    print("ℹ️ Event not handled.")
    return {"ok": True}
