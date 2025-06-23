# services/bitbucket_review.py

def handle_bitbucket_pr_event(payload: dict):
    # TODO: implement real diff and comment logic
    pr_id = payload["pullRequest"]["id"]
    return f"Bitbucket PR {pr_id} received and processed"
