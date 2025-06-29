from sqlalchemy import Column, Integer, String, Boolean
from db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name= Column(String, nullable=True)  # Optional for login, required for registration
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
