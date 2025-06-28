from fastapi import FastAPI, Request, HTTPException
import httpx
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()
app = FastAPI()

# Set your Bitbucket credentials via env vars or hardcode for local testing
BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME")
BITBUCKET_APP_PASSWORD = os.getenv("BITBUCKET_APP_PASSWORD")

@app.get("/")
async def root():
    return {"message": "Hello, Bitbucket Webhook!"}

@app.post("/webhook")
async def bitbucket_webhook(request: Request):
    print("[INFO] Received webhook request")

    event_key = request.headers.get("X-Event-Key")
    print(f"[DEBUG] Event Key: {event_key}")

    if event_key != "pullrequest:created":
        print("[INFO] Event ignored")
        return {"message": "Event ignored"}

    payload = await request.json()
    print(f"[INFO] Payload received")
    print("[DEBUG] Payload content:", payload)

    try:
        pr = payload["pullrequest"]
        pr_id = pr["id"]
        repo_full_name = pr["destination"]["repository"]["full_name"]
        workspace, repo_slug = repo_full_name.split("/")
        diff_url = pr["links"]["diff"]["href"]

        print(f"[DEBUG] PR ID: {pr_id}, Repo: {repo_full_name}")
        print(f"[DEBUG] Diff URL: {diff_url}")

        # General comment
        message = "👋 Hello! This is an automated review comment for your new PR. We'll analyze your code shortly. Stay tuned!"
        await post_bitbucket_general_comment(workspace, repo_slug, pr_id, message)

        # Fetch and parse the diff
        print("[INFO] Fetching PR diff...")
        diff_text = await fetch_pr_diff(workspace,diff_url)
        print("[DEBUG] Diff fetched:\n", diff_text[:500], "...\n[INFO] Diff truncated for preview")

        # Example: post an inline comment on line 3 of a file named `test.py`
        file_path = "test.js"
        line = 3
        inline_comment = "Consider renaming this variable for clarity."
        await post_inline_comment(workspace, repo_slug, pr_id, file_path, line, inline_comment)

        return {"status": "inline comment posted"}

    except Exception as e:
        print("[ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Internal processing error")

async def fetch_pr_diff(diff_url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(diff_url, auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD))
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch diff: {response.status_code} - {response.text}")

async def post_bitbucket_general_comment(
    workspace: str,
    repo_slug: str,
    pr_id: int,
    message: str,
    username: Optional[str] = BITBUCKET_USERNAME,
    app_password: Optional[str] = BITBUCKET_APP_PASSWORD
) -> None:
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/comments"
    payload = {
        "content": {"raw": message}
    }

    print(f"[DEBUG] Posting general comment to {url}")

    async with httpx.AsyncClient() as client:
        response = await client.post(url, auth=(username, app_password), json=payload)

    if response.status_code in (200, 201):
        print("[✅] General comment posted successfully")
    else:
        print(f"[❌] Failed to post general comment: {response.status_code} - {response.text}")

async def post_inline_comment(
    workspace: str,
    repo_slug: str,
    pr_id: int,
    file_path: str,
    line: int,
    message: str,
    username: Optional[str] = BITBUCKET_USERNAME,
    app_password: Optional[str] = BITBUCKET_APP_PASSWORD
):
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/comments"
    payload = {
        "inline": {
            "path": file_path,
            "to": line  # for newly added lines
        },
        "content": {
            "raw": message
        }
    }

    print(f"[DEBUG] Posting inline comment at {file_path}:{line}")

    async with httpx.AsyncClient() as client:
        response = await client.post(url, auth=(username, app_password), json=payload)

    if response.status_code in (200, 201):
        print("[✅] Inline comment posted successfully")
    else:
        print(f"[❌] Failed to post inline comment: {response.status_code} - {response.text}")
