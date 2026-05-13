INDUSTRY_KEYWORDS = {
    "ecommerce": ["商品", "卖点", "下单", "购买", "价格", "优惠", "带货", "种草"],
    "education": ["课程", "学习", "知识", "教程", "训练", "考试", "方法"],
    "local_life": ["探店", "门店", "活动", "节日", "婚礼", "开业", "现场", "喜庆"],
    "saas": ["工具", "效率", "自动化", "工作流", "软件", "SaaS", "系统"],
    "creator": ["vlog", "博主", "粉丝", "互动", "剧情", "日常", "创作"],
}

INDUSTRY_STRATEGIES = {
    "ecommerce": {
        "opening": "前 3 秒突出利益点、使用场景或价格锚点。",
        "clip_bias": "优先选择商品露出、使用过程、结果对比镜头。",
        "cta": "引导评论、私信或点击购买。",
    },
    "education": {
        "opening": "前 3 秒提出一个具体问题或错误认知。",
        "clip_bias": "优先选择结论清晰、步骤明确、信息密度高的片段。",
        "cta": "引导收藏、关注和继续学习。",
    },
    "local_life": {
        "opening": "前 3 秒放热闹场景、氛围、人群或空间亮点。",
        "clip_bias": "优先选择环境、活动、人流、招牌和情绪高点。",
        "cta": "引导到店、预约、定位或转发给朋友。",
    },
    "saas": {
        "opening": "前 3 秒展示低效痛点或自动化后的结果。",
        "clip_bias": "优先选择功能演示、前后对比、结果页。",
        "cta": "引导试用、咨询或领取模板。",
    },
    "creator": {
        "opening": "前 3 秒用情绪、反差、悬念或结果画面抓人。",
        "clip_bias": "优先选择表情、动作、反转和节奏变化。",
        "cta": "引导评论互动或关注系列内容。",
    },
}


def infer_industry(text: str) -> str:
    normalized = text.lower()
    scores = {}
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        scores[industry] = sum(1 for keyword in keywords if keyword.lower() in normalized)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "creator"


def strategy_for(industry: str) -> dict:
    return INDUSTRY_STRATEGIES.get(industry) or INDUSTRY_STRATEGIES["creator"]
