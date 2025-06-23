from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.github import router as github_router
from feedback.routes import router as feedback_router
from services.issue_mapper import router as issue_mapper_router  # new
from api.bitbucket import router as bitbucket_router


app = FastAPI(title="Code Review Platform")
# main.py


# CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(github_router, prefix="/github", tags=["GitHub"])
app.include_router(feedback_router, tags=["Feedback"])
app.include_router(issue_mapper_router, prefix="/issue-check", tags=["Issue Validation"])
app.include_router(bitbucket_router, prefix="/bitbucket", tags=["Bitbucket"])
