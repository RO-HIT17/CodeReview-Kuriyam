from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import json
from services.bitbucket_review import  fetch_pr_diff, handle_file_review
from utils.bitbucket_utils import parse_diff
from models.schemas import TestRequest

router = APIRouter()

@router.get("/atlassian-connect.json")
async def serve_manifest():
    with open("atlassian-connect.json", "r") as f:
        manifest = json.load(f)
    return JSONResponse(content=manifest)

from utils.verify_jwt import verify_bitbucket_jwt

@router.post("/webhook")
async def bitbucket_webhook(request: Request):
    headers = request.headers
    event = headers.get("X-Event-Key")

    # JWT Verification
    try:
        path = "/bitbucket/webhook"  # Exact path in your manifest
        verify_bitbucket_jwt(headers, method="POST", path=path)
    except HTTPException as e:
        print("[❌] JWT verification failed")
        raise e

    payload = await request.json()
    print(f"[DEBUG] Received event: {event}")

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
        
        diff_text = await fetch_pr_diff(diff_url)
        print("[✅] PR diff fetched (preview):", diff_text[:500])
        files = parse_diff(diff_text)
        print(f"[DEBUG] Parsed files : {(files)} ")

        for f in files:
            await handle_file_review(f, workspace, repo_slug, pr_id)
  
        return {"status": "PR handled"}

    except Exception as e:
        print("[ERROR]", e)
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.post("/test")
async def test_endpoint(request: TestRequest):
    try:
        diff_text = await fetch_pr_diff(request.diff_url)
        print("[✅] PR diff fetched (preview):", diff_text[:500])
        files = parse_diff(diff_text)
        print(f"[DEBUG] Parsed files : {files}")

        for f in files:
            await handle_file_review(f, request.workspace, request.repo_slug, request.pr_id)

        return {"status": "PR handled successfully"}

    except Exception as e:
        print("[ERROR]", e)
        raise HTTPException(status_code=500, detail="Webhook processing failed")