import httpx, json, requests
from app.github_auth import get_installation_token

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama:7b"

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

def extract_diff_blocks(patch: str):
    diff_blocks = []
    current_block = []
    position = 0

    for line in patch.splitlines():
        if line.startswith("@@"):
            if current_block:
                diff_blocks.append(current_block)
                current_block = []
            position = 0
        elif line.startswith("+") and not line.startswith("+++"):
            position += 1
            current_block.append({"type": "add", "position": position, "line": line[1:]})
        elif line.startswith("-") and not line.startswith("---"):
            current_block.append({"type": "del", "position": None, "line": line[1:]})
        else:
            position += 1
            current_block.append({"type": "context", "position": position, "line": line})

    if current_block:
        diff_blocks.append(current_block)

    return diff_blocks

def build_review_prompt(filename: str, diff_blocks: list):
    blocks = []
    for block in diff_blocks:
        lines = []
        for entry in block:
            prefix = "+" if entry["type"] == "add" else "-" if entry["type"] == "del" else " "
            lines.append(f"{prefix}{entry['line']}")
        blocks.append("\n".join(lines))
    diff_text = "\n\n".join(blocks)

    return f"""
You are an expert code reviewer.

Review the following GitHub Pull Request **diff** from the file `{filename}`. Focus **only** on meaningful added or changed logic.

Provide line-level review comments under the following categories:
- 🔧 Optimization
- 🚫 Bad Practices
- 🔐 Security Issues
- 🎨 Style Issues
- ❗ Logic Errors
- ⏱️ Complexity Warnings

Respond with a JSON array, where each item follows this structure:
```json
[
  {{
    "line_snippet": "<exact line added or changed>",
    "comment": "<your review comment>"
  }},
  ...
]
Only include lines that need a comment.
Code diff:
{diff_text}
"""

def match_comments_to_positions(diff_blocks, suggestions):
    results = []
    for suggestion in suggestions:
        line_text = suggestion["line_snippet"].strip()
        for block in diff_blocks:
            for entry in block:
                if entry["type"] == "add" and entry["line"].strip() == line_text:
                    results.append({
                        "comment": suggestion["comment"],
                        "position": entry["position"],
                        "line": line_text
                    })
                    break
    return results

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

async def post_inline_comment(owner, repo, pr_number, file_path, position, comment):
    token = await get_installation_token()
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"
    
    headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
    }
    commit_id = await get_latest_commit_sha(owner, repo, pr_number)

    data = {
        "body": comment,
        "commit_id": commit_id,
        "path": file_path,
        "position": position
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=data)
        res.raise_for_status()
async def handle_pr_review(owner: str, repo: str, pr_number: int):
    pr_files = await get_pr_files(repo, owner, pr_number)
    for file in pr_files:
        filename = file["filename"]
        patch = file.get("patch", "")
        if not patch:
            continue

        diff_blocks = extract_diff_blocks(patch)
        prompt = build_review_prompt(filename, diff_blocks)

        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        })

        try:
            suggestions = json.loads(response.json()["response"])
        except Exception:
            continue  # Skip on bad model output

        matched = match_comments_to_positions(diff_blocks, suggestions)

        for item in matched:
            await post_inline_comment(owner, repo, pr_number, filename, item["position"], item["comment"])
