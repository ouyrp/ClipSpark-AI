from datetime import datetime

from pydantic import BaseModel


class GenerateRequest(BaseModel):
    asset_id: str
    target_platform: str = "douyin"
    aspect_ratio: str = "9:16"
    version_count: int = 3
    user_goal: str | None = None


class EditPlanRead(BaseModel):
    id: str
    project_id: str
    asset_id: str
    target_platform: str
    aspect_ratio: str
    duration_seconds: float | None
    plan: dict
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
