from fastapi import FastAPI, Request, Header
from app.github_auth import get_installation_access_token
from app.utils import post_comment, get_pr_diff

app = FastAPI()




@app.post("/webhook")
async def github_webhook(request: Request, x_github_event: str = Header(None)):
    payload = await request.json()

    if x_github_event == "pull_request":
        action = payload.get("action")
        if action in ["opened", "synchronize"]:
            repo_full_name = payload["repository"]["full_name"]
            pr_number = payload["pull_request"]["number"]

            token = await get_installation_access_token()

            # 1. Post temp comment
            await post_comment(token, repo_full_name, pr_number, "👋 Reviewing your PR...")

            # 2. Get PR diff (can be passed to LLM later)
            diff_text = await get_pr_diff(token, repo_full_name, pr_number)

            print("=== DIFF START ===")
            print(diff_text[:1000])  # Print preview
            print("=== DIFF END ===")

            # In future: LLM-based review + post detailed comment

    return {"status": "ok"}
