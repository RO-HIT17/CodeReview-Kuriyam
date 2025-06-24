# feedback/routes.py

from fastapi import APIRouter, Query, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from feedback.store import load_feedbacks, save_feedbacks
from datetime import datetime

router = APIRouter()

@router.get("/feedback")
async def collect_feedback(pr: int = Query(...), issue: int = Query(...), vote: str = Query(...), redirect: str = Query(...), request: Request = None):
    user_ip = request.client.host
    feedbacks = load_feedbacks()
    for fb in feedbacks:
        if fb["pr"] == pr and fb["issue"] == issue and fb["ip"] == user_ip:
            return RedirectResponse(url=redirect)

    feedbacks.append({
        "timestamp": datetime.utcnow().isoformat(),
        "pr": pr,
        "issue": issue,
        "vote": vote,
        "ip": user_ip,
        "approved": False
    })
    save_feedbacks(feedbacks)
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
                    <th>Status</th>
                    <th>Action</th>
                </tr>
    """

    for fb in feedbacks:
        status = "✅ Approved" if fb["approved"] else "❌ Pending"
        css_class = "approved" if fb["approved"] else "pending"
        approve_link = (
            f"/approve-feedback?pr={fb['pr']}&issue={fb['issue']}&timestamp={fb['timestamp']}"
            if not fb["approved"] else "-"
        )
        html += f"""
            <tr>
                <td>{fb['timestamp']}</td>
                <td>{fb['pr']}</td>
                <td>{fb['issue']}</td>
                <td>{fb['vote']}</td>
                <td>{fb['ip']}</td>
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
