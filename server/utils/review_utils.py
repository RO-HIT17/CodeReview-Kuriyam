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

def build_review_prompt(filename: str, added_lines: list[str]) -> str:
    """
    Builds a detailed prompt for reviewing added Python code lines in a file.
    """
    diff_text = "\n".join(added_lines)

    return f"""
        You are an expert Python code reviewer and software engineer.

        Your task is to review **only the newly added lines** from a GitHub Pull Request diff. The code may be partial, so focus only on the provided lines and avoid assumptions about the rest of the file.

        Perform your review with emphasis on:

        1. 🔧 **Optimization & Refactoring**  
        - Recommend cleaner or faster alternatives.  
        - Identify redundant or inefficient logic.

        2. 🚫 **Bad Practices / Anti-Patterns**  
        - Flag risky coding patterns that could cause bugs or poor maintainability.

        3. 🔐 **Security Concerns**  
        - Watch for insecure code: hardcoded credentials, unsanitized inputs, dangerous patterns.

        4. ❗ **Logic Issues**  
        - Look for incorrect logic, missed edge cases, or invalid assumptions.

        5. ⏱️ **Complexity Analysis**  
        - Briefly comment on time/space complexity of loops/functions if applicable.

        6. ✅ **Final Suggestions**  
        - Include brief fixes or example corrections for the above.

        Return your review as structured JSON like:
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

def match_comments_to_positions(diff_blocks, suggestions):
    def normalize_line(line: str) -> str:
        return line.lstrip("+").strip().replace(" ", "")

    print("\n🔗 Matching comments to positions...")
    print("📄 Diff blocks:")
    for b in diff_blocks:
        print(f"  - {b}")
    print("🧠 Suggestions:")
    for s in suggestions:
        print(f"  - {s}")

    matched_results = []
    matched_lines = set()

    for suggestion in suggestions:
        raw_line = suggestion.get("line_snippet", "").strip()
        comment = suggestion.get("comment", "").strip()
        if not raw_line or not comment:
            continue

        normalized_suggestion_line = normalize_line(raw_line)

        for entry in diff_blocks:
            if entry.get("type") != "add":
                continue  

            normalized_entry_line = normalize_line(entry.get("line", ""))
            position = entry.get("position")

            if (normalized_entry_line, position) in matched_lines:
                continue

            if normalized_entry_line == normalized_suggestion_line:
                matched_results.append({
                    "comment": comment,
                    "position": position,
                    "line": entry.get("line", "").lstrip("+").strip(),
                })
                matched_lines.add((normalized_entry_line, position))
                break

    return matched_results