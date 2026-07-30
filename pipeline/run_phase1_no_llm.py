"""
Phase 1 bypass: scrape + screenshots only, skip LLM (quota exhausted).
Uses hand-crafted doublespeed.ai scripts. Saves result.json + prints HeyGen prompt.
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from scraper import scrape_content, take_screenshots
from config import OUTPUT_DIR, HEYGEN_API_KEY, SYNTHESIA_API_KEY

URL = "https://doublespeed.ai"

# Hand-crafted scripts for doublespeed.ai
SCRIPTS = [
    {
        "style": "mind_blown",
        "text": "This company just created something absolutely mind-blowing. DoubleSpeed AI takes any website URL and automatically generates a viral marketing video in minutes. It scrapes your site, creates an AI avatar talking-head video, adds karaoke captions and screenshot overlays — fully automated. Check it out, link in bio!",
        "hook": "This company just created something absolutely mind-blowing",
    },
    {
        "style": "discovery",
        "text": "I just discovered this tool and I genuinely cannot believe it's real. DoubleSpeed AI turns any website into a full viral video with an AI avatar, auto-captions, and timed screenshot overlays — zero editing. I went from URL to finished video in under 10 minutes. Seriously check this out, link in bio.",
        "hook": "I just discovered this tool and I genuinely cannot believe it's real",
    },
    {
        "style": "storytime",
        "text": "Okay so I need to tell you about this because nobody is talking about it. DoubleSpeed AI is an automated video pipeline — paste a URL, and it scrapes the site, generates a viral script, renders an AI avatar video, adds captions and overlays, then posts it to Twitter automatically. It's wild. Link in bio.",
        "hook": "Okay so I need to tell you about this because nobody is talking about it",
    },
]


async def main():
    print(f"\n{'='*60}")
    print(f"  DOUBLESPEED — PHASE 1 (no LLM mode)")
    print(f"  Target: {URL}")
    print(f"{'='*60}\n")

    print("[1/2] Scraping website content...")
    content = scrape_content(URL)
    print(f"  Extracted {len(content)} characters")

    print("[2/2] Taking screenshots...")
    screenshots = await take_screenshots(URL)
    print(f"  Captured {len(screenshots)} screenshots")

    result = {
        "url": URL,
        "scripts": SCRIPTS,
        "screenshots": screenshots,
        "avatar_video": None,
        "status": "awaiting_avatar",
        "content_excerpt": content[:2000],
    }

    result_path = os.path.join(OUTPUT_DIR, "result.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    chosen = SCRIPTS[0]

    print(f"\n{'='*60}")
    print(f"  PHASE 1 COMPLETE")
    print(f"{'='*60}")
    print(f"\n  HEYGEN SCRIPT (copy this into HeyGen to generate your avatar):\n")
    print(f"  {chosen['text']}")
    print(f"\n  Save the generated MP4 as:")
    print(f"     {os.path.join(OUTPUT_DIR, 'avatar_ben.mp4')}")
    print(f"\n  Then run Phase 2:")
    print(f"     python main.py --resume (no job-id needed)")
    print(f"\n  Result saved: {result_path}")
    print(f"{'='*60}\n")


asyncio.run(main())
