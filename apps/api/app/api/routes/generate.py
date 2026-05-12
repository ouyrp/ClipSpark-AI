from typing import Optional

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
from app.services.video.render_service import render_preview_clip

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
    for index, plan in enumerate(plans[: payload.version_count]):
        _prepare_plan_variant(plan, index, asset.duration_seconds)
        try:
            render_path = storage.new_render_path()
            render_preview_clip(asset.original_url, render_path, plan, payload.aspect_ratio)
            plan["preview_url"] = storage.public_url_for_path(render_path, str(request.base_url))
            plan["preview_type"] = "rendered_clip"
            plan["render_features"] = [
                "smart_trim",
                "resize",
                "title_overlay",
                "style_effect",
                "fade",
                "auto_bgm",
            ]
        except Exception as exc:
            plan["preview_url"] = preview_url
            plan["preview_type"] = "source_clip"
            plan["render_error"] = str(exc)
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


def _prepare_plan_variant(plan: dict, index: int, source_duration: Optional[float]) -> None:
    plan["variant_index"] = index
    plan["style_variant"] = ["痛点开场版", "效率节奏版", "产品卖点版"][index % 3]
    plan.setdefault("visual_style", ["vivid_pain_point", "fast_impact", "clean_product"][index % 3])
    plan.setdefault("effect_style", ["vignette_focus", "rhythm_flash", "soft_glow"][index % 3])
    bgm = plan.get("bgm")
    if not isinstance(bgm, dict):
        bgm = {}
        plan["bgm"] = bgm
    bgm.setdefault("style", ["tech_pulse", "upbeat_drive", "warm_brand"][index % 3])
    bgm.setdefault("volume", 0.22)
    if not isinstance(plan.get("caption_lines"), list):
        plan["caption_lines"] = [
            ["痛点放大", "AI 自动剪辑", "直接生成可发布版本"],
            ["节奏拉满", "高光前置", "快速出片"],
            ["卖点更清楚", "字幕自动包装", "适合预览发布"],
        ][index % 3]

    clips = plan.get("clips")
    if not isinstance(clips, list) or not clips or not isinstance(clips[0], dict):
        clips = [{"source_start": 0, "source_end": 35, "timeline_start": 0, "timeline_end": 35}]
        plan["clips"] = clips

    clip = clips[0]
    duration = max(float(source_duration or 0), 0)
    target_len = 28 if index == 0 else 24 if index == 1 else 32

    if duration > 0:
        max_start = max(duration - min(target_len, duration), 0)
        start = min(max_start, max(index * 0.28 * duration, 0))
        end = min(duration, start + min(target_len, duration))
    else:
        start = index * 8
        end = start + target_len

    clip["source_start"] = round(start, 2)
    clip["source_end"] = round(max(end, start + 4), 2)
    clip["timeline_start"] = 0
    clip["timeline_end"] = round(clip["source_end"] - clip["source_start"], 2)
