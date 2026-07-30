export interface Avatar {
  id: string;
  name: string;
  thumbnail: string;
}

export type GenerationStep = "input" | "avatar" | "processing" | "awaiting_avatar" | "preview";

export interface GenerationStatus {
  step: string;
  progress: number;
  message: string;
}

export interface GenerationResult {
  jobId: string;
  videoUrl: string;
}
