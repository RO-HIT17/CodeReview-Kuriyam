# app/main.py
from fastapi import FastAPI
from app.api.webhook import router

app = FastAPI()
app.include_router(router)
