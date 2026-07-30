"""
Main pipeline orchestrator — Two-Phase Architecture:

  Phase 1:  URL → scrape → screenshots → script → PAUSE (awaiting avatar)
  Phase 2:  avatar MP4 → transcribe → captions → image overlays → final video

Usage:
  # Phase 1: Generate scripts + screenshots (pauses for manual avatar creation)
  python main.py https://doublespeed.ai
  python main.py https://doublespeed.ai --job-id my-job

  # Phase 2: Resume after placing avatar_ben.mp4 in output folder
  python main.py --resume my-job

  # Local mode: skip scraping, reuse existing output/ files
  python main.py --local
  python main.py --local --avatar output/avatar_xxx.mp4
"""

import asyncio
import sys
import json
import os
import glob
from scraper import scrape_content, take_screenshots
from script_generator import generate_scripts, generate_image_overlay_plan, generate_caption
from video_creator import create_and_download
from transcriber import transcribe_video, words_to_srt, save_srt
from video_composer import add_captions_overlay, add_image_overlays
from twitter_poster import post_to_twitter
from config import OUTPUT_DIR


def _save_result(result: dict) -> str:
    """Save result.json to OUTPUT_DIR."""
    result_path = os.path.join(OUTPUT_DIR, "result.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    return result_path


def _load_result() -> dict:
    """Load existing result.json from OUTPUT_DIR."""
    result_path = os.path.join(OUTPUT_DIR, "result.json")
    if not os.path.exists(result_path):
        raise FileNotFoundError(f"No result.json found at {result_path}. Run Phase 1 first.")
    with open(result_path, "r") as f:
        return json.load(f)


def _find_avatar_video() -> str | None:
    """Look for avatar_ben.mp4 or any avatar_*.mp4 in OUTPUT_DIR."""
    # Primary: avatar_ben.mp4
    ben_path = os.path.join(OUTPUT_DIR, "avatar_ben.mp4")
    if os.path.exists(ben_path) and os.path.getsize(ben_path) > 1024:
        return ben_path

    # Fallback: any avatar_*.mp4 that isn't empty
    mp4s = sorted(glob.glob(os.path.join(OUTPUT_DIR, "avatar_*.mp4")))
    for mp4 in mp4s:
        if os.path.getsize(mp4) > 1024:
            return mp4

    return None


async def run_phase1(url: str, post_to_x: bool = False) -> dict:
    """
    Phase 1: Scrape website, take screenshots, generate scripts.
    Saves result.json with status 'awaiting_avatar' and prints instructions.
    """
    print(f"\n{'='*60}")
    print(f"  DOUBLESPEED PIPELINE — PHASE 1")
    print(f"  Target: {url}")
    print(f"{'='*60}\n")

    # Step 1: Scrape website content
    print("[1/7] Scraping website content...")
    content = scrape_content(url)
    print(f"  Extracted {len(content)} characters of content")

    # Step 2: Take multiple screenshots
    print("[2/7] Taking screenshots at different scroll positions...")
    screenshots = await take_screenshots(url)
    print(f"  Captured {len(screenshots)} screenshots")

    # Step 3: Generate product scripts (informed by screenshots)
    print("[3/7] Generating marketing scripts...")
    scripts = generate_scripts(content, url, screenshots, num_scripts=3)
    for s in scripts:
        print(f"  [{s['style']}] {s['text'][:80]}...")

    # Step 4: Check if we can auto-generate avatar video
    print("[4/7] Selecting AI avatar video...")

    # Check for CLI --avatar flag
    custom_avatar = None
    if "--avatar" in sys.argv:
        idx = sys.argv.index("--avatar")
        if idx + 1 < len(sys.argv):
            custom_avatar = sys.argv[idx + 1]

    from config import HEYGEN_API_KEY, SYNTHESIA_API_KEY

    avatar_path = None
    status = "awaiting_avatar"

    if custom_avatar and os.path.exists(custom_avatar) and os.path.getsize(custom_avatar) > 1024:
        print(f"  Using user-provided avatar video: {custom_avatar}")
        avatar_path = custom_avatar
        status = "avatar_ready"
    elif HEYGEN_API_KEY or SYNTHESIA_API_KEY:
        try:
            chosen_script = scripts[0]
            avatar_path = create_and_download(chosen_script["text"])
            status = "avatar_ready"
        except Exception as e:
            print(f"  [Notice] API avatar generation failed ({e}).")
            avatar_path = None
    else:
        # Check if avatar already exists in output dir (user may have placed it)
        existing = _find_avatar_video()
        if existing:
            print(f"  Found existing avatar video: {existing}")
            avatar_path = existing
            status = "avatar_ready"

    # Save Phase 1 result
    result = {
        "url": url,
        "scripts": scripts,
        "screenshots": screenshots,
        "avatar_video": avatar_path,
        "status": status,
        "post_to_x": post_to_x,
        "content_excerpt": content[:2000],
    }

    if status == "avatar_ready" and avatar_path:
        # We have an avatar — continue to Phase 2 inline
        print(f"\n  Avatar video ready: {avatar_path}")
        _save_result(result)
        return await _run_phase2_steps(result)
    else:
        # No avatar — save and pause
        result_path = _save_result(result)
        chosen_script = scripts[0]

        print(f"\n{'='*60}")
        print(f"  PHASE 1 COMPLETE -- AWAITING AVATAR VIDEO")
        print(f"{'='*60}")
        print(f"\n  [SCRIPT] Copy this into HeyGen to generate your avatar video:\n")
        print(f"  --- Script ({chosen_script['style']}) ---")
        print(f"  {chosen_script['text']}")
        print(f"  {'-'*30}\n")
        print(f"  [OUTPUT] Save the generated MP4 to:")
        print(f"     {os.path.join(OUTPUT_DIR, 'avatar_ben.mp4')}")
        print(f"\n  Then run Phase 2:")
        print(f"     python main.py --resume {os.path.basename(OUTPUT_DIR)}")
        print(f"\n  Results saved: {result_path}")
        print(f"{'='*60}\n")

        return result


async def run_phase2(job_id: str | None = None) -> dict:
    """
    Phase 2: Resume from saved result.json — transcribe, caption, overlay, compose.
    Requires avatar_ben.mp4 to exist in the output directory.
    """
    print(f"\n{'='*60}")
    print(f"  DOUBLESPEED PIPELINE — PHASE 2 (RESUME)")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"{'='*60}\n")

    # Load Phase 1 result
    result = _load_result()

    # Find avatar video
    avatar_path = _find_avatar_video()
    if not avatar_path:
        expected = os.path.join(OUTPUT_DIR, "avatar_ben.mp4")
        raise FileNotFoundError(
            f"No avatar video found in {OUTPUT_DIR}. "
            f"Please save your HeyGen-generated video as: {expected}"
        )

    print(f"  Found avatar video: {avatar_path}")
    result["avatar_video"] = avatar_path
    result["status"] = "processing"
    _save_result(result)

    return await _run_phase2_steps(result)


