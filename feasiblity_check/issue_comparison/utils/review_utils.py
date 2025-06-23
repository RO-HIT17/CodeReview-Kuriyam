def extract_diff_blocks(patch: str):
    """
    Parses the patch and returns a list of dictionaries
    with line type, text, and position for added lines.
    """
    diff_blocks = []
    position = 0

    for line in patch.splitlines():
        if line.startswith("@@"):
            position = 0  
        elif line.startswith("+") and not line.startswith("+++"):
            position += 1
            diff_blocks.append({"type": "add", "line": line[:], "position": position})
        elif not line.startswith("-"):
            position += 1

    return diff_blocks

def build_review_prompt(filename: str, diff_blocks: list):
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

        line_text = raw_line.lstrip("+").strip().replace(" ", "")

        for entry in diff_blocks:
        
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
                break 

    return matched_results
