import re

def parse_diff(diff_text):
    files = []
    current_file = None
    new_line_num = 0
    diff_lines = diff_text.splitlines()
    i = 0

    while i < len(diff_lines):
        line = diff_lines[i]

        if line.startswith('diff --git'):
            match = re.match(r'diff --git a/(.+) b/(.+)', line)
            if match:
                current_file = match.group(2)
                files.append({
                    'file_path': current_file,
                    'added_lines': [],
                    'deleted_lines': []
                })

        elif line.startswith('@@'):
            hunk = re.match(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', line)
            if hunk:
                new_line_num = int(hunk.group(1))
                j = i + 1
                while j < len(diff_lines) and not diff_lines[j].startswith('diff --git'):
                    diff_line = diff_lines[j]
                    if diff_line.startswith('+') and not diff_line.startswith('+++'):
                        files[-1]['added_lines'].append({
                            'line_number': new_line_num,
                            'content': diff_line[1:]
                        })
                        new_line_num += 1
                    elif diff_line.startswith('-') and not diff_line.startswith('---'):
                        files[-1]['deleted_lines'].append(diff_line[1:])
                    elif not diff_line.startswith('-'):
                        new_line_num += 1
                    j += 1
                i = j - 1
        i += 1

    return files

def match_comments_to_lines(diff_lines, suggestions):
    def normalize(line):
        return line.strip().replace(" ", "").replace(";", "")
    matched = []
    used = set()

    for s in suggestions:
        target = normalize(s["line_snippet"])
        for entry in diff_lines:
            entry_line = normalize(entry["content"])
            if (entry_line, entry["line_number"]) in used:
                continue
            if target in entry_line or entry_line in target:
                matched.append({
                    "comment": s["comment"],
                    "line_number": entry["line_number"],
                    "content": entry["content"]
                })
                used.add((entry_line, entry["line_number"]))
                break
    return matched
        

def build_review_prompt(added_lines: list[str]) -> str:
    """
    Builds a detailed prompt for reviewing added Python code lines in a file.
    """
    diff_text = "\n".join(added_lines)

    return f"""
        You are an expert code reviewer. Review only the newly added lines from a PR diff. Do not assume missing context.

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