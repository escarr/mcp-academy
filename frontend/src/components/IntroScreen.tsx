import { useEffect, useState } from "react";
import { sfx } from "../audio";
import { Ghost } from "./Ghost";
import { Pacman, Pellet } from "./Pacman";

interface Props {
  onStart: () => void;
}

const WORLDS = [
  { n: 1, title: "Pellet Basics",        what: "Tools, state, computed values, persistence" },
  { n: 2, title: "The Tool Maze",        what: "Descriptions, annotations, structured output, errors" },
  { n: 3, title: "Resource Tunnels",     what: "Static + templated resources Claude can browse" },
  { n: 4, title: "Prompt Power-Pellets", what: "Reusable + parameterized slash-command workflows" },
  { n: 5, title: "Bidirectional MCP",    what: "Sampling, elicitation, progress notifications" },
  { n: 6, title: "Escape to Claude",     what: "Wire into Claude Desktop, Claude Code, Inspector" },
  { n: 7, title: "Going Public",         what: "Streamable HTTP, API keys, OAuth 2.1 + PKCE" },
  { n: 8, title: "Distribute + Skills",  what: "DXT one-click packaging, SKILL.md companion" },
];

export function IntroScreen({ onStart }: Props) {
  const [pellets, setPellets] = useState<{ x: number; y: number; id: number }[]>([]);

  useEffect(() => {
    // sprinkle decorative pellets across the page
    setPellets(
      Array.from({ length: 18 }, (_, i) => ({
        id: i,
        x: Math.random() * 90 + 5,
        y: Math.random() * 90 + 5,
      }))
    );
  }, []);

  return (
    <div className="min-h-full overflow-auto relative">
      {/* Decorative pellet field */}
      <div className="pointer-events-none absolute inset-0 z-0">
        {pellets.map((p) => (
          <span
            key={p.id}
            className="absolute"
            style={{ left: `${p.x}%`, top: `${p.y}%` }}
          >
            <Pellet size={6} />
          </span>
        ))}
      </div>

      <div className="relative z-10 max-w-4xl mx-auto px-6 py-10 space-y-12">
        {/* MARQUEE */}
        <header className="text-center">
          <div className="flex items-center justify-center gap-3 mb-5">
            <Pacman size={56} facing="right" />
            <Ghost name="blinky" size={44} />
            <Ghost name="pinky" size={44} />
            <Ghost name="inky" size={44} />
            <Ghost name="clyde" size={44} />
          </div>
          <h1 className="font-arcade neon-yellow text-2xl mb-3">
            MCP&nbsp;ACADEMY
          </h1>
          <p className="font-arcade neon-pink text-xs tracking-widest">
            PRESS&nbsp;START&nbsp;TO&nbsp;BEGIN
          </p>
        </header>

        {/* MISSION */}
        <section className="arcade-card p-6">
          <h2 className="neon-cyan font-arcade text-xs mb-3">▌YOUR&nbsp;MISSION</h2>
          <p className="text-[17px] leading-relaxed opacity-90">
            Build a real MCP server — <strong className="text-pac">Pellet Tracker</strong>,
            a personal habit-and-streak tool — one level at a time. By the end you'll
            have a working server installed in Claude Desktop, a complete understanding
            of every MCP primitive, and a Claude-native template repo you can reuse for
            future projects.
          </p>
          <p className="text-[17px] leading-relaxed opacity-90 mt-3">
            <em className="text-inky not-italic">Pellets</em> are habits you log.{" "}
            <em className="text-inky not-italic">Power-pellets</em> are streak rewards.
            The four ghosts are your concept mascots. The arcade keeps score.
          </p>
        </section>

        {/* THE END GAME — mock Claude chat */}
        <section className="arcade-card p-6">
          <h2 className="neon-cyan font-arcade text-xs mb-4">▌THE&nbsp;END&nbsp;GAME</h2>
          <p className="text-[16px] opacity-80 mb-4">
            Here's what your finished Pellet Tracker looks like talking to real Claude:
          </p>
          <div className="bg-black/60 border-2 border-maze rounded p-4 space-y-3 text-[15px]">
            <ChatLine speaker="you">Log a pellet for "meditation"</ChatLine>
            <ChatLine speaker="claude">I'll log that for you.</ChatLine>
            <ToolCall name="log_pellet" args='habit="meditation"' result='"Logged: meditation"' />
            <ChatLine speaker="claude">
              Logged. That's your 3rd meditation this week — a real streak.
            </ChatLine>
            <ChatLine speaker="you">What's my current count for running?</ChatLine>
            <ToolCall
              name="count_pellets"
              args='habit="running"'
              result='{"habit": "running", "total": 5, "longest_run": 5}'
            />
            <ChatLine speaker="claude">
              5 running pellets — and your longest run is 5 days. Keep it going.
            </ChatLine>
          </div>
          <p className="text-[14px] opacity-60 mt-4 italic">
            Every tool call, resource read, and prompt above is something you'll build.
          </p>
        </section>

        {/* THE ARCADE TOUR */}
        <section className="arcade-card p-6">
          <h2 className="neon-cyan font-arcade text-xs mb-4">▌THE&nbsp;ARCADE&nbsp;TOUR</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {WORLDS.map((w) => (
              <div
                key={w.n}
                className="border border-maze/60 p-3 flex items-start gap-3 bg-black/30"
              >
                <div className="font-arcade neon-yellow text-xs w-14 shrink-0">
                  W{w.n}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-arcade neon-yellow text-[11px] mb-1">
                    {w.title}
                  </div>
                  <div className="text-[14px] opacity-75">{w.what}</div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* HOW IT WORKS */}
        <section className="arcade-card p-6">
          <h2 className="neon-cyan font-arcade text-xs mb-3">▌HOW&nbsp;IT&nbsp;WORKS</h2>
          <ul className="space-y-2 text-[16px] opacity-90">
            <li>
              <strong className="text-pac">Read</strong> the briefing on the left — every
              new concept gets explained with examples.
            </li>
            <li>
              <strong className="text-pac">Code</strong> in the middle — fill in the
              <code className="mx-1 px-1 bg-black/60 border border-inky/40 text-inky font-mono text-[13px]">
                # TODO
              </code>{" "}
              section, prior levels' solutions are already wired in.
            </li>
            <li>
              <strong className="text-pac">Watch</strong> the Protocol Inspector — every
              JSON-RPC message between Claude and your server appears live as you hit RUN.
            </li>
            <li>
              <strong className="text-pac">Save</strong> — every passing level writes
              your working code to{" "}
              <code className="mx-1 px-1 bg-black/60 border border-inky/40 text-inky font-mono text-[13px]">
                .claude/mcp_servers/pellet-tracker/
              </code>{" "}
              so the repo grows alongside your knowledge.
            </li>
          </ul>
        </section>

        {/* START */}
        <div className="text-center py-8">
          <button
            onClick={() => {
              sfx.powerPellet();
              onStart();
            }}
            className="arcade-btn neon-yellow text-sm px-12 py-5 blink"
          >
            ► PRESS&nbsp;START
          </button>
        </div>
      </div>
    </div>
  );
}

function ChatLine({ speaker, children }: { speaker: "you" | "claude"; children: React.ReactNode }) {
  const isYou = speaker === "you";
  return (
    <div className="flex gap-3 items-start">
      <div
        className={`font-arcade text-[10px] w-14 shrink-0 pt-0.5 ${
          isYou ? "neon-pink" : "neon-yellow"
        }`}
      >
        {isYou ? "YOU" : "CLAUDE"}
      </div>
      <div className="flex-1 text-[15px]">{children}</div>
    </div>
  );
}

function ToolCall({ name, args, result }: { name: string; args: string; result: string }) {
  return (
    <div className="ml-[60px] text-[12px] font-mono space-y-1 border-l-2 border-inky/50 pl-3">
      <div className="text-inky">
        → tool_use: <span className="text-pac">{name}</span>({args})
      </div>
      <div className="text-green-300">← tool_result: {result}</div>
    </div>
  );
}
