# DoubleSpeed AI — Automated Video Generation Pipeline

## What This Project Does

Automated pipeline that generates high-converting marketing videos promoting any website/product:

1. **Scrape** — Extracts website content + takes screenshots via Firecrawl + Playwright
2. **Script** — Generates multiple viral marketing scripts (mind-blown, discovery, storytime) via Gemini 2.5 Flash
3. **Video** — Creates AI avatar talking-head video via Synthesia / HeyGen API (or user MP4 video)
4. **Compose** — Overlays website screenshots + karaoke captions onto the avatar video in vertical 9:16 format using FFmpeg
5. **Post** — Auto-publishes to Twitter/X using browser-use

## Architecture

- **Frontend**: Next.js (landing page + URL submission app)
- **Backend Pipeline**: Python (scraper → script gen → avatar video → ffmpeg → browser-use)
- **Orchestrator**: Next.js API Routes / Python Orchestrator (`main.py`)

## How to Run

```bash
# Frontend
npm run dev

# Pipeline (standalone)
cd pipeline
python3 main.py https://target-url.com

# With user-provided avatar MP4
python3 main.py https://target-url.com --avatar output/avatar_ben.mp4

# With Twitter posting
python3 main.py https://target-url.com --post
```

## Key Files

- `src/app/page.tsx` — Landing page with waitlist + URL input
- `src/app/app/page.tsx` — Main product application interface
- `pipeline/main.py` — Main pipeline orchestrator
- `pipeline/scraper.py` — Website scraping + Playwright screenshots
- `pipeline/script_generator.py` — Gemini AI script generation & overlay planning
- `pipeline/video_creator.py` — Synthesia / HeyGen API integration
- `pipeline/transcriber.py` — ElevenLabs / Whisper STT timestamp generator
- `pipeline/video_composer.py` — FFmpeg vertical video composition
- `pipeline/twitter_poster.py` — Browser-use Twitter/X automation
- `pipeline/agent_skill.py` — AI Agent integration skill entry point
