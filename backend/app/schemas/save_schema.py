from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SaveCreate(BaseModel):
    url: str
    title: Optional[str] = None
    selected_text: Optional[str] = None


class SaveResponse(BaseModel):
    id: int
    url: str
    title: Optional[str]
    selected_text: Optional[str]
    summary: Optional[str]
    screenshot_text: Optional[str]
    intent: Optional[str]
    intent_confidence: Optional[float]
    suggested_action: Optional[str]
    action_taken: bool
    engagement_score: float
    decay_score: float
    created_at: datetime
    last_opened_at: Optional[datetime]

    class Config:
        from_attributes = True


class SaveUpdate(BaseModel):
    action_taken: Optional[bool] = None
    engagement_score: Optional[float] = None

# from datetime import datetime
# from typing import Optional
# from pydantic import BaseModel


# # What the Chrome Extension sends to the backend
# class SaveCreate(BaseModel):
#     url: str
#     title: Optional[str] = None
#     selected_text: Optional[str] = None


# # What the backend sends back to the dashboard
# class SaveResponse(BaseModel):
#     id: int
#     url: str
#     title: Optional[str]
#     selected_text: Optional[str]
#     summary: Optional[str]
#     intent: Optional[str]
#     intent_confidence: Optional[float]
#     suggested_action: Optional[str]
#     action_taken: bool
#     engagement_score: float
#     decay_score: float
#     created_at: datetime
#     last_opened_at: Optional[datetime]

#     class Config:
#         from_attributes = True


# # For updating action_taken from the dashboard
# class SaveUpdate(BaseModel):
#     action_taken: Optional[bool] = None
#     engagement_score: Optional[float] = None