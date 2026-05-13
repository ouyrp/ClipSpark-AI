import json
from typing import Optional

from openai import OpenAI

from app.core.config import get_settings
from app.services.ai.prompts import build_edit_plan_prompt
from app.services.ai.utils import image_to_data_url, parse_json_object


class OpenAICompatibleProvider:
    def __init__(
        self,
        provider_id: str,
        api_key: str,
        base_url: str,
        text_model: str,
        vision_model: Optional[str] = None,
    ) -> None:
        self.provider_id = provider_id
        self.text_model = text_model
        self.vision_model = vision_model or text_model
        self.client = OpenAI(api_key=api_key or "not-needed", base_url=base_url)

    def generate_edit_plans(self, context: dict) -> list[dict]:
        content = self._chat_json(
            model=self.text_model,
            messages=[
                {"role": "system", "content": "你是专业短视频剪辑导演，只输出严格 JSON。"},
                {"role": "user", "content": build_edit_plan_prompt(context)},
            ],
        )
        data = json.loads(content)
        plans = data.get("plans", [])
        if not isinstance(plans, list):
            raise ValueError(f"{self.provider_id} 返回的 plans 不是数组")
        for plan in plans:
            if isinstance(plan, dict):
                plan["ai_provider"] = self.provider_id
                plan["ai_model"] = self.text_model
        return plans

    def analyze_frames(self, frame_paths: list[str]) -> dict:
        content = [
            {
                "type": "text",
                "text": (
                    "你是短视频剪辑视觉分析师。根据关键帧判断画面主体、场景、情绪、可用高光和适合的剪辑效果。"
                    "只输出 JSON："
                    "{\"summary\":\"画面总结\",\"scenes\":[{\"frame\":1,\"description\":\"\",\"mood\":\"\","
                    "\"suggested_effect\":\"\"}],\"recommended_tone\":\"festival/cinematic/anime/high_energy/clean_product/auto\"}"
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
        result = parse_json_object(response.choices[0].message.content or "{}")
        result["ai_provider"] = self.provider_id
        result["ai_model"] = self.vision_model
        return result

    def _chat_json(self, model: str, messages: list[dict]) -> str:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"},
            )
        except Exception:
            response = self.client.chat.completions.create(model=model, messages=messages)
        return response.choices[0].message.content or "{}"


def build_free_provider(provider_id: Optional[str] = None) -> OpenAICompatibleProvider:
    settings = get_settings()
    selected = (provider_id or settings.ai_provider or "gemini").strip()

    if selected == "gemini":
        return OpenAICompatibleProvider(
            provider_id="gemini",
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url,
            text_model=settings.gemini_text_model,
            vision_model=settings.gemini_vision_model,
        )
    if selected == "openrouter_free":
        return OpenAICompatibleProvider(
            provider_id="openrouter_free",
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            text_model=settings.openrouter_text_model,
            vision_model=settings.openrouter_vision_model,
        )
    if selected == "ollama":
        return OpenAICompatibleProvider(
            provider_id="ollama",
            api_key=settings.ollama_api_key,
            base_url=settings.ollama_base_url,
            text_model=settings.ollama_text_model,
            vision_model=settings.ollama_vision_model,
        )

    from app.services.ai.bailian_provider import BailianProvider

    return BailianProvider()
