import re
import requests
from core.config import OLLAMA_URL, MODEL_NAME
 
def extract_issue_number(text: str) -> str | None:
    if not text:
        return None
    match = re.search(r'#(\d+)', text)
    return match.group(1) if match else None

def get_llama_response(prompt: str) -> str:
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        })
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        print("🔥 LLM issue check failed:", e)
        return ""
    
def build_issue_check_prompt(issue_title: str, issue_body: str, diff_text: str) -> str:
    return f"""
        You are a senior software engineer and expert open-source contributor tasked with evaluating whether a GitHub pull request (PR) effectively resolves the linked issue.

        Please carefully assess the provided **issue title and description** alongside the **PR diff**. Analyze the intent of the issue and the nature of the code changes. Based on your analysis, provide:

        1. A clear **judgment** on whether the PR fully addresses the issue.
        2. If not, explain **what is missing or insufficient**.
        3. Optionally, suggest improvements or required changes.

        ### Issue Title:
        {issue_title}

        ### Issue Description:
        {issue_body}

        ### PR Diff:
        {diff_text}

        Please return a concise review paragraph in natural language.
        """

