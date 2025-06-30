from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from services.auth_service import get_user_by_email, create_user
from utils.hash import verify_password
from utils.email_validator import is_valid_email
from utils.jwt_handler import create_access_token
from models.schemas import AuthRequest
from db.database import get_db

router = APIRouter()

@router.post("/register")
def register(payload: AuthRequest, db: Session = Depends(get_db)):
    if not is_valid_email(payload.email):
        raise HTTPException(status_code=400, detail="Invalid email domain")

    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="User already exists")

    user = create_user(db, payload.name,payload.email, payload.password)
    return {"message": "User registered", "email": user.email}


@router.post("/login")
def login(payload: AuthRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email})

    return {
        "message": "Login successful",
        "user_id":user.id,
        "token": token,
        "name": user.name,
        "email": user.email,
        "is_admin": user.is_admin,
        "github_installation_id": user.github_installation_id   
    }