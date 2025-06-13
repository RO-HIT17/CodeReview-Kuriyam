import httpx

async def post_inline_review_comment(owner, repo, pr_number, token, file_path, comment, position):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"

    payload = {
        "body": "Suggestions by reviewer model",
        "event": "COMMENT",
        "comments": [
            {
                "path": file_path,
                "position": position,
                "body": comment
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=payload)
        return res.status_code, res.json()
