import { Pellet } from "./Pacman";

interface Props {
  pellets: number;
  cleared: number;
  onReset?: () => void;
  onIntro?: () => void;
}

export function HUD({ pellets, cleared, onReset, onIntro }: Props) {
  return (
    <header className="flex items-center justify-between px-6 py-3 border-b-2 border-maze font-arcade">
      <div className="flex items-center gap-4">
        <span className="neon-yellow text-sm tracking-widest">MCP&nbsp;ACADEMY</span>
        <span className="text-[10px] opacity-50">v0.1 — INSERT COIN</span>
      </div>
      <div className="flex items-center gap-6 text-xs">
        <div className="flex items-center gap-2 neon-yellow">
          <Pellet size={10} />
          <span>{pellets.toString().padStart(5, "0")}</span>
          <span className="opacity-60 text-[10px]">PELLETS</span>
        </div>
        <div className="neon-cyan text-xs">
          {cleared.toString().padStart(2, "0")} <span className="opacity-60 text-[10px]">CLEARED</span>
        </div>
        {onIntro && (
          <button
            onClick={onIntro}
            className="text-[10px] opacity-50 hover:opacity-100 hover:neon-cyan"
            title="Replay intro"
          >
            ▸ INTRO
          </button>
        )}
        {onReset && (
          <button
            onClick={onReset}
            className="text-[10px] opacity-50 hover:opacity-100 hover:neon-pink"
            title="Reset save game"
          >
            RESET
          </button>
        )}
      </div>
    </header>
  );
}
