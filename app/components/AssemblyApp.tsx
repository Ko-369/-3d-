"use client";

import { useEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";
import { ArrowLeft, Check, ClipboardCopy, Loader2, RotateCcw, Shuffle, ListOrdered } from "lucide-react";
import { ASSEMBLY_SLOTS, BUILD_ORDER, slotById, type AssemblyPartId } from "../lib/assembly-data";
import { getAssemblyStrings } from "../lib/assembly-strings";
import type { AssemblyViewer, CalibrationPose } from "../lib/three/assembly-viewer";

type Mode = "free" | "guided";

/** `?calibration=1` turns on the slot-authoring mode, mirroring the viewer's authoring flag. */
function useCalibrationFlag() {
  return useSyncExternalStore(
    () => () => {},
    () => new URLSearchParams(window.location.search).get("calibration") === "1",
    () => false,
  );
}

function formatSnippet(pose: CalibrationPose): string {
  const slot = slotById[pose.id];
  return [
    "  {",
    `    id: "${pose.id}",`,
    `    model: "${slot.model}",`,
    `    accent: "${slot.accent}",`,
    `    size: [${pose.size.join(", ")}],`,
    `    position: [${pose.position.join(", ")}],`,
    `    rotation: [${pose.rotation.join(", ")}],`,
    `    snap: ${slot.snap},`,
    "  },",
  ].join("\n");
}

export function AssemblyApp({ locale }: { locale: string }) {
  const t = useMemo(() => getAssemblyStrings(locale), [locale]);
  const mountRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<AssemblyViewer | null>(null);

  const [placed, setPlaced] = useState<Set<AssemblyPartId>>(new Set());
  const [mode, setMode] = useState<Mode>("free");
  const [loading, setLoading] = useState(true);
  const [progress, setProgress] = useState(0);
  const [done, setDone] = useState(false);
  const [dragId, setDragId] = useState<AssemblyPartId | null>(null);

  const calibration = useCalibrationFlag();
  const calibrationRef = useRef(calibration);
  const [pose, setPose] = useState<CalibrationPose | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    calibrationRef.current = calibration;
  }, [calibration]);

  const next = useMemo(() => BUILD_ORDER.find((id) => !placed.has(id)) ?? null, [placed]);
  const total = ASSEMBLY_SLOTS.length;

  useEffect(() => {
    let cancelled = false;
    let viewer: AssemblyViewer | null = null;

    void import("../lib/three/assembly-viewer").then(({ AssemblyViewer: V }) => {
      if (cancelled || !mountRef.current) return;
      viewer = new V(mountRef.current, {
        onLoading: (isLoading, value) => {
          setLoading(isLoading);
          setProgress(value);
        },
        onPlace: (id) => {
          setPlaced((prev) => {
            if (prev.has(id)) return prev;
            const nextSet = new Set(prev);
            nextSet.add(id);
            return nextSet;
          });
        },
        onComplete: () => setDone(true),
        onDragState: (id) => setDragId(id),
        onPoseChange: (p) => setPose(p),
      });
      viewerRef.current = viewer;
      viewer.setCalibration(calibrationRef.current);
      viewer.setGuided(null);
      void viewer.loadAll();
    });

    return () => {
      cancelled = true;
      viewerRef.current = null;
      viewer?.dispose();
    };
  }, []);

  // Keep the engine's guided target in sync with mode + progress.
  useEffect(() => {
    viewerRef.current?.setGuided(mode === "guided" ? next : null);
  }, [mode, next]);

  const reset = () => {
    viewerRef.current?.reset();
    setPlaced(new Set());
    setDone(false);
  };

  const copyPose = () => {
    if (!pose) return;
    void navigator.clipboard.writeText(formatSnippet(pose)).then(() => {
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1200);
    });
  };

  const nextName = next ? t.partNames[next] : "";

  return (
    <div className="assembly-app">
      <header className="assembly-bar">
        <div className="assembly-brand">
          <a className="assembly-back" href={`/${locale}`}>
            <ArrowLeft size={16} /> {t.back}
          </a>
          <div>
            <h1>{t.title}</h1>
            <em>{t.subtitle}</em>
          </div>
        </div>

        {calibration ? (
          <span className="assembly-calib-badge">{t.calib.title}</span>
        ) : (
          <div className="assembly-controls">
            <div className="assembly-mode" role="group" aria-label={t.hint}>
              <button
                type="button"
                className={mode === "free" ? "active" : ""}
                onClick={() => setMode("free")}
                aria-pressed={mode === "free"}
                title={t.modeHintFree}
              >
                <Shuffle size={15} /> {t.modeFree}
              </button>
              <button
                type="button"
                className={mode === "guided" ? "active" : ""}
                onClick={() => setMode("guided")}
                aria-pressed={mode === "guided"}
                title={t.modeHintGuided}
              >
                <ListOrdered size={15} /> {t.modeGuided}
              </button>
            </div>
            <button type="button" className="assembly-reset" onClick={reset} title={t.reset}>
              <RotateCcw size={15} /> {t.reset}
            </button>
            <span className="assembly-progress" role="status" aria-live="polite">
              {t.progress(placed.size, total)}
            </span>
          </div>
        )}
      </header>

      <div className="assembly-stage">
        <div ref={mountRef} className="assembly-mount" />

        {!calibration && mode === "guided" && next && !done && (
          <div className="assembly-prompt" role="status" aria-live="polite">
            <span className="assembly-prompt-dot" style={{ background: ASSEMBLY_SLOTS.find((s) => s.id === next)?.accent }} />
            <strong>{t.next(nextName)}</strong>
          </div>
        )}

        {!calibration && (
        <aside className="assembly-checklist" aria-label={t.title}>
          {BUILD_ORDER.map((id) => {
            const slot = ASSEMBLY_SLOTS.find((s) => s.id === id)!;
            const isPlaced = placed.has(id);
            const isNext = mode === "guided" && next === id;
            const isDragging = dragId === id;
            return (
              <div
                key={id}
                className={`assembly-part ${isPlaced ? "placed" : ""} ${isNext ? "next" : ""} ${isDragging ? "dragging" : ""}`}
                style={{ "--part-accent": slot.accent } as React.CSSProperties}
              >
                <span className="assembly-part-glyph" aria-hidden>{isPlaced ? <Check size={14} /> : "▢"}</span>
                <span className="assembly-part-name">{t.partNames[id]}</span>
              </div>
            );
          })}
        </aside>
        )}

        {!calibration && (
          <div className="assembly-hint">
            {t.hintDrag}
            <br />
            {t.hintScroll}
          </div>
        )}

        {calibration && (
          <div className="assembly-calib">
            <header>
              <strong>{t.calib.title}</strong>
              {pose && <em>{t.calib.active(t.partNames[pose.id])}</em>}
            </header>
            {pose ? <pre>{formatSnippet(pose)}</pre> : <p>{t.calib.hint}</p>}
            <button type="button" onClick={copyPose} disabled={!pose}>
              <ClipboardCopy size={14} /> {copied ? t.calib.copied : t.calib.copy}
            </button>
            <ul>
              {t.calib.keys.map((key) => (
                <li key={key}>{key}</li>
              ))}
            </ul>
          </div>
        )}

        {loading && (
          <div className="assembly-loading" role="status" aria-live="polite">
            <Loader2 size={22} className="assembly-spinner" />
            <strong>{t.loading}</strong>
            <span>{Math.max(6, Math.round(progress * 100))}%</span>
          </div>
        )}

        {done && (
          <div className="assembly-done" role="dialog" aria-modal="true">
            <span className="assembly-done-icon">✓</span>
            <h2>{t.doneTitle}</h2>
            <p>{t.doneBody}</p>
            <button type="button" onClick={reset}>
              <RotateCcw size={15} /> {t.doneAgain}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
