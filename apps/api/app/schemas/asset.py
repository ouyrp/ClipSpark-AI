from datetime import datetime

from pydantic import BaseModel


class AssetRead(BaseModel):
    id: str
    project_id: str
    type: str
    filename: str
    original_url: str
    created_at: datetime

    model_config = {"from_attributes": True}
