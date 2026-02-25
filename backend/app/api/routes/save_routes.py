from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.save import Save
from app.models.user import User
from app.schemas.save_schema import SaveCreate, SaveResponse, SaveUpdate
from app.services.ai_service import generate_summary
from app.services.intent_service import classify_intent
from app.services.embedding_service import generate_embedding
from app.services.screenshot_service import extract_text_from_screenshot
from app.services.decay_engine import calculate_decay

router = APIRouter(prefix="/saves", tags=["saves"])


@router.post("/", response_model=SaveResponse)
async def create_save(
    payload: SaveCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    raw_text = " ".join(filter(None, [payload.title, payload.selected_text]))
    summary = await generate_summary(raw_text)
    intent_result = await classify_intent(
        title=payload.title or "",
        url=payload.url or "",
        content=payload.selected_text or payload.title or ""
    )
    embedding = await generate_embedding(raw_text or summary)

    new_save = Save(
        user_id=current_user.id,
        url=payload.url,
        title=payload.title,
        selected_text=payload.selected_text,
        summary=summary,
        intent=intent_result.get("intent"),
        intent_confidence=intent_result.get("confidence"),
        suggested_action=intent_result.get("suggested_action"),
        embedding=embedding,
        action_taken=False,
        engagement_score=0.0,
        decay_score=0.0,
    )
    db.add(new_save)
    await db.flush()
    new_save.decay_score = calculate_decay(new_save.created_at, new_save.engagement_score)
    await db.commit()
    await db.refresh(new_save)
    return new_save


@router.post("/screenshot", response_model=SaveResponse)
async def save_screenshot(
    file: UploadFile = File(...),
    url: str = Form(default="screenshot://local"),
    title: str = Form(default="Screenshot"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    image_bytes = await file.read()
    screenshot_text = await extract_text_from_screenshot(image_bytes)
    raw_text = screenshot_text or title
    summary = await generate_summary(raw_text)
    intent_result = await classify_intent(
        title=title or "Screenshot",
        url=url or "",
        content=screenshot_text or title or ""
    )
    embedding = await generate_embedding(raw_text)

    new_save = Save(
        user_id=current_user.id,
        url=url,
        title=title,
        screenshot_text=screenshot_text,
        summary=summary,
        intent=intent_result.get("intent"),
        intent_confidence=intent_result.get("confidence"),
        suggested_action=intent_result.get("suggested_action"),
        embedding=embedding,
        action_taken=False,
        engagement_score=0.0,
        decay_score=0.0,
    )
    db.add(new_save)
    await db.flush()
    new_save.decay_score = calculate_decay(new_save.created_at, new_save.engagement_score)
    await db.commit()
    await db.refresh(new_save)
    return new_save


@router.get("/", response_model=list[SaveResponse])
async def get_saves(
    intent: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Save).where(Save.user_id == current_user.id).order_by(Save.created_at.desc())
    if intent:
        query = query.where(Save.intent == intent)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/forgotten", response_model=list[SaveResponse])
async def get_forgotten_saves(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(days=14)
    query = (
        select(Save)
        .where(Save.user_id == current_user.id)
        .where(Save.action_taken == False)
        .where(Save.created_at < cutoff)
        .order_by(Save.decay_score.desc())
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{save_id}", response_model=SaveResponse)
async def get_save(
    save_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Save).where(Save.id == save_id, Save.user_id == current_user.id)
    )
    save = result.scalar_one_or_none()
    if not save:
        raise HTTPException(status_code=404, detail="Save not found")
    return save


@router.patch("/{save_id}", response_model=SaveResponse)
async def update_save(
    save_id: int,
    payload: SaveUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Save).where(Save.id == save_id, Save.user_id == current_user.id)
    )
    save = result.scalar_one_or_none()
    if not save:
        raise HTTPException(status_code=404, detail="Save not found")
    if payload.action_taken is not None:
        save.action_taken = payload.action_taken
    if payload.engagement_score is not None:
        save.engagement_score = payload.engagement_score
        save.decay_score = calculate_decay(save.created_at, save.engagement_score)
    await db.commit()
    await db.refresh(save)
    return save


@router.delete("/{save_id}")
async def delete_save(
    save_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Save).where(Save.id == save_id, Save.user_id == current_user.id)
    )
    save = result.scalar_one_or_none()
    if not save:
        raise HTTPException(status_code=404, detail="Save not found")
    await db.delete(save)
    await db.commit()
    return {"deleted": True, "id": save_id}



# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, update
# from app.core.database import get_db
# from app.models.save import Save
# from app.schemas.save_schema import SaveCreate, SaveResponse, SaveUpdate
# from app.services.ai_service import generate_summary
# from app.services.intent_service import classify_intent
# from app.services.embedding_service import generate_embedding
# from app.services.decay_engine import calculate_decay

# router = APIRouter(prefix="/saves", tags=["saves"])


# # ── POST /saves ───────────────────────────────────────────────
# # Called by Chrome Extension when user saves something
# @router.post("/", response_model=SaveResponse)
# async def create_save(payload: SaveCreate, db: AsyncSession = Depends(get_db)):

#     # Build text for AI to analyze
#     # raw_text = " ".join(filter(None, [payload.title, payload.selected_text]))
#     raw_text = " ".join(
#     filter(None, [payload.title, payload.selected_text, payload.url])
# )

#     # Run all three AI services
#     summary = await generate_summary(raw_text)
#     intent_result = await classify_intent(
#     payload.title,
#     payload.url,
#     payload.selected_text or ""
# )
#     embedding = await generate_embedding(raw_text or summary)

#     # Build the Save object
#     new_save = Save(
#         url=payload.url,
#         title=payload.title,
#         selected_text=payload.selected_text,
#         summary=summary,
#         intent=intent_result.get("intent"),
#         intent_confidence=intent_result.get("confidence"),
#         suggested_action=intent_result.get("suggested_action"),
#         embedding=embedding,
#         action_taken=False,
#         engagement_score=0.0,
#         decay_score=0.0,
#     )

#     db.add(new_save)
#     await db.flush()  # get the ID before commit

#     # Calculate initial decay (will be 0 since just saved)
#     new_save.decay_score = calculate_decay(new_save.created_at, new_save.engagement_score)

#     await db.commit()
#     await db.refresh(new_save)
#     return new_save


# # ── GET /saves ────────────────────────────────────────────────
# # Called by dashboard to list all saves
# @router.get("/", response_model=list[SaveResponse])
# async def get_saves(
#     intent: str = None,
#     db: AsyncSession = Depends(get_db)
# ):
#     query = select(Save).order_by(Save.created_at.desc())

#     if intent:
#         query = query.where(Save.intent == intent)

#     result = await db.execute(query)
#     return result.scalars().all()


# # ── GET /saves/forgotten ──────────────────────────────────────
# # Saves older than 14 days with no action taken
# @router.get("/forgotten", response_model=list[SaveResponse])
# async def get_forgotten_saves(db: AsyncSession = Depends(get_db)):
#     from datetime import datetime, timedelta
#     cutoff = datetime.utcnow() - timedelta(days=14)

#     query = (
#         select(Save)
#         .where(Save.action_taken == False)
#         .where(Save.created_at < cutoff)
#         .order_by(Save.decay_score.desc())
#     )

#     result = await db.execute(query)
#     return result.scalars().all()


# # ── GET /saves/{id} ───────────────────────────────────────────
# @router.get("/{save_id}", response_model=SaveResponse)
# async def get_save(save_id: int, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Save).where(Save.id == save_id))
#     save = result.scalar_one_or_none()
#     if not save:
#         raise HTTPException(status_code=404, detail="Save not found")
#     return save


# # ── PATCH /saves/{id} ─────────────────────────────────────────
# # Mark as action taken, update engagement from dashboard
# @router.patch("/{save_id}", response_model=SaveResponse)
# async def update_save(
#     save_id: int,
#     payload: SaveUpdate,
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await db.execute(select(Save).where(Save.id == save_id))
#     save = result.scalar_one_or_none()
#     if not save:
#         raise HTTPException(status_code=404, detail="Save not found")

#     if payload.action_taken is not None:
#         save.action_taken = payload.action_taken
#     if payload.engagement_score is not None:
#         save.engagement_score = payload.engagement_score
#         save.decay_score = calculate_decay(save.created_at, save.engagement_score)

#     await db.commit()
#     await db.refresh(save)
#     return save


# # ── DELETE /saves/{id} ────────────────────────────────────────
# @router.delete("/{save_id}")
# async def delete_save(save_id: int, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Save).where(Save.id == save_id))
#     save = result.scalar_one_or_none()
#     if not save:
#         raise HTTPException(status_code=404, detail="Save not found")
#     await db.delete(save)
#     await db.commit()
#     return {"deleted": True, "id": save_id}