def extract_diff_blocks(patch: str):
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
    diff_text = "\n".join([f"+ {entry['line']}" for entry in diff_blocks if entry["type"] == "add"])
    return f"""
You are an expert code reviewer. Analyze the following GitHub Pull Request diff. Return JSON:
[
  {{ "line_snippet": "...", "comment": "..." }}
]
```diff
{diff_text}
```"""

def match_comments_to_positions(diff_blocks, suggestions):
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
