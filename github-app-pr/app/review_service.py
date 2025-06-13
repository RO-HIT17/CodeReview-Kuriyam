# --- services/review_service.py ---
import httpx
import requests
import json
import re

from app.review_utils import extract_diff_blocks, build_review_prompt, match_comments_to_positions
from app.github_auth import get_installation_token
from app.service import get_pr_files, get_latest_commit_sha, post_inline_comment

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama:7b"

async def handle_pr_review(owner: str, repo: str, pr_number: int):
    pr_files = await get_pr_files(repo, owner, pr_number)
    all_diff_blocks = []
    filename_map = {}

    print(f"Processing PR #{pr_number} for {owner}/{repo}")
    
    for file in pr_files:
        filename = file["filename"]
        patch = file.get("patch", "")
        if not patch:
            continue

        diff_blocks = extract_diff_blocks(patch)
        for block in diff_blocks:
            block["filename"] = filename
        all_diff_blocks.extend(diff_blocks)
        filename_map[filename] = diff_blocks

    # Build single prompt with all added lines
    prompt = build_review_prompt("ALL_FILES", all_diff_blocks)

    print(f"Generated prompt for {len(all_diff_blocks)} diff blocks")
    print("Sending request to Ollama... with " , prompt )
    
    res = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    })

    #print("Received response from Ollama:",res.json()["response"])    
    
    raw_response = res.json().get("response", "")
    print("Raw model response:\n", raw_response)

    # 🧹 Match all individual JSON objects
    json_objects = re.findall(r'{\s*"line_snippet"\s*:\s*".+?",\s*"comment"\s*:\s*".+?"\s*}', raw_response, re.DOTALL)

    if not json_objects:
        print("❌ No JSON objects found in response.")
        return

    # ✅ Wrap in a JSON array string
    json_text = "[" + ",".join(json_objects) + "]"

    try:
        suggestions = json.loads(json_text)
        print("✅ Parsed suggestions:", suggestions)
    except Exception as e:
        print("❌ Failed to parse cleaned JSON:", e)
        print("Extracted JSON:", json_text)
        return

    # Match and post comments
    grouped_by_file = {}
    for block in all_diff_blocks:
        grouped_by_file.setdefault(block["filename"], []).append(block)

    for filename, blocks in grouped_by_file.items():
        matched = match_comments_to_positions(blocks, suggestions)
        print(f"Matched {len(matched)} comments for file: {filename}")
        print("Matched comments:", matched)
        for item in matched:
            if item["comment"]:
                commit_id = await get_latest_commit_sha(owner, repo, pr_number)
                await post_inline_comment(
                    owner, repo, pr_number,
                    file_path=filename,
                    position=item["position"],
                    comment=item["comment"],
                    commit_id=commit_id
                )
