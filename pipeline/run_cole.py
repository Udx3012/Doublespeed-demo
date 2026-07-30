"""
Process doublespeed_cole.mp4 for doublespeed.ai:
- Video: assets/source_videos/doublespeed_cole.mp4
- Website: https://doublespeed.ai
- Transcribe audio -> SRT
- Render PupCaps animated captions
- Take screenshots of doublespeed.ai
- Composite with FFmpeg (1080x1920 canvas, padded screenshots, wrapped captions)
"""

import asyncio
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

from scraper import take_screenshots
from transcriber import transcribe_video, words_to_srt
from config import OUTPUT_DIR, ELEVENLABS_API_KEY

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_VIDEO_CANDIDATES = [
    os.path.join(BASE_DIR, "assets", "source_videos", "doublespeed_cole.mp4"),
    os.path.join(OUTPUT_DIR, "cole_avatar.mp4"),
    os.path.join(BASE_DIR, "doublespeed_cole.mp4"),
]

SRC_VIDEO = next((p for p in SRC_VIDEO_CANDIDATES if os.path.exists(p) and os.path.getsize(p) > 1024), SRC_VIDEO_CANDIDATES[0])
URL = "https://doublespeed.ai"


def _resolve_pupcaps() -> str:
    found = shutil.which("pupcaps")
    if found:
        return found
    candidates = [
        os.path.join(os.environ.get("APPDATA", ""), "npm", "pupcaps.cmd"),
        r"C:\Users\Dell\AppData\Roaming\npm\pupcaps.cmd",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return "pupcaps"


async def main():
    print(f"\n{'='*60}")
    print(f"  DOUBLESPEED COLE PIPELINE EXECUTION")
    print(f"  Source Video: {SRC_VIDEO}")
    print(f"  Website: {URL}")
    print(f"{'='*60}\n")

    if not os.path.exists(SRC_VIDEO):
        raise FileNotFoundError(f"Source video not found: {SRC_VIDEO}")

    # Copy source video
    avatar_path = os.path.join(OUTPUT_DIR, "cole_avatar.mp4")
    if os.path.abspath(SRC_VIDEO) != os.path.abspath(avatar_path):
        shutil.copyfile(SRC_VIDEO, avatar_path)
        print(f"[1/6] Copied video to: {avatar_path}")
    else:
        print(f"[1/6] Using source video: {avatar_path}")

    # Step 2: Take screenshots of doublespeed.ai
    print("[2/6] Taking fresh screenshots of https://doublespeed.ai ...")
    screenshots = await take_screenshots(URL)
    print(f"  Captured {len(screenshots)} screenshots")

    # Step 3: Transcribe video audio via ElevenLabs
    print("[3/6] Transcribing video audio via ElevenLabs STT...")
    word_timestamps = transcribe_video(avatar_path)
    print(f"  Extracted {len(word_timestamps)} words with timestamps")

    script_text = " ".join(w["word"] for w in word_timestamps)
    print(f"\n--- Transcribed Script from Video ---")
    print(script_text)
    print(f"-------------------------------------\n")

    # Step 4: Save SRT captions with unix line endings
    srt_content = words_to_srt(word_timestamps)
    srt_path = os.path.join(OUTPUT_DIR, "cole_captions.srt")
    with open(srt_path, "w", newline="\n", encoding="utf-8") as f:
        f.write(srt_content)
    print(f"[4/6] Saved SRT captions: {srt_path}")

    # Step 5: Render PupCaps transparent animated captions .mov
    print("[5/6] Rendering PupCaps animated captions .mov ...")
    captions_mov = os.path.join(OUTPUT_DIR, "cole_captions.mov")
    css_path = os.path.join(os.path.dirname(__file__), "captions.css")

    pupcaps_bin = _resolve_pupcaps()
    env = os.environ.copy()
    env["PUPPETEER_EXECUTABLE_PATH"] = r"C:\Users\Dell\.cache\puppeteer\chrome\win64-151.0.7922.47\chrome-win64\chrome.exe"

    pupcaps_cmd = [
        pupcaps_bin,
        srt_path,
        "--output", captions_mov,
        "--width", "1080",
        "--height", "1920",
        "--style", css_path,
    ]
    print(f"  Running: {' '.join(pupcaps_cmd)}")
    p = subprocess.run(pupcaps_cmd, capture_output=True, text=True, env=env)
    if p.returncode != 0:
        print(f"  [Warning] PupCaps failed ({p.stderr})")
    else:
        print(f"  PupCaps captions rendered: {captions_mov}")

    # Step 6: Plan & apply image overlays + captions with FFmpeg
    print("[6/6] Compositing video with 1080x1920 canvas, captions, & padded overlays...")
    duration = word_timestamps[-1]["end"] if word_timestamps else 15.0
    num_shots = min(len(screenshots), 4)
    step = max(3.0, duration / max(1, num_shots))

    inputs = ["-i", avatar_path]
    has_captions = os.path.exists(captions_mov) and os.path.getsize(captions_mov) > 1024
    if has_captions:
        inputs.extend(["-i", captions_mov])

    # Add screenshots as inputs
    ss_start_idx = 2 if has_captions else 1
    for i in range(num_shots):
        inputs.extend(["-i", screenshots[i]])

    filter_parts = []
    # Step A: Scale avatar video to 1080x1920 vertical canvas
    filter_parts.append("[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[bg]")

    if has_captions:
        filter_parts.append("[bg][1:v]overlay=0:0:shortest=1[base]")
        current_stream = "[base]"
    else:
        current_stream = "[bg]"

    INNER_WIDTH = 760
    MAX_HEIGHT = 400
    PAD_SIZE = 16

    for i in range(num_shots):
        start_time = round(i * step, 1)
        end_time = round((i + 1) * step if i < num_shots - 1 else duration, 1)
        inp_idx = ss_start_idx + i

        scale_filter = (
            f"[{inp_idx}:v]scale=w={INNER_WIDTH}:h={MAX_HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad=w=iw+{PAD_SIZE * 2}:h=ih+{PAD_SIZE * 2}:x={PAD_SIZE}:y={PAD_SIZE}:color=0x0d0d12@0.92,"
            f"format=yuva420p,setsar=1[img{i}]"
        )
        filter_parts.append(scale_filter)

        overlay_filter = (
            f"{current_stream}[img{i}]overlay=(main_w-overlay_w)/2:main_h-overlay_h-140"
            f":enable='between(t,{start_time},{end_time})'[v{i}]"
        )
        filter_parts.append(overlay_filter)
        current_stream = f"[v{i}]"

    output_path = os.path.join(OUTPUT_DIR, "doublespeed_cole_final.mp4")
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

    print(f"  Running FFmpeg...")
    p2 = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if p2.returncode != 0:
        print(f"  [Error] FFmpeg failed: {p2.stderr}")
        raise RuntimeError(f"FFmpeg error: {p2.stderr}")

    print(f"\n{'='*60}")
    print(f"  DOUBLESPEED COLE PIPELINE COMPLETE!")
    print(f"  Final Video: {output_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
