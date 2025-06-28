import requests, json, re
from utils.review_utils import extract_diff_blocks, build_review_prompt, match_comments_to_positions
from services.github_service import get_pr_files, get_latest_commit_sha, post_inline_comment, get_pr_commits, get_pr_metadata, get_issue_details, post_issue_check_comment
from utils.issue_utils import extract_issue_number, get_llama_response, build_issue_check_prompt
from feedback.store import store_feedback_draft
from core.config import OLLAMA_URL, MODEL_NAME ,NGROK_URL
import textwrap

async def handle_pr_review(owner: str, repo: str, pr_number: int, installation_id: int):
    issue_number = None

    pr_metadata = await get_pr_metadata(repo, owner, pr_number, installation_id)
    pr_body = pr_metadata.get("body", "")
    pr_title = pr_metadata.get("title", "")
    issue_number = extract_issue_number(pr_body) or extract_issue_number(pr_title)

    if not issue_number:
        pr_commits = await get_pr_commits(repo, owner, pr_number, installation_id)
        for commit in pr_commits:
            msg = commit.get("commit", {}).get("message", "")
            issue_number = extract_issue_number(msg)
            if issue_number:
                break

    print(f"🔗 LINKED ISSUE: #{issue_number}" if issue_number else "⚠️ NO LINKED ISSUE FOUND.")

    pr_files = await get_pr_files(repo, owner, pr_number, installation_id)
    all_diff_blocks = []

    print("📂 PR FILES RECEIVED:", pr_files)

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

        print("🔍 DIFF BLOCKS FOR FILE:", filename.upper(), diff_blocks)
        print("📦 UPDATED ALL DIFF BLOCKS:", all_diff_blocks)

    for file_entry in all_diff_blocks:
        filename = file_entry["filename"]
        added_lines = [entry["line"] for entry in file_entry["diff"] if entry["type"] == "add"]
        if not added_lines:
            continue

        prompt = build_review_prompt(added_lines)

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
                print(f"❌ NO REVIEW SUGGESTIONS FOR FILE: {filename} — RAW OUTPUT:\n{raw_output}")
                continue

            suggestions = json.loads("[" + ",".join(json_objects) + "]")
            print(f"💡 SUGGESTIONS FOR {filename.upper()}:", suggestions)

            matched = match_comments_to_positions(file_entry["diff"], suggestions,owner, repo, pr_number)

            print(f"📌 MATCHED COMMENTS FOR {filename.upper()}:", matched)
            print(f"🔢 COUNT OF MATCHED COMMENTS FOR {filename.upper()}: {len(matched)}")

            commit_id = await get_latest_commit_sha(owner, repo, pr_number, installation_id)

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
            print(f"🔥 ERROR WHILE PROCESSING FILE {filename.upper()}: {e}")

    if issue_number:
        try:
            
            diff_text = "\n".join([
                f"File: {entry['filename']}\n" + "\n".join([x['line'] for x in entry['diff']])
                for entry in all_diff_blocks
            ])
            feedback_id = store_feedback_draft(pr_number, issue_number, diff_text,"github",f"https://github.com/{owner}/{repo}/pull/{pr_number}",repo)

            issue_title, issue_body = await get_issue_details(owner, repo, issue_number, installation_id)
            prompt = build_issue_check_prompt(issue_title,issue_body, diff_text)
            llama_output = get_llama_response(prompt)

            comment_body = textwrap.dedent(f"""
                🔍 **Review Check**
                This PR tries to address issue #{issue_number}.
                {(llama_output.lstrip()).rstrip()}
                **Was this helpful?**
                [👍 Yes]({NGROK_URL}/feedback?vote=up&id={feedback_id}&redirect=https://github.com/{owner}/{repo}/pull/{pr_number}&platform=github&repo={repo})  
                [👎 No]({NGROK_URL}/feedback?vote=down&id={feedback_id}&redirect=https://github.com/{owner}/{repo}/pull/{pr_number}&platform=github&repo={repo})
                """).strip()


            await post_issue_check_comment(owner, repo, pr_number, issue_number, comment_body, installation_id)

            print(f"✅ POSTED ISSUE LINKAGE COMMENT FOR ISSUE #{issue_number}")
        except Exception as e:
            print("⚠️ ISSUE CHECK FAILED:", e)
