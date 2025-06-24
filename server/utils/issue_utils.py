import re
import textwrap
import requests
import json
from core.config import OLLAMA_URL, MODEL_NAME
 
def extract_issue_number(text: str) -> str | None:
    if not text:
        return None
    match = re.search(r'#(\d+)', text)
    return match.group(1) if match else None

def get_llama_response(prompt: str) -> str:
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        })
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        print("🔥 LLM issue check failed:", e)
        return ""
    
def build_issue_check_prompt(issue_body: str, diff_blocks: list) -> str:
    pr_diff_full = "\n".join([
        f"File: {entry['filename']}\n" + "\n".join([x['line'] for x in entry['diff']])
        for entry in diff_blocks
    ])

    return textwrap.dedent(f"""
        You are a code reviewer.
        Given the following GitHub issue and PR diff, determine if the PR addresses the issue.
        Respond with YES if fully addressed, else explain why not.

        Issue:
        {issue_body}

        PR Diff:
        {pr_diff_full}
    """).strip()
