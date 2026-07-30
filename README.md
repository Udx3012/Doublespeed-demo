# DoubleSpeed AI — Automated Video Generation Pipeline

**Turn any website URL into high-converting AI marketing videos — automatically.**

DoubleSpeed AI is an end-to-end automated video pipeline that scrapes any target product page, generates vision-aware marketing scripts, creates realistic AI avatar videos, overlays product screenshots at exact speech timestamps with animated captions, and auto-posts to social media. One URL in, publish-ready product video out.

## Demo

Paste a product URL → select an AI avatar → get a polished 9:16 vertical product marketing video in minutes.

## How It Works

```
URL → Scrape + Screenshots → AI Vision Script → Avatar Render → Transcribe → Dynamic Overlays → Auto-Post
```

| Step | What happens | Powered by |
|------|-------------|------------|
| 1. Scrape | Extracts markdown content from the target website | Firecrawl API |
| 2. Screenshots | Captures high-res screenshots at multiple scroll positions | Playwright |
| 3. Script | Generates 3 viral marketing scripts in different styles (mind-blown, discovery, storytime) | Google Gemini 2.5 Flash / AgentRouter |
| 4. Avatar Video | Creates a talking-head video with an AI avatar (Ben) reading the script | Synthesia / HeyGen API (or user MP4 fallback) |
| 5. Transcribe | Obtains word-level timestamps from spoken audio | ElevenLabs / Local Whisper |
| 6. Captions | Adds karaoke-style animated captions | PupCaps + FFmpeg |
| 7. Overlays | AI plans screenshot popup timing; FFmpeg composites avatar + screenshots + captions | Google Gemini + FFmpeg |
| 8. Post | Auto-publishes to Twitter/X via autonomous browser agent | browser-use + Gemini |

## Architecture

```
┌────────────────────────────────────────────────────┐
│                  Next.js Frontend                   │
│                                                    │
│  Landing Page (/)      App (/app)                  │
│  ┌──────────────┐     ┌─────────────────────────┐  │
│  │  Waitlist     │     │ URL → Avatar → Generate │  │
│  │  (Supabase)   │     │ → Preview → Post        │  │
│  └──────────────┘     └─────────────────────────┘  │
└──────────────────────────┬─────────────────────────┘
                           │ SSE (real-time progress)
                           ▼
┌────────────────────────────────────────────────────┐
│            DoubleSpeed Python Pipeline             │
│                                                    │
│  scraper.py → script_generator.py → video_creator  │
│  → transcriber.py → video_composer.py → poster     │
└────────────────────────────────────────────────────┘
```

## Tech Stack

**Frontend**
- Next.js 16 (App Router)
- Tailwind CSS 4
- Firebase Firestore (waitlist)

**Pipeline**
- Python 3.11+
- Google Gemini 2.5 Flash / OpenAI SDK (vision script generation + overlay planning)
- Synthesia / HeyGen API (AI avatar video)
- ElevenLabs Scribe / Local Whisper (speech-to-text with word timestamps)
- Firecrawl (web scraping)
- Playwright (screenshots)
- PupCaps (animated captions)
- FFmpeg (video composition)
- browser-use (autonomous social media posting)

## Getting Started

### Prerequisites

- Node.js 20+
- Python 3.11+
- FFmpeg installed
- [PupCaps](https://github.com/nicholasgasior/pupcaps) installed (`npm install -g pupcaps`)

### 1. Clone & Install

```bash
git clone https://github.com/your-username/doublespeed-pipeline.git
cd doublespeed-pipeline

# Frontend
npm install

# Pipeline
cd pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment

```bash
# Frontend
cp .env.local.example .env.local

# Pipeline
# Edit pipeline/.env and add your Gemini API Key
```

**Key Environment Variables (`pipeline/.env`):**
| Key | Service | Purpose |
|-----|---------|---------|
| `GEMINI_API_KEY` | Google AI Studio | Free AI script generation + overlay timing |
| `FIRECRAWL_API_KEY` | Firecrawl | Web content scraping |
| `SYNTHESIA_API_KEY` / `HEYGEN_API_KEY` | Synthesia / HeyGen | Avatar video rendering |
| `ELEVENLABS_API_KEY` | ElevenLabs | Word timestamp transcription |
| `BROWSER_USE_API_KEY` | Browser-Use | Autonomous social posting |

### 3. Run

```bash
# Start the web app
npm run dev

# Or run the pipeline directly
cd pipeline
python3 main.py https://your-product.com

# With auto-posting to Twitter
python3 main.py https://your-product.com --post

# Run with user-provided avatar MP4
python3 main.py https://your-product.com --avatar output/avatar_ben.mp4
```

## Project Structure

```
├── src/
│   ├── app/
│   │   ├── page.tsx              # Landing page (waitlist)
│   │   ├── app/page.tsx          # Product app (generation flow)
│   │   └── api/
│   │       ├── generate/route.ts # Streams pipeline progress via SSE
│   │       ├── video/[jobId]/    # Serves generated videos
│   │       └── youtube/route.ts  # YouTube upload endpoint
│   ├── config/
│   │   ├── firebase.ts           # Firebase client config
│   │   └── avatars.ts            # Avatar definitions (Ben)
│   └── types/index.ts
├── pipeline/
│   ├── main.py                   # Pipeline orchestrator
│   ├── scraper.py                # Firecrawl + Playwright
│   ├── script_generator.py       # Gemini script + overlay planning
│   ├── video_creator.py          # Synthesia / HeyGen API
│   ├── transcriber.py            # ElevenLabs / Whisper STT
│   ├── video_composer.py         # FFmpeg composition
│   ├── twitter_poster.py         # browser-use automation
│   └── agent_skill.py            # AI Agent integration skill
└── .env.local
```

## License

MIT
