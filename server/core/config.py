import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME")
BITBUCKET_APP_PASSWORD = os.getenv("BITBUCKET_APP_PASSWORD")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama:7b"
NGROK_URL = os.getenv("NGROK_URL")
