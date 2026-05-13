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
7. 用户选择的效果基调：{context.get("creative_tone", "auto")}。
8. 当前可用效果素材库：{json.dumps(context.get("effect_options", {}), ensure_ascii=False)}。
9. visual_style 必须从素材库 visual_styles 中选择。
10. effect_style 必须从素材库 effect_styles 中选择。
11. bgm.style 必须从素材库 bgm_styles 中选择。
12. 根据素材分析结果决定剪辑节奏、特效和字幕层，不要只套固定模板。
13. 如果视觉分析提示喜庆、舞台、活动、婚礼、节日，可以优先使用 fireworks/sparkle 类效果。
14. 使用 strategy_intelligence 里的行业策略、爆款样本、历史反馈和风格匹配结果优化剪辑。
15. caption_lines 给 2 到 3 条适合叠加到视频里的短字幕。
16. 如果素材缺少字幕，先按通用口播/产品介绍视频生成可执行剪辑策略。

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
      }},
      "analysis_summary": "为什么这样剪、画面和声音判断依据"
    }}
  ]
}}
"""
