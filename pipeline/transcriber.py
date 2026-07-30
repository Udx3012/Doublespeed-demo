"""Transcribe video audio using ElevenLabs STT to get word-level timestamps."""

import requests
from config import ELEVENLABS_API_KEY, OUTPUT_DIR
import os


def transcribe_video(video_path: str) -> list[dict]:
    """
    Use ElevenLabs Speech-to-Text (Scribe v2) or local fallback to get word-level timestamps.

    Returns list of: {"word": str, "start": float, "end": float}
    """
    if not os.path.exists(video_path) or os.path.getsize(video_path) < 1024:
        raise FileNotFoundError(
            f"Avatar video is empty or missing: {video_path}. "
            f"Please place a real avatar MP4 in the output folder before running Phase 2."
        )

    if not ELEVENLABS_API_KEY:
        print("  [Notice] ELEVENLABS_API_KEY not set. Trying local Whisper...")
        try:
            import whisper
            model = whisper.load_model("tiny")
            res = model.transcribe(video_path, word_timestamps=True)
            words = []
            for seg in res.get("segments", []):
                for w in seg.get("words", []):
                    words.append({"word": w["word"].strip(), "start": w["start"], "end": w["end"]})
            if words:
                return words
        except Exception as e:
            print(f"  Local whisper unavailable ({e}).")

        raise RuntimeError(
            "Cannot transcribe video: No ELEVENLABS_API_KEY set and local Whisper is not installed. "
            "Please set ELEVENLABS_API_KEY in pipeline/.env or install openai-whisper."
        )

    url = "https://api.elevenlabs.io/v1/speech-to-text"
    headers = {"xi-api-key": ELEVENLABS_API_KEY}

    with open(video_path, "rb") as f:
        resp = requests.post(
            url,
            headers=headers,
            data={
                "model_id": "scribe_v2",
                "timestamps_granularity": "word",
                "tag_audio_events": "false",
            },
            files={"file": (os.path.basename(video_path), f)},
            timeout=120,
        )

    if not resp.ok:
        print(f"  ElevenLabs STT error {resp.status_code}: {resp.text}")
        resp.raise_for_status()

    data = resp.json()
    words = []

    # Extract word-level timestamps from response, skipping whitespace-only tokens
    for word_info in data.get("words", []):
        text = word_info["text"].strip()
        if not text:
            continue
        words.append({
            "word": text,
            "start": word_info["start"],
            "end": word_info["end"],
        })

    return words


def words_to_srt(words: list[dict], words_per_caption: int = 4) -> str:
    """
    Convert word timestamps to continuous SRT format with karaoke-style highlighting.
    
    Ensures that captions stay continuously visible on screen for the full phrase duration
    without disappearing or flickering between individual words.
    """
    if not words:
        return ""

    srt_entries = []
    caption_idx = 1

    # Chunk words into group phrases
    groups = []
    for i in range(0, len(words), words_per_caption):
        group = words[i : i + words_per_caption]
        group = [w for w in group if w["word"].strip()]
        if group:
            groups.append(group)

    for g_idx, group in enumerate(groups):
        group_text_words = [w["word"] for w in group]

        # Determine the start of the next group (if any) to prevent gap at group end
        if g_idx < len(groups) - 1:
            group_end = groups[g_idx + 1][0]["start"]
        else:
            group_end = group[-1]["end"] + 0.3

        for j, word in enumerate(group):
            start_ts = _format_srt_time(word["start"])

            # Extend end timestamp to next word's start time (or group_end for last word in group)
            if j < len(group) - 1:
                next_word_start = group[j + 1]["start"]
                end_ts = _format_srt_time(next_word_start)
            else:
                end_ts = _format_srt_time(group_end)

            # Build line with current word highlighted in brackets
            parts = []
            for k, w in enumerate(group_text_words):
                if k == j:
                    parts.append(f"[{w}]")
                else:
                    parts.append(w)

            line = " ".join(parts)
            srt_entries.append(f"{caption_idx}\n{start_ts} --> {end_ts}\n{line}\n")
            caption_idx += 1

    return "\n".join(srt_entries)


def _format_srt_time(seconds: float) -> str:
    """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def save_srt(srt_content: str, filename: str = "captions.srt") -> str:
    """Save SRT content to file."""
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", newline="\n", encoding="utf-8") as f:
        f.write(srt_content)
    return path


if __name__ == "__main__":
    import sys

    video = sys.argv[1] if len(sys.argv) > 1 else "output/avatar.mp4"
    print(f"Transcribing: {video}")

    words = transcribe_video(video)
    print(f"Got {len(words)} words")
    for w in words[:10]:
        print(f"  {w['start']:.2f}-{w['end']:.2f}: {w['word']}")

    srt = words_to_srt(words)
    path = save_srt(srt)
    print(f"SRT saved: {path}")
