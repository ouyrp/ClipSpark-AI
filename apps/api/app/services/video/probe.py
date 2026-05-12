import json
import re
import subprocess
from pathlib import Path
from typing import Optional

import imageio_ffmpeg


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
        return _probe_with_ffmpeg(target)

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


def _probe_with_ffmpeg(path: Path) -> dict:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    result = subprocess.run([ffmpeg, "-i", str(path)], capture_output=True, text=True)
    output = result.stderr or result.stdout
    duration = _parse_duration(output)
    width, height = _parse_video_size(output)
    return {
        "duration_seconds": duration,
        "width": width,
        "height": height,
        "fps": None,
        "metadata": {"probe_source": "ffmpeg", "raw": output[-2000:]},
    }


def _parse_duration(output: str) -> Optional[float]:
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", output)
    if not match:
        return None
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def _parse_video_size(output: str) -> tuple[Optional[int], Optional[int]]:
    match = re.search(r"Video:.*?(\d{3,5})x(\d{3,5})", output)
    if not match:
        return None, None
    width, height = match.groups()
    return int(width), int(height)
