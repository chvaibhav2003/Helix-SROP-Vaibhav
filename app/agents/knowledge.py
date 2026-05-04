from app.agents.tools.search_docs import search_docs
import ollama


async def knowledge_agent(query: str):
    """
    Knowledge agent using RAG + Ollama (local LLM)
    """

    # 🔹 Step 1: Retrieve chunks
    results = await search_docs(query, k=3)

    if not results:
        return "No relevant documentation found.", [], []

    context = "\n\n".join([r.content for r in results])

    # 🔹 Step 2: Prepare prompt
    prompt = f"""
You are a helpful DevOps support assistant.

Use the context below to answer the user query.

Context:
{context}

User Query:
{query}

Answer clearly and concisely.
"""

    # 🔹 Step 3: Try Ollama LLM
    try:
        response = ollama.chat(
            model="phi3:mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        final_answer = response["message"]["content"]

    except Exception as e:
        # 🔥 FALLBACK (VERY IMPORTANT)
        final_answer = context[:500] + "\n\n[Fallback response due to LLM issue]"

    # 🔹 Step 4: Trace data
    chunk_ids = [r.chunk_id for r in results]

    tool_calls = [
        {
            "tool_name": "search_docs",
            "args": {"query": query},
            "result": f"{len(results)} chunks retrieved"
        }
    ]

    return final_answer, tool_calls, chunk_ids