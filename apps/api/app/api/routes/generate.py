from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.asset import Asset
from app.models.edit_plan import EditPlan
from app.models.project import Project
from app.schemas.generate import EditPlanRead, GenerateRequest
from app.services.ai.bailian_provider import BailianProvider
from app.services.ai.fallback import fallback_edit_plans
from app.services.storage.local_storage import LocalStorage

router = APIRouter(prefix="/projects/{project_id}/generate", tags=["generate"])


@router.post("", response_model=list[EditPlanRead])
def generate(project_id: str, payload: GenerateRequest, request: Request, db: Session = Depends(get_db)) -> list[EditPlan]:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    asset = db.get(Asset, payload.asset_id)
    if not asset or asset.project_id != project_id:
        raise HTTPException(status_code=404, detail="Asset not found")

    context = {
        "project_id": project.id,
        "project_name": project.name,
        "asset_id": asset.id,
        "filename": asset.filename,
        "duration_seconds": asset.duration_seconds,
        "width": asset.width,
        "height": asset.height,
        "fps": asset.fps,
        "target_platform": payload.target_platform,
        "aspect_ratio": payload.aspect_ratio,
        "version_count": payload.version_count,
        "user_goal": payload.user_goal,
    }

    try:
        plans = BailianProvider().generate_edit_plans(context)
    except Exception as exc:
        plans = fallback_edit_plans({**context, "ai_error": str(exc)})

    storage = LocalStorage()
    preview_url = storage.public_url_for_path(asset.original_url, str(request.base_url))
    edit_plans: list[EditPlan] = []
    for plan in plans[: payload.version_count]:
        plan["preview_url"] = preview_url
        plan["preview_type"] = "source_clip"
        edit_plan = EditPlan(
            project_id=project_id,
            asset_id=asset.id,
            target_platform=payload.target_platform,
            aspect_ratio=payload.aspect_ratio,
            duration_seconds=plan.get("duration"),
            plan=plan,
            status="planned",
        )
        db.add(edit_plan)
        edit_plans.append(edit_plan)

    project.status = "planned"
    db.commit()
    for edit_plan in edit_plans:
        db.refresh(edit_plan)
    return edit_plans


@router.get("/plans", response_model=list[EditPlanRead])
def list_edit_plans(project_id: str, db: Session = Depends(get_db)) -> list[EditPlan]:
    return list(db.scalars(select(EditPlan).where(EditPlan.project_id == project_id).order_by(EditPlan.created_at.desc())).all())
