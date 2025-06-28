import os
import json
import uuid
from datetime import datetime

FEEDBACK_FILE = os.path.join("static", "feedback_store.json")  

def load_feedbacks() -> list:
    """
    Loads feedback from a JSON file.
    If the file doesn't exist, returns an empty list.
    """
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_feedbacks(data: list):
    """
    Saves feedback data to a JSON file.
    """
    os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(data, f, indent=2)


def store_feedback_draft(pr, issue, diff_text, source, redirect_link, repo):
    """
    Stores a draft feedback item with additional metadata.
    
    Args:
        pr (int): Pull Request number
        issue (int): Issue number or ID
        diff_text (str): Diff/patch content
        source (str): "github" or "bitbucket"
        redirect_link (str): URL to PR or issue
        repo (str): Repository name
    """
    feedbacks = load_feedbacks()
    feedback_id = str(uuid.uuid4())
    feedbacks.append({
        "id": feedback_id,
        "timestamp": datetime.utcnow().isoformat(),
        "pr": pr,
        "issue": issue,
        "vote": None,
        "ip": None,
        "diff": diff_text,
        "platform": source,               
        "redirect": redirect_link, 
        "repo": repo,                   
        "approved": False
    })
    save_feedbacks(feedbacks)
    return feedback_id
