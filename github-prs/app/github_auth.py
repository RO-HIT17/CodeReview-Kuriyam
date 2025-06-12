import time
import httpx
import os
from dotenv import load_dotenv
from pathlib import Path
import jwt  # ✅ this ensures you're using PyJWT's encode

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
        "iat": now - 60,
        "exp": now + (10 * 60),
        "iss": APP_ID,
    }

    jwt_token = jwt.encode(payload, private_key, algorithm="RS256")

    # In PyJWT ≥ 2.x, encode returns a string; in older versions, it returns bytes
    if isinstance(jwt_token, bytes):
        jwt_token = jwt_token.decode("utf-8")

    return jwt_token


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
