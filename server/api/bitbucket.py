from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import json
from services.bitbucket_review import  fetch_pr_diff, handle_file_review
from utils.bitbucket_utils import parse_diff
from models.schemas import TestRequest
from utils.verify_jwt import verify_bitbucket_request
from core.config import BITBUCKET_CLIENT_ID, BITBUCKET_CLIENT_SECRET
import httpx
from fastapi.responses import RedirectResponse
from services.test import post_inline_comment
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
    
    full_url = str(request.url)
    method = request.method
    success, client_key, claims = verify_bitbucket_request(request)
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
async def on_installed(request: Request):
    data = await request.json()

    client_key = data.get("clientKey")
    shared_secret = data.get("sharedSecret")
    base_url = data.get("baseUrl")
    user = data.get("principal", {}).get("username")


    print("Data received from Bitbucket installation:", json.dumps(data, indent=2))
    print(f"[✅] App installed by: {user}")
    print(f"[🔐] Client key: {client_key}")
    print(f"[🔐] Shared secret: {shared_secret}")
    print(f"[🔗] Base URL: {base_url}")

    # 🗃️ Store this securely in your DB (keyed by clientKey)
    # e.g. db.save(client_key, shared_secret)

    return JSONResponse(content={"message": "Installation handled"})


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
    
#code="nat5cfy46sdKGmGC8v"

@router.get("/oauth/login")
def login():
    redirect_uri = "https://666f-2405-201-e048-7046-3563-b3b6-b29c-a53d.ngrok-free.app/bitbucket/oauth/callback"
    auth_url = (
        "https://bitbucket.org/site/oauth2/authorize"
        f"?client_id={BITBUCKET_CLIENT_ID}&response_type=code"
        f"&redirect_uri={redirect_uri}"
    )
    return RedirectResponse(auth_url)

@router.get("/oauth/callback")
async def oauth_callback(request: Request):
    code = request.query_params.get("code")
    redirect_uri = "https://666f-2405-201-e048-7046-3563-b3b6-b29c-a53d.ngrok-free.app/bitbucket/oauth/callback"

    token_url = "https://bitbucket.org/site/oauth2/access_token"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            token_url,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri
            },
            auth=(BITBUCKET_CLIENT_ID, BITBUCKET_CLIENT_SECRET)
        )
    token_data = response.json()
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")

    print("[✅] Access Token:", access_token)
    return {"access_token": access_token, "refresh_token": refresh_token}    

@router.post("/test/inline")
async def test_inline_comment():
    try:
        await post_inline_comment()

    except Exception as e:
        print("[ERROR]", e)
        raise HTTPException(status_code=500, detail="Webhook processing failed")