from fastapi import APIRouter, Request, Header, HTTPException
from services.github_review import handle_pr_review
import hmac, hashlib
from models.schemas import PRReviewRequest
from core.config import WEBHOOK_SECRET
from core.tenants import GITHUB_REPO_DATA
router = APIRouter()

def verify_signature(payload: bytes, signature: str):
    mac = hmac.new(WEBHOOK_SECRET.encode(), msg=payload, digestmod=hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, signature)

@router.post("/webhook")
async def github_webhook(request: Request, x_hub_signature_256: str = Header(None)):
    body = await request.body()

    if WEBHOOK_SECRET and not verify_signature(body, x_hub_signature_256):
        return {"error": "Invalid signature"}

    payload = await request.json()
    action = payload.get("action")
    event = payload.get("pull_request")
    
    pr_number = event["number"]
    repo = payload["repository"]["name"]
    owner = payload["repository"]["owner"]["login"]
    installation_id = payload["installation"]["id"]
    
    GITHUB_REPO_DATA[owner]= installation_id
    
    
    print(f"Received GitHub webhook: action={action}")
    
    if action == "opened" and event:
        
        
        try:
            await handle_pr_review(owner, repo, pr_number,installation_id)
            
            return {"status": "success", "message": "Review comments posted!"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {"ok": True}


@router.post("/review-pr")
async def review_pr_route(payload: PRReviewRequest):
    try:
        await handle_pr_review(payload.owner, payload.repo, payload.pr_number, payload.installation_id)
        return {"status": "success", "message": "Review comments posted!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
