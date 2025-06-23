from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import json
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME")
BITBUCKET_APP_PASSWORD = os.getenv("BITBUCKET_APP_PASSWORD")

if not BITBUCKET_USERNAME or not BITBUCKET_APP_PASSWORD:
    raise Exception("❌ Missing Bitbucket credentials in .env file.")

app = FastAPI()

# Serve manifest file
@app.get("/atlassian-connect.json")
async def serve_manifest():
    with open("atlassian-connect.json", "r") as f:
        manifest = json.load(f)
    return JSONResponse(content=manifest)


# Reusable function to post general comment
async def post_bitbucket_general_comment(
    comments_url: str,
    message: str,
    username: str = BITBUCKET_USERNAME,
    app_password: str = BITBUCKET_APP_PASSWORD,
):
    payload = {
        "content": {
            "raw": message
        }
    }

    print(f"[🔗] URL: {comments_url}")
    print(f"[📦] Payload: {payload}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            comments_url,
            auth=(username, app_password),
            headers={"Content-Type": "application/json"},
            json=payload
        )

    if response.status_code in (200, 201):
        print("[✅] General comment posted successfully")
    else:
        print(f"[❌] Failed to post general comment: {response.status_code}")
        print(f"[📥] Response: {response.text}")
        raise HTTPException(status_code=500, detail="Bitbucket comment failed")


# Webhook listener
@app.post("/webhook")
async def webhook(request: Request):
    headers = request.headers
    event = headers.get("X-Event-Key")
    payload = await request.json()

    if event != "pullrequest:created":
        return {"message": "Event ignored"}

    payload = payload.get("data", payload)  # fallback in case "data" is not wrapped

    try:
        pr = payload["pullrequest"]
        pr_id = pr["id"]
        repo_full_name = pr["destination"]["repository"]["full_name"]
        comments_url = pr["links"]["comments"]["href"]

        message = "👋 Thanks for creating this pull request! Our bot will review your code shortly."

        # Use the reusable comment function
        await post_bitbucket_general_comment(comments_url, message)

        return {"status": "comment posted"}

    except Exception as e:
        print("[ERROR]", e)
        raise HTTPException(status_code=500, detail="Webhook processing failed")
