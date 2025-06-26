import time, jwt, hashlib, httpx
from core.config import BITBUCKET_SHARED_SECRET
BITBUCKET_CLIENT_KEY="5499549"
def generate_qsh(method, path, query=""):
    canonical_request = f"{method.upper()}&{path}&{query}"
    return hashlib.sha256(canonical_request.encode()).hexdigest()

def create_jwt():
    now = int(time.time())
    exp = now + 180
    qsh = generate_qsh("POST", "/site/oauth2/access_token")  # Must match

    payload = {
        "iss": BITBUCKET_CLIENT_KEY,
        "iat": now,
        "exp": exp,
        "qsh": qsh
    }

    token = jwt.encode(payload, BITBUCKET_SHARED_SECRET, algorithm="HS256")
    return token

async def get_oauth_token_from_jwt():
    jwt_token = create_jwt()
    print("[DEBUG] JWT Token:", jwt_token)
    headers = {
        "Authorization": f"JWT {jwt_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "urn:bitbucket:oauth2:jwt"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post("https://bitbucket.org/site/oauth2/access_token", data=data, headers=headers)
        print(response.status_code)
        print(response.json())
        return response.json().get("access_token")

async def test_api():
    token = await get_oauth_token_from_jwt()
    print("[DEBUG] Access Token:", token)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        r = await client.get("https://api.bitbucket.org/2.0/user", headers=headers)
        print(r.status_code)
        print(r.text)
