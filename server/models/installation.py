from sqlalchemy import Column, String
from core.database import Base

class Installation(Base):
    __tablename__ = "bitbucket_installations"

    client_key = Column(String, primary_key=True)  # e.g. connection:xxxx
    shared_secret = Column(String, nullable=False)
    workspace_uuid = Column(String, nullable=False)
    workspace_name = Column(String, nullable=False)
    base_api_url = Column(String, nullable=False)
    installed_by_user = Column(String, nullable=True)