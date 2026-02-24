from datetime import datetime


def calculate_decay(created_at: datetime, engagement_score: float) -> float:
    """
    Higher decay = more forgotten = should be resurfaced.

    Formula: days_since_save * (1 - engagement_score)
    Range: 0.0 (fresh/engaged) → high float (forgotten)
    """
    days_since_save = (datetime.utcnow() - created_at).days
    decay = days_since_save * (1 - max(0.0, min(1.0, engagement_score)))
    return round(decay, 2)