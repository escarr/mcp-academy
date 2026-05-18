// Per-level scratchpad persistence: code + last run result (JSON-RPC trace,
// stderr, step results, errors). Keyed by world.level in localStorage so
// navigating away and back restores the user's in-progress state.

import type { RunResponse } from "./types";

const KEY_PREFIX = "mcp-teacher:level:";

export interface PersistedLevel {
  code: string;
  result: RunResponse | null;
}

function levelKey(w: number, l: number): string {
  return `${KEY_PREFIX}${w}.${l}`;
}

export function loadLevelState(w: number, l: number): PersistedLevel | null {
  try {
    const raw = localStorage.getItem(levelKey(w, l));
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (typeof parsed.code !== "string") return null;
    return {
      code: parsed.code,
      result: parsed.result ?? null,
    };
  } catch {
    return null;
  }
}

export function saveLevelState(w: number, l: number, state: PersistedLevel): void {
  try {
    localStorage.setItem(levelKey(w, l), JSON.stringify(state));
  } catch {
    // quota exceeded or storage unavailable — drop silently
  }
}

export function clearLevelState(w: number, l: number): void {
  try {
    localStorage.removeItem(levelKey(w, l));
  } catch {
    // ignore
  }
}

export function clearAllLevelState(): void {
  try {
    const toRemove: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (k && k.startsWith(KEY_PREFIX)) toRemove.push(k);
    }
    toRemove.forEach((k) => localStorage.removeItem(k));
  } catch {
    // ignore
  }
}
