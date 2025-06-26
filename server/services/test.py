import time
import jwt  # PyJWT
import httpx
from urllib.parse import urlencode, urlparse
from core.config import BITBUCKET_CLIENT_KEY as CLIENT_KEY,BITBUCKET_SHARED_SECRET as SHARED_SECRET

def generate_qsh(method, path, query=""):
    canonical_request = f"{method.upper()}&{path}&{query}"
    import hashlib
    return hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()

def generate_jwt(method, url):
    issued_at = int(time.time())
    exp = issued_at + 180  # expires in 3 minutes

    payload = {
        "iss": CLIENT_KEY,
        "iat": issued_at,
        "exp": exp,
        "qsh": generate_qsh(method, url),
    }

    token = jwt.encode(payload, SHARED_SECRET, algorithm="HS256")
    return token

async def post_inline_comment():
    method = "POST"
    url = "https://api.bitbucket.org/2.0/repositories/kuriyamcodereview/code-review-tests/pullrequests/46/comments"

    jwt_token = generate_jwt(method, url)
    print("Token:", jwt_token)
    headers = {
        "Authorization": f"JWT {jwt_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "inline": {
            "path": "test.js",
            "to": 4
        },
        "content": {
            "raw": "bruh"
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)

    print(f"[✅] Status: {response.status_code}")
    print(f"[✅] Response: {response.text}")
    print(f"[✅] Headers: {response.headers}")
    print(f"[✅] URL: {response.url}")
    print(f"[✅] Request body: {response.request.content}")
    print(response.text)
