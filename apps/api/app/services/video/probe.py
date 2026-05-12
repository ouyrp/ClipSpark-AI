import json
import subprocess
from pathlib import Path
from typing import Optional


def probe_video(path: str) -> dict:
    target = Path(path)
    if not target.exists():
        return {}

    command = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(target),
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return {}

    data = json.loads(result.stdout)
    video_stream = next((stream for stream in data.get("streams", []) if stream.get("codec_type") == "video"), {})
    return {
        "duration_seconds": float(data.get("format", {}).get("duration") or 0) or None,
        "width": video_stream.get("width"),
        "height": video_stream.get("height"),
        "fps": _parse_fps(video_stream.get("r_frame_rate")),
        "metadata": data,
    }


def _parse_fps(value: Optional[str]) -> Optional[float]:
    if not value or "/" not in value:
        return None
    numerator, denominator = value.split("/", 1)
    try:
        return float(numerator) / float(denominator)
    except (ValueError, ZeroDivisionError):
        return None
