import ollama


async def classify_intent(query: str) -> str:

    query_lower = query.lower()

    # 🔹 Fast fallback first
    if any(x in query_lower for x in ["build", "status", "plan", "usage"]):
        return "account"

    try:
        response = ollama.chat(
            model="phi3:mini",
            messages=[
                {
                    "role": "user",
                    "content": f"""
Classify this query:

{query}

Answer ONLY:
knowledge OR account
"""
                }
            ]
        )

        decision = response["message"]["content"].lower()

        if "account" in decision:
            return "account"
        return "knowledge"

    except Exception:
        return "knowledge"