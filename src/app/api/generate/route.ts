import { NextResponse } from "next/server";
import { spawn } from "child_process";
import { join } from "path";

function parseProgressLine(line: string): { step: string; progress: number; message: string } | null {
  // Match [N/7] pattern for pipeline steps
  const match = line.match(/\[(\d+)\/7\]\s*(.*)/);
  if (!match) return null;

  const stepNum = parseInt(match[1]);
  const message = match[2].trim();
  const progress = Math.round((stepNum / 7) * 100);

  const stepNames: Record<number, string> = {
    1: "scraping",
    2: "screenshots",
    3: "scripting",
    4: "rendering",
    5: "transcribing",
    6: "composing",
    7: "posting",
  };

  return {
    step: stepNames[stepNum] || "processing",
    progress,
    message: `[${match[1]}/7] ${message}`,
  };
}

function detectPhaseCompletion(line: string): "phase1" | "done" | null {
  if (line.includes("PHASE 1 COMPLETE") || line.includes("AWAITING AVATAR VIDEO")) {
    return "phase1";
  }
  if (line.includes("DONE! Final video:")) {
    return "done";
  }
  return null;
}

export async function POST(req: Request) {
  let url = "";
  let avatarId = "";
  try {
    const body = await req.json();
    url = body.url;
    avatarId = body.avatarId;
  } catch (e) {
    return NextResponse.json({ error: "Invalid request body" }, { status: 400 });
  }

  if (!url || typeof url !== "string") {
    return NextResponse.json({ error: "URL required" }, { status: 400 });
  }

  const pipelineDir = join(process.cwd(), "pipeline");
  const jobId = crypto.randomUUID();

  const args = ["main.py", url, "--job-id", jobId];
  if (avatarId) {
    args.push("--avatar-id", avatarId);
  }

  const pythonCmd = process.platform === "win32" ? "python" : "python3";

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      // Send initial step notification immediately
      controller.enqueue(
        encoder.encode(
          `data: ${JSON.stringify({ step: "scraping", progress: 10, message: "[1/7] Initializing scrape..." })}\n\n`
        )
      );

      const child = spawn(pythonCmd, ["-u", ...args], {
        cwd: pipelineDir,
        env: { ...process.env },
      });

      let fullOutput = "";

      child.stdout.on("data", (data: Buffer) => {
        const str = data.toString();
        fullOutput += str;
        console.log(`[pipeline stdout] ${str}`);
        const lines = str.split("\n");
        for (const line of lines) {
          const event = parseProgressLine(line);
          if (event) {
            controller.enqueue(encoder.encode(`data: ${JSON.stringify(event)}\n\n`));
          }
        }
      });

      child.stderr.on("data", (data: Buffer) => {
        console.error(`[pipeline stderr] ${data.toString()}`);
      });

      child.on("close", (code) => {
        if (code === 0) {
          let resultData = null;
          const resultFile = join(pipelineDir, "output", jobId, "result.json");
          try {
            const fs = require("fs");
            if (fs.existsSync(resultFile)) {
              resultData = JSON.parse(fs.readFileSync(resultFile, "utf-8"));
            }
          } catch (e) {
            console.error("Failed to read result.json:", e);
          }

          const status = resultData?.status || "complete";

          if (status === "awaiting_avatar") {
            // Phase 1 complete — pipeline paused for manual avatar creation
            controller.enqueue(
              encoder.encode(
                `data: ${JSON.stringify({
                  step: "awaiting_avatar",
                  progress: 50,
                  message: "Phase 1 complete — awaiting avatar video",
                  jobId,
                  result: resultData,
                })}\n\n`
              )
            );
          } else {
            // Full pipeline complete (avatar was available)
            controller.enqueue(
              encoder.encode(
                `data: ${JSON.stringify({
                  step: "done",
                  progress: 100,
                  videoUrl: `/api/video/${jobId}`,
                  jobId,
                  result: resultData,
                })}\n\n`
              )
            );
          }
        } else {
          controller.enqueue(
            encoder.encode(
              `data: ${JSON.stringify({ step: "error", progress: 0, message: `Pipeline exited with code ${code}` })}\n\n`
            )
          );
        }
        controller.close();
      });

      child.on("error", (err) => {
        controller.enqueue(
          encoder.encode(
            `data: ${JSON.stringify({ step: "error", progress: 0, message: err.message })}\n\n`
          )
        );
        controller.close();
      });
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
