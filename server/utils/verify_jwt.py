from atlassian_jwt import Authenticator, DecodeError
from core.config import BITBUCKET_CLIENT_KEY, BITBUCKET_SHARED_SECRET 

tenant_info_store = {
    BITBUCKET_CLIENT_KEY: {
        "clientKey": BITBUCKET_CLIENT_KEY,
        "sharedSecret": BITBUCKET_SHARED_SECRET
    }
}

class BitbucketAuthenticator(Authenticator):
    def __init__(self, store):
        super().__init__()
        self.store = store

    def get_shared_secret(self, client_key):
        tenant_info = self.store.get(client_key)
        print(f"[DEBUG] Tenant info for client key '{client_key}': {tenant_info}")
        if not tenant_info:
            raise ValueError("Unknown client key")
        return tenant_info['sharedSecret']

authenticator = BitbucketAuthenticator(tenant_info_store)

def verify_bitbucket_request(request):
    try:
        client_key, claims = authenticator.authenticate(
            http_method=request.method,
            url=str(request.url),
            headers=dict(request.headers)
        )
        print(f"[DEBUG] Client Key from JWT: {client_key}")
        return True, client_key, claims
    except DecodeError as e:
        print(f"[❌] JWT verification failed: {str(e)}")
        return False, None, None
