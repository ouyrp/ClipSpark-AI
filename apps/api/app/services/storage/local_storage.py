import shutil
import uuid
from pathlib import Path
from urllib.parse import quote

from fastapi import UploadFile

from app.core.config import get_settings


class LocalStorage:
    def __init__(self) -> None:
        self.root = get_settings().storage_root_path
        self.uploads = self.root / "uploads"
        self.renders = self.root / "renders"
        self.covers = self.root / "covers"
        self.uploads.mkdir(parents=True, exist_ok=True)
        self.renders.mkdir(parents=True, exist_ok=True)
        self.covers.mkdir(parents=True, exist_ok=True)

    def save_upload(self, file: UploadFile) -> tuple[str, str]:
        suffix = Path(file.filename or "").suffix
        safe_name = f"{uuid.uuid4()}{suffix}"
        target = self.uploads / safe_name
        with target.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return file.filename or safe_name, str(target)

    def public_url_for_path(self, path: str, base_url: str) -> str:
        relative = Path(path).resolve().relative_to(self.root)
        return f"{base_url.rstrip('/')}/media/{quote(relative.as_posix())}"

    def new_render_path(self) -> str:
        return str(self.renders / f"{uuid.uuid4()}.mp4")

    def new_cover_path(self) -> str:
        return str(self.covers / f"{uuid.uuid4()}.jpg")
