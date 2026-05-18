export type GhostName = "blinky" | "pinky" | "inky" | "clyde" | "pacman";

export interface WorldArcEntry {
  world: number;
  title: string;
  concept: string;
  ghost: GhostName;
}

export interface LessonSummary {
  world: number;
  level: number;
  title: string;
  ghost: GhostName;
  concept: string;
  pellet_reward: number;
}

export interface WorldArcResponse {
  worlds: WorldArcEntry[];
  implemented_worlds: number[];
  implemented_levels: [number, number][];
}

export interface GraderStepInfo {
  kind: string;
  description: string;
}

export interface LessonDetail {
  world: number;
  level: number;
  title: string;
  ghost: GhostName;
  concept: string;
  story: string;
  concept_brief: string;
  instructions: string;
  starter_code: string;
  solution_hint: string;
  post_pass_debrief: string;
  pellet_reward: number;
  grader_steps: GraderStepInfo[];
}

export type TraceDirection = "out" | "in" | "log";

export interface TraceEntry {
  direction: TraceDirection;
  message: any;
}

export interface RunStepResult {
  kind: string;
  description: string;
  passed: boolean;
  message: string;
}

export interface RunResponse {
  passed: boolean;
  trace: TraceEntry[];
  stderr: string;
  steps: RunStepResult[];
  errors: string[];
  pellet_reward: number;
}
