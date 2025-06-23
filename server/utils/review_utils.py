# utils/review_utils.py

def generate_review(diff):
    inline = []
    for file in diff:
        for line in file.patch.split("\n"):
            if "TODO" in line:
                inline.append({
                    "path": file.filename,
                    "position": 1,  # Replace with accurate position logic
                    "text": "Consider resolving TODOs before merging."
                })

    general = "Automated review complete. Please address inline suggestions."

    return {"inline": inline, "general": general}
