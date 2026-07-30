import { NextResponse } from "next/server";
import { spawn } from "child_process";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

function parseProgressLine(line: string): { step: string; progress: number; message: string } | null {
  // Match [N/7] pattern for pipeline steps
  const match = line.match(/\[(\d+)\/7\]\s*(.*)/);
  if (!match) return null;

  const stepNum = parseInt(match[1]);
  const message = match[2].trim();

  // Phase 2 starts at step 5, so progress offset from 50%
  const progress = Math.round(50 + ((stepNum - 4) / 3) * 50);

  const stepNames: Record<number, string> = {
    5: "transcribing",
    6: "composing",
    7: "posting",
  };

  return {
    step: stepNames[stepNum] || "processing",
    progress: Math.min(progress, 95),
    message: `[${match[1]}/7] ${message}`,
  };
}

export async function POST(req: Request) {
  let jobId = "";
  try {
    const body = await req.json();
    jobId = body.jobId;
  } catch (e) {
    return NextResponse.json({ error: "Invalid request body" }, { status: 400 });
  }

  if (!jobId || typeof jobId !== "string" || !/^[a-f0-9-]+$/.test(jobId)) {
    return NextResponse.json({ error: "Valid jobId required" }, { status: 400 });
  }

  const pipelineDir = join(process.cwd(), "pipeline");
  const outputDir = join(pipelineDir, "output", jobId);

  // Verify result.json exists (Phase 1 completed)
  const resultFile = join(outputDir, "result.json");
  if (!existsSync(resultFile)) {
    return NextResponse.json({ error: "Job not found. Run Phase 1 first." }, { status: 404 });
  }

  // Verify avatar video exists
  const avatarPath = join(outputDir, "avatar_ben.mp4");
  if (!existsSync(avatarPath)) {
    return NextResponse.json(
      { error: "Avatar video not found. Please save avatar_ben.mp4 to the job output folder." },
      { status: 400 }
    );
  }

  const pythonCmd = process.platform === "win32" ? "python" : "python3";
  const args = ["main.py", "--resume", jobId];

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(
        encoder.encode(
          `data: ${JSON.stringify({ step: "transcribing", progress: 55, message: "[5/7] Starting transcription..." })}\n\n`
        )
      );

      const child = spawn(pythonCmd, ["-u", ...args], {
        cwd: pipelineDir,
        env: { ...process.env },
      });

      child.stdout.on("data", (data: Buffer) => {
        const str = data.toString();
        console.log(`[pipeline-resume stdout] ${str}`);
        const lines = str.split("\n");
        for (const line of lines) {
          const event = parseProgressLine(line);
          if (event) {
            controller.enqueue(encoder.encode(`data: ${JSON.stringify(event)}\n\n`));
          }
        }
      });

      child.stderr.on("data", (data: Buffer) => {
        console.error(`[pipeline-resume stderr] ${data.toString()}`);
      });

      child.on("close", (code) => {
        if (code === 0) {
          let resultData = null;
          try {
            if (existsSync(resultFile)) {
              resultData = JSON.parse(readFileSync(resultFile, "utf-8"));
            }
          } catch (e) {
            console.error("Failed to read result.json:", e);
          }

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
        } else {
          controller.enqueue(
            encoder.encode(
              `data: ${JSON.stringify({ step: "error", progress: 0, message: `Pipeline Phase 2 exited with code ${code}` })}\n\n`
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
