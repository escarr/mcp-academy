import { useEffect, useState } from "react";
import { HUD } from "./components/HUD";
import { IntroScreen } from "./components/IntroScreen";
import { Level } from "./components/Level";
import { WorldDetail } from "./components/WorldDetail";
import { WorldMap } from "./components/WorldMap";
import { clearAllLevelState } from "./levelStore";
import { loadSave, markCleared, saveSave } from "./store";

type Screen =
  | { kind: "intro" }
  | { kind: "map" }
  | { kind: "world"; world: number }
  | { kind: "level"; world: number; level: number };

export default function App() {
  const [save, setSave] = useState(loadSave());
  const [screen, setScreen] = useState<Screen>(
    save.introSeen ? { kind: "map" } : { kind: "intro" }
  );

  useEffect(() => {
    saveSave(save);
  }, [save]);

  function handleClear(pellets: number) {
    if (screen.kind !== "level") return;
    setSave((s) => markCleared(s, screen.world, screen.level, pellets));
  }

  return (
    <div className="h-screen flex flex-col crt-overlay overflow-hidden">
      <HUD
        pellets={save.pellets}
        cleared={save.clearedLevels.length}
        onReset={() => {
          if (confirm("Wipe save game?")) {
            clearAllLevelState();
            setSave({ pellets: 0, clearedLevels: [], introSeen: false });
            setScreen({ kind: "intro" });
          }
        }}
        onIntro={() => setScreen({ kind: "intro" })}
      />
      <main className="flex-1 min-h-0 flex flex-col overflow-hidden">
        {screen.kind === "intro" && (
          <IntroScreen
            onStart={() => {
              setSave((s) => ({ ...s, introSeen: true }));
              setScreen({ kind: "map" });
            }}
          />
        )}
        {screen.kind === "map" && (
          <WorldMap
            clearedLevels={save.clearedLevels}
            onPickWorld={(w) => setScreen({ kind: "world", world: w })}
          />
        )}
        {screen.kind === "world" && (
          <WorldDetail
            world={screen.world}
            clearedLevels={save.clearedLevels}
            onBack={() => setScreen({ kind: "map" })}
            onPickLevel={(w, l) => setScreen({ kind: "level", world: w, level: l })}
          />
        )}
        {screen.kind === "level" && (
          <Level
            world={screen.world}
            level={screen.level}
            onExit={() =>
              setScreen({ kind: "world", world: screen.world })
            }
            onClear={handleClear}
          />
        )}
      </main>
      <footer className="text-center text-[9px] opacity-30 py-2 tracking-widest font-arcade">
        © 2026 MCP&nbsp;ACADEMY — A LEARN-BY-DOING ARCADE
      </footer>
    </div>
  );
}
