from app.agents.tools.account_tools import (
    get_recent_builds,
    get_account_status,
)


#agent for account queries but it can be extended
async def account_agent(user_id: str, query: str):
    """
    Account agent
    MUST return: (response, tool_calls, chunk_ids)
    """

    query_lower = query.lower()

    # 🔹 CASE 1: builds
    if "build" in query_lower:
        builds = await get_recent_builds(user_id)

        response = "Here are your recent builds:\n\n"
        for b in builds:
            response += f"- {b.build_id} ({b.status}) on {b.branch}\n"

        tool_calls = [
            {
                "tool_name": "get_recent_builds",
                "args": {"user_id": user_id},
                "result": f"{len(builds)} builds returned"
            }
        ]

        return response, tool_calls, []  # ✅ ALWAYS 3 VALUES

    # 🔹 CASE 2: account status
    else:
        status = await get_account_status(user_id)

        response = (
            f"Plan: {status.plan_tier}\n"
            f"Storage: {status.storage_used_gb}/{status.storage_limit_gb} GB\n"
        )

        tool_calls = [
            {
                "tool_name": "get_account_status",
                "args": {"user_id": user_id},
                "result": "status retrieved"
            }
        ]

        return response, tool_calls, []  # ✅ ALWAYS 3 VALUES