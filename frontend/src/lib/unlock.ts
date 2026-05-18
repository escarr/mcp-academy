import type { LessonSummary } from "../types";

export function levelKey(world: number, level: number): string {
  return `${world}.${level}`;
}

/** Levels grouped by world, sorted by level number. */
export function byWorld(all: LessonSummary[]): Record<number, LessonSummary[]> {
  const out: Record<number, LessonSummary[]> = {};
  for (const l of all) {
    (out[l.world] ||= []).push(l);
  }
  for (const w of Object.keys(out)) {
    out[Number(w)].sort((a, b) => a.level - b.level);
  }
  return out;
}

/** Set of `${world}.${level}` strings that the player can play right now. */
export function computeUnlocked(
  all: LessonSummary[],
  cleared: string[]
): Set<string> {
  const result = new Set<string>();
  const clearedSet = new Set(cleared);
  const byW = byWorld(all);
  const worlds = Object.keys(byW).map(Number).sort((a, b) => a - b);

  let prevWorldComplete = true; // entering W1 implies "previous world done"
  for (const w of worlds) {
    const levels = byW[w];
    if (!prevWorldComplete) {
      prevWorldComplete = false;
      continue; // and every later world stays locked
    }
    // First level of an accessible world is always unlocked
    let prevLevelCleared = true;
    for (const lvl of levels) {
      const k = levelKey(lvl.world, lvl.level);
      if (prevLevelCleared) result.add(k);
      prevLevelCleared = clearedSet.has(k);
    }
    // World is "complete" iff every level in it is cleared
    prevWorldComplete = levels.every((l) => clearedSet.has(levelKey(l.world, l.level)));
  }
  return result;
}

/** Convenience: is this exact (world, level) playable now? */
export function isUnlocked(
  all: LessonSummary[],
  cleared: string[],
  world: number,
  level: number
): boolean {
  return computeUnlocked(all, cleared).has(levelKey(world, level));
}

/** First unlocked level in a given world, or null if the whole world is locked. */
export function firstUnlockedInWorld(
  all: LessonSummary[],
  cleared: string[],
  world: number
): LessonSummary | null {
  const unlocked = computeUnlocked(all, cleared);
  const inWorld = byWorld(all)[world] || [];
  for (const l of inWorld) {
    if (unlocked.has(levelKey(l.world, l.level))) return l;
  }
  return null;
}

/** Is the entire world cleared? */
export function isWorldComplete(
  all: LessonSummary[],
  cleared: string[],
  world: number
): boolean {
  const inWorld = byWorld(all)[world] || [];
  if (inWorld.length === 0) return false;
  return inWorld.every((l) => cleared.includes(levelKey(l.world, l.level)));
}
