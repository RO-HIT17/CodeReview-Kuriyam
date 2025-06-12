import jwt  # Make sure this is from PyJWT
import time
import httpx
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

APP_ID = os.getenv("GITHUB_APP_ID")
INSTALLATION_ID = os.getenv("GITHUB_INSTALLATION_ID")
PRIVATE_KEY_PATH = Path("kuriyamcodereview.2025-06-12.private-key.pem")


def generate_jwt():
    if not PRIVATE_KEY_PATH.exists():
        raise FileNotFoundError("Private key file not found.")

    with open(PRIVATE_KEY_PATH, "r") as f:
        private_key = f.read()

    now = int(time.time())
    payload = {
        "iat": now - 60,            # issued at
        "exp": now + 10 * 60,       # expires after 10 minutes
        "iss": APP_ID               # GitHub App ID
    }

    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    return encoded_jwt


async def get_installation_access_token():
    jwt_token = generate_jwt()
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }

    url = f"https://api.github.com/app/installations/{INSTALLATION_ID}/access_tokens"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers)
        response.raise_for_status()

    return response.json()["token"]
