"""
Process Hermes pipeline:
- Input video: assets/source_videos/Hermes_captioned.mp4 (already captioned)
- Website: https://hermes-agent.nousresearch.com/
- Captures screenshots of website
- Adds screenshot overlays in the lower portion of the video (borderless, larger)
- Saves final composited video to:
    pipeline/output/hermes_final.mp4
    pipeline/output/avatar_jibran.mp4
"""

import asyncio
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

from scraper import take_screenshots
from config import OUTPUT_DIR

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_VIDEO_CANDIDATES = [
    os.path.join(BASE_DIR, "assets", "source_videos", "Hermes_captioned.mp4"),
    os.path.join(OUTPUT_DIR, "hermes_captioned.mp4"),
    os.path.join(BASE_DIR, "Hermes_captioned.mp4"),
]

SRC_VIDEO = next((p for p in SRC_VIDEO_CANDIDATES if os.path.exists(p) and os.path.getsize(p) > 1024), SRC_VIDEO_CANDIDATES[0])
URL = "https://hermes-agent.nousresearch.com/"


async def main():
    print(f"\n{'='*60}")
    print(f"  HERMES PIPELINE EXECUTION")
    print(f"  Source Video (Captioned): {SRC_VIDEO}")
    print(f"  Target Website: {URL}")
    print(f"{'='*60}\n")

    if not os.path.exists(SRC_VIDEO):
        raise FileNotFoundError(f"Source video not found: {SRC_VIDEO}")

    # 1. Take fresh screenshots of official Hermes website
    print("[1/3] Capturing screenshots of official Hermes website...")
    screenshots = await take_screenshots(URL)
    print(f"  Captured {len(screenshots)} screenshots")

    # 2. Plan timed screenshot overlays across video duration
    print("[2/3] Planning screenshot overlays for lower portion (borderless, larger)...")
    duration = 28.0
    try:
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            SRC_VIDEO
        ]
        res = subprocess.run(probe_cmd, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            duration = float(res.stdout.strip())
    except Exception as e:
        print(f"  [Notice] Could not probe video duration ({e}), defaulting to {duration}s")

    num_shots = min(len(screenshots), 5)
    step = duration / num_shots

    # 3. Build FFmpeg command with borderless larger lower-portion display
    print("[3/3] Compositing screenshot overlays into lower portion...")
    inputs = ["-i", SRC_VIDEO]
    for i in range(num_shots):
        inputs.extend(["-i", screenshots[i]])

    filter_parts = []
    current_stream = "[0:v]"

    INNER_WIDTH = 960
    MAX_HEIGHT = 500

    for i in range(num_shots):
        start_time = round(i * step, 1)
        end_time = round((i + 1) * step if i < num_shots - 1 else duration, 1)
        inp_idx = i + 1

        scale_filter = (
            f"[{inp_idx}:v]scale=w={INNER_WIDTH}:h={MAX_HEIGHT}:force_original_aspect_ratio=decrease,"
            f"format=yuva420p,setsar=1[img{i}]"
        )
        filter_parts.append(scale_filter)

        overlay_filter = (
            f"{current_stream}[img{i}]overlay=(main_w-overlay_w)/2:main_h-overlay_h-110"
            f":enable='between(t,{start_time},{end_time})'[v{i}]"
        )
        filter_parts.append(overlay_filter)
        current_stream = f"[v{i}]"

    output_path = os.path.join(OUTPUT_DIR, "hermes_final.mp4")
    jibran_path = os.path.join(OUTPUT_DIR, "avatar_jibran.mp4")
    filter_complex = ";".join(filter_parts)

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", current_stream,
        "-map", "0:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        output_path,
    ]

    print("  Running FFmpeg...")
    p = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print(f"  [Error] FFmpeg failed: {p.stderr}")
        raise RuntimeError(f"FFmpeg compositing failed: {p.stderr}")

    shutil.copyfile(output_path, jibran_path)

    print(f"\n{'='*60}")
    print(f"  HERMES PIPELINE COMPLETE!")
    print(f"  Final Hermes Video: {output_path}")
    print(f"  Avatar Jibran Video: {jibran_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
