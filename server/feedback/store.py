# feedback/store.py

import json
from datetime import datetime

FEEDBACK_FILE = "static/feedback_store.json"

def store_feedback_vote(data):
    with open(FEEDBACK_FILE, "r") as f:
        feedback = json.load(f)

    data["timestamp"] = str(datetime.utcnow())
    feedback.append(data)

    with open(FEEDBACK_FILE, "w") as f:
        json.dump(feedback, f, indent=2)
