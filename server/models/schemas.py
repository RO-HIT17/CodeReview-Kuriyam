from pydantic import BaseModel

class PRReviewRequest(BaseModel):
    owner: str
    repo: str
    pr_number: int
    installation_id: int
    
class TestRequest(BaseModel):
    workspace: str
    repo_slug: str
    pr_id: int
    diff_url: str    
    
class AuthRequest(BaseModel):
    name: str = None  
    email: str
    password: str

class Feedback(BaseModel):
    pr: int
    issue: str
    timestamp: str
     