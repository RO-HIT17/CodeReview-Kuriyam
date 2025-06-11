import jwt
from datetime import datetime, timedelta
from pathlib import Path
import httpx
import os

def generate_jwt():
    app_id = os.getenv("GITHUB_APP_ID")
    private_key = Path(os.getenv("GITHUB_PRIVATE_KEY_PATH")).read_text()

    now = int(datetime.utcnow().timestamp())
    payload = {
        "iat": now,
        "exp": now + (10 * 60),
        "iss": app_id
    }

    return jwt.encode(payload, private_key, algorithm="RS256")

async def get_installation_token():
    jwt_token = generate_jwt()
    install_id = os.getenv("GITHUB_INSTALLATION_ID")

    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"https://api.github.com/app/installations/{install_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github+json"
            }
        )
        return res.json()["token"]

async def fetch_pr_diff(owner, repo, pr_number):
    token = await get_installation_token()
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"

    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers={"Authorization": f"Bearer {token}"})
        return "\n".join(file.get("patch", "") for file in res.json())
