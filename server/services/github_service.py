import httpx
from utils.github_auth import get_installation_token

async def get_pr_files(repo: str, owner: str, pr_number: int , installation_id: int):
    
    token = await get_installation_token(installation_id)

    print("TOKEN:", token)    
    
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        res.raise_for_status()
        return res.json()

async def get_latest_commit_sha(owner, repo, pr_number,installation_id):
    token = await get_installation_token(installation_id)
    
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        res.raise_for_status()
        return res.json()["head"]["sha"]

async def post_inline_comment(owner, repo, pr_number, file_path, position, comment, commit_id,installation_id):
    token = await get_installation_token(installation_id)
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

async def get_pr_metadata(repo, owner, pr_number, installation_id):
    token = await get_installation_token(installation_id)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()

async def get_pr_commits(repo, owner, pr_number, installation_id):
    token = await get_installation_token(installation_id)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()
    
    
async def get_issue_details(owner: str, repo: str, issue_number: str, installation_id: int):
    token = await get_installation_token(installation_id)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}",
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        return data.get("title", ""), data.get("body", "")
    
async def post_issue_check_comment(owner, repo, pr_number, issue_number, comment_body, installation_id):
    token = await get_installation_token(installation_id)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments",
            json={"body": comment_body},
            headers=headers
        )    