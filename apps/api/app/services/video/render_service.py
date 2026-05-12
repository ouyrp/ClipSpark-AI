import math
import subprocess
from pathlib import Path

import imageio_ffmpeg


FONT_FILE = "/System/Library/Fonts/STHeiti Medium.ttc"


def render_preview_clip(source_path: str, output_path: str, plan: dict, aspect_ratio: str) -> None:
    variant = int(plan.get("variant_index") or 0) % 3
    clip = _first_clip(plan)
    start = _safe_float(clip.get("source_start"), 0)
    requested_end = _safe_float(clip.get("source_end"), start + 35)
    duration = max(8, min(60, requested_end - start))
    title = str(plan.get("title") or "ClipSpark AI")
    hook = str(plan.get("hook") or "")
    width, height = _target_size(aspect_ratio)
    fade_out_start = max(duration - 0.45, 0)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    style = _style_for_plan(plan, variant)
    caption = _caption_text(plan, style)

    video_filter = ",".join(
        [
            f"trim=start={start}:duration={duration}",
            "setpts=PTS-STARTPTS",
            f"scale={width}:{height}:force_original_aspect_ratio=increase",
            f"crop={width}:{height}",
            style["eq"],
            "unsharp=5:5:0.6:3:3:0.2",
            style["effect"],
            "fade=t=in:st=0:d=0.35",
            f"fade=t=out:st={fade_out_start}:d=0.4",
            "drawbox=x=0:y=0:w=iw:h=270:color=black@0.46:t=fill",
            style["accent"],
            _drawtext(title, 48, 56, 54),
            _drawtext(hook, 48, 142, 38),
            "drawbox=x=0:y=ih-180:w=iw:h=180:color=black@0.28:t=fill",
            _drawtext(caption, 48, "h-118", 34),
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
        f"sine=frequency={style['bass']}:sample_rate=44100",
        "-f",
        "lavfi",
        "-t",
        str(duration),
        "-i",
        f"sine=frequency={style['lead']}:sample_rate=44100",
        "-filter_complex",
        f"[0:v]{video_filter}[v];"
        f"[0:a]atrim=start={start}:duration={duration},asetpts=PTS-STARTPTS,volume=0.82[a0];"
        f"[1:a]volume={style['bass_volume']},tremolo=f={style['pulse']}:d=0.35[a1];"
        f"[2:a]volume={style['lead_volume']},tremolo=f={style['pulse'] + 2}:d=0.45,aecho=0.8:0.65:80:0.25[a2];"
        "[a0][a1][a2]amix=inputs=3:duration=shortest:dropout_transition=0,"
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
        _render_without_source_audio(ffmpeg, source_path, output_path, video_filter, duration, fade_out_start, style)


def _render_without_source_audio(
    ffmpeg: str,
    source_path: str,
    output_path: str,
    video_filter: str,
    duration: float,
    fade_out_start: float,
    style: dict,
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
        f"sine=frequency={style['bass']}:sample_rate=44100",
        "-f",
        "lavfi",
        "-t",
        str(duration),
        "-i",
        f"sine=frequency={style['lead']}:sample_rate=44100",
        "-filter_complex",
        f"[0:v]{video_filter}[v];"
        f"[1:a]volume={style['bass_volume']},tremolo=f={style['pulse']}:d=0.35[a1];"
        f"[2:a]volume={style['lead_volume']},tremolo=f={style['pulse'] + 2}:d=0.45,aecho=0.8:0.65:80:0.25[a2];"
        "[a1][a2]amix=inputs=2:duration=shortest:dropout_transition=0,"
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


def _style_for_plan(plan: dict, variant: int) -> dict:
    styles = [
        {
            "label": "痛点开场版",
            "visual_style": "vivid_pain_point",
            "effect_style": "vignette_focus",
            "bgm_style": "tech_pulse",
            "eq": "eq=contrast=1.12:saturation=1.22:brightness=0.01",
            "effect": "vignette=angle=PI/5:mode=backward",
            "accent": "drawbox=x=0:y=0:w=18:h=ih:color=0x1677ff@0.9:t=fill",
            "bass": 196,
            "lead": 392,
            "pulse": 4,
            "bass_volume": 0.07,
            "lead_volume": 0.035,
        },
        {
            "label": "效率节奏版",
            "visual_style": "fast_impact",
            "effect_style": "rhythm_flash",
            "bgm_style": "upbeat_drive",
            "eq": "eq=contrast=1.18:saturation=1.35:brightness=0.025",
            "effect": "tblend=all_mode=lighten:all_opacity=0.10",
            "accent": "drawbox=x=0:y=0:w=iw:h=14:color=0x16a34a@0.9:t=fill",
            "bass": 247,
            "lead": 494,
            "pulse": 7,
            "bass_volume": 0.075,
            "lead_volume": 0.04,
        },
        {
            "label": "产品卖点版",
            "visual_style": "clean_product",
            "effect_style": "soft_glow",
            "bgm_style": "warm_brand",
            "eq": "eq=contrast=1.05:saturation=1.12:brightness=0.04",
            "effect": "gblur=sigma=0.22",
            "accent": "drawbox=x=iw-18:y=0:w=18:h=ih:color=0xf59e0b@0.9:t=fill",
            "bass": 220,
            "lead": 330,
            "pulse": 5,
            "bass_volume": 0.065,
            "lead_volume": 0.045,
        },
        {
            "label": "喜庆烟花版",
            "visual_style": "festival_bright",
            "effect_style": "fireworks_pop",
            "bgm_style": "festival_pulse",
            "eq": "eq=contrast=1.16:saturation=1.55:brightness=0.035",
            "effect": "drawbox=x=96:y=168:w=34:h=34:color=0xffd166@0.9:t=fill",
            "accent": "drawbox=x=0:y=0:w=iw:h=18:color=0xef4444@0.95:t=fill",
            "bass": 262,
            "lead": 523,
            "pulse": 8,
            "bass_volume": 0.085,
            "lead_volume": 0.052,
        },
        {
            "label": "电影质感版",
            "visual_style": "cinematic_warm",
            "effect_style": "letterbox_fade",
            "bgm_style": "cinematic_rise",
            "eq": "eq=contrast=1.2:saturation=0.92:brightness=-0.015",
            "effect": "vignette=angle=PI/4:mode=backward",
            "accent": "drawbox=x=0:y=0:w=iw:h=96:color=black@0.82:t=fill",
            "bass": 147,
            "lead": 294,
            "pulse": 3,
            "bass_volume": 0.075,
            "lead_volume": 0.03,
        },
        {
            "label": "动漫弹出版",
            "visual_style": "anime_pop",
            "effect_style": "comic_flash",
            "bgm_style": "anime_upbeat",
            "eq": "eq=contrast=1.24:saturation=1.65:brightness=0.04",
            "effect": "hue=s=1.25",
            "accent": "drawbox=x=0:y=ih-24:w=iw:h=24:color=0xff4ecd@0.95:t=fill",
            "bass": 330,
            "lead": 660,
            "pulse": 9,
            "bass_volume": 0.07,
            "lead_volume": 0.055,
        },
    ]
    visual_style = str(plan.get("visual_style") or "")
    effect_style = str(plan.get("effect_style") or "")
    bgm = plan.get("bgm") if isinstance(plan.get("bgm"), dict) else {}
    bgm_style = str(bgm.get("style") or "")
    for style in styles:
        if visual_style == style["visual_style"] or effect_style == style["effect_style"] or bgm_style == style["bgm_style"]:
            return style
    return styles[variant % len(styles)]


def _caption_text(plan: dict, style: dict) -> str:
    lines = plan.get("caption_lines")
    if isinstance(lines, list) and lines:
        clean_lines = [str(line).strip() for line in lines if str(line).strip()]
        if clean_lines:
            return " · ".join(clean_lines[:3])
    return f"{style['label']} · AI 已动态选择调色、特效、背景音乐"


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
