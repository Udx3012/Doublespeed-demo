"""Auto-post product video to Twitter/X using browser-use."""

import os
import asyncio
from browser_use import Agent
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, OPENAI_BASE_URL, GEMINI_API_KEY


def _get_llm():
    """Configure LLM for browser-use agent."""
    if GEMINI_API_KEY:
        return ChatOpenAI(
            model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
            api_key=GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
    return ChatOpenAI(
        model=os.getenv("LLM_MODEL", "gpt-4o"),
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL if OPENAI_BASE_URL else None,
    )


async def post_to_twitter(video_path: str, caption: str) -> None:
    """Use browser-use to upload and post a video to Twitter/X, or simulate if requested."""
    simulate = os.getenv("SIMULATE_POSTING", "true").lower() in ("true", "1", "yes")
    
    if simulate or not (os.getenv("TWITTER_USERNAME") or os.getenv("BROWSER_USE_API_KEY")):
        print(f"  [Simulated Post] Video: {video_path}")
        print(f"  [Simulated Post] Caption: {caption}")
        print(f"  [Simulated Post] Status: Successfully posted to Twitter/X (Simulation mode)")
        return

    username = os.getenv("TWITTER_USERNAME", "")
    password = os.getenv("TWITTER_PASSWORD", "")

    login_instructions = ""
    if username and password:
        login_instructions = f"""
    - If presented with a login page (x.com/i/flow/login or x.com/login):
      a. Type username '{username}' into the username field and click Next.
      b. Type password '{password}' into the password field and click Log in.
        """

    task = f"""
    1. Go to https://x.com/compose/post
    2. Check if logged in: {login_instructions}
    3. Click the media upload button (the image/gallery icon in the compose toolbar).
    4. Upload the video file located at: {video_path}
    5. Wait for the video to finish uploading (progress bar completes).
    6. Click in the text area and type this caption: {caption}
    7. Click the "Post" button to publish.
    8. Wait for confirmation that the post was published.
    """

    llm = _get_llm()
    agent = Agent(task=task, llm=llm)
    await agent.run()


if __name__ == "__main__":
    import sys

    video = sys.argv[1] if len(sys.argv) > 1 else "output/video_doublespeed.mp4"
    caption = sys.argv[2] if len(sys.argv) > 2 else "Check this out! #DoubleSpeed #AI"
    asyncio.run(post_to_twitter(video, caption))
