async def review_with_model(diff: str):
    prompt = f"Review this PR diff:\n{diff}\nSuggest security and refactoring improvements."

    async with httpx.AsyncClient() as client:
        res = await client.post("http://localhost:11434/api/generate", json={
            "model": "codellama",
            "prompt": prompt,
            "stream": False
        })
        return res.json()["response"]
