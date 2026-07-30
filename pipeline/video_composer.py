"""
Compose final marketing video:
1. Keep avatar video at its native aspect ratio (9:16)
2. Overlay styled captions on top using PupCaps
3. Overlay cropped screenshots on the bottom portion at timed intervals
"""

import os
import subprocess
import json
import shutil
from config import OUTPUT_DIR


def _resolve_pupcaps() -> str:
    """Return the pupcaps executable path, falling back to known npm global locations on Windows."""
    import shutil as _shutil
    found = _shutil.which("pupcaps")
    if found:
        return found
    # Windows npm global bin fallback
    candidates = [
        os.path.join(os.environ.get("APPDATA", ""), "npm", "pupcaps.cmd"),
        r"C:\Users\Dell\AppData\Roaming\npm\pupcaps.cmd",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return "pupcaps"  # last resort, let subprocess raise


def add_captions_overlay(video_path: str, srt_path: str, output_filename: str = "captioned.mp4") -> str:
    """
    Use PupCaps to generate a .mov caption overlay, then composite it on the video.
    """
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    captions_mov = os.path.join(OUTPUT_DIR, "captions.mov")

    if not os.path.exists(video_path) or os.path.getsize(video_path) < 1024:
        print("  [Notice] Input video is empty or missing. Skipping caption overlay.")
        shutil.copyfile(video_path, output_path) if os.path.exists(video_path) else None
        return video_path

    css_path = os.path.join(os.path.dirname(__file__), "captions.css")

    pupcaps_bin = _resolve_pupcaps()
    pupcaps_cmd = [pupcaps_bin, srt_path, "--output", captions_mov, "--width", "1080", "--height", "1920"]
    if os.path.exists(css_path):
        pupcaps_cmd.extend(["--style", css_path])

    print(f"  Running PupCaps: {' '.join(pupcaps_cmd)}")
    try:
        result = subprocess.run(pupcaps_cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"  [Warning] PupCaps skipped ({result.stderr}). Continuing with uncaptioned video.")
            shutil.copyfile(video_path, output_path)
            return video_path
    except Exception as err:
        print(f"  [Warning] PupCaps not found or failed ({err}). Continuing with base video.")
        shutil.copyfile(video_path, output_path)
        return video_path

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", captions_mov,
        "-filter_complex", "[0:v][1:v]overlay=0:0:shortest=1",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        output_path,
    ]

    try:
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"  [Warning] ffmpeg caption overlay failed. Returning base video.")
            shutil.copyfile(video_path, output_path)
            return video_path
    except Exception as err:
        print(f"  [Warning] ffmpeg failed ({err}). Returning base video.")
        shutil.copyfile(video_path, output_path)
        return video_path

    print(f"  Captioned video: {output_path}")
    return output_path


def add_image_overlays(
    video_path: str,
    overlay_plan: list[dict],
    screenshots: list[str],
    output_filename: str = "video_doublespeed.mp4",
) -> str:
    """
    Overlay screenshots on the bottom portion of the video.
    """
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    if not overlay_plan or not os.path.exists(video_path) or os.path.getsize(video_path) < 1024:
        if os.path.exists(video_path):
            shutil.copyfile(video_path, output_path)
        return output_path

    IMG_WIDTH = 880
    MAX_HEIGHT = 460
    X_POS = 100

    inputs = ["-i", video_path]
    filter_parts = []
    current_stream = "[0:v]"
    overlay_idx = 0

    for i, overlay in enumerate(overlay_plan):
        ss_idx = overlay["screenshot_index"]
        if ss_idx >= len(screenshots) or not os.path.exists(screenshots[ss_idx]):
            continue

        start = overlay["start_time"]
        end = overlay["end_time"]

        inputs.extend(["-i", screenshots[ss_idx]])
        input_idx = overlay_idx + 1

        scale_filter = (
            f"[{input_idx}:v]scale=w={IMG_WIDTH}:h={MAX_HEIGHT}:force_original_aspect_ratio=decrease,"
            f"format=yuva420p,setsar=1[img{overlay_idx}]"
        )
        filter_parts.append(scale_filter)

        overlay_filter = (
            f"{current_stream}[img{overlay_idx}]overlay=(main_w-overlay_w)/2:main_h-overlay_h-120"
            f":enable='between(t,{start},{end})'[v{overlay_idx}]"
        )
        filter_parts.append(overlay_filter)
        current_stream = f"[v{overlay_idx}]"
        overlay_idx += 1

    if not filter_parts:
        shutil.copyfile(video_path, output_path)
        return output_path

    filter_complex = ";".join(filter_parts)

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", current_stream,
        "-map", "0:a?",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        output_path,
    ]

    print(f"  Running ffmpeg with {len(overlay_plan)} image overlays...")
    try:
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=180)
        if result.returncode != 0:
            print(f"  [Warning] ffmpeg image overlay failed ({result.stderr}). Saving base video.")
            shutil.copyfile(video_path, output_path)
            return output_path
    except Exception as err:
        print(f"  [Warning] ffmpeg failed ({err}). Saving base video.")
        shutil.copyfile(video_path, output_path)
        return output_path

    print(f"  Final video with overlays: {output_path}")
    return output_path


if __name__ == "__main__":
    import sys

    video = sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUTPUT_DIR, "avatar.mp4")
    srt = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUTPUT_DIR, "captions.srt")

    # Test caption overlay
    captioned = add_captions_overlay(video, srt)
    print(f"Done: {captioned}")
