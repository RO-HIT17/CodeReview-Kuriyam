import httpx
from app.github_auth import get_installation_token
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama:7b"

async def comment_on_pr(pr_number: int, repo: str, owner: str, message: str):
    token = await get_installation_token()
    #print("Using token:", token)
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    payload = {"body": message}

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=payload)
        res.raise_for_status()
        return res.json()


async def get_pr_diff(repo_full_name: str, pr_number: int) -> str:
    token = await get_installation_token()
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff"
    }

    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        res.raise_for_status()
        return res.text


async def generate_review_comment(diff_text: str) -> str:
    prompt = f"""
        You are an expert code reviewer.

        Review the following GitHub Pull Request diff and provide:
        - 🔧 Optimization
        - 🚫 Bad Practices
        - 🔐 Security Issues
        - 🎨 Style
        - ❗ Logic Issues
        - ⏱️ Complexity
        - ✅ Final Suggestions

        ```diff
        {diff_text}
        """
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        })
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"❌ Failed to review diff: {e}"