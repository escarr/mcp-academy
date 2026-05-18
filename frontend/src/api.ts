import type { LessonDetail, LessonSummary, RunResponse, WorldArcResponse } from "./types";

const BASE = "/api";

export async function fetchWorldArc(): Promise<WorldArcResponse> {
  const r = await fetch(`${BASE}/world-arc`);
  if (!r.ok) throw new Error(`world-arc: ${r.status}`);
  return r.json();
}

export async function fetchLessons(): Promise<LessonSummary[]> {
  const r = await fetch(`${BASE}/lessons`);
  if (!r.ok) throw new Error(`lessons: ${r.status}`);
  return r.json();
}

export async function fetchLesson(world: number, level: number): Promise<LessonDetail> {
  const r = await fetch(`${BASE}/lessons/${world}/${level}`);
  if (!r.ok) throw new Error(`lesson ${world}/${level}: ${r.status}`);
  return r.json();
}

export async function runCode(
  world: number,
  level: number,
  code: string
): Promise<RunResponse> {
  const r = await fetch(`${BASE}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ world, level, code }),
  });
  if (!r.ok) throw new Error(`run: ${r.status}`);
  return r.json();
}

export interface SaveResponse {
  saved: boolean;
  path: string;
  abs_path: string;
}

export async function saveToRepo(
  world: number,
  level: number,
  code: string
): Promise<SaveResponse> {
  const r = await fetch(`${BASE}/save-to-repo`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ world, level, code }),
  });
  if (!r.ok) throw new Error(`save: ${r.status}`);
  return r.json();
}
