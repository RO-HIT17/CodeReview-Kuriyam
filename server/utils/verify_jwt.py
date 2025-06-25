from atlassian_jwt import encode_token, decode_token, errors
from atlassian_jwt.validator import JWTValidator
from fastapi import HTTPException
from core.config import BITBUCKET_SHARED_SECRET as SHARED_SECRET

def verify_bitbucket_jwt(headers, method: str, path: str):
    try:
        # Extract JWT token
        auth_header = headers.get("Authorization")
        if not auth_header or not auth_header.startswith("JWT "):
            raise HTTPException(status_code=401, detail="Missing JWT token")

        token = auth_header.split(" ")[1]

        # Get context (canonical request)
        canonical_url = path
        query_params = {}  # You can parse from request.url if needed

        # Prepare validator
        validator = JWTValidator(SHARED_SECRET)
        decoded = validator.validate(
            token,
            method=method,
            path=canonical_url,
            query_params=query_params,
        )

        print("[✅] JWT verified")
        return decoded

    except errors.JWTError as e:
        print(f"[❌ JWT ERROR] {e}")
        raise HTTPException(status_code=401, detail=f"JWT verification failed: {e}")
