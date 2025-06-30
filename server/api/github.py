from fastapi import APIRouter, Request, Header, HTTPException
from services.github_review import handle_pr_review
import hmac, hashlib
from models.schemas import PRReviewRequest
from core.config import WEBHOOK_SECRET
from core.tenants import GITHUB_REPO_DATA
import requests
from utils.github_auth import get_installation_token
from fastapi import Depends
from services.auth_service import get_current_user
from sqlalchemy.orm import Session
from db.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    
    
    
    print(f"Received GitHub webhook: action={action}")
    
    if action == "opened" and event:
        
        pr_number = event["number"]
        repo = payload["repository"]["name"]
        owner = payload["repository"]["owner"]["login"]
        installation_id = payload["installation"]["id"]
        
        GITHUB_REPO_DATA[owner]= installation_id
        
    
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

@router.get("/formatted-repos")
async def formatted_repos(installation_id: int,user = Depends(get_current_user),db: Session = Depends(get_db)):
    
    user.github_installation_id = installation_id
    db.commit()
    
    token = await get_installation_token(installation_id)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(
        "https://api.github.com/installation/repositories",
        headers=headers
    )

    if response.status_code != 200:
        return {"error": response.json()}

    repos = response.json().get("repositories", [])

    formatted = []
    for repo in repos:
        formatted.append({
            "id": str(repo["id"]),
            "name": repo["name"],
            "description": repo.get("description") or "No description",
            "provider": "github",
            "private": repo["private"],
            "url": repo["html_url"],
            "language": repo.get("language") or "Unknown",
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
        })

    return formatted