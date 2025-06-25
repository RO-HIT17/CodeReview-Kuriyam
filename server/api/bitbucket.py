from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import json, os, httpx
from typing import Optional
from services.bitbucket_review import post_bitbucket_general_comment,post_inline_comment, fetch_pr_diff

router = APIRouter()

@router.get("/atlassian-connect.json")
async def serve_manifest():
    with open("atlassian-connect.json", "r") as f:
        manifest = json.load(f)
    return JSONResponse(content=manifest)


@router.post("/webhook")
async def bitbucket_webhook(request: Request):
    headers = request.headers
    event = headers.get("X-Event-Key")
    payload = await request.json()

    print(f"[DEBUG] Received event: {event}")
    print(f"[DEBUG] Payload: {json.dumps(payload, indent=2)}")
        
    if event != "pullrequest:created":
        return {"message": "Event ignored"}

    try:
        payload = payload.get("data", payload)  
        pr = payload["pullrequest"]
        pr_id = pr["id"]
        repo_full_name = pr["destination"]["repository"]["full_name"]
        workspace, repo_slug = repo_full_name.split("/")
        comments_url = pr["links"]["comments"]["href"]
        diff_url = pr["links"]["diff"]["href"]


        print(f"[INFO] Handling PR #{pr_id} in `{repo_full_name}`")
        print(f"[DEBUG] Diff URL: {diff_url}")
        print(f"[DEBUG] Comments URL: {comments_url}")
        print(f"[DEBUG] Workspace: {workspace}, Repo: {repo_slug}")
        print(f"[DEBUG] PR Title: {pr['title']}")
        
        message = f"👋 Thanks for opening PR #{pr_id} in `{repo_full_name}`! Our bot will review this soon."
        await post_bitbucket_general_comment(comments_url, message)

        diff_text = await fetch_pr_diff(diff_url)
        print("[✅] PR diff fetched (preview):", diff_text[:500])

        await post_inline_comment(
            workspace=workspace,
            repo_slug=repo_slug,
            pr_id=pr_id,
            file_path="test.js",  
            line=3,  
            message="🛠️ Consider renaming this variable for clarity."
        )

        return {"status": "PR handled"}

    except Exception as e:
        print("[ERROR]", e)
        raise HTTPException(status_code=500, detail="Webhook processing failed")