async def _run_phase2_steps(result: dict) -> dict:
    """Shared Phase 2 logic: transcribe → captions → overlays → final video."""
    avatar_path = result["avatar_video"]
    screenshots = result.get("screenshots", [])
    scripts = result.get("scripts", [])
    chosen_script = scripts[0] if scripts else {"text": "", "style": "mind_blown"}

    # Step 5: Transcribe video → word timestamps → SRT
    print("[5/7] Transcribing video for captions...")
    word_timestamps = transcribe_video(avatar_path)
    print(f"  Got {len(word_timestamps)} words with timestamps")

    srt_content = words_to_srt(word_timestamps)
    srt_path = save_srt(srt_content)
    print(f"  SRT saved: {srt_path}")

    # Step 5b: Add styled captions overlay using PupCaps
    print("  Adding styled captions (PupCaps)...")
    captioned_video = add_captions_overlay(avatar_path, srt_path)

    # Step 6: Decide when to show screenshots as overlays
    print("[6/7] Planning image overlays with AI...")
    if word_timestamps and screenshots:
        overlay_plan = generate_image_overlay_plan(
            chosen_script["text"], word_timestamps, screenshots
        )
    else:
        overlay_plan = []
    print(f"  Overlay plan: {json.dumps(overlay_plan, indent=2)}")

    # Step 6b: Compose final video with timed screenshot overlays
    final_video = add_image_overlays(captioned_video, overlay_plan, screenshots)

    # Step 7 (optional): Post to Twitter
    post_to_x = result.get("post_to_x", False)
    if post_to_x:
        print("[7/7] Posting to Twitter/X...")
        content = result.get("content_excerpt", "")
        caption = generate_caption(content, chosen_script["style"])
        await post_to_twitter(final_video, caption)
        print(f"  Posted with caption: {caption}")
    else:
        print("[7/7] Skipping Twitter post (use --post to enable)")

    # Update result with Phase 2 data
    result["word_timestamps"] = word_timestamps[:20]
    result["overlay_plan"] = overlay_plan
    result["final_video"] = final_video
    result["status"] = "complete"
    # Remove content excerpt from final result (not needed)
    result.pop("content_excerpt", None)
    result.pop("post_to_x", None)

    result_path = _save_result(result)

    print(f"\n{'='*60}")
    print(f"  DONE! Final video: {final_video}")
    print(f"  Results saved: {result_path}")
    print(f"{'='*60}\n")

    return result


