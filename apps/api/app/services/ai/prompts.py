import json


def build_edit_plan_prompt(context: dict) -> str:
    return f"""
你是 ClipSpark AI 的短视频剪辑导演。请根据素材信息生成 {context["version_count"]} 个可发布短视频剪辑方案。

要求：
1. 只输出 JSON，不要输出 Markdown。
2. 每个方案适合 {context["target_platform"]} 平台。
3. 比例为 {context["aspect_ratio"]}。
4. 每个方案包含 hook、title、clips、subtitle_style、bgm、cover、publish_copy。
5. clips 中 source_start/source_end 可以先基于素材时长做合理估算。
6. 如果素材缺少字幕，先按通用口播/产品介绍视频生成可执行剪辑策略。

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
      "bgm": {{
        "style": "light_trend",
        "volume": 0.18
      }},
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
