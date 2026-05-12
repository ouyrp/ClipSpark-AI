import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import get_settings


class LocalStorage:
    def __init__(self) -> None:
        self.root = get_settings().storage_root_path
        self.uploads = self.root / "uploads"
        self.uploads.mkdir(parents=True, exist_ok=True)

    def save_upload(self, file: UploadFile) -> tuple[str, str]:
        suffix = Path(file.filename or "").suffix
        safe_name = f"{uuid.uuid4()}{suffix}"
        target = self.uploads / safe_name
        with target.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return file.filename or safe_name, str(target)
