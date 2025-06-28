from atlassian_jwt import Authenticator, DecodeError
from core.tenants import BITBUCKET_CONNECT_APP_DATA

class BitbucketAuthenticator(Authenticator):
    def __init__(self, store):
        super().__init__()
        self.store = store  

    def get_shared_secret(self, client_key):
        for workspace, data in self.store.items():
            if data.get("clientKey") == client_key:
                tenant_info = data.get("tenant")
                print(f"[DEBUG] Tenant info for client key '{client_key}': {tenant_info}")
                if tenant_info and "sharedSecret" in tenant_info:
                    return tenant_info["sharedSecret"]
        print(f"[❌] Client key '{client_key}' not found in any workspace")
        raise ValueError("Unknown client key")

authenticator = BitbucketAuthenticator(BITBUCKET_CONNECT_APP_DATA)

def verify_bitbucket_request(request):
    try:
        print(f"[DEBUG] Verifying JWT for request: {request.method} {request.url}")
        client_key, claims = authenticator.authenticate(
            http_method=request.method,
            url=str(request.url),
            headers=dict(request.headers)
        )
        print(f"[✅] JWT verified. Client Key: {client_key}")
        return True
    except DecodeError as e:
        print(f"[❌] JWT verification failed: {str(e)}")
        return False
