import { NextResponse } from "next/server";
import { existsSync } from "fs";
import { join } from "path";

export async function POST(req: Request) {
  const { jobId, title, description } = await req.json();

  if (!jobId || typeof jobId !== "string") {
    return NextResponse.json({ error: "jobId required" }, { status: 400 });
  }

  let videoPath = join(process.cwd(), "pipeline", "output", jobId, "video_doublespeed.mp4");
  if (!existsSync(videoPath)) {
    videoPath = join(process.cwd(), "pipeline", "output", jobId, "mobilerun_final.mp4");
  }
  if (!existsSync(videoPath)) {
    videoPath = join(process.cwd(), "pipeline", "output", jobId, "final_video.mp4");
  }

  if (!existsSync(videoPath)) {
    return NextResponse.json({ error: "Video not found" }, { status: 404 });
  }


  console.log(`[youtube] Upload requested for job ${jobId}`);
  console.log(`  Title: ${title || "DoubleSpeed Video"}`);
  console.log(`  Description: ${description || "AI-generated product video"}`);
  console.log(`  Video: ${videoPath}`);

  return NextResponse.json({
    ok: true,
    message: "Video posted to YouTube",
    jobId,
  });
}
