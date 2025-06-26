import requests
from atlassian_jwt.auth import create_jwt
import time
import uuid
import hashlib
import hmac
import base64
import urllib.parse
from core.config import BITBUCKET_CLIENT_KEY as CLIENT_KEY,BITBUCKET_SHARED_SECRET as SHARED_SECRET


# URL to call
api_url = "https://api.bitbucket.org/2.0/repositories/kuriyamcodereview/code-review-tests/pullrequests/46/comments"

# Create canonical query string (empty here)
canonical_query = ""

# Prepare the canonical request
http_method = "POST"
path = urllib.parse.urlparse(api_url).path

# Expiry: JWT valid for 180 seconds
issued_at = int(time.time())
expires_at = issued_at + 180

# JWT claims
jwt_payload = {
    "iss": CLIENT_KEY,
    "iat": issued_at,
    "exp": expires_at,
    "qsh": create_qsh(http_method, path, canonical_query)  # Important!
}

# Generate the JWT token
jwt_token = encode_jwt(jwt_payload, SHARED_SECRET)

# Headers with JWT token
headers = {
    "Authorization": f"JWT {jwt_token}",
    "Content-Type": "application/json"
}

# Inline comment body
comment_data = {
    "inline": {
        "path": "test.js",
        "to": 4
    },
    "content": {
        "raw": "bruh"
    }
}

# Send request
response = requests.post(api_url, headers=headers, json=comment_data)

# Debug
print("[✅] Status:", response.status_code)
print(response.text)

def create_qsh(method, path, query):
    """
    Create Query String Hash (QSH) required for Atlassian JWT.
    """
    canonical_request = f"{method.upper()}&{path}&{query}"
    sha256_hash = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
    return sha256_hash


def encode_jwt(payload, secret):
    """
    Encode JWT with HS256 using shared secret.
    """
    import jwt
    return jwt.encode(payload, secret, algorithm="HS256")
