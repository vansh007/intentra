from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.core.database import get_db
from app.models.save import Save
from app.schemas.save_schema import SaveResponse
from app.services.embedding_service import generate_embedding

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=list[SaveResponse])
async def semantic_search(q: str, db: AsyncSession = Depends(get_db)):
    if not q or len(q.strip()) < 2:
        return []

    # Generate embedding for the search query
    query_embedding = await generate_embedding(q)

    if not query_embedding:
        # Fallback to basic title/summary text search
        result = await db.execute(
            select(Save).where(
                Save.title.ilike(f"%{q}%") | Save.summary.ilike(f"%{q}%")
            ).limit(10)
        )
        return result.scalars().all()

    # pgvector cosine similarity search
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    result = await db.execute(
        text("""
            SELECT * FROM saves
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT 10
        """),
        {"embedding": embedding_str}
    )

    rows = result.mappings().all()
    return [Save(**dict(row)) for row in rows]