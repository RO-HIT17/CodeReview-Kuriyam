# utils/verify_jwt.py
import base64
import hashlib
import hmac
import time
import json
from fastapi import HTTPException
from urllib.parse import urlencode, urlparse
from jose import jwt
import os

BITBUCKET_SHARED_SECRET = os.getenv("BITBUCKET_SHARED_SECRET")

def compute_qsh(method: str, path: str, query: dict) -> str:
    canonical_request = "&".join([
        method.upper(),
        path,
        urlencode(sorted(query.items())) if query else '',
        '',
    ])
    return hashlib.sha256(canonical_request.encode()).hexdigest()

def verify_bitbucket_jwt(headers, method, path, query={}):
    try:
        jwt_token = headers.get("Authorization", "").replace("JWT ", "")
        if not jwt_token:
            raise HTTPException(status_code=401, detail="JWT token missing")

        decoded = jwt.decode(jwt_token, BITBUCKET_SHARED_SECRET, algorithms=["HS256"])
        
        # QSH verification
        expected_qsh = compute_qsh(method, path, query)
        if decoded.get("qsh") != expected_qsh:
            raise HTTPException(status_code=401, detail="QSH mismatch (signature invalid)")

        print("✅ JWT verified successfully for issuer:", decoded.get("iss"))
        return decoded

    except Exception as e:
        print("❌ JWT verification failed:", str(e))
        raise HTTPException(status_code=401, detail="JWT verification failed")
