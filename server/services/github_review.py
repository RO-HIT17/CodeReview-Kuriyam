import requests, json, re
from utils.review_utils import extract_diff_blocks, build_review_prompt, match_comments_to_positions
from services.github_service import get_pr_files, get_latest_commit_sha, post_inline_comment

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama:7b"

async def handle_pr_review(owner: str, repo: str, pr_number: int,installation_id: int ):
    
    pr_files = await get_pr_files(repo, owner, pr_number ,installation_id)
    all_diff_blocks = []
    
    print("PR FILES:", pr_files)
    
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
        
    for file_entry in all_diff_blocks:
        filename = file_entry["filename"]
        added_lines = [entry["line"] for entry in file_entry["diff"] if entry["type"] == "add"]
        if not added_lines:
            continue  

        prompt = build_review_prompt(filename, added_lines)

        try:
            response = requests.post(
                OLLAMA_URL,
                json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
                
            )
            response.raise_for_status()

            raw_output = response.json().get("response", "")
            json_objects = re.findall(
                r'{\s*"line_snippet"\s*:\s*".+?",\s*"comment"\s*:\s*".+?"\s*}',
                raw_output,
                re.DOTALL
            )

            if not json_objects:
                print(f"❌ No review suggestions for {filename} is {raw_output}" )
                continue

            suggestions = json.loads("[" + ",".join(json_objects) + "]")
            print(f"✅ Suggestions for {filename}:", suggestions)

            matched = match_comments_to_positions(file_entry["diff"], suggestions)

            print(f"🔗 Matched comments for {filename}:", matched)
                
            commit_id = await get_latest_commit_sha(owner, repo, pr_number,installation_id)
            for item in matched:
                await post_inline_comment(
                    owner, repo, pr_number,
                    file_path=filename,
                    position=item["position"],
                    comment=item["comment"],
                    commit_id=commit_id,
                    installation_id=installation_id
                )

        except Exception as e:
            print(f"🔥 Error processing {filename}:", e)
