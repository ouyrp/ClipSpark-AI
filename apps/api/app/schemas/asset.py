from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AssetRead(BaseModel):
    id: str
    project_id: str
    type: str
    filename: str
    original_url: str
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}