async def run_local(avatar_path: str | None = None) -> dict:
    """
    Local mode: reuse existing output/ files to test composition
    without calling HeyGen, Firecrawl, or scraping again.
    """
    print(f"\n{'='*60}")
    print(f"  DOUBLESPEED PIPELINE — LOCAL MODE")
    print(f"  Reusing files from: {OUTPUT_DIR}")
    print(f"{'='*60}\n")

    # Find avatar video
    if not avatar_path:
        avatar_path = _find_avatar_video()
        if not avatar_path:
            raise FileNotFoundError("No avatar_*.mp4 found in output/. Run full pipeline first.")
    print(f"  Using avatar: {avatar_path}")

    # Find screenshots
    screenshots = sorted(glob.glob(os.path.join(OUTPUT_DIR, "screenshot_[0-9]*.png")))
    if not screenshots:
        raise FileNotFoundError("No screenshot_*.png found in output/. Run full pipeline first.")
    print(f"  Using {len(screenshots)} screenshots")

    # Build a minimal result dict for Phase 2
    result = {
        "avatar_video": avatar_path,
        "screenshots": screenshots,
        "scripts": [{"text": "", "style": "local"}],
        "status": "processing",
    }

    # Step 5: Transcribe
    print("[1/3] Transcribing video for captions...")
    word_timestamps = transcribe_video(avatar_path)
    print(f"  Got {len(word_timestamps)} words with timestamps")

    srt_content = words_to_srt(word_timestamps)
    srt_path = save_srt(srt_content)
    print(f"  SRT saved: {srt_path}")

    # Step 5b: Captions overlay
    print("  Adding styled captions (PupCaps)...")
    captioned_video = add_captions_overlay(avatar_path, srt_path)

    # Step 6: Image overlay plan
    print("[2/3] Planning image overlays with AI...")
    script_text = " ".join(w["word"] for w in word_timestamps)
    overlay_plan = generate_image_overlay_plan(script_text, word_timestamps, screenshots)
    print(f"  Overlay plan: {json.dumps(overlay_plan, indent=2)}")

    # Step 6b: Compose
    print("[3/3] Composing final video with overlays...")
    final_video = add_image_overlays(captioned_video, overlay_plan, screenshots)

    print(f"\n{'='*60}")
    print(f"  DONE! Final video: {final_video}")
    print(f"{'='*60}\n")

    return {"final_video": final_video, "overlay_plan": overlay_plan}


if __name__ == "__main__":
    from config import RESUME_JOB_ID

    local_mode = "--local" in sys.argv
    resume_mode = RESUME_JOB_ID is not None

    if local_mode:
        # Check for --avatar flag
        avatar = None
        if "--avatar" in sys.argv:
            idx = sys.argv.index("--avatar")
            if idx + 1 < len(sys.argv):
                avatar = sys.argv[idx + 1]
        asyncio.run(run_local(avatar_path=avatar))
    elif resume_mode:
        asyncio.run(run_phase2(job_id=RESUME_JOB_ID))
    else:
        url = sys.argv[1] if len(sys.argv) > 1 else "https://doublespeed.ai"
        post = "--post" in sys.argv
        asyncio.run(run_phase1(url, post_to_x=post))
