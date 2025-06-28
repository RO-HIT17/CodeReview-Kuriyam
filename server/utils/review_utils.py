from fastapi import HTTPException
from core.config import NGROK_URL
from feedback.store import store_feedback_draft

def extract_diff_blocks(patch: str):
    diff_blocks = []
    position = 0

    for line in patch.splitlines():
        if line.startswith("@@"):
            position = 0  
            continue

        if line.startswith("+") and not line.startswith("+++"):
            position += 1
            diff_blocks.append({"type": "add", "line": line, "position": position})

        elif line.startswith("-") and not line.startswith("---"):
            diff_blocks.append({"type": "del", "line": line, "position": position})

        elif not line.startswith("-"):
            position += 1

    return diff_blocks

def build_review_prompt(added_lines: list[str]) -> str:
    """
    Builds a detailed prompt for reviewing added Python code lines in a file.
    """
    diff_text = "\n".join(added_lines)

    return f"""
        You are an expert code reviewer. Review only the newly added lines from a GitHub PR diff. Do not assume missing context.

        1. 🔧 Optimization & Refactoring – Suggest cleaner, faster, or simpler alternatives.
        2. 🚫 Bad Practices & Security – Flag insecure code, hardcoded secrets, or risky patterns.
        3. ❗ Logic & Edge Cases – Identify logical errors, unhandled inputs, or invalid assumptions.
        4. ⏱️ Complexity – Mention time/space complexity where applicable.
        5. ✅ Improvements – Suggest concise fixes or better code snippets.

        Return your response as **strict JSON** in the following format:
        ```json
        [
        {{
            "line_snippet": "...",
            "comment": "..."
        }}
        ]
        ```
        {diff_text}
        """.strip()

def match_comments_to_positions(diff_blocks, suggestions, owner, repo, pr_number):
    def normalize_line(line: str) -> str:
        return line.lstrip("+").strip().replace(" ", "")

    matched_results = []
    matched_lines = set()

    for suggestion in suggestions:
        raw_line = suggestion.get("line_snippet", "").strip()
        comment = suggestion.get("comment", "").strip()
        feedback_id = store_feedback_draft(pr_number, "Nil", raw_line)
 
        if not raw_line or not comment or not feedback_id:
            continue

        normalized_suggestion_line = normalize_line(raw_line)

        for entry in diff_blocks:
            if entry.get("type") != "add":
                continue  

            normalized_entry_line = normalize_line(entry.get("line", ""))
            position = entry.get("position")

            if (normalized_entry_line, position) in matched_lines:
                continue

            if normalized_entry_line == normalized_suggestion_line or normalized_suggestion_line in normalized_entry_line:
                feedback_prompt = (
                    f"\n\n**Was this helpful?**\n"
                    f"[👍 Yes]({NGROK_URL}/feedback?vote=up&id={feedback_id}&redirect=https://github.com/{owner}/{repo}/pull/{pr_number})  \n"
                    f"[👎 No]({NGROK_URL}/feedback?vote=down&id={feedback_id}&redirect=https://github.com/{owner}/{repo}/pull/{pr_number})"
                ).strip()

                matched_results.append({
                    "comment": f"{comment}\n\n{feedback_prompt}",
                    "position": position,
                    "line": entry.get("line", "").lstrip("+").strip(),
                })
                matched_lines.add((normalized_entry_line, position))
                break

    return matched_results