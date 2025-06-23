from fastapi import FastAPI, Request, Header, HTTPException, Query
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import datetime
import httpx
import requests
import hmac, hashlib, os, re, json, textwrap

from middleware.github_auth import get_installation_token
from service.review_service import handle_pr_review

load_dotenv()
app = FastAPI()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama:7b"
FEEDBACK_FILE = "feedback_store.json"

# --------------------- Utility Functions ---------------------

def verify_signature(payload: bytes, signature: str):
    mac = hmac.new(WEBHOOK_SECRET.encode(), msg=payload, digestmod=hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, signature)

def extract_issue_number(text: str) -> str | None:
    if not text:
        return None
    match = re.search(r'#(\d+)', text)
    return match.group(1) if match else None

def load_feedbacks():
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r") as f:
            return json.load(f)
    return []

def save_feedbacks(data):
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(data, f, indent=2)

# --------------------- GitHub Webhook Handler ---------------------

@app.post("/webhook")
async def github_webhook(request: Request, x_hub_signature_256: str = Header(None)):
    body = await request.body()
    print(f"📩 Received webhook event")
    
    if WEBHOOK_SECRET and not verify_signature(body, x_hub_signature_256):
        print("❌ Invalid webhook signature")
        return {"error": "Invalid signature"}

    payload = await request.json()
    action = payload.get("action")
    event = payload.get("pull_request")

    if action != "opened" or not event:
        print("ℹ️ Ignoring non-PR-opened events")
        return {"ok": True}

    pr_number = event["number"]
    repo = payload["repository"]["name"]
    owner = payload["repository"]["owner"]["login"]
    print(f"🔍 PR #{pr_number} opened in {owner}/{repo}")

    GITHUB_TOKEN = await get_installation_token()
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    timeout = httpx.Timeout(30.0, connect=10.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            diff_resp = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}",
                headers={**headers, "Accept": "application/vnd.github.v3.diff"}
            )
            if diff_resp.status_code != 200:
                print("❌ Failed to fetch PR diff")
                return {"error": "PR diff fetch failed"}
            pr_diff = diff_resp.text

            pr_body = event.get("body", "")
            pr_title = event.get("title", "")
            issue_number = extract_issue_number(pr_body) or extract_issue_number(pr_title)

            if not issue_number:
                print("🔍 Scanning commit messages for issue link...")
                commits_resp = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits",
                    headers=headers
                )
                for commit in commits_resp.json():
                    issue_number = extract_issue_number(commit.get("commit", {}).get("message", ""))
                    if issue_number:
                        break

            if not issue_number:
                print("⚠️ No issue found")
                return {"status": "skipped", "message": "No linked issue"}

            issue_resp = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}",
                headers=headers
            )
            issue_body = issue_resp.json().get("body", "")

            print("🧠 Calling LLM for review...")
            prompt = (
                "You are a code reviewer.\n"
                "Given the following GitHub issue and PR diff, determine if the PR addresses the issue.\n"
                "Respond with YES if fully addressed, else explain why not.\n\n"
                f"Issue:\n{issue_body}\n\nPR Diff:\n{pr_diff}"
            )

            llama_resp = requests.post(OLLAMA_URL, json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            })

            llama_output = llama_resp.json().get("response", "").strip()
            clean_output = textwrap.dedent(llama_output).strip()
            GITHUB_PR_URL = f"https://github.com/{owner}/{repo}/pull/{pr_number}"

            comment_payload = {
                "body": textwrap.dedent(f"""
                    🔍 **Review Check**

                    This PR tries to address issue #{issue_number}.

                    ---

                    {clean_output}

                    ---

                    **Was this helpful?**

                    [👍 Yes](https://4bda-2405-201-e048-7046-dc8f-e49c-617e-17ec.ngrok-free.app/feedback?pr={pr_number}&issue={issue_number}&vote=up&redirect={GITHUB_PR_URL})  
                    [👎 No](https://4bda-2405-201-e048-7046-dc8f-e49c-617e-17ec.ngrok-free.app/feedback?pr={pr_number}&issue={issue_number}&vote=down&redirect={GITHUB_PR_URL})
                """).strip()
            }

            print("💬 Posting comment to PR...")
            comment_resp = await client.post(
                f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments",
                json=comment_payload,
                headers=headers
            )
            if comment_resp.status_code != 201:
                print("❌ Failed to post comment")
                raise HTTPException(status_code=comment_resp.status_code, detail="Failed to post comment")

            print("✅ Review comment posted.")
            return {"status": "success", "llama_output": llama_output}

        except Exception as e:
            print("🔥 Error:", e)
            raise HTTPException(status_code=500, detail=str(e))

# --------------------- Feedback ---------------------

@app.get("/feedback")
async def collect_feedback(
    pr: int = Query(...),
    issue: int = Query(...),
    vote: str = Query(...),
    redirect: str = Query(...),
    request: Request = None
):
    user_ip = request.client.host
    print(f"🗳 Feedback from {user_ip} on PR #{pr}, Issue #{issue}: {vote}")

    feedbacks = load_feedbacks()
    for fb in feedbacks:
        if fb["pr"] == pr and fb["issue"] == issue and fb["ip"] == user_ip:
            print("⚠️ Duplicate vote, ignoring.")
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
    print("✅ Feedback recorded")
    return RedirectResponse(url=redirect)

# --------------------- Admin API ---------------------

@app.get("/feedback-list")
async def list_feedback():
    return load_feedbacks()

@app.post("/approve-feedback")
async def approve_feedback(pr: int, issue: int, timestamp: str):
    print(f"🔐 Approving feedback for PR #{pr}, Issue #{issue}")
    feedbacks = load_feedbacks()
    for entry in feedbacks:
        if entry["pr"] == pr and entry["issue"] == issue and entry["timestamp"] == timestamp:
            entry["approved"] = True
            break
    save_feedbacks(feedbacks)
    return {"message": "Feedback approved."}

# --------------------- Admin UI ---------------------

@app.get("/admin", response_class=HTMLResponse)
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
