"""Generate viral product scripts from scraped website content + screenshots."""

import base64
import os
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_BASE_URL, GEMINI_API_KEY, HEYGEN_TEST_MODE

client_args = {"api_key": OPENAI_API_KEY}
if OPENAI_BASE_URL:
    client_args["base_url"] = OPENAI_BASE_URL

client = OpenAI(**client_args)

DEFAULT_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash" if GEMINI_API_KEY else "gpt-4o-mini")

VIDEO_STYLES = [
    {
        "name": "mind_blown",
        "hook": "This company just created something absolutely mind-blowing",
        "tone": "excited, disbelief, sharing a secret",
    },
    {
        "name": "discovery",
        "hook": "I just discovered this tool and I genuinely cannot believe it's real",
        "tone": "authentic surprise, casual, relatable",
    },
    {
        "name": "storytime",
        "hook": "Okay so I need to tell you about this because nobody is talking about it",
        "tone": "conversational, urgent, insider knowledge",
    },
]


def _encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def generate_scripts(
    content: str, url: str, screenshots: list[str], num_scripts: int = 3
) -> list[dict]:
    """Generate product scripts informed by both content and visual screenshots."""
    scripts = []

    # Build image content for the prompt
    image_messages = []
    for i, ss in enumerate(screenshots[:4]):
        if os.path.exists(ss):
            image_messages.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{_encode_image(ss)}",
                    "detail": "low",
                },
            })

    for style in VIDEO_STYLES[:num_scripts]:
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""You are a top viral video creator for DoubleSpeed AI. Generate a short product video script (50-80 words, 15-25 seconds when spoken) promoting a product/website.

STYLE: {style['name']}
HOOK: {style['hook']}
TONE: {style['tone']}

WEBSITE CONTENT:
{content[:3000]}

URL: {url}

I'm also showing you screenshots of the website. Reference specific visual elements you see (UI, dashboard, features shown on screen) to make the script feel authentic.

RULES:
- Start with a strong hook that grabs attention in the first 2 seconds
- Sound natural and authentic, like a real person talking to camera
- Mention 1-2 specific features or benefits visible in the screenshots
- End with a soft CTA (check it out, link in bio, etc.)
- Do NOT sound like an ad. Sound like genuine excitement.
- Keep it under 80 words total.

Return ONLY the script text, nothing else.""",
                    },
                    *image_messages,
                ],
            }
        ]

        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            temperature=0.9,
            max_tokens=2000,
        )

        script_text = response.choices[0].message.content.strip()

        if HEYGEN_TEST_MODE:
            # Trim to first sentence only
            first_sentence = script_text.split(".")[0] + "."
            script_text = first_sentence

        scripts.append({
            "style": style["name"],
            "text": script_text,
            "hook": style["hook"],
        })

    return scripts


def generate_image_overlay_plan(
    script_text: str, word_timestamps: list[dict], screenshots: list[str]
) -> list[dict]:
    """
    Use OpenAI to decide when to show which screenshot as an overlay.

    Args:
        script_text: The full video script
        word_timestamps: List of {"word": str, "start": float, "end": float}
        screenshots: List of screenshot file paths

    Returns:
        List of {"screenshot_index": int, "start_time": float, "end_time": float, "description": str}
    """
    # Build descriptions of available screenshots
    image_messages = []
    for i, ss in enumerate(screenshots[:5]):
        if os.path.exists(ss):
            image_messages.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{_encode_image(ss)}",
                    "detail": "low",
                },
            })

    # Format word timestamps for context
    timed_script = " ".join(
        f"[{w['start']:.1f}s]{w['word']}" for w in word_timestamps
    )

    # Get total video duration from last word timestamp
    video_duration = word_timestamps[-1]["end"] if word_timestamps else 15.0

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""You are planning image overlays for a product marketing video. The avatar is speaking the script below, and we want to show relevant screenshots on the BOTTOM portion of the video to support what's being said.

SCRIPT WITH TIMESTAMPS:
{timed_script}

TOTAL VIDEO DURATION: {video_duration:.1f}s

I'm showing you {len(screenshots)} screenshots of the website (numbered 0 to {len(screenshots)-1}).

RULES:
- Screenshots should stay visible for LONG durations — each one stays until the next one replaces it
- The first screenshot should appear early (within the first 2 seconds)
- Use 2-4 different screenshots total, shown sequentially
- Each screenshot's end_time should equal the next screenshot's start_time (no gaps — always showing something)
- The last screenshot should stay until the end of the video
- Pick the most relevant screenshot for what's being discussed at that moment
- When the speaker mentions a new feature/section, switch to a more relevant screenshot

Return a JSON array of overlay instructions:
[
  {{"screenshot_index": 0, "start_time": 1.0, "end_time": 6.0, "description": "showing the hero section"}},
  {{"screenshot_index": 2, "start_time": 6.0, "end_time": {video_duration:.1f}, "description": "showing features section"}},
  ...
]

Return ONLY the JSON array, no other text.""",
                },
                *image_messages,
            ],
        }
    ]

    import json
    import re

    def _default_plan():
        duration = word_timestamps[-1]["end"] if word_timestamps else 15.0
        n = min(len(screenshots), 4)
        step = max(3.0, duration / max(1, n))
        plan = []
        for i in range(n):
            plan.append({
                "screenshot_index": i,
                "start_time": round(i * step, 1),
                "end_time": round((i + 1) * step if i < n - 1 else duration, 1),
                "description": f"screenshot_{i}",
            })
        return plan

    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=2000,
        )
        raw = response.choices[0].message.content.strip()
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(raw)
    except Exception as e:
        print(f"  [Notice] Overlay plan LLM call failed ({type(e).__name__}). Using default sequence.")
        return _default_plan()


def generate_caption(content: str, style: str) -> str:
    """Generate a Twitter caption with hashtags."""
    prompt = f"""Generate a short Twitter/X caption (under 200 chars) for a product video. Include 2-3 relevant hashtags. Style: {style}

Content summary: {content[:500]}

Return ONLY the caption text."""

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=100,
    )
    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    test_content = "Acme Corp makes AI-powered widgets that save developers 10 hours per week."
    scripts = generate_scripts(test_content, "https://acme.com", [])
    for s in scripts:
        print(f"\n--- {s['style']} ---")
        print(s["text"])
