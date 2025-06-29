from db import models, database
from utils.hash import hash_password, verify_password
from sqlalchemy.orm import Session

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, name : str,email: str, password: str, is_admin=False):
    user = models.User(
        name=name,
        email=email,
        hashed_password=hash_password(password),
        is_admin=is_admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
