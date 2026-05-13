import base64
import json
from pathlib import Path


def image_to_data_url(path: str) -> str:
    data = Path(path).read_bytes()
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def parse_json_object(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"summary": text[:500], "scenes": []}
