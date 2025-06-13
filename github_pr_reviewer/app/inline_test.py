import httpx
from app.github_auth import get_installation_token
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


async def post_inline_comment(owner, repo, pr_number, token, file_path, comment, line ):
    """
    Posts a single inline comment on a pull request at a specific position in the diff.
    Requires the latest commit SHA as `commit_id`.
    """
    commit_id = await get_latest_commit_sha(owner, repo, pr_number)
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"

    payload = {
        "body": comment,
        "commit_id": commit_id,
        "path": file_path,
        "line": line,
        "side": "RIGHT"  # Use "RIGHT" for the PR diff side
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=payload)
        return res.status_code, res.json()
