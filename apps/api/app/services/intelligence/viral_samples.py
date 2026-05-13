VIRAL_SAMPLES = [
    {
        "id": "edu_pain_hook_001",
        "industry": "education",
        "tone": "clean_product",
        "hook_pattern": "先抛学习痛点，再给一个明确结果",
        "pace": "medium",
        "caption_style": "大字重点词高亮",
        "structure": ["痛点", "解决方案", "结果展示", "行动引导"],
    },
    {
        "id": "ecommerce_offer_001",
        "industry": "ecommerce",
        "tone": "high_energy",
        "hook_pattern": "前 2 秒展示商品利益点或价格锚点",
        "pace": "fast",
        "caption_style": "卖点词闪现",
        "structure": ["强利益点", "场景展示", "核心卖点", "促单 CTA"],
    },
    {
        "id": "local_life_festival_001",
        "industry": "local_life",
        "tone": "festival",
        "hook_pattern": "先给热闹氛围，再放地址/活动亮点",
        "pace": "fast",
        "caption_style": "喜庆标题 + 氛围词",
        "structure": ["氛围开场", "活动亮点", "人群/场景", "到店引导"],
    },
    {
        "id": "saas_problem_solution_001",
        "industry": "saas",
        "tone": "cinematic",
        "hook_pattern": "用一个工作流问题切入，再展示自动化结果",
        "pace": "medium",
        "caption_style": "克制标题 + 功能关键词",
        "structure": ["问题", "自动化过程", "效率结果", "试用引导"],
    },
    {
        "id": "creator_anime_energy_001",
        "industry": "creator",
        "tone": "anime",
        "hook_pattern": "用夸张表情/状态词制造开场反差",
        "pace": "fast",
        "caption_style": "漫画感短句",
        "structure": ["情绪钩子", "过程快切", "反转/结果", "互动问题"],
    },
]


def samples_for(industry: str, tone: str) -> list[dict]:
    exact = [sample for sample in VIRAL_SAMPLES if sample["industry"] == industry and sample["tone"] == tone]
    if exact:
        return exact[:3]
    industry_matches = [sample for sample in VIRAL_SAMPLES if sample["industry"] == industry]
    tone_matches = [sample for sample in VIRAL_SAMPLES if sample["tone"] == tone]
    return (industry_matches + tone_matches + VIRAL_SAMPLES)[:3]
