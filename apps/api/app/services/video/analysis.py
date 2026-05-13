import base64
import json
import subprocess
import uuid
from pathlib import Path
from typing import Optional

import imageio_ffmpeg

from app.core.config import get_settings
from app.services.storage.local_storage import LocalStorage


def analyze_asset(source_path: str, duration_seconds: Optional[float], public_base_url: str) -> dict:
    from app.services.ai.bailian_provider import BailianProvider

    storage = LocalStorage()
    audio_path = _extract_audio(source_path, storage)
    frames = _extract_keyframes(source_path, storage, duration_seconds)
    try:
        vision = BailianProvider().analyze_frames(frames) if frames else {"summary": "未抽取到关键帧", "scenes": []}
    except Exception as exc:
        message = _describe_ai_error(exc)
        vision = {
            "summary": f"已抽取关键帧，但{message}，使用本地素材信息生成剪辑。",
            "scenes": [],
            "error": str(exc),
        }
    asr = _asr_status(audio_path, public_base_url)
    return {
        "audio": asr,
        "vision": vision,
        "frames": [storage.public_url_for_path(frame, public_base_url) for frame in frames],
        "summary": _build_summary(asr, vision),
    }


def _extract_audio(source_path: str, storage: LocalStorage) -> str:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    processed = storage.root / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    output = processed / f"{uuid.uuid4()}.m4a"
    command = [
        ffmpeg,
        "-y",
        "-i",
        source_path,
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "aac",
        str(output),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        return ""
    return str(output)


def _extract_keyframes(source_path: str, storage: LocalStorage, duration_seconds: Optional[float]) -> list[str]:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    processed = storage.root / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    duration = max(float(duration_seconds or 0), 1)
    points = sorted({0.8, duration * 0.28, duration * 0.55, max(duration - 1.0, 0.8)})
    frames = []
    for point in points[:4]:
        output = processed / f"{uuid.uuid4()}.jpg"
        command = [
            ffmpeg,
            "-y",
            "-ss",
            str(point),
            "-i",
            source_path,
            "-frames:v",
            "1",
            "-vf",
            "scale=640:-1",
            str(output),
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0 and output.exists():
            frames.append(str(output))
    return frames


def _asr_status(audio_path: str, public_base_url: str) -> dict:
    settings = get_settings()
    if not audio_path:
        return {"status": "no_audio", "text": "", "segments": []}
    if not settings.asr_public_base_url:
        return {
            "status": "asr_pending_public_url",
            "text": "",
            "segments": [],
            "note": "百炼 Paraformer 录音文件识别要求公网可访问的 HTTP/HTTPS 文件 URL；配置 ASR_PUBLIC_BASE_URL 或接入 OSS 后可启用。",
        }
    base_url = settings.asr_public_base_url or public_base_url
    public_url = LocalStorage().public_url_for_path(audio_path, base_url)
    return {
        "status": "ready_for_paraformer",
        "file_url": public_url,
        "text": "",
        "segments": [],
    }


def _build_summary(asr: dict, vision: dict) -> str:
    parts = []
    if vision.get("summary"):
        parts.append(str(vision["summary"]))
    if asr.get("text"):
        parts.append(str(asr["text"])[:260])
    if not parts:
        return "已完成音频提取和关键帧抽取，等待更完整的 ASR 结果。"
    return "；".join(parts)


def _describe_ai_error(exc: Exception) -> str:
    error_text = str(exc).lower()
    if "invalid_api_key" in error_text or "incorrect api key" in error_text or "401" in error_text:
        return "百炼 API Key 认证失败"
    if "model" in error_text and ("not" in error_text or "access" in error_text or "permission" in error_text):
        return "视觉模型名称或权限不可用"
    if "timeout" in error_text or "timed out" in error_text:
        return "视觉模型请求超时"
    return "视觉模型暂时不可用"


def image_to_data_url(path: str) -> str:
    data = Path(path).read_bytes()
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def parse_json_object(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"summary": text[:500], "scenes": []}
