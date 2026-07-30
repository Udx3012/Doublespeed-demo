"""Create avatar videos using HeyGen API v3.

Docs:
- https://developers.heygen.com/generate-avatar-video
- https://developers.heygen.com/avatar-v

Flow:
1. POST /v3/videos → returns video_id (async, does NOT wait for render)
2. GET /v3/videos/{video_id} → poll until status is "completed" or "failed"
3. Download from video_url in the completed response
"""

import time
import requests
import os
from config import (
    HEYGEN_API_KEY, HEYGEN_AVATAR_ID, HEYGEN_VOICE_ID, HEYGEN_BASE_URL,
    SYNTHESIA_API_KEY, SYNTHESIA_BASE_URL, OUTPUT_DIR
)


def create_synthesia_video(script: str) -> str:
    """Create avatar video using Synthesia API v2."""
    headers = {
        "Authorization": SYNTHESIA_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "title": "DoubleSpeed Video",
        "visibility": "public",
        "input": [
            {
                "scriptText": script,
                "avatar": os.getenv("SYNTHESIA_AVATAR_ID", "anna_costume_transparent"),
                "background": "transparent"
            }
        ]
    }
    resp = requests.post(f"{SYNTHESIA_BASE_URL}/videos", headers=headers, json=payload, timeout=60)
    if not resp.ok:
        print(f"  Synthesia error {resp.status_code}: {resp.text}")
        resp.raise_for_status()

    data = resp.json()
    video_id = data.get("id")
    if not video_id:
        raise RuntimeError(f"No video id in Synthesia response: {data}")
    return video_id


def poll_synthesia_video(video_id: str, timeout: int = 600, interval: int = 15) -> dict:
    """Poll Synthesia video status until complete."""
    headers = {"Authorization": SYNTHESIA_API_KEY}
    start = time.time()

    while time.time() - start < timeout:
        resp = requests.get(f"{SYNTHESIA_BASE_URL}/videos/{video_id}", headers=headers, timeout=30)
        if not resp.ok:
            print(f"  Synthesia poll error {resp.status_code}: {resp.text}")
            resp.raise_for_status()

        data = resp.json()
        status = data.get("status", "unknown")
        elapsed = int(time.time() - start)
        print(f"  [{elapsed}s] Synthesia Video {video_id}: {status}")

        if status in ("complete", "completed"):
            return data
        elif status in ("failed", "error"):
            raise RuntimeError(f"Synthesia Video failed: {data}")

        time.sleep(interval)

    raise TimeoutError(f"Synthesia Video {video_id} timed out")


def create_avatar_video(script: str, aspect_ratio: str = "9:16") -> str:
    """
    POST /v3/videos — async video creation.
    Returns video_id immediately. Video renders in the background.
    """
    headers = {
        "x-api-key": HEYGEN_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "type": "avatar",
        "avatar_id": HEYGEN_AVATAR_ID,
        "script": script,
        "resolution": "1080p",
        "aspect_ratio": aspect_ratio,
        "engine": {"type": "avatar_v"},
    }
    if HEYGEN_VOICE_ID:
        payload["voice_id"] = HEYGEN_VOICE_ID

    resp = requests.post(
        f"{HEYGEN_BASE_URL}/v3/videos",
        headers=headers,
        json=payload,
        timeout=60,
    )

    if not resp.ok:
        print(f"  HeyGen create error {resp.status_code}: {resp.text}")
        resp.raise_for_status()

    data = resp.json()
    video_id = data.get("data", {}).get("video_id")
    if not video_id:
        raise RuntimeError(f"No video_id in response: {data}")
    return video_id


def poll_video(video_id: str, timeout: int = 600, interval: int = 15) -> dict:
    """
    GET /v3/videos/{video_id} — poll until status is completed/failed.
    HeyGen renders asynchronously; typical wait is 1-5 minutes.
    """
    headers = {"x-api-key": HEYGEN_API_KEY}
    start = time.time()

    while time.time() - start < timeout:
        resp = requests.get(
            f"{HEYGEN_BASE_URL}/v3/videos/{video_id}",
            headers=headers,
            timeout=30,
        )

        if not resp.ok:
            print(f"  Poll error {resp.status_code}: {resp.text}")
            resp.raise_for_status()

        data = resp.json().get("data", {})
        status = data.get("status", "unknown")
        elapsed = int(time.time() - start)
        print(f"  [{elapsed}s] Video {video_id}: {status}")

        if status == "completed":
            return data
        elif status == "failed":
            raise RuntimeError(
                f"Video failed: {data.get('failure_message', data.get('failure_code', 'unknown'))}"
            )

        time.sleep(interval)

    raise TimeoutError(f"Video {video_id} did not complete in {timeout}s")


def download_video(video_url: str, filename: str = "avatar.mp4") -> str:
    """Download the rendered video file."""
    output_path = os.path.join(OUTPUT_DIR, filename)
    resp = requests.get(video_url, timeout=120, stream=True)
    resp.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    return output_path


def create_and_download(script: str) -> str:
    """Full flow: create video via Synthesia or HeyGen, poll, download. Returns local file path."""
    provider = os.getenv("VIDEO_PROVIDER", "synthesia" if SYNTHESIA_API_KEY else "heygen").lower()

    if provider == "synthesia" or (SYNTHESIA_API_KEY and not HEYGEN_API_KEY):
        print(f"Creating Synthesia avatar video for script: {script[:50]}...")
        video_id = create_synthesia_video(script)
        print(f"  Synthesia Video ID: {video_id} — polling for completion...")
        data = poll_synthesia_video(video_id)
        video_url = data.get("download")
        if not video_url:
            raise RuntimeError(f"No download URL in Synthesia response: {data}")
        print(f"  Synthesia Video URL: {video_url}")
        local_path = download_video(video_url, f"avatar_{video_id}.mp4")
        print(f"  Downloaded: {local_path}")
        return local_path

    print(f"Creating HeyGen video for script: {script[:50]}...")
    video_id = create_avatar_video(script)
    print(f"  Video ID: {video_id} — polling for completion...")

    data = poll_video(video_id)
    video_url = data.get("video_url")
    if not video_url:
        raise RuntimeError(f"No video_url in completed data: {data}")
    print(f"  Video URL: {video_url}")

    local_path = download_video(video_url, f"avatar_{video_id}.mp4")
    print(f"  Downloaded: {local_path}")
    return local_path


if __name__ == "__main__":
    test_script = "Hey everyone, I just found this incredible tool that saves developers ten hours a week. You have to check it out, link in bio."
    path = create_and_download(test_script)
    print(f"Done: {path}")
