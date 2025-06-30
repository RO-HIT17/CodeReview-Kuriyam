from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.types import TypeDecorator
import json
from db.database import Base

class JSONEncodedDict(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is None:
            return json.dumps({})
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return {}
        return json.loads(value)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name= Column(String, nullable=True)  
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    github_installation_id = Column(String, nullable=True)
    
    bitbucket_repo_data = Column(JSONEncodedDict, default=dict)
