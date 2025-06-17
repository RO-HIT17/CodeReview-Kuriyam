from fastapi import FastAPI, Request, Header , HTTPException
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()


