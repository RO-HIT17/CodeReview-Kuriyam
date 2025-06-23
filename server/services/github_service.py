# services/github_service.py

def fetch_pr_diff(client, repo, pr):
    owner = repo["owner"]["login"]
    repo_name = repo["name"]
    number = pr["number"]

    files = client.pull_requests.list_files(owner, repo_name, number)
    return [f for f in files if f.status == "added" or f.status == "modified"]

def post_comments(client, repo, pr, review):
    owner = repo["owner"]["login"]
    repo_name = repo["name"]
    number = pr["number"]

    for comment in review.get("inline", []):
        client.pulls.create_review_comment(
            owner,
            repo_name,
            number,
            body=comment["text"],
            commit_id=pr["head"]["sha"],
            path=comment["path"],
            position=comment["position"]
        )

    if "general" in review:
        client.issues.create_comment(owner, repo_name, number, review["general"])
