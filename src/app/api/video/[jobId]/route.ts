import { NextResponse } from "next/server";
import { createReadStream, existsSync, statSync } from "fs";
import { join } from "path";
import { Readable } from "stream";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ jobId: string }> }
) {
  const { jobId } = await params;

  // Sanitize jobId to prevent directory traversal
  if (!/^[a-f0-9-]+$/.test(jobId)) {
    return NextResponse.json({ error: "Invalid job ID" }, { status: 400 });
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

  const stat = statSync(videoPath);
  const fileStream = createReadStream(videoPath);
  const webStream = Readable.toWeb(fileStream) as ReadableStream;

  return new Response(webStream, {
    headers: {
      "Content-Type": "video/mp4",
      "Content-Length": stat.size.toString(),
      "Cache-Control": "public, max-age=3600",
    },
  });
}
