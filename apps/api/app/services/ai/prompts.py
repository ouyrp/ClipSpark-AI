import json


def build_edit_plan_prompt(context: dict) -> str:
    return f"""
你是 ClipSpark AI 的短视频剪辑导演。请根据素材信息生成 {context["version_count"]} 个可发布短视频剪辑方案。

要求：
1. 只输出 JSON，不要输出 Markdown。
2. 每个方案适合 {context["target_platform"]} 平台。
3. 比例为 {context["aspect_ratio"]}。
4. 每个方案包含 hook、title、clips、subtitle_style、visual_style、effect_style、bgm、caption_lines、cover、publish_copy。
5. 三个方案必须明显不同：不同剪辑片段、不同开头钩子、不同画面风格、不同节奏和不同音乐方向。
6. clips 中 source_start/source_end 可以基于素材时长做合理估算，不能三个方案都取同一个时间段。
7. visual_style 只能从 vivid_pain_point、fast_impact、clean_product 中选择。
8. effect_style 只能从 vignette_focus、rhythm_flash、soft_glow 中选择。
9. bgm.style 只能从 tech_pulse、upbeat_drive、warm_brand 中选择。
10. caption_lines 给 2 到 3 条适合叠加到视频里的短字幕。
11. 如果素材缺少字幕，先按通用口播/产品介绍视频生成可执行剪辑策略。

素材上下文：
{json.dumps(context, ensure_ascii=False, indent=2)}

输出 JSON 格式：
{{
  "plans": [
    {{
      "title": "短视频标题",
      "hook": "前三秒钩子",
      "target_platform": "{context["target_platform"]}",
      "aspect_ratio": "{context["aspect_ratio"]}",
      "duration": 45,
      "clips": [
        {{
          "source_start": 0,
          "source_end": 15,
          "timeline_start": 0,
          "timeline_end": 15,
          "reason": "为什么选择这个片段"
        }}
      ],
      "subtitle_style": {{
        "font_size": 48,
        "position": "bottom",
        "keyword_highlight": true
      }},
      "visual_style": "vivid_pain_point",
      "effect_style": "vignette_focus",
      "bgm": {{
        "style": "tech_pulse",
        "volume": 0.22
      }},
      "caption_lines": ["痛点放大", "AI 自动剪辑", "直接生成可发布版本"],
      "cover": {{
        "source_time": 3,
        "title": "封面标题"
      }},
      "publish_copy": {{
        "caption": "发布文案",
        "hashtags": ["AI剪辑", "短视频"]
      }}
    }}
  ]
}}
"""
