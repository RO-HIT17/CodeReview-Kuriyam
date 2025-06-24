from pydantic import BaseModel

class PRReviewRequest(BaseModel):
    owner: str
    repo: str
    pr_number: int
    installation_id: int