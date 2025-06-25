from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import json, os, httpx
from typing import Optional
from server.services.bitbucket_review import post_bitbucket_general_comment,post_inline_comment, fetch_pr_diff

router = APIRouter()

@router.get("/atlassian-connect.json")
async def serve_manifest():
    with open("atlassian-connect.json", "r") as f:
        manifest = json.load(f)
    return JSONResponse(content=manifest)


# Main webhook handler
@router.post("/webhook")
async def bitbucket_webhook(request: Request):
    headers = request.headers
    event = headers.get("X-Event-Key")
    payload = await request.json()

    if event != "pullrequest:created":
        return {"message": "Event ignored"}

    try:
        payload = payload.get("data", payload)  # unwrap if needed
        pr = payload["pullrequest"]
        pr_id = pr["id"]
        repo_full_name = pr["destination"]["repository"]["full_name"]
        workspace, repo_slug = repo_full_name.split("/")
        comments_url = pr["links"]["comments"]["href"]
        diff_url = pr["links"]["diff"]["href"]

        print(f"[INFO] Handling PR #{pr_id} in `{repo_full_name}`")
        print(f"[DEBUG] Diff URL: {diff_url}")

        # General comment
        message = f"👋 Thanks for opening PR #{pr_id} in `{repo_full_name}`! Our bot will review this soon."
        await post_bitbucket_general_comment(comments_url, message)

        # Fetch diff for future use (currently just logging)
        diff_text = await fetch_pr_diff(diff_url)
        print("[✅] PR diff fetched (preview):", diff_text[:500])

        # 🔥 You can loop over actual changes to find file + line, here's dummy:
        await post_inline_comment(
            workspace=workspace,
            repo_slug=repo_slug,
            pr_id=pr_id,
            file_path="test.js",  # replace dynamically later
            line=3,  # dummy line
            message="🛠️ Consider renaming this variable for clarity."
        )

        return {"status": "PR handled"}

    except Exception as e:
        print("[ERROR]", e)
        raise HTTPException(status_code=500, detail="Webhook processing failed")
