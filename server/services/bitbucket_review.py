import httpx
from fastapi import HTTPException
from core.config import BITBUCKET_APP_PASSWORD, BITBUCKET_USERNAME,OLLAMA_URL, MODEL_NAME
from utils.bitbucket_utils import build_review_prompt, match_comments_to_lines
import json
import re
from typing import Optional

async def handle_file_review(file_entry, workspace, repo_slug, pr_id):
    file_path = file_entry["file_path"]
    added_lines = file_entry["added_lines"]

    if not added_lines:
        print(f"[ℹ️] No additions in {file_path}, skipping.")
        return

    raw_lines = [line["content"] for line in added_lines]
    prompt = build_review_prompt(raw_lines)

    print(f"[🤖] Calling LLM for {file_path}...")

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                OLLAMA_URL,
                json={"model": MODEL_NAME, "prompt": prompt, "stream": False}
            )
        response.raise_for_status()
        print(f"[✅] LLM response received for {response}")
        raw_output = response.json().get("response", "")
        
                
        json_objects = re.findall(r'{\s*"line_snippet"\s*:\s*".+?",\s*"comment"\s*:\s*".+?"\s*}', raw_output)

        if not json_objects:
            print(f"[❌] No LLM comments for {file_path}")
            return

        suggestions = json.loads("[" + ",".join(json_objects) + "]")
        matched = match_comments_to_lines(added_lines, suggestions)

        print(f"[📌] {len(matched)} comments matched in {file_path}")
        print(f"[📌] Suggestions: {json.dumps(suggestions, indent=2)}")
        print(f"[📌] Matched comments: {json.dumps(matched, indent=2)}")
        
        for m in matched:
            await post_bitbucket_inline_comment(
                workspace=workspace,
                repo_slug=repo_slug,
                pr_id=pr_id,
                file_path=file_path,
                line=m["line_number"],
                message=m["comment"]
            )

    except Exception as e:
        print(f"[🔥] Error reviewing {file_path}: {e}")
        
        
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

async def post_bitbucket_inline_comment(
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
