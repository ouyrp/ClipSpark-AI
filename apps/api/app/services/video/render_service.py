import math
import subprocess
from pathlib import Path

import imageio_ffmpeg


FONT_FILE = "/System/Library/Fonts/STHeiti Medium.ttc"


def render_preview_clip(source_path: str, output_path: str, plan: dict, aspect_ratio: str) -> None:
    clip = _first_clip(plan)
    start = _safe_float(clip.get("source_start"), 0)
    requested_end = _safe_float(clip.get("source_end"), start + 35)
    duration = max(8, min(60, requested_end - start))
    title = str(plan.get("title") or "ClipSpark AI")
    hook = str(plan.get("hook") or "")
    width, height = _target_size(aspect_ratio)
    fade_out_start = max(duration - 0.45, 0)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    video_filter = ",".join(
        [
            f"trim=start={start}:duration={duration}",
            "setpts=PTS-STARTPTS",
            f"scale={width}:{height}:force_original_aspect_ratio=increase",
            f"crop={width}:{height}",
            "eq=contrast=1.08:saturation=1.18:brightness=0.015",
            "unsharp=5:5:0.6:3:3:0.2",
            "fade=t=in:st=0:d=0.35",
            f"fade=t=out:st={fade_out_start}:d=0.4",
            "drawbox=x=0:y=0:w=iw:h=270:color=black@0.46:t=fill",
            _drawtext(title, 48, 56, 54),
            _drawtext(hook, 48, 142, 38),
            "drawbox=x=0:y=ih-180:w=iw:h=180:color=black@0.28:t=fill",
            _drawtext("AI 自动剪辑 · 已添加标题、调色、淡入淡出、背景音", 48, "h-118", 34),
        ]
    )

    command = [
        ffmpeg,
        "-y",
        "-i",
        source_path,
        "-f",
        "lavfi",
        "-t",
        str(duration),
        "-i",
        "sine=frequency=220:sample_rate=44100",
        "-filter_complex",
        f"[0:v]{video_filter}[v];"
        f"[0:a]atrim=start={start}:duration={duration},asetpts=PTS-STARTPTS,volume=0.82[a0];"
        "[1:a]volume=0.045[a1];"
        "[a0][a1]amix=inputs=2:duration=shortest:dropout_transition=0,"
        "afade=t=in:st=0:d=0.35,"
        f"afade=t=out:st={fade_out_start}:d=0.4[a]",
        "-map",
        "[v]",
        "-map",
        "[a]",
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        output_path,
    ]

    try:
        _run(command)
    except RuntimeError:
        _render_without_source_audio(ffmpeg, source_path, output_path, video_filter, duration, fade_out_start)


def _render_without_source_audio(
    ffmpeg: str,
    source_path: str,
    output_path: str,
    video_filter: str,
    duration: float,
    fade_out_start: float,
) -> None:
    command = [
        ffmpeg,
        "-y",
        "-i",
        source_path,
        "-f",
        "lavfi",
        "-t",
        str(duration),
        "-i",
        "sine=frequency=220:sample_rate=44100",
        "-filter_complex",
        f"[0:v]{video_filter}[v];"
        "[1:a]volume=0.055,"
        "afade=t=in:st=0:d=0.35,"
        f"afade=t=out:st={fade_out_start}:d=0.4[a]",
        "-map",
        "[v]",
        "-map",
        "[a]",
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        output_path,
    ]
    _run(command)


def _run(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-1200:] or "FFmpeg render failed")


def _first_clip(plan: dict) -> dict:
    clips = plan.get("clips")
    if isinstance(clips, list) and clips:
        first = clips[0]
        if isinstance(first, dict):
            return first
    return {"source_start": 0, "source_end": 35}


def _safe_float(value: object, fallback: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    if not math.isfinite(number):
        return fallback
    return max(number, 0)


def _target_size(aspect_ratio: str) -> tuple[int, int]:
    if aspect_ratio == "16:9":
        return 1920, 1080
    if aspect_ratio == "1:1":
        return 1080, 1080
    return 1080, 1920


def _drawtext(text: str, x: object, y: object, size: int) -> str:
    safe_text = _escape_drawtext(text[:42])
    font = _escape_drawtext_path(FONT_FILE if Path(FONT_FILE).exists() else "")
    font_part = f"fontfile='{font}':" if font else ""
    return (
        "drawtext="
        f"{font_part}"
        f"text='{safe_text}':"
        "fontcolor=white:"
        f"fontsize={size}:"
        f"x={x}:"
        f"y={y}:"
        "line_spacing=12:"
        "box=1:"
        "boxcolor=black@0.22:"
        "boxborderw=14"
    )


def _escape_drawtext(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("%", "\\%")
        .replace("\n", " ")
    )


def _escape_drawtext_path(value: str) -> str:
    return value.replace("\\", "\\\\").replace(":", "\\:")
