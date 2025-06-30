import json

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from services.bitbucket_review import  fetch_pr_diff, handle_file_review 
from utils.bitbucket_utils import parse_diff
from models.schemas import TestRequest
from middleware.verify_jwt import verify_bitbucket_request
from fastapi import Depends
from services.auth_service import get_current_user
from db.database import get_db
from sqlalchemy.orm import Session

from core.tenants import BITBUCKET_CONNECT_APP_DATA, BITBUCKET_NEW_REPO_DATA

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
    
    print("BITBUCKET_CONNECT_APP_DATA contents:", json.dumps(BITBUCKET_CONNECT_APP_DATA, indent=2)) 
    
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
        diff_text = await fetch_pr_diff(workspace,diff_url)
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
async def on_installed(request: Request):
    data = await request.json()

    client_key = data.get("clientKey")
    shared_secret = data.get("sharedSecret")
    base_api_url = data.get("baseApiUrl")
    workspace_uuid = data.get("principal", {}).get("uuid", "").strip("{}")
    workspace_name = data.get("principal", {}).get("username")
    installed_by = data.get("actor", {}).get("account_id")
    created_at = data.get("principal", {}).get("created_on")

    BITBUCKET_NEW_REPO_DATA["data"] = {
        "clientKey": client_key,
        "sharedSecret": shared_secret,
        "baseApiUrl": base_api_url,
        "workspaceUuid": workspace_uuid,    
        "workspaceName": workspace_name,
        "installedByUser": installed_by,   
        "createdAt": created_at,
    }
    
    print(f"[✅] Installed by: {workspace_name} ({installed_by})")

    BITBUCKET_CONNECT_APP_DATA[workspace_name] = {
    "clientKey": client_key,
    "sharedSecret": shared_secret,
    "baseApiUrl": base_api_url,
    "workspaceUuid": workspace_uuid,
    "workspaceName": workspace_name,
    "installedByUser": installed_by,
    "tenant": {
        "clientKey": client_key,
        "sharedSecret": shared_secret
    }
}
    
    return JSONResponse(content={"message": "Installation stored successfully"})


@router.post("/test")
async def test_endpoint(request: TestRequest):
    try:
        diff_text = await fetch_pr_diff(request.workspace,request.diff_url)
        print("[✅] PR diff fetched (preview):", diff_text[:500])
        files = parse_diff(diff_text)
        print(f"[DEBUG] Parsed files : {files}")

        for f in files:
            await handle_file_review(f, request.workspace, request.repo_slug, request.pr_id)

        return {"status": "PR handled successfully"}

    except Exception as e:
        print("[ERROR]", e)
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.post("/workspaces")
async def get_workspaces(user = Depends(get_current_user),db: Session = Depends(get_db)):
    try:
        if BITBUCKET_NEW_REPO_DATA:
            user.bitbucket_repo_data = BITBUCKET_NEW_REPO_DATA["data"]
            db.commit()

            return JSONResponse(content={
                "data": BITBUCKET_NEW_REPO_DATA["data"]
            })
        else :
            return JSONResponse(content={
                "data": None
            })    
    except Exception as e:
        print("[ERROR]", e)
        raise HTTPException(status_code=500, detail="Failed to update workspaces")