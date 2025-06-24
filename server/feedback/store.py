import os
import json

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
