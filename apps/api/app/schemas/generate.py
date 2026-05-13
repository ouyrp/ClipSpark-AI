from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GenerateRequest(BaseModel):
    asset_id: str
    target_platform: str = "douyin"
    aspect_ratio: str = "9:16"
    version_count: int = 3
    user_goal: Optional[str] = None
    creative_tone: str = "auto"


class EditPlanRead(BaseModel):
    id: str
    project_id: str
    asset_id: str
    target_platform: str
    aspect_ratio: str
    duration_seconds: Optional[float]
    plan: dict
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class EditPlanUpdate(BaseModel):
    title: Optional[str] = None
    hook: Optional[str] = None
    caption_lines: Optional[list[str]] = None
    visual_style: Optional[str] = None
    effect_style: Optional[str] = None
    bgm_style: Optional[str] = None
    bgm_volume: Optional[float] = None
