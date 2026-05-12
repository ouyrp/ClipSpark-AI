EFFECT_LIBRARY = {
    "auto": {
        "label": "AI 自动判断",
        "visual_styles": ["vivid_pain_point", "fast_impact", "clean_product"],
        "effect_styles": ["vignette_focus", "rhythm_flash", "soft_glow"],
        "bgm_styles": ["tech_pulse", "upbeat_drive", "warm_brand"],
    },
    "festival": {
        "label": "喜庆烟花",
        "visual_styles": ["festival_bright"],
        "effect_styles": ["fireworks_pop", "sparkle_transition"],
        "bgm_styles": ["festival_pulse"],
    },
    "cinematic": {
        "label": "电影风",
        "visual_styles": ["cinematic_warm"],
        "effect_styles": ["letterbox_fade", "film_grain"],
        "bgm_styles": ["cinematic_rise"],
    },
    "anime": {
        "label": "动漫风",
        "visual_styles": ["anime_pop"],
        "effect_styles": ["comic_flash", "speed_lines"],
        "bgm_styles": ["anime_upbeat"],
    },
    "high_energy": {
        "label": "高能卡点",
        "visual_styles": ["fast_impact"],
        "effect_styles": ["rhythm_flash", "zoom_punch"],
        "bgm_styles": ["upbeat_drive"],
    },
    "clean_product": {
        "label": "干净产品风",
        "visual_styles": ["clean_product"],
        "effect_styles": ["soft_glow", "minimal_slide"],
        "bgm_styles": ["warm_brand"],
    },
}


def effect_options_for_prompt(tone: str) -> dict:
    return EFFECT_LIBRARY.get(tone) or EFFECT_LIBRARY["auto"]
