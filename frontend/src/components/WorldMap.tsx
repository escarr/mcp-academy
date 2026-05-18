import { useEffect, useState } from "react";
import { fetchLessons, fetchWorldArc } from "../api";
import { sfx } from "../audio";
import { computeUnlocked, isWorldComplete, levelKey } from "../lib/unlock";
import type { GhostName, LessonSummary, WorldArcResponse } from "../types";
import { Ghost } from "./Ghost";
import { Pacman, Pellet } from "./Pacman";

interface Props {
  clearedLevels: string[];
  onPickWorld: (world: number) => void;
}

export function WorldMap({ clearedLevels, onPickWorld }: Props) {
  const [arc, setArc] = useState<WorldArcResponse | null>(null);
  const [all, setAll] = useState<LessonSummary[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([fetchWorldArc(), fetchLessons()])
      .then(([a, ls]) => {
        setArc(a);
        setAll(ls);
      })
      .catch((e) => setErr(String(e)));
  }, []);

  if (err) {
    return (
      <div className="p-8 neon-red text-sm">
        FAILED TO LOAD WORLD MAP — is the backend running?
        <br />
        <span className="opacity-60 text-xs">{err}</span>
      </div>
    );
  }
  if (!arc || all.length === 0) {
    return <div className="p-8 neon-yellow blink text-sm">LOADING…</div>;
  }

  const unlocked = computeUnlocked(all, clearedLevels);
  // A world is "accessible" iff any of its levels is unlocked.
  const isWorldAccessible = (w: number) =>
    all.some((l) => l.world === w && unlocked.has(levelKey(l.world, l.level)));

  return (
    <div className="px-6 py-8 max-w-6xl mx-auto overflow-auto h-full">
      <div className="text-center mb-10">
        <h1 className="neon-yellow text-2xl mb-3 font-arcade">SELECT A WORLD</h1>
        <p className="text-[10px] opacity-70 tracking-wider font-arcade">
          EAT&nbsp;THE&nbsp;PELLETS - LEARN&nbsp;THE&nbsp;PROTOCOL
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {arc.worlds.map((w) => {
          const accessible = isWorldAccessible(w.world);
          const complete = isWorldComplete(all, clearedLevels, w.world);
          const partialCleared = clearedLevels.some((k) => k.startsWith(`${w.world}.`));
          return (
            <WorldCard
              key={w.world}
              world={w.world}
              title={w.title}
              concept={w.concept}
              ghost={w.ghost}
              locked={!accessible}
              complete={complete}
              inProgress={partialCleared && !complete}
              onPick={() => {
                if (!accessible) {
                  sfx.fail();
                  return;
                }
                sfx.powerPellet();
                onPickWorld(w.world);
              }}
            />
          );
        })}
      </div>

      <div className="mt-12 text-center text-[10px] opacity-50 font-arcade">
        MORE&nbsp;WORLDS&nbsp;UNLOCK&nbsp;AS&nbsp;YOU&nbsp;CLEAR&nbsp;LEVELS
      </div>
    </div>
  );
}

function WorldCard({
  world,
  title,
  concept,
  ghost,
  locked,
  complete,
  inProgress,
  onPick,
}: {
  world: number;
  title: string;
  concept: string;
  ghost: GhostName;
  locked: boolean;
  complete: boolean;
  inProgress: boolean;
  onPick: () => void;
}) {
  return (
    <button
      onClick={onPick}
      disabled={locked}
      className={`arcade-card p-5 text-left transition-all ${
        locked ? "opacity-40 cursor-not-allowed" : "hover:-translate-y-1 hover:shadow-neon"
      }`}
    >
      <div className="flex items-center gap-4 font-arcade">
        <div className="shrink-0">
          {ghost === "pacman" ? <Pacman size={56} /> : <Ghost name={ghost} size={56} scared={locked} />}
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-[10px] opacity-60 mb-1">WORLD {world}</div>
          <div className="neon-yellow text-sm mb-2">{title}</div>
          <div className="text-[10px] opacity-70 uppercase">{concept}</div>
        </div>
        <div className="shrink-0 flex flex-col items-center gap-1">
          {locked && <span className="neon-pink text-[10px]">LOCKED</span>}
          {!locked && complete && <span className="neon-cyan text-[10px]">★ CLEAR</span>}
          {!locked && !complete && inProgress && <span className="neon-orange text-[10px]">⋯ ACTIVE</span>}
          {!locked && !complete && !inProgress && <Pellet size={10} />}
        </div>
      </div>
    </button>
  );
}
