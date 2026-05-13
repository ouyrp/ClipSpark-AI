from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.asset import Asset
from app.models.project import Project
from app.schemas.asset import AssetRead
from app.services.storage.local_storage import LocalStorage
from app.services.video.analysis import analyze_asset
from app.services.video.probe import probe_video

router = APIRouter(prefix="/projects/{project_id}/assets", tags=["assets"])


@router.post("", response_model=AssetRead)
def upload_asset(project_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)) -> Asset:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Only video uploads are supported in MVP")

    original_filename, saved_path = LocalStorage().save_upload(file)
    metadata = probe_video(saved_path)
    asset = Asset(
        project_id=project_id,
        type="video",
        filename=original_filename,
        original_url=saved_path,
        duration_seconds=metadata.get("duration_seconds"),
        width=metadata.get("width"),
        height=metadata.get("height"),
        fps=metadata.get("fps"),
        asset_metadata=metadata.get("metadata"),
    )
    project.status = "uploaded"
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("", response_model=list[AssetRead])
def list_assets(project_id: str, db: Session = Depends(get_db)) -> list[Asset]:
    return list(db.scalars(select(Asset).where(Asset.project_id == project_id).order_by(Asset.created_at.desc())).all())


@router.post("/{asset_id}/analyze")
def analyze_uploaded_asset(project_id: str, asset_id: str, request: Request, db: Session = Depends(get_db)) -> dict:
    asset = db.get(Asset, asset_id)
    if not asset or asset.project_id != project_id:
        raise HTTPException(status_code=404, detail="Asset not found")
    analysis = analyze_asset(asset.original_url, asset.duration_seconds, str(request.base_url))
    return {
        "asset_id": asset.id,
        "filename": asset.filename,
        "duration_seconds": asset.duration_seconds,
        "width": asset.width,
        "height": asset.height,
        "fps": asset.fps,
        "analysis": analysis,
    }
