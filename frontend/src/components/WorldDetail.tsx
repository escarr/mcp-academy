import { useEffect, useState } from "react";
import { fetchLessons } from "../api";
import { sfx } from "../audio";
import {
  byWorld,
  computeUnlocked,
  isWorldComplete,
  levelKey,
} from "../lib/unlock";
import type { LessonSummary } from "../types";
import { Ghost } from "./Ghost";
import { Pacman, Pellet } from "./Pacman";

interface Props {
  world: number;
  clearedLevels: string[];
  onBack: () => void;
  onPickLevel: (world: number, level: number) => void;
}

const WORLD_TITLES: Record<number, string> = {
  1: "Pellet Basics",
  2: "The Tool Maze",
  3: "Resource Tunnels",
  4: "Prompt Power-Pellets",
  5: "Bidirectional MCP",
  6: "Escape to Claude",
  7: "Going Public",
  8: "Distribute + Skills",
};

const GHOST_FOR_WORLD: Record<number, "blinky" | "pinky" | "inky" | "clyde" | "pacman"> = {
  1: "pacman",
  2: "blinky",
  3: "pinky",
  4: "inky",
  5: "clyde",
  6: "pacman",
  7: "blinky",
  8: "pacman",
};

export function WorldDetail({ world, clearedLevels, onBack, onPickLevel }: Props) {
  const [all, setAll] = useState<LessonSummary[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    fetchLessons().then(setAll).catch((e) => setErr(String(e)));
  }, []);

  if (err) {
    return (
      <div className="p-8 neon-red text-sm">
        FAILED TO LOAD LESSONS — <span className="opacity-60 text-xs">{err}</span>
      </div>
    );
  }
  if (all.length === 0) {
    return <div className="p-8 neon-yellow blink text-sm">LOADING…</div>;
  }

  const levels = (byWorld(all)[world] || []).slice();
  const unlocked = computeUnlocked(all, clearedLevels);
  const ghost = GHOST_FOR_WORLD[world] ?? "pacman";
  const title = WORLD_TITLES[world] ?? `World ${world}`;
  const complete = isWorldComplete(all, clearedLevels, world);

  return (
    <div className="px-6 py-8 max-w-4xl mx-auto">
      <button
        onClick={onBack}
        className="arcade-btn text-[10px] neon-yellow mb-6"
      >
        ← MAP
      </button>

      <div className="flex items-center gap-5 mb-8">
        {ghost === "pacman" ? <Pacman size={72} /> : <Ghost name={ghost} size={72} />}
        <div className="font-arcade">
          <div className="text-[10px] opacity-60">WORLD {world}</div>
          <div className="neon-yellow text-xl">{title}</div>
          {complete && (
            <div className="neon-cyan text-[10px] mt-1">★ WORLD COMPLETE</div>
          )}
        </div>
      </div>

      <div className="space-y-3">
        {levels.map((l, idx) => {
          const key = levelKey(l.world, l.level);
          const cleared = clearedLevels.includes(key);
          const playable = unlocked.has(key);
          return (
            <button
              key={key}
              onClick={() => {
                if (!playable) {
                  sfx.fail();
                  return;
                }
                sfx.click();
                onPickLevel(l.world, l.level);
              }}
              disabled={!playable}
              className={`arcade-card w-full text-left p-4 flex items-center gap-4 transition-all ${
                playable ? "hover:-translate-y-0.5 hover:shadow-neon" : "opacity-40 cursor-not-allowed"
              }`}
            >
              <div className="font-arcade neon-yellow text-sm w-16 shrink-0">
                {l.world}.{l.level}
              </div>
              <div className="flex-1 min-w-0">
                <div className="neon-yellow font-arcade text-xs mb-1 truncate">
                  {l.title}
                </div>
                <div className="text-[11px] opacity-60 uppercase font-arcade">
                  {l.concept}
                </div>
              </div>
              <div className="shrink-0 font-arcade text-[10px] text-right">
                {!playable && <span className="neon-pink">LOCKED</span>}
                {playable && cleared && <span className="neon-cyan">★ CLEAR</span>}
                {playable && !cleared && (
                  <span className="flex items-center gap-2 neon-yellow">
                    <Pellet size={9} />
                    +{l.pellet_reward}
                  </span>
                )}
              </div>
              {!playable && <span className="ml-1">🔒</span>}
              <span className="ml-2 opacity-30 text-[10px]">{idx + 1}/{levels.length}</span>
            </button>
          );
        })}
      </div>

      <div className="mt-10 text-center text-[10px] opacity-50 font-arcade">
        CLEAR EACH LEVEL TO UNLOCK THE NEXT
      </div>
    </div>
  );
}
