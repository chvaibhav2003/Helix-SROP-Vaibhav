from app.agents.knowledge import knowledge_agent
from app.agents.account import account_agent
from app.llm.router_llm import classify_intent


async def route_query(user_id: str, query: str):
    """
    LLM-based routing (agentic behavior)
    """

    intent = await classify_intent(query)

    if intent == "account":
        response, tool_calls, chunk_ids = await account_agent(user_id, query)
        return response, "account", tool_calls, chunk_ids

    else:
        response, tool_calls, chunk_ids = await knowledge_agent(query)
        return response, "knowledge", tool_calls, chunk_ids