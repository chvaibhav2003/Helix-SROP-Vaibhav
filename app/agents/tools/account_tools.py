from dataclasses import dataclass
from datetime import datetime
import random


@dataclass
class BuildSummary:
    build_id: str
    pipeline: str
    status: str
    branch: str
    started_at: datetime
    duration_seconds: int


@dataclass
class AccountStatus:
    user_id: str
    plan_tier: str
    concurrent_builds_used: int
    concurrent_builds_limit: int
    storage_used_gb: float
    storage_limit_gb: float


async def get_recent_builds(user_id: str, limit: int = 5) -> list[BuildSummary]:
    builds = []

    for i in range(limit):
        builds.append(
            BuildSummary(
                build_id=f"build_{i}",
                pipeline="deploy",
                status=random.choice(["passed", "failed", "cancelled"]),
                branch="main",
                started_at=datetime.utcnow(),
                duration_seconds=random.randint(30, 300),
            )
        )

    return builds


async def get_account_status(user_id: str) -> AccountStatus:
    return AccountStatus(
        user_id=user_id,
        plan_tier="pro",
        concurrent_builds_used=2,
        concurrent_builds_limit=5,
        storage_used_gb=3.5,
        storage_limit_gb=10.0,
    )