from datetime import datetime
from sqlalchemy import String, Text, Float, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class Save(Base):
    __tablename__ = "saves"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # ── Core content ──────────────────────────────────────────
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=True)
    selected_text: Mapped[str] = mapped_column(Text, nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)

    # ── Intent Engine ─────────────────────────────────────────
    intent: Mapped[str] = mapped_column(String(100), nullable=True)
    intent_confidence: Mapped[float] = mapped_column(Float, nullable=True)
    suggested_action: Mapped[str] = mapped_column(String(512), nullable=True)

    # ── Behavioral tracking ───────────────────────────────────
    action_taken: Mapped[bool] = mapped_column(Boolean, default=False)
    engagement_score: Mapped[float] = mapped_column(Float, default=0.0)
    decay_score: Mapped[float] = mapped_column(Float, default=0.0)

    # ── Embedding (pgvector) ──────────────────────────────────
    embedding: Mapped[list] = mapped_column(Vector(3072), nullable=True)

    # ── Timestamps ────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_opened_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)