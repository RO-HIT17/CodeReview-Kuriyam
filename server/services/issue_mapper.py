from fastapi import APIRouter, Request, Header, HTTPException
from fastapi.responses import RedirectResponse
from datetime import datetime
from utils.github_auth import get_installation_token
import httpx, re, requests, os, json, textwrap

router = APIRouter()
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama:7b"
FEEDBACK_FILE = "static/feedback_store.json"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

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

@router.post("/webhook")
async def issue_mapper_webhook(request: Request, x_hub_signature_256: str = Header(None)):
    body = await request.body()
    payload = await request.json()

    # (Optional) verify_signature if shared secret is set
    if WEBHOOK_SECRET:
        import hmac, hashlib
        mac = hmac.new(WEBHOOK_SECRET.encode(), msg=body, digestmod=hashlib.sha256)
        expected = "sha256=" + mac.hexdigest()
        if not hmac.compare_digest(expected, x_hub_signature_256):
            return {"error": "Invalid signature"}

    action = payload.get("action")
    pr = payload.get("pull_request")
    if action != "opened" or not pr:
        return {"status": "skipped", "message": "Not a PR open event"}

    pr_number = pr["number"]
    repo = payload["repository"]["name"]
    owner = payload["repository"]["owner"]["login"]

    token = await get_installation_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    async with httpx.AsyncClient() as client:
        diff_resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}",
            headers={**headers, "Accept": "application/vnd.github.v3.diff"}
        )
        pr_diff = diff_resp.text
        pr_body = pr.get("body", "")
        pr_title = pr.get("title", "")
        issue_number = extract_issue_number(pr_body) or extract_issue_number(pr_title)

        if not issue_number:
            commits_resp = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits",
                headers=headers
            )
            for commit in commits_resp.json():
                issue_number = extract_issue_number(commit.get("commit", {}).get("message", ""))
                if issue_number:
                    break

        if not issue_number:
            return {"status": "skipped", "message": "No issue linked"}

        issue_resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}",
            headers=headers
        )
        issue_body = issue_resp.json().get("body", "")

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

        comment = {
            "body": textwrap.dedent(f"""
                🔍 **Review Check**

                This PR tries to address issue #{issue_number}.

                ---
                {llama_output}
                ---

                **Was this helpful?**

                [👍 Yes](/feedback?pr={pr_number}&issue={issue_number}&vote=up&redirect=https://github.com/{owner}/{repo}/pull/{pr_number})  
                [👎 No](/feedback?pr={pr_number}&issue={issue_number}&vote=down&redirect=https://github.com/{owner}/{repo}/pull/{pr_number})
            """).strip()
        }

        await client.post(
            f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments",
            json=comment,
            headers=headers
        )

        return {"status": "commented", "llama_output": llama_output}
