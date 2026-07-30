import { NextResponse } from "next/server";
import { createReadStream, existsSync, statSync } from "fs";
import { join } from "path";
import { Readable } from "stream";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ product: string }> }
) {
  const { product } = await params;

  let candidates: string[] = [];
  if (product === "doublespeed") {
    candidates = ["doublespeed.mp4", "doublespeed_cole_final.mp4", "video_doublespeed.mp4", "doublespeed_cole.mp4"];
  } else if (product === "mobilerun") {
    candidates = ["mobilerun.mp4", "mobilerun_final_captioned.mp4", "mobilerun_captioned.mp4", "mobilerun_final.mp4"];
  } else if (product === "hermes") {
    candidates = ["hermes.mp4", "hermes_final.mp4", "hermes_captioned.mp4", "Hermes_captioned.mp4"];
  } else {
    return NextResponse.json({ error: "Product not found" }, { status: 404 });
  }

  let videoPath = "";

  // 1. Check public/videos/
  for (const filename of candidates) {
    const pubPath = join(process.cwd(), "public", "videos", filename);
    if (existsSync(pubPath) && statSync(pubPath).size > 1024) {
      videoPath = pubPath;
      break;
    }
  }

  // 2. Fallback to pipeline/output/
  if (!videoPath) {
    for (const filename of candidates) {
      const outPath = join(process.cwd(), "pipeline", "output", filename);
      if (existsSync(outPath) && statSync(outPath).size > 1024) {
        videoPath = outPath;
        break;
      }
    }
  }

  // 3. Fallback to assets/source_videos/
  if (!videoPath) {
    for (const filename of candidates) {
      const assetPath = join(process.cwd(), "assets", "source_videos", filename);
      if (existsSync(assetPath) && statSync(assetPath).size > 1024) {
        videoPath = assetPath;
        break;
      }
    }
  }

  if (!videoPath) {
    return NextResponse.json({ error: "Video file missing" }, { status: 404 });
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
