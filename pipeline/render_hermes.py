import os
import subprocess
import shutil

def render_hermes():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    src_candidates = [
        os.path.join(base_dir, "assets", "source_videos", "Hermes_captioned.mp4"),
        os.path.join(base_dir, "Hermes_captioned.mp4"),
    ]
    src_video = next((p for p in src_candidates if os.path.exists(p) and os.path.getsize(p) > 1024), src_candidates[0])

    output_dir = os.path.join(base_dir, "pipeline", "output")
    out_video = os.path.join(output_dir, "hermes_final.mp4")
    jibran_video = os.path.join(output_dir, "hermes_captioned.mp4")

    screenshots = [
        os.path.join(output_dir, "screenshot_0.png"),
        os.path.join(output_dir, "screenshot_1.png"),
        os.path.join(output_dir, "screenshot_2.png"),
        os.path.join(output_dir, "screenshot_3.png"),
        os.path.join(output_dir, "screenshot_4.png"),
    ]

    duration = 28.0
    try:
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            src_video
        ]
        res = subprocess.run(probe_cmd, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            duration = float(res.stdout.strip())
    except Exception as e:
        print(f"  [Notice] Could not probe video duration ({e}), defaulting to {duration}s")

    num_shots = min(len(screenshots), 5)
    step = duration / num_shots

    inputs = ["-i", src_video]
    for i in range(num_shots):
        inputs.extend(["-i", screenshots[i]])

    filter_parts = []
    current_stream = "[0:v]"
    INNER_WIDTH = 960
    MAX_HEIGHT = 500

    for i in range(num_shots):
        start_time = round(i * step, 1)
        end_time = round((i + 1) * step if i < num_shots - 1 else duration, 1)
        inp_idx = i + 1

        scale_filter = (
            f"[{inp_idx}:v]scale=w={INNER_WIDTH}:h={MAX_HEIGHT}:force_original_aspect_ratio=decrease,"
            f"format=yuva420p,setsar=1[img{i}]"
        )
        filter_parts.append(scale_filter)

        overlay_filter = (
            f"{current_stream}[img{i}]overlay=(main_w-overlay_w)/2:main_h-overlay_h-110"
            f":enable='between(t,{start_time},{end_time})'[v{i}]"
        )
        filter_parts.append(overlay_filter)
        current_stream = f"[v{i}]"

    filter_complex = ";".join(filter_parts)

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", current_stream,
        "-map", "0:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        out_video,
    ]

    print("Running FFmpeg for Nous Research Hermes video...")
    subprocess.run(ffmpeg_cmd, check=True)
    shutil.copyfile(out_video, jibran_video)
    print("Nous Research Hermes video rendered successfully!")

if __name__ == "__main__":
    render_hermes()
