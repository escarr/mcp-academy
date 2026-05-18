import { ArcadeMarkdown } from "./ArcadeMarkdown";
import { Pacman, Pellet } from "./Pacman";

interface Props {
  pellets: number;
  debrief?: string;
  savedPath?: string;
  onContinue: () => void;
  onReplay: () => void;
}

export function LevelCompleteModal({ pellets, debrief, savedPath, onContinue, onReplay }: Props) {
  return (
    <div className="fixed inset-0 z-40 bg-black/80 backdrop-blur-sm flex items-center justify-center p-6">
      <div className="arcade-card p-8 max-w-2xl w-full max-h-[90vh] overflow-auto">
        <div className="text-center">
          <div className="flex justify-center mb-5">
            <Pacman size={72} />
          </div>
          <h2 className="neon-yellow text-xl mb-3 font-arcade">LEVEL&nbsp;CLEAR!</h2>
          <div className="flex items-center justify-center gap-2 mb-6 neon-cyan text-sm font-arcade">
            <Pellet size={10} />
            <span>+{pellets}&nbsp;PELLETS</span>
          </div>
        </div>

        {debrief && (
          <div className="mb-6 border-2 border-maze/60 bg-black/30 p-4">
            <div className="neon-pink font-arcade text-[10px] mb-2 tracking-widest">
              ▌WHAT YOU JUST LEARNED
            </div>
            <ArcadeMarkdown source={debrief} />
          </div>
        )}

        {savedPath && (
          <div className="mb-6 border-2 border-inky/40 bg-black/30 p-3 text-[14px]">
            <div className="neon-cyan font-arcade text-[10px] mb-1 tracking-widest">
              ▌SAVED TO REPO
            </div>
            <code className="font-mono text-inky text-[13px] break-all">
              {savedPath}
            </code>
            <div className="opacity-60 mt-1 text-[12px]">
              Your working server has been written to disk — install it in Claude when you're ready.
            </div>
          </div>
        )}

        <div className="flex gap-3 justify-center">
          <button onClick={onReplay} className="arcade-btn text-[10px] neon-cyan">
            ↻ REPLAY
          </button>
          <button onClick={onContinue} className="arcade-btn text-[10px] neon-yellow">
            BACK TO MAP →
          </button>
        </div>
      </div>
    </div>
  );
}
