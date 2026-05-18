// localStorage-backed game state.

const KEY = "mcp-teacher:save";

export interface SaveState {
  pellets: number;
  clearedLevels: string[]; // "world.level"
  introSeen: boolean;
}

const empty: SaveState = { pellets: 0, clearedLevels: [], introSeen: false };

export function loadSave(): SaveState {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return { ...empty };
    const parsed = JSON.parse(raw);
    return {
      pellets: typeof parsed.pellets === "number" ? parsed.pellets : 0,
      clearedLevels: Array.isArray(parsed.clearedLevels) ? parsed.clearedLevels : [],
      introSeen: typeof parsed.introSeen === "boolean" ? parsed.introSeen : false,
    };
  } catch {
    return { ...empty };
  }
}

export function saveSave(s: SaveState): void {
  localStorage.setItem(KEY, JSON.stringify(s));
}

export function key(w: number, l: number): string {
  return `${w}.${l}`;
}

export function markCleared(state: SaveState, w: number, l: number, pellets: number): SaveState {
  const k = key(w, l);
  if (state.clearedLevels.includes(k)) return state;
  return {
    ...state,
    pellets: state.pellets + pellets,
    clearedLevels: [...state.clearedLevels, k],
  };
}
