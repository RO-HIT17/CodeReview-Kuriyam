import time
import jwt
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("GITHUB_APP_ID")
PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH")

def generate_jwt():
    with open(PRIVATE_KEY_PATH, "r") as f:
        private_key = f.read()
    now = int(time.time())
    payload = {"iat": now, "exp": now + 540, "iss": APP_ID}
    
    return jwt.encode(payload, private_key, algorithm="RS256")

async def get_installation_token(installation_id : int ):
    
    jwt_token = generate_jwt()
    print(f"Generated JWT token: {jwt_token}")
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }
    
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers)
        res.raise_for_status()
        return res.json()["token"]
