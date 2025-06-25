import httpx
from fastapi import HTTPException
from core.config import BITBUCKET_APP_PASSWORD, BITBUCKET_USERNAME
from typing import Optional

async def post_bitbucket_general_comment(comments_url: str, message: str):
    payload = {
        "content": {"raw": message}
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            comments_url,
            auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD),
            headers={"Content-Type": "application/json"},
            json=payload
        )

    if response.status_code in (200, 201):
        print("[✅] Bitbucket general comment posted")
    else:
        print(f"[❌] Failed to post general comment: {response.status_code}, {response.text}")
        raise HTTPException(status_code=500, detail="Bitbucket comment failed")


async def post_inline_comment(
    workspace: str,
    repo_slug: str,
    pr_id: int,
    file_path: str,
    line: int,
    message: str,
    username: Optional[str] = BITBUCKET_USERNAME,
    app_password: Optional[str] = BITBUCKET_APP_PASSWORD
):
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/comments"
    payload = {
        "inline": {
            "path": file_path,
            "to": line  
        },
        "content": {
            "raw": message
        }
    }

    print(f"[DEBUG] Posting inline comment at {file_path}:{line}")

    async with httpx.AsyncClient() as client:
        response = await client.post(url, auth=(username, app_password), json=payload)

    if response.status_code in (200, 201):
        print("[✅] Inline comment posted successfully")
    else:
        print(f"[❌] Failed to post inline comment: {response.status_code}, {response.text}")
        raise HTTPException(status_code=500, detail="Bitbucket inline comment failed")

async def fetch_pr_diff(diff_url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(diff_url, auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD))
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch diff: {response.status_code} - {response.text}")
