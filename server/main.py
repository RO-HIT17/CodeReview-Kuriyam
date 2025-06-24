from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.github import router as github_router
from api.feedback import router as feedback_router
from api.bitbucket import router as bitbucket_router

app = FastAPI(title="Code Review Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(github_router, prefix="/github", tags=["GitHub"])
app.include_router(feedback_router, tags=["Feedback"])
app.include_router(bitbucket_router, prefix="/bitbucket", tags=["Bitbucket"])
