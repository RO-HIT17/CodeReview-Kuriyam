import requests, json, re
from utils.review_utils import extract_diff_blocks, build_review_prompt, match_comments_to_positions
from services.github_service import get_pr_files, get_latest_commit_sha, post_inline_comment

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama:7b"

async def handle_pr_review(owner: str, repo: str, pr_number: int,installation_id: int ):
    
    pr_files = await get_pr_files(repo, owner, pr_number ,installation_id)
    all_diff_blocks = []
    
    print("PR FILES:", pr_files)
    #print(f"Processing PR #{pr_number} for {owner}/{repo}")
    
    for file in pr_files:
        filename = file["filename"]
        patch = file.get("patch", "")
        if not patch:
            continue

        diff_blocks = extract_diff_blocks(patch)

        all_diff_blocks.append({
            "filename": filename,
            "diff": diff_blocks
        })

        print("DIFF BLOCKS:", diff_blocks)
        print("ALL DIFF BLOCKS:", all_diff_blocks)
        
    prompt = build_review_prompt("ALL_FILES", all_diff_blocks)
    
    res = requests.post(OLLAMA_URL, json={"model": MODEL_NAME, "prompt": prompt, "stream": False})

    raw_response = res.json().get("response", "")
    json_objects = re.findall(r'{\s*"line_snippet"\s*:\s*".+?",\s*"comment"\s*:\s*".+?"\s*}', raw_response, re.DOTALL)

    #print(f"Found {len(json_objects)} JSON objects in response")
    
    if not json_objects:
        return

    suggestions = json.loads("[" + ",".join(json_objects) + "]")

    grouped_by_file = {}
    for block in all_diff_blocks:
        grouped_by_file.setdefault(block["filename"], []).append(block)

    for filename, blocks in grouped_by_file.items():
        matched = match_comments_to_positions(blocks, suggestions)
        for item in matched:
            #print(f"Processing comment for {filename} at position {item['position']}: {item['comment']}")
            if item["comment"]:
                commit_id = await get_latest_commit_sha(owner, repo, pr_number)
                await post_inline_comment(owner, repo, pr_number,
                                          file_path=filename,
                                          position=item["position"],
                                          comment=item["comment"],
                                          commit_id=commit_id)
