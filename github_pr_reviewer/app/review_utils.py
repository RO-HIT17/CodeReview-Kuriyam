# --- utils/review_utils.py ---
import re
import json

def extract_diff_blocks(patch: str):
    """
    Parses the patch and returns a list of dictionaries
    with line type, text, and position for added lines.
    """
    diff_blocks = []
    position = 0

    for line in patch.splitlines():
        if line.startswith("@@"):
            position = 0  # Reset position on new hunk
        elif line.startswith("+") and not line.startswith("+++"):
            position += 1
            diff_blocks.append({"type": "add", "line": line[:], "position": position})
        elif not line.startswith("-"):
            position += 1

    return diff_blocks

def build_review_prompt(filename: str, diff_blocks: list):
    """Builds the prompt string for the model."""
    diff_text = "\n".join(
        [f"+ {entry['line']}" for entry in diff_blocks if entry["type"] == "add"]
    )
    return f"""
You are an expert code reviewer.

Review the following GitHub Pull Request diff and provide per-line review suggestions ONLY for the added lines. Identify issues such as:
- 🔧 Optimization
- 🚫 Bad Practices
- 🔐 Security Issues
- 🎨 Style
- ❗ Logic Issues
- ⏱️ Complexity

Return JSON as:
[
  {{ "line_snippet": "...", "comment": "..." }}
]

```diff
{diff_text}
```
    """

def match_comments_to_positions(diff_blocks, suggestions):
    """
    Matches model suggestions to actual added lines and their positions from a flat list of diff blocks.
    """
    matched_results = []
    matched_lines = set()

    for suggestion in suggestions:
        raw_line = suggestion.get("line_snippet", "").strip()
        comment = suggestion.get("comment", "").strip()

        if not raw_line or not comment:
            continue

        # Normalize suggestion line
        line_text = raw_line.lstrip("+").strip().replace(" ", "")

        for entry in diff_blocks:
            if entry.get("type") != "add":
                continue

            entry_line = entry.get("line", "").lstrip("+").strip().replace(" ", "")
            position = entry.get("position")
            filename = entry.get("filename")

            if (entry_line, position) in matched_lines:
                continue

            if entry_line == line_text:
                matched_results.append({
                    "comment": comment,
                    "position": position,
                    "line": entry.get("line", "").lstrip("+").strip(),
                    "filename": filename
                })
                matched_lines.add((entry_line, position))
                break  # move to next suggestion after match

    return matched_results
