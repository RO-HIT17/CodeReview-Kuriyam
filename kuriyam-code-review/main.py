from fastapi import FastAPI, Request, Header , HTTPException
from pydantic import BaseModel
import os
from utils.verify import verify_signature
from fastapi.responses import JSONResponse
import json

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

@app.post("/webhook")
async def github_webhook(request: Request, x_hub_signature_256: str = Header(None)):
    body = await request.body()

    if WEBHOOK_SECRET and not verify_signature(body, x_hub_signature_256):
        return {"error": "Invalid signature"}

    payload = await request.json()
    action = payload.get("action")
    event = payload.get("pull_request")

    print("Received webhook event:", action, event)
    print("Payload:", payload)
        
    if action == "opened" and event:
        pr_number = event["number"]
        repo = payload["repository"]["name"]
        owner = payload["repository"]["owner"]["login"]
    
    return {"ok": True}


@app.get("/test.json")
async def serve_manifest():
    with open("test.json", "r") as f:
        manifest = json.load(f)
    return JSONResponse(content=manifest)

@app.get("/test1.json")
async def serve_manifest():
    with open("test1.json", "r") as f:
        manifest = json.load(f)
    return JSONResponse(content=manifest)