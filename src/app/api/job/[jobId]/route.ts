import { NextResponse } from "next/server";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ jobId: string }> }
) {
  const { jobId } = await params;

  if (!/^[a-f0-9-]+$/.test(jobId)) {
    return NextResponse.json({ error: "Invalid job ID" }, { status: 400 });
  }

  const resultPath = join(process.cwd(), "pipeline", "output", jobId, "result.json");
  if (!existsSync(resultPath)) {
    return NextResponse.json({ error: "Result not found" }, { status: 404 });
  }

  try {
    const data = JSON.parse(readFileSync(resultPath, "utf-8"));
    return NextResponse.json(data);
  } catch (e) {
    return NextResponse.json({ error: "Failed to read result data" }, { status: 500 });
  }
}
