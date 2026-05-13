from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.edit_plan import EditPlan


def project_feedback_signals(db: Session, project_id: str) -> dict:
    plans = list(db.scalars(select(EditPlan).where(EditPlan.project_id == project_id)).all())
    if not plans:
        return {
            "history_count": 0,
            "preferred_styles": [],
            "note": "当前项目暂无用户反馈，优先使用行业策略和爆款样本。",
        }

    style_counts: dict[str, int] = {}
    for edit_plan in plans:
        style = str(edit_plan.plan.get("visual_style") or edit_plan.plan.get("style_variant") or "unknown")
        style_counts[style] = style_counts.get(style, 0) + 1
    preferred = sorted(style_counts.items(), key=lambda item: item[1], reverse=True)
    return {
        "history_count": len(plans),
        "preferred_styles": [style for style, _ in preferred[:3]],
        "note": "已根据当前项目历史生成结果提取偏好，后续可接入下载、点赞、重生成、手动编辑等显式反馈。",
    }
