from db import models, database
from utils.hash import hash_password, verify_password
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi import Depends, Request
from utils.jwt_handler import decode_access_token
from db.models import User
from db.database import get_db

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, name : str,email: str, password: str, is_admin=False , github_installation_id=None,bitbucket_repo_data={}):
    user = models.User(
        name=name,
        email=email,
        hashed_password=hash_password(password),
        is_admin=is_admin,
        github_installation_id=github_installation_id,
        bitbucket_repo_data=bitbucket_repo_data
        
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token missing")
    
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user