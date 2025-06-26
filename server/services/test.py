import time
import jwt  # pip install pyjwt
import hashlib

def generate_jwt(app_key, shared_secret, method, uri_path, context_path=""):
    """
    Generate JWT for Bitbucket app authentication.
    """

    # Step 1: Times
    issued_at = int(time.time())
    expiry = issued_at + 180  # 3 minutes validity

    # Step 2: Query String Hash (QSH)
    canonical_request = f"{method.upper()}&{uri_path}&"
    qsh = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()

    # Step 3: Build Claims
    claims = {
        "iss": app_key,
        "iat": issued_at,
        "exp": expiry,
        "qsh": qsh,
        "sub":"connection:5499549"
    }

    # Step 4: Encode JWT
    encoded_jwt = jwt.encode(
        payload=claims,
        key=shared_secret,
        algorithm="HS256"
    )

    return encoded_jwt

import requests

jwt_token = generate_jwt(
    app_key="my-bitbucket-app",
    shared_secret="ATBCDZFX0Lj+jK+GJvm+R/+UEnLTM0/YYNPv2QTjN7TdUyoKFoPE28D408D",
    method="GET",
    uri_path="/2.0/user"
)

headers = {
    "Authorization": f"JWT {jwt_token}",
    "Content-Type": "application/x-www-form-urlencoded"
}

response = requests.post(
    "https://bitbucket.org/site/oauth2/access_token",
    headers=headers,
    data={"grant_type": "urn:bitbucket:oauth2:jwt"}
)

print(response.status_code)
print(response.json())
