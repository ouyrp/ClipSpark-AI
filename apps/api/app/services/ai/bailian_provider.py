import json

from openai import OpenAI

from app.core.config import get_settings
from app.services.ai.prompts import build_edit_plan_prompt
from app.services.ai.utils import image_to_data_url, parse_json_object


class BailianProvider:
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.bailian_text_model
        self.vision_model = settings.bailian_vision_model
        self.client = OpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.bailian_base_url,
        )

    def generate_edit_plans(self, context: dict) -> list[dict]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是专业短视频剪辑导演，只输出严格 JSON。"},
                {"role": "user", "content": build_edit_plan_prompt(context)},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        plans = data.get("plans", [])
        if not isinstance(plans, list):
            raise ValueError("百炼返回的 plans 不是数组")
        return plans

    def analyze_frames(self, frame_paths: list[str]) -> dict:
        content = [
            {
                "type": "text",
                "text": (
                    "你是短视频剪辑的视觉分析师。请分析这些关键帧，输出 JSON："
                    "{\"summary\":\"画面总结\",\"scenes\":[{\"frame\":1,\"description\":\"\",\"mood\":\"\",\"suggested_effect\":\"\"}],"
                    "\"recommended_tone\":\"festival/cinematic/anime/high_energy/clean_product/auto\"}"
                ),
            }
        ]
        for frame_path in frame_paths[:4]:
            content.append({"type": "image_url", "image_url": {"url": image_to_data_url(frame_path)}})
        response = self.client.chat.completions.create(
            model=self.vision_model,
            messages=[{"role": "user", "content": content}],
            response_format={"type": "json_object"},
        )
        return parse_json_object(response.choices[0].message.content or "{}")
