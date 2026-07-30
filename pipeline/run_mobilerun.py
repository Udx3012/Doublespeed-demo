"""
Process MobileRun pipeline:
- Input video: assets/source_videos/mobilerun_final.mp4
- Website: https://mobilerun.ai
- Transcribes video to extract script & word timestamps
- Captures screenshots of mobilerun.ai
- Plans screenshot overlays
- Composes final video: pipeline/output/mobilerun_final_captioned.mp4
"""

import asyncio
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))

from scraper import take_screenshots
from transcriber import transcribe_video, words_to_srt, save_srt
from script_generator import generate_image_overlay_plan
from video_composer import add_captions_overlay, add_image_overlays
from config import OUTPUT_DIR

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_VIDEO_CANDIDATES = [
    os.path.join(BASE_DIR, "assets", "source_videos", "mobilerun_final.mp4"),
    os.path.join(OUTPUT_DIR, "mobilerun_avatar.mp4"),
    os.path.join(BASE_DIR, "mobilerun_final.mp4"),
]

SRC_VIDEO = next((p for p in SRC_VIDEO_CANDIDATES if os.path.exists(p) and os.path.getsize(p) > 1024), SRC_VIDEO_CANDIDATES[0])
URL = "https://mobilerun.ai"


async def main():
    print(f"\n{'='*60}")
    print(f"  MOBILERUN PIPELINE EXECUTION")
    print(f"  Source Video: {SRC_VIDEO}")
    print(f"  Website: {URL}")
    print(f"{'='*60}\n")

    if not os.path.exists(SRC_VIDEO):
        raise FileNotFoundError(f"Source video not found: {SRC_VIDEO}")

    # Copy source video to output folder
    avatar_path = os.path.join(OUTPUT_DIR, "mobilerun_avatar.mp4")
    shutil.copyfile(SRC_VIDEO, avatar_path)
    print(f"[1/5] Copied video to: {avatar_path}")

    # Step 2: Take screenshots of mobilerun.ai
    print("[2/5] Taking screenshots of https://mobilerun.ai ...")
    screenshots = await take_screenshots(URL)
    print(f"  Captured {len(screenshots)} screenshots")

    # Step 3: Transcribe video for word-level timestamps & script extraction
    print("[3/5] Transcribing video audio via ElevenLabs STT...")
    word_timestamps = transcribe_video(avatar_path)
    print(f"  Extracted {len(word_timestamps)} words with timestamps")

    # Reconstruct script text from transcription
    script_text = " ".join(w["word"] for w in word_timestamps)
    print(f"\n--- Transcribed Script from Video ---")
    print(script_text)
    print(f"-------------------------------------\n")

    # Step 4: Create captions SRT & attempt overlay
    srt_content = words_to_srt(word_timestamps)
    srt_path = save_srt(srt_content, filename="mobilerun_captions.srt")
    print(f"[4/5] Saved SRT captions: {srt_path}")

    captioned_video = add_captions_overlay(avatar_path, srt_path, output_filename="mobilerun_captioned.mp4")

    # Step 5: Plan & apply image overlays
    print("[5/5] Planning and applying screenshot overlays...")
    overlay_plan = generate_image_overlay_plan(script_text, word_timestamps, screenshots)
    print(f"  Overlay plan: {json.dumps(overlay_plan, indent=2)}")

    final_video = add_image_overlays(
        captioned_video,
        overlay_plan,
        screenshots,
        output_filename="mobilerun_final_captioned.mp4",
    )

    # Save result.json
    result = {
        "url": URL,
        "transcribed_script": script_text,
        "screenshots": screenshots,
        "avatar_video": avatar_path,
        "word_timestamps": word_timestamps[:20],
        "overlay_plan": overlay_plan,
        "final_video": final_video,
        "status": "complete",
    }
    result_path = os.path.join(OUTPUT_DIR, "mobilerun_result.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n{'='*60}")
    print(f"  MOBILERUN PIPELINE COMPLETE!")
    print(f"  Transcribed Script: {script_text[:120]}...")
    print(f"  Final Video: {final_video}")
    print(f"  Result JSON: {result_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
