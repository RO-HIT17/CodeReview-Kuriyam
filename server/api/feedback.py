from fastapi import APIRouter, Query, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from feedback.store import load_feedbacks, save_feedbacks

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
async def list_feedback():
    return load_feedbacks()


@router.post("/approve-feedback")
async def approve_feedback(pr: int, issue: int, timestamp: str):
    feedbacks = load_feedbacks()
    for entry in feedbacks:
        if entry["pr"] == pr and entry["issue"] == issue and entry["timestamp"] == timestamp:
            entry["approved"] = True
            break
    save_feedbacks(feedbacks)
    return {"message": "Feedback approved."}


@router.get("/admin", response_class=HTMLResponse)
async def admin_panel():
    feedbacks = load_feedbacks()

    html = """
    <html>
        <head>
            <title>Feedback Admin Panel</title>
            <style>
                body { font-family: Arial; padding: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .approved { color: green; font-weight: bold; }
                .pending { color: red; font-weight: bold; }
            </style>
        </head>
        <body>
            <h2>🛠 Feedback Admin Panel</h2>
            <table>
                <tr>
                    <th>Timestamp</th>
                    <th>PR</th>
                    <th>Issue</th>
                    <th>Vote</th>
                    <th>IP</th>
                    <th>Platform</th>
                    <th>Repo</th>
                    <th>Redirect</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
    """

    for fb in feedbacks:
        status = "✅ Approved" if fb.get("approved") else "❌ Pending"
        css_class = "approved" if fb.get("approved") else "pending"
        approve_link = (
            f"/approve-feedback?pr={fb['pr']}&issue={fb['issue']}&timestamp={fb['timestamp']}"
            if not fb.get("approved") else "-"
        )

        html += f"""
            <tr>
                <td>{fb.get('timestamp', '-')}</td>
                <td>{fb.get('pr', '-')}</td>
                <td>{fb.get('issue', '-')}</td>
                <td>{fb.get('vote', '-')}</td>
                <td>{fb.get('ip', '-')}</td>
                <td>{fb.get('platform', '-')}</td>
                <td>{fb.get('repo', '-')}</td>
                <td><a href="{fb.get('redirect', '#')}" target="_blank">🔗</a></td>
                <td class="{css_class}">{status}</td>
                <td>{f'<a href="{approve_link}">Approve</a>' if approve_link != '-' else '-'}</td>
            </tr>
        """

    html += """
            </table>
        </body>
    </html>
    """
    return HTMLResponse(content=html)
