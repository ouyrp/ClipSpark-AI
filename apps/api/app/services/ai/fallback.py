def fallback_edit_plans(context: dict) -> list[dict]:
    version_count = max(1, min(context.get("version_count", 3), 5))
    platform = context.get("target_platform", "douyin")
    ratio = context.get("aspect_ratio", "9:16")
    base_titles = ["痛点开场版", "效率提升版", "产品卖点版", "教程拆解版", "种草推荐版"]
    styles = [
        ("vivid_pain_point", "vignette_focus", "tech_pulse", ["剪视频太慢？", "AI 自动剪出重点", "先给你能发的版本"]),
        ("fast_impact", "rhythm_flash", "upbeat_drive", ["节奏拉满", "高光直接前置", "快速生成 3 条短片"]),
        ("clean_product", "soft_glow", "warm_brand", ["产品卖点更清楚", "字幕和标题自动包装", "适合直接预览发布"]),
        ("fast_impact", "rhythm_flash", "upbeat_drive", ["教程重点拆出来", "少剪一点，多发一点"]),
        ("clean_product", "soft_glow", "warm_brand", ["种草表达更自然", "封面文案一起生成"]),
    ]
    plans = []
    for index in range(version_count):
        start = index * 10
        end = start + 35
        visual_style, effect_style, bgm_style, captions = styles[index % len(styles)]
        plans.append(
            {
                "title": f"AI 一键剪辑短视频 - {base_titles[index]}",
                "hook": "剪视频太慢？让 AI 先帮你剪出能发的版本。",
                "target_platform": platform,
                "aspect_ratio": ratio,
                "duration": 35,
                "clips": [
                    {
                        "source_start": start,
                        "source_end": end,
                        "timeline_start": 0,
                        "timeline_end": 35,
                        "reason": "MVP 阶段缺少字幕和场景分析，先生成可执行的候选片段。",
                    }
                ],
                "subtitle_style": {
                    "font_size": 48,
                    "position": "bottom",
                    "keyword_highlight": True,
                },
                "visual_style": visual_style,
                "effect_style": effect_style,
                "bgm": {"style": bgm_style, "volume": 0.22},
                "caption_lines": captions,
                "cover": {"source_time": start + 3, "title": base_titles[index]},
                "publish_copy": {
                    "caption": "上传长视频，AI 自动生成可发布短视频。",
                    "hashtags": ["AI剪辑", "短视频工具", "内容创作"],
                },
            }
        )
    return plans
