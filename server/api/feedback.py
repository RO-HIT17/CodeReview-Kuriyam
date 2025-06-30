from fastapi import APIRouter, Query, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from feedback.store import load_feedbacks, save_feedbacks
from fastapi import Depends
from services.auth_service import get_current_user
from models.schemas import Feedback

router = APIRouter()

@router.get("/feedback")
async def collect_feedback(
    vote: str = Query(...),
    id: str = Query(...),
    redirect: str = Query(...),
    platform: str = Query(None),
    repo: str = Query(None),
    request: Request = None,
):
    user_ip = request.client.host
    feedbacks = load_feedbacks()

    for fb in feedbacks:
        if fb["id"] == id:
            if fb["vote"] is None:
                fb["vote"] = vote
                fb["ip"] = user_ip
                if platform:
                    fb["platform"] = platform
                if repo:
                    fb["repo"] = repo
                fb["redirect"] = redirect
                save_feedbacks(feedbacks)
            break

    return RedirectResponse(url=redirect)


@router.get("/feedback-list")
async def list_feedback(user = Depends(get_current_user)):
    return load_feedbacks()


@router.post("/approve-feedback")
async def approve_feedback(payload: Feedback,user = Depends(get_current_user)):
    feedbacks = load_feedbacks()
    for entry in feedbacks:
        if entry["pr"] == payload.pr and entry["issue"] == payload.issue and entry["timestamp"] == payload.timestamp:
            entry["approved"] = True
            break
    save_feedbacks(feedbacks)
    return {"message": "Feedback approved."}

@router.post("/reject-feedback")
async def approve_feedback(payload: Feedback,user = Depends(get_current_user)):
    feedbacks = load_feedbacks()
    for entry in feedbacks:
        if entry["pr"] == payload.pr and entry["issue"] == payload.issue and entry["timestamp"] == payload.timestamp:
            entry["rejected"] = True
            break
    save_feedbacks(feedbacks)
    return {"message": "Feedback rejected."}
