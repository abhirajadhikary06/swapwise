from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    name: str
    location: Optional[str] = None
    profile_photo: Optional[str] = None
    is_public: bool = True
    availability: Optional[str] = None

class UserCreate(UserBase):
    auth0_id: str

class UserResponse(UserBase):
    id: int
    is_admin: bool
    created_at: datetime

    class Config:
        orm_mode = True

class SkillBase(BaseModel):
    skill_name: str
    description: Optional[str] = None
    is_offered: bool

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class SwapBase(BaseModel):
    offered_skill_id: int
    requested_skill_id: int
    receiver_id: int

class SwapCreate(SwapBase):
    pass

class SwapResponse(SwapBase):
    id: int
    requester_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class FeedbackBase(BaseModel):
    swap_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackResponse(FeedbackBase):
    id: int
    reviewer_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class AdminMessage(BaseModel):
    message: str

class ReportResponse(BaseModel):
    user_id: int
    name: str
    skills_offered: List[SkillResponse]
    skills_wanted: List[SkillResponse]
    swaps: List[SwapResponse]
    feedback: List[FeedbackResponse]
