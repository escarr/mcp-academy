import { useEffect, useState } from "react";
import { fetchLesson, runCode, saveToRepo, type SaveResponse } from "../api";
import { sfx } from "../audio";
import type { LessonDetail, RunResponse } from "../types";
import { ArcadeMarkdown } from "./ArcadeMarkdown";
import { CodeEditor } from "./CodeEditor";
import { Ghost } from "./Ghost";
import { ProtocolInspector } from "./ProtocolInspector";
import { LevelCompleteModal } from "./LevelCompleteModal";

interface Props {
  world: number;
  level: number;
  onExit: () => void;
  onClear: (pellets: number) => void;
}

export function Level({ world, level, onExit, onClear }: Props) {
  const [lesson, setLesson] = useState<LessonDetail | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [code, setCode] = useState<string>("");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<RunResponse | null>(null);
  const [showComplete, setShowComplete] = useState(false);
  const [hintOpen, setHintOpen] = useState(false);
  const [saved, setSaved] = useState<SaveResponse | null>(null);

  useEffect(() => {
    setLesson(null);
    setResult(null);
    setShowComplete(false);
    fetchLesson(world, level)
      .then((l) => {
        setLesson(l);
        setCode(l.starter_code);
      })
      .catch((e) => setErr(String(e)));
  }, [world, level]);

  if (err) {
    return (
      <div className="p-8 neon-red text-sm">
        FAILED TO LOAD LESSON<br />
        <span className="opacity-60 text-xs">{err}</span>
        <div className="mt-4">
          <button onClick={onExit} className="arcade-btn text-[10px] neon-yellow">
            ← BACK
          </button>
        </div>
      </div>
    );
  }
  if (!lesson) {
    return <div className="p-8 neon-yellow blink text-sm">LOADING&nbsp;LEVEL&hellip;</div>;
  }

  async function handleRun() {
    if (!lesson) return;
    setRunning(true);
    setResult(null);
    sfx.click();
    try {
      const r = await runCode(world, level, code);
      setResult(r);
      if (r.passed) {
        sfx.levelClear();
        setShowComplete(true);
        onClear(r.pellet_reward);
        // Persist the passing code into the actual repo so the user
        // accumulates a real Pellet Tracker server they can deploy.
        saveToRepo(world, level, code)
          .then(setSaved)
          .catch((e) => console.warn("save-to-repo failed", e));
      } else {
        sfx.fail();
      }
    } catch (e) {
      sfx.fail();
      setResult({
        passed: false,
        trace: [],
        stderr: "",
        steps: [],
        errors: [String(e)],
        pellet_reward: 0,
      });
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Top bar: ghost + title + nav */}
      <div className="flex items-center justify-between px-5 py-3 border-b-2 border-maze">
        <div className="flex items-center gap-4">
          <button onClick={onExit} className="arcade-btn text-[10px] neon-yellow">
            ← MAP
          </button>
          <Ghost name={lesson.ghost} size={36} />
          <div className="font-arcade">
            <div className="text-[9px] opacity-60">
              WORLD&nbsp;{lesson.world} · LEVEL&nbsp;{lesson.level} · {lesson.concept.toUpperCase()}
            </div>
            <div className="neon-yellow text-sm">{lesson.title}</div>
          </div>
        </div>
        <button
          onClick={handleRun}
          disabled={running}
          className={`arcade-btn text-xs ${running ? "neon-orange" : "neon-cyan"}`}
        >
          {running ? "RUNNING…" : "► RUN"}
        </button>
      </div>

      {/* Body: 2 columns — briefing (50%) | (editor + inspector stacked) (50%) */}
      <div className="flex-1 grid grid-cols-2 gap-3 p-3 min-h-0">
        {/* Briefing */}
        <aside className="arcade-card p-4 overflow-auto leading-relaxed min-h-0">
          <h3 className="neon-pink text-xs mb-2 font-arcade">▌MISSION</h3>
          <p className="opacity-90 mb-4 text-[17px]">{lesson.story}</p>

          {lesson.concept_brief && (
            <>
              <h3 className="neon-orange text-xs mb-1 mt-1 font-arcade">▌BRIEFING</h3>
              <div className="mb-4">
                <ArcadeMarkdown source={lesson.concept_brief} />
              </div>
            </>
          )}

          <h3 className="neon-cyan text-xs mb-2 font-arcade">▌TASK</h3>
          <div className="opacity-90 text-[17px]">
            <ArcadeMarkdown source={lesson.instructions} />
          </div>

          <h3 className="neon-yellow text-xs mt-5 mb-2 font-arcade">▌TEST STEPS</h3>
          <ol className="text-[16px] opacity-90 space-y-1 list-decimal pl-5">
            {lesson.grader_steps.map((s, i) => {
              const stepResult = result?.steps[i];
              const icon = !stepResult ? "·" : stepResult.passed ? "✓" : "✗";
              const cls = !stepResult
                ? "opacity-60"
                : stepResult.passed
                ? "neon-cyan"
                : "neon-red";
              return (
                <li key={i} className={cls}>
                  <span className="mr-1">{icon}</span>
                  {s.description || s.kind}
                </li>
              );
            })}
          </ol>

          <div className="mt-5">
            <button
              onClick={() => setHintOpen((h) => !h)}
              className="font-arcade text-[10px] neon-orange opacity-80 hover:opacity-100"
            >
              {hintOpen ? "▾ HIDE HINT" : "▸ NEED A HINT?"}
            </button>
            {hintOpen && (
              <div className="mt-2 text-[16px] opacity-80">
                <ArcadeMarkdown source={lesson.solution_hint} />
              </div>
            )}
          </div>
        </aside>

        {/* Right column: editor on top, inspector below */}
        <div className="min-w-0 flex flex-col gap-3 min-h-0">
          {/* Editor (top ~60% of column) */}
          <section className="min-w-0 flex flex-col flex-[3] min-h-0">
            <CodeEditor value={code} onChange={setCode} />
            {result && !result.passed && result.errors.length > 0 && (
              <div className="mt-2 arcade-card p-3 text-[16px] neon-red max-h-32 overflow-auto shrink-0">
                <div className="mb-1 font-arcade text-[10px] opacity-70">▌FAILURES</div>
                <ul className="list-disc pl-5 space-y-1">
                  {result.errors.map((e, i) => (
                    <li key={i}>{e}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>

          {/* Protocol Inspector (bottom ~40% of column) */}
          <section className="min-w-0 flex-[2] min-h-0">
            <ProtocolInspector trace={result?.trace ?? []} stderr={result?.stderr ?? ""} />
          </section>
        </div>
      </div>

      {showComplete && (
        <LevelCompleteModal
          pellets={result?.pellet_reward ?? lesson.pellet_reward}
          debrief={lesson.post_pass_debrief}
          savedPath={saved?.path}
          onContinue={() => {
            setShowComplete(false);
            onExit();
          }}
          onReplay={() => {
            setShowComplete(false);
            setCode(lesson.starter_code);
            setResult(null);
          }}
        />
      )}
    </div>
  );
}
