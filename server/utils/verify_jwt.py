from atlassian_jwt import Authenticator, DecodeError
from core.tenants import TENANT_STORE

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

authenticator = BitbucketAuthenticator(TENANT_STORE)

def verify_bitbucket_request(request):
    try:
        client_key, claims = authenticator.authenticate(
            http_method=request.method,
            url=str(request.url),
            headers=dict(request.headers)
        )
        print(f"[DEBUG] JWT verified. Client Key: {client_key}")
        return True
    except DecodeError as e:
        print(f"[❌] JWT verification failed: {str(e)}")
        return False
