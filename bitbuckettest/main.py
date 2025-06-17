from fastapi import FastAPI, Request, HTTPException
import httpx
import os

app = FastAPI()

# Set your Bitbucket credentials via env vars or hardcode for local testing
BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME", "RO_HIT17")
BITBUCKET_APP_PASSWORD = os.getenv("BITBUCKET_APP_PASSWORD", "ATBBn6xXftHzwEQGznusTSTm62spF11B4CC6")


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
        await post_bitbucket_general_comment(workspace, repo_slug, pr_id, message)

        return {"status": "comment posted"}

    except Exception as e:
        print("[ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Internal processing error")


async def post_bitbucket_general_comment(workspace: str, repo_slug: str, pr_id: int, message: str):
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/comments"

    payload = {
        "content": {
            "raw": message
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD),
            json=payload
        )

        if response.status_code not in [200, 201]:
            print(f"[ERROR] Failed to comment: {response.status_code} - {response.text}")
        else:
            print("[SUCCESS] General comment posted successfully")
