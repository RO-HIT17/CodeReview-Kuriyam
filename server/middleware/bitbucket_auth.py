import time
import jwt  
import hashlib
import requests
from core.config import BITBUCKET_KEY
from core.tenants import BITBUCKET_CONNECT_APP_DATA
 
def get_bitbucket_access_token(workspace_name : str) -> dict:
    
    method = "GET"
    uri_path = "/2.0/user"
    
    app_key = BITBUCKET_KEY
    shared_secret = BITBUCKET_CONNECT_APP_DATA[workspace_name]["sharedSecret"]
    sub=BITBUCKET_CONNECT_APP_DATA[workspace_name]["clientKey"]
    
    print(f"[DEBUG] Generating JWT for Bitbucket access token with app_key: {app_key}, sub: {sub}")
    
    issued_at = int(time.time())
    expiry = issued_at + 180  

    canonical_request = f"{method.upper()}&{uri_path}&"
    qsh = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()

    claims = {
        "iss": app_key,
        "iat": issued_at,
        "exp": expiry,
        "qsh": qsh,
        "sub": sub
    }

    encoded_jwt = jwt.encode(claims, shared_secret, algorithm="HS256")

    headers = {
        "Authorization": f"JWT {encoded_jwt}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "urn:bitbucket:oauth2:jwt"
    }

    response = requests.post(
        "https://bitbucket.org/site/oauth2/access_token",
        headers=headers,
        data=data
    )

    if response.status_code != 200:
        raise requests.HTTPError(f"Token request failed: {response.status_code} - {response.text}")

    return response.json()["access_token"]