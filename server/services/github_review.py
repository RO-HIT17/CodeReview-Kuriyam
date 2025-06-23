# services/github_review.py

from services.github_service import fetch_pr_diff, post_comments
from utils.github_auth import get_github_client
from utils.review_utils import generate_review

async def handle_github_pr_event(payload: dict):
    action = payload.get("action")
    if action not in ["opened", "synchronize"]:
        return "No action taken"

    pr = payload["pull_request"]
    repo = payload["repository"]
    installation_id = payload["installation"]["id"]

    client = get_github_client(installation_id)
    diff = fetch_pr_diff(client, repo, pr)
    review = generate_review(diff)
    post_comments(client, repo, pr, review)

    return "Review posted"
