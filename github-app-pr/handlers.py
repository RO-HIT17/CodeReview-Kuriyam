import os
from github_auth import get_installation_token
import httpx

async def comment_on_pr(pr_number: int, repo: str, owner: str, body: str):
    token = await get_installation_token()
    
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    payload = {"body": body}

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=payload)
        res.raise_for_status()
        return res.json()
