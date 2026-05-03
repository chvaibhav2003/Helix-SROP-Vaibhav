import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import User, Session as SessionModel
from app.srop.state import SessionState

router = APIRouter(tags=["sessions"])


class CreateSessionRequest(BaseModel):
    user_id: str
    plan_tier: str = "free"


class CreateSessionResponse(BaseModel):
    session_id: str
    user_id: str


@router.post("/sessions", response_model=CreateSessionResponse)
async def create_session(
    body: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
) -> CreateSessionResponse:
    """
    Create a new session. Upsert the user if not seen before.
    Initialize SessionState and persist to DB.
    """

    # 🔹 1. Check if user exists
    result = await db.execute(
        select(User).where(User.user_id == body.user_id)
    )
    user = result.scalar_one_or_none()

    # 🔹 2. Create user if not exists
    if not user:
        user = User(
            user_id=body.user_id,
            plan_tier=body.plan_tier,
        )
        db.add(user)

    # 🔹 3. Create session_id
    session_id = str(uuid.uuid4())

    # 🔹 4. Initialize session state
    state = SessionState(
        user_id=body.user_id,
        plan_tier=body.plan_tier,
        last_agent=None,
        turn_count=0,
    )

    # 🔹 5. Create session row
    session = SessionModel(
        session_id=session_id,
        user_id=body.user_id,
        state=state.to_db_dict(),
    )

    db.add(session)

    # 🔹 6. Commit changes
    await db.commit()

    return CreateSessionResponse(
        session_id=session_id,
        user_id=body.user_id,
    )