from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.asset import Asset
from app.models.edit_plan import EditPlan
from app.schemas.generate import EditPlanRead, EditPlanUpdate
from app.services.storage.local_storage import LocalStorage
from app.services.video.render_service import render_cover_image, render_preview_clip

router = APIRouter(prefix="/edit-plans", tags=["edit-plans"])


@router.patch("/{edit_plan_id}", response_model=EditPlanRead)
def update_edit_plan(edit_plan_id: str, payload: EditPlanUpdate, db: Session = Depends(get_db)) -> EditPlan:
    edit_plan = db.get(EditPlan, edit_plan_id)
    if not edit_plan:
        raise HTTPException(status_code=404, detail="Edit plan not found")

    plan = dict(edit_plan.plan)
    if payload.title is not None:
        plan["title"] = payload.title
        cover = plan.get("cover") if isinstance(plan.get("cover"), dict) else {}
        cover["title"] = payload.title
        plan["cover"] = cover
    if payload.hook is not None:
        plan["hook"] = payload.hook
    if payload.caption_lines is not None:
        plan["caption_lines"] = [line for line in payload.caption_lines if line.strip()]
    if payload.visual_style is not None:
        plan["visual_style"] = payload.visual_style
    if payload.effect_style is not None:
        plan["effect_style"] = payload.effect_style
    if payload.bgm_style is not None:
        bgm = plan.get("bgm") if isinstance(plan.get("bgm"), dict) else {}
        bgm["style"] = payload.bgm_style
        plan["bgm"] = bgm
    if payload.bgm_volume is not None:
        bgm = plan.get("bgm") if isinstance(plan.get("bgm"), dict) else {}
        bgm["volume"] = max(0, min(payload.bgm_volume, 1))
        plan["bgm"] = bgm

    edit_plan.plan = plan
    edit_plan.status = "edited"
    db.commit()
    db.refresh(edit_plan)
    return edit_plan


@router.post("/{edit_plan_id}/render", response_model=EditPlanRead)
def rerender_edit_plan(edit_plan_id: str, request: Request, db: Session = Depends(get_db)) -> EditPlan:
    edit_plan = db.get(EditPlan, edit_plan_id)
    if not edit_plan:
        raise HTTPException(status_code=404, detail="Edit plan not found")
    asset = db.get(Asset, edit_plan.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    plan = dict(edit_plan.plan)
    storage = LocalStorage()
    try:
        render_path = storage.new_render_path()
        render_preview_clip(asset.original_url, render_path, plan, edit_plan.aspect_ratio)
        cover_path = storage.new_cover_path()
        render_cover_image(render_path, cover_path, plan, edit_plan.aspect_ratio)
        plan["preview_url"] = storage.public_url_for_path(render_path, str(request.base_url))
        plan["cover_url"] = storage.public_url_for_path(cover_path, str(request.base_url))
        plan["preview_type"] = "rendered_clip"
        plan.pop("render_error", None)
        edit_plan.status = "planned"
    except Exception as exc:
        plan["render_error"] = str(exc)
        edit_plan.status = "render_failed"

    edit_plan.plan = plan
    db.commit()
    db.refresh(edit_plan)
    return edit_plan
