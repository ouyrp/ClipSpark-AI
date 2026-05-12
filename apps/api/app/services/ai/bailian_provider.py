import json

from openai import OpenAI

from app.core.config import get_settings
from app.services.ai.prompts import build_edit_plan_prompt


class BailianProvider:
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.bailian_text_model
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
