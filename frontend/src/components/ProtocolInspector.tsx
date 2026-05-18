import { useMemo, useState } from "react";
import type { TraceEntry } from "../types";

interface Props {
  trace: TraceEntry[];
  stderr: string;
}

export function ProtocolInspector({ trace, stderr }: Props) {
  const [tab, setTab] = useState<"trace" | "stderr">("trace");
  const [expanded, setExpanded] = useState<number | null>(null);

  const labelFor = (t: TraceEntry, idx: number): string => {
    const m = t.message;
    if (t.direction === "log") return "log";
    if (m?.method) return m.method;
    if (m?.result !== undefined) return "response";
    if (m?.error !== undefined) return "error";
    return `msg ${idx}`;
  };

  const summary = useMemo(() => {
    const out: { method: string; count: number }[] = [];
    for (const t of trace) {
      if (t.direction !== "out") continue;
      const method = t.message?.method ?? "?";
      const found = out.find((x) => x.method === method);
      if (found) found.count++;
      else out.push({ method, count: 1 });
    }
    return out;
  }, [trace]);

  return (
    <div className="arcade-card h-full flex flex-col">
      <div className="flex items-center justify-between px-3 py-2 border-b-2 border-maze">
        <div className="flex gap-3 text-[10px]">
          <button
            onClick={() => setTab("trace")}
            className={tab === "trace" ? "neon-yellow" : "opacity-50 hover:opacity-100"}
          >
            JSON-RPC
          </button>
          <button
            onClick={() => setTab("stderr")}
            className={tab === "stderr" ? "neon-yellow" : "opacity-50 hover:opacity-100"}
          >
            STDERR
          </button>
        </div>
        <div className="text-[9px] opacity-60">
          {summary.map((s) => `${s.method}×${s.count}`).join("  ")}
        </div>
      </div>

      <div className="flex-1 overflow-auto p-2 font-mono text-[11px] leading-snug">
        {tab === "trace" && (
          <>
            {trace.length === 0 && (
              <div className="opacity-50 text-center mt-12 text-[10px] tracking-widest">
                NO&nbsp;MESSAGES&nbsp;YET
                <div className="mt-2 normal-case">Hit ► RUN to see JSON-RPC traffic.</div>
              </div>
            )}
            {trace.map((t, i) => (
              <TraceRow
                key={i}
                idx={i}
                entry={t}
                label={labelFor(t, i)}
                expanded={expanded === i}
                onToggle={() => setExpanded(expanded === i ? null : i)}
              />
            ))}
          </>
        )}
        {tab === "stderr" && (
          <pre className="whitespace-pre-wrap text-clyde">
            {stderr || <span className="opacity-50">— empty —</span>}
          </pre>
        )}
      </div>
    </div>
  );
}

function TraceRow({
  entry,
  idx,
  label,
  expanded,
  onToggle,
}: {
  entry: TraceEntry;
  idx: number;
  label: string;
  expanded: boolean;
  onToggle: () => void;
}) {
  const cls =
    entry.direction === "out"
      ? "trace-row-out"
      : entry.direction === "in"
      ? "trace-row-in"
      : "trace-row-log";
  const arrow =
    entry.direction === "out" ? "→ client → server" :
    entry.direction === "in"  ? "← server → client" :
                                "· log";
  return (
    <div className={`${cls} px-2 py-1 mb-1 bg-black/20`}>
      <button
        onClick={onToggle}
        className="w-full text-left flex items-center justify-between gap-2"
      >
        <span className="truncate">
          <span className="opacity-50 mr-2">{String(idx + 1).padStart(2, "0")}</span>
          <span
            className={
              entry.direction === "out"
                ? "neon-yellow"
                : entry.direction === "in"
                ? "neon-cyan"
                : "neon-orange"
            }
          >
            {label}
          </span>
        </span>
        <span className="opacity-50 text-[9px] shrink-0">{arrow}</span>
      </button>
      {expanded && (
        <pre className="mt-1 text-[10px] opacity-80 whitespace-pre-wrap break-words">
          {JSON.stringify(entry.message, null, 2)}
        </pre>
      )}
    </div>
  );
}
