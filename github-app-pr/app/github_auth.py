import time
import jwt
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("GITHUB_APP_ID")
INSTALLATION_ID = os.getenv("GITHUB_INSTALLATION_ID")
PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH", "kuriyamcodereview.2025-06-12.private-key.pem")


def generate_jwt():
    with open("kuriyamcodereview.2025-06-12.private-key.pem", "r") as f:
        private_key = f.read()

    now = int(time.time())
    payload = {
        "iat": now,
        "exp": now + 540,  
        "iss": os.getenv("GITHUB_APP_ID")
    }

    return jwt.encode(payload, private_key, algorithm="RS256")

async def get_installation_token():
    jwt_token = generate_jwt()
    #print("JWT Token:\n", jwt_token)

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }

    url = f"https://api.github.com/app/installations/{INSTALLATION_ID}/access_tokens"

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers)
        if res.status_code != 201:
            print("Error status code:", res.status_code)
            print("Response body:", res.text)
        res.raise_for_status()
        token = res.json()["token"]
        #print("Installation token:", token)
        return token
