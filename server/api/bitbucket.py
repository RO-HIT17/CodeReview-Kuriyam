from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import json
from services.bitbucket_review import  fetch_pr_diff, handle_file_review
from utils.bitbucket_utils import parse_diff
from models.schemas import TestRequest
from utils.verify_jwt import verify_bitbucket_request
from deps import get_db
from models.installation import Installation
from sqlalchemy.orm import Session
from fastapi import Depends
from core.tenants import TENANT_STORE

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
    
    success = verify_bitbucket_request(request)
    
    if not success:
        raise HTTPException(status_code=401, detail="JWT verification failed")

    payload = await request.json()
    print(f"[DEBUG] Received event: {event}")

    if event != "pullrequest:created":
        return {"message": "Event ignored"}

    try:
        pr_data = payload.get("data", payload)
        pr = pr_data["pullrequest"]
        pr_id = pr["id"]
        repo_full_name = pr["destination"]["repository"]["full_name"]
        workspace, repo_slug = repo_full_name.split("/")

        diff_url = pr["links"]["diff"]["href"]
        diff_text = await fetch_pr_diff(diff_url)
        print("[✅] PR diff fetched")

        files = parse_diff(diff_text)
        print(f"[DEBUG] Parsed files: {files}")

        for file in files:
            await handle_file_review(file, workspace, repo_slug, pr_id)

        return {"status": "PR handled successfully"}

    except Exception as e:
        print(f"[❌ ERROR] {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/installed")
async def on_installed(request: Request, db: Session = Depends(get_db)):
    data = await request.json()

    client_key = data.get("clientKey")
    shared_secret = data.get("sharedSecret")
    base_api_url = data.get("baseApiUrl")
    workspace_uuid = data.get("principal", {}).get("uuid", "").strip("{}")
    workspace_name = data.get("principal", {}).get("username")
    installed_by = data.get("actor", {}).get("account_id")

    print(f"[✅] Installed by: {workspace_name} ({installed_by})")

    TENANT_STORE[client_key] = {
        "clientKey": client_key,
        "sharedSecret": shared_secret,
        "baseUrl": base_api_url,
        "user": workspace_name
    }
    
    existing = db.query(Installation).filter_by(client_key=client_key).first()
    if existing:
        existing.shared_secret = shared_secret
        existing.base_api_url = base_api_url
        existing.workspace_uuid = workspace_uuid
        existing.workspace_name = workspace_name
        existing.installed_by_user = installed_by
    else:
        new_install = Installation(
            client_key=client_key,
            shared_secret=shared_secret,
            base_api_url=base_api_url,
            workspace_uuid=workspace_uuid,
            workspace_name=workspace_name,
            installed_by_user=installed_by,
        )
        db.add(new_install)

    db.commit()

    return JSONResponse(content={"message": "Installation stored successfully"})


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
