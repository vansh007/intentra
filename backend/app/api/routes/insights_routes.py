from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.save import Save
from app.models.user import User
from datetime import datetime, timedelta

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/")
async def get_insights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    uid = current_user.id

    total = (await db.execute(select(func.count(Save.id)).where(Save.user_id == uid))).scalar()

    intent_result = await db.execute(
        select(Save.intent, func.count(Save.id))
        .where(Save.user_id == uid)
        .group_by(Save.intent)
        .order_by(func.count(Save.id).desc())
    )
    intent_breakdown = [
        {"intent": row[0] or "unclassified", "count": row[1]}
        for row in intent_result.all()
    ]

    cutoff = datetime.utcnow() - timedelta(days=14)
    forgotten_count = (await db.execute(
        select(func.count(Save.id))
        .where(Save.user_id == uid, Save.action_taken == False, Save.created_at < cutoff)
    )).scalar()

    acted_count = (await db.execute(
        select(func.count(Save.id)).where(Save.user_id == uid, Save.action_taken == True)
    )).scalar()

    action_rate = round((acted_count / total * 100), 1) if total > 0 else 0

    return {
        "total_saves": total,
        "forgotten_saves": forgotten_count,
        "action_rate_percent": action_rate,
        "intent_breakdown": intent_breakdown,
    }

# from fastapi import APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, func
# from app.core.database import get_db
# from app.models.save import Save
# from datetime import datetime, timedelta

# router = APIRouter(prefix="/insights", tags=["insights"])


# @router.get("/")
# async def get_insights(db: AsyncSession = Depends(get_db)):

#     # Total saves
#     total_result = await db.execute(select(func.count(Save.id)))
#     total = total_result.scalar()

#     # Intent breakdown
#     intent_result = await db.execute(
#         select(Save.intent, func.count(Save.id))
#         .group_by(Save.intent)
#         .order_by(func.count(Save.id).desc())
#     )
#     intent_breakdown = [
#         {"intent": row[0] or "unclassified", "count": row[1]}
#         for row in intent_result.all()
#     ]

#     # Forgotten saves (14+ days, no action)
#     cutoff = datetime.utcnow() - timedelta(days=14)
#     forgotten_result = await db.execute(
#         select(func.count(Save.id))
#         .where(Save.action_taken == False)
#         .where(Save.created_at < cutoff)
#     )
#     forgotten_count = forgotten_result.scalar()

#     # Action taken rate
#     acted_result = await db.execute(
#         select(func.count(Save.id)).where(Save.action_taken == True)
#     )
#     acted_count = acted_result.scalar()
#     action_rate = round((acted_count / total * 100), 1) if total > 0 else 0

#     return {
#         "total_saves": total,
#         "forgotten_saves": forgotten_count,
#         "action_rate_percent": action_rate,
#         "intent_breakdown": intent_breakdown,
#     }