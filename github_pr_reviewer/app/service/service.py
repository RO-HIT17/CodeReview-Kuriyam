import httpx
from app.middleware.github_auth import get_installation_token

async def get_pr_files(repo: str, owner: str, pr_number: int):
    token = await get_installation_token()
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        res.raise_for_status()
        return res.json()

async def get_latest_commit_sha(owner, repo, pr_number):
    token = await get_installation_token()
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        res.raise_for_status()
        return res.json()["head"]["sha"]

async def post_inline_comment(owner, repo, pr_number, file_path, position, comment, commit_id):
    token = await get_installation_token()
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    data = {
        "body": comment,
        "commit_id": commit_id,
        "path": file_path,
        "line": position,
        "side": "RIGHT"  
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=data)
        res.raise_for_status()
