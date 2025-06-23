# utils/github_auth.py

from github import GithubIntegration

APP_ID = "YOUR_APP_ID"
PRIVATE_KEY_PATH = "path/to/your.pem"

def get_github_client(installation_id):
    with open(PRIVATE_KEY_PATH) as key_file:
        private_key = key_file.read()

    integration = GithubIntegration(APP_ID, private_key)
    access_token = integration.get_access_token(installation_id).token
    return integration.get_installation_client(installation_id)
