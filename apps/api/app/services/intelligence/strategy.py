from sqlalchemy.orm import Session

from app.services.intelligence.embedding import style_matches
from app.services.intelligence.feedback import project_feedback_signals
from app.services.intelligence.industry_strategy import infer_industry, strategy_for
from app.services.intelligence.viral_samples import samples_for


def build_intelligence_context(context: dict, db: Session) -> dict:
    analysis = context.get("asset_analysis") or {}
    query = " ".join(
        [
            str(context.get("project_name") or ""),
            str(context.get("user_goal") or ""),
            str(context.get("creative_tone") or ""),
            str(analysis.get("summary") or ""),
        ]
    )
    industry = infer_industry(query)
    tone = str(context.get("creative_tone") or "auto")
    return {
        "industry": industry,
        "industry_strategy": strategy_for(industry),
        "viral_samples": samples_for(industry, tone),
        "style_matches": style_matches(query),
        "feedback": project_feedback_signals(db, str(context["project_id"])),
        "embedding_note": "当前为本地轻量 embedding 检索；生产环境可替换为百炼 text-embedding-v4 或向量数据库。",
    }
