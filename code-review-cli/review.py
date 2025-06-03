import sys
import requests
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama"  

def read_file(file_path):
    """
    Read the contents of the Python file at the given path.
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"❌ Error reading file '{file_path}': {e}")
        sys.exit(1)

def send_to_ollama(code: str):
    """
    Send the code to the Ollama LLM and return the model's response.
    """
    prompt = f"""
        You are an expert Python code reviewer and software engineer.

        Please perform a comprehensive review of the following Python code. Your review should include:

        1. **Code Optimization & Refactoring Suggestions**:
        - Recommend cleaner, more efficient ways to achieve the same functionality.
        - Highlight any redundant code or unnecessary computations.

        2. **Detection of Bad Practices or Anti-Patterns**:
        - Point out any design or implementation issues that could lead to bugs or maintenance problems.

        3. **Security Vulnerabilities**:
        - Detect hardcoded credentials, unsanitized inputs, or insecure practices.

        4. **PEP8 & Style Guide Violations**:
        - Identify any violations of Python style guidelines (e.g., naming, spacing, line length).

        5. **Logic Issues & Edge Case Handling**:
        - Check for correctness in algorithm logic.
        - Highlight potential issues with unhandled inputs or edge cases.

        6. **Time and Space Complexity Analysis**:
        - For all functions and loops, provide a brief analysis of time and space complexity.
        - Suggest improvements where possible.

        7. **Performance & Readability Enhancements**:
        - Recommend ways to make the code faster or more understandable. 
        - Also provide refactored code snippets in final suggestions.

        Return your response in a structured format like:

        - 🔧 Optimization:
        - 🚫 Bad Practices:
        - 🔐 Security:
        - 🎨 Style:
        - ❗ Logic Issues:
        - ⏱️ Complexity:
        - ✅ Final Suggestions:

        Only review the code provided inside the triple backticks.

        ```python
        {code}
        """
    try:
        response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
        })
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Ollama at localhost:11434. Is it running?")
        sys.exit(1)
    
    if response.status_code != 200:
        print(f"❌ Ollama returned an error: {response.text}")
        sys.exit(1)
    
    return response.json()["response"]

    
def main():
    """
    Entry point for the CLI.
    """
    if len(sys.argv) != 2:
        print("Usage: python review.py <python_script.py>")
        sys.exit(1)

    file_path = sys.argv[1]
    print(f"📄 Reading file: {file_path}")
    code = read_file(file_path)

    print(f"🚀 Sending code to {MODEL_NAME} model...")
    start_time = time.time()

    review = send_to_ollama(code)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print("🧠 Code Review Output:\n")
    print(review)
    print(f"\n⏱️ Time taken: {elapsed_time:.2f} seconds")

    
    output_file = f"{MODEL_NAME}_review.txt"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(review)
        print(f"✅ Review saved to: {output_file}")
    except Exception as e:
        print(f"❌ Failed to write review to file: {e}")

    
main()