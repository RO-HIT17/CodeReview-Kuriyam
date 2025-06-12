import jwt
import time
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

APP_ID = os.getenv("GITHUB_APP_ID")
INSTALLATION_ID = os.getenv("GITHUB_INSTALLATION_ID")

def generate_jwt():
    with open("private-key.pem", "r") as f:
        private_key = f.read()

    payload = {
        "iat": int(time.time()) - 60,
        "exp": int(time.time()) + (10 * 60),
        "iss": APP_ID,
    }

    token = jwt.encode(payload, private_key, algorithm="RS256")
    return token


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
