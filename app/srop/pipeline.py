import uuid
import time
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Session as SessionModel, Message, AgentTrace
from app.srop.state import SessionState
from app.agents.orchestrator import route_query


@dataclass
class PipelineResult:
    content: str
    routed_to: str
    trace_id: str


async def run(session_id: str, user_message: str, db: AsyncSession) -> PipelineResult:
    start_time = time.time()
    trace_id = str(uuid.uuid4())

    # 🔹 1. Load session
    result = await db.execute(
        select(SessionModel).where(SessionModel.session_id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise Exception("Session not found")

    state = SessionState.from_db_dict(session.state)

    # 🔹 2. Route query
    response, routed_to, tool_calls, chunk_ids = await route_query(
        state.user_id, user_message
    )
    # 🔹 3. Save messages
    user_msg = Message(
        message_id=str(uuid.uuid4()),
        session_id=session_id,
        role="user",
        content=user_message,
        trace_id=trace_id,
    )

    assistant_msg = Message(
        message_id=str(uuid.uuid4()),
        session_id=session_id,
        role="assistant",
        content=response,
        trace_id=trace_id,
    )

    db.add(user_msg)
    db.add(assistant_msg)

    # 🔹 4. Update state
    state.turn_count += 1
    state.last_agent = routed_to
    session.state = state.to_db_dict()

    # 🔹 5. Save trace
    trace = AgentTrace(
        trace_id=trace_id,
        session_id=session_id,
        routed_to=routed_to,
        tool_calls=[],  # simple version
        retrieved_chunk_ids=[],  # can improve later
        latency_ms=int((time.time() - start_time) * 1000),
    )

    db.add(trace)

    await db.commit()

    return PipelineResult(
        content=response,
        routed_to=routed_to,
        trace_id=trace_id,
    )