"""
AI Agent Skill: Video Generator

This skill allows an AI Agent to generate marketing videos
for any website URL. It scrapes the site, generates viral scripts,
creates avatar videos with HeyGen, and can auto-post to Twitter.

Usage:
  python3 agent_skill.py "https://example.com"
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from main import run_pipeline


def skill_entry(args: dict) -> dict:
    """Entry point for AI Agent skill integration.

    Args:
        args: {
            "url": "https://target-website.com",
            "post": false,  # whether to auto-post to Twitter
            "num_scripts": 3
        }

    Returns:
        dict with generated scripts, video paths, and status
    """
    url = args.get("url", "")
    post = args.get("post", False)

    if not url:
        return {"error": "URL is required"}

    result = asyncio.run(run_pipeline(url, post_to_x=post))
    return result


if __name__ == "__main__":
    import json

    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    result = skill_entry({"url": url, "post": False})
    print(json.dumps(result, indent=2))
