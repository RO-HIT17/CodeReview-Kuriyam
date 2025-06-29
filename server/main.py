from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.github import router as github_router
from api.feedback import router as feedback_router
from api.bitbucket import router as bitbucket_router
from api.auth import router as auth_router

from db.database import Base, engine, SessionLocal
from services.auth_service import create_user, get_user_by_email

app = FastAPI(title="Code Review Platform")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables
Base.metadata.create_all(bind=engine)

# Hardcoded admin setup
@app.on_event("startup")
def create_admin():
    db = SessionLocal()
    if not get_user_by_email(db, "admin@codereviewai.com"):
        create_user(db, "admin@codereviewai.com", "admin123", is_admin=True)
    db.close()

# Include routers
app.include_router(github_router, prefix="/github", tags=["GitHub"])
app.include_router(feedback_router, tags=["Feedback"])
app.include_router(bitbucket_router, prefix="/bitbucket", tags=["Bitbucket"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
