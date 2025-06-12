import requests
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama"

def send_diff_to_ollama(diff: str):
    """
    Send the GitHub PR diff to the Ollama LLM and return the model's structured review.
    """
    prompt = f"""
    You are an expert Python code reviewer.

    The following is a GitHub Pull Request diff. Review the **changes only**, and provide:
    1. 🔧 Code Optimization Suggestions
    2. 🚫 Detection of Bad Practices
    3. 🔐 Security Vulnerabilities
    4. 🎨 PEP8 & Style Guide Violations
    5. ❗ Logic & Edge Case Issues
    6. ⏱️ Time & Space Complexity
    7. ✅ Final Suggestions (with refactored snippets where possible)

    Respond using this format:
    - 🔧 Optimization:
    - 🚫 Bad Practices:
    - 🔐 Security:
    - 🎨 Style:
    - ❗ Logic Issues:
    - ⏱️ Complexity:
    - ✅ Final Suggestions:

    Only review the code within the diff below:

    ```diff
    {diff}
    ```
    """

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        })
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Ollama at localhost:11434. Is it running?")
        return None

    if response.status_code != 200:
        print(f"❌ Ollama returned an error: {response.text}")
        return None

    return response.json()["response"]


def review_diff(diff_text: str):
    print("🚀 Sending diff to Ollama for review...")
    start_time = time.time()

    review = send_diff_to_ollama(diff_text)

    if not review:
        print("❌ Review failed.")
        return

    elapsed = time.time() - start_time
    print("🧠 Code Review Output:\n")
    print(review)
    print(f"\n⏱️ Time taken: {elapsed:.2f} seconds")

    output_file = f"{MODEL_NAME}_diff_review.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(review)
        f.write(f"\n\nTime taken: {elapsed:.2f} seconds")
    print(f"✅ Review saved to: {output_file}")
