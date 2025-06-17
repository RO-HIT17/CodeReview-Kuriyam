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


@app.post("/webhook")
async def bitbucket_webhook(request: Request):
    print("[INFO] Received webhook request")

    # Get event key from headers
    event_key = request.headers.get("X-Event-Key")
    print(f"[DEBUG] Event Key: {event_key}")

    if event_key != "pullrequest:created":
        print("[INFO] Event ignored")
        return {"message": "Event ignored"}

    payload = await request.json()
    print(f"[INFO] Payload received")

    try:
        # Extract relevant info from the payload
        pr = payload["pullrequest"]
        pr_id = pr["id"]
        repo_full_name = pr["destination"]["repository"]["full_name"]  # e.g., workspace/repo
        workspace, repo_slug = repo_full_name.split("/")

        print(f"[DEBUG] PR ID: {pr_id}, Repo: {repo_full_name}")

        # Post a general comment
        message = "👋 Hello! This is an automated review comment for your new PR. We'll analyze your code shortly. Stay tuned!"
        await post_bitbucket_general_comment(
            workspace=workspace,
            repo_slug=repo_slug,
            pr_id=pr_id,
            message=message
        )

        return {"status": "comment posted"}

    except Exception as e:
        print("[ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Internal processing error")

async def post_bitbucket_general_comment(
    workspace: str,
    repo_slug: str,
    pr_id: int,
    message: str,
    username: Optional[str] = BITBUCKET_USERNAME,
    app_password: Optional[str] = BITBUCKET_APP_PASSWORD
) -> None:
    """
    Post a general comment on a Bitbucket pull request.

    Args:
        workspace (str): Bitbucket workspace name.
        repo_slug (str): Repository slug.
        pr_id (int): Pull request ID.
        message (str): The comment message to post.
        username (str, optional): Bitbucket username. Defaults to global.
        app_password (str, optional): Bitbucket app password. Defaults to global.
    """
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/comments"
    payload = {
        "content": {
            "raw": message
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            auth=(username, app_password),
            json=payload
        )

    if response.status_code in (200, 201):
        print("[✅] Comment posted successfully")
    else:
        print(f"[❌] Failed to post comment: {response.status_code} - {response.text}")