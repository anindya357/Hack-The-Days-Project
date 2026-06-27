"use client";

import { FormEvent, useState } from "react";
import { GitCompare, Split } from "lucide-react";
import { CitationList } from "@/components/CitationList";
import { api, type Citation } from "@/lib/api";

export default function ComparePage() {
  const [left, setLeft] = useState("FastAPI");
  const [right, setRight] = useState("Django");
  const [comparison, setComparison] = useState("");
  const [citations, setCitations] = useState<Citation[]>([]);
  const [confidence, setConfidence] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const result = await api.compare({ left, right });
      setComparison(result.comparison);
      setCitations(result.citations);
      setConfidence(result.confidence);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Compare request failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-normal">Compare</h1>
        <p className="mt-1 text-sm text-slate-500">Retrieve from multiple docs and produce side-by-side framework comparisons.</p>
      </div>
      <section className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
        <form onSubmit={submit} className="rounded-md border border-line bg-white p-5 shadow-soft">
          <div className="grid gap-4">
            <label className="grid gap-2 text-sm font-medium">
              Left
              <input
                value={left}
                onChange={(event) => setLeft(event.target.value)}
                className="h-11 rounded-md border border-line px-3 text-sm outline-none focus:border-teal"
              />
            </label>
            <div className="grid place-items-center">
              <span className="grid h-10 w-10 place-items-center rounded-md bg-slate-100 text-slate-600">
                <Split size={18} />
              </span>
            </div>
            <label className="grid gap-2 text-sm font-medium">
              Right
              <input
                value={right}
                onChange={(event) => setRight(event.target.value)}
                className="h-11 rounded-md border border-line px-3 text-sm outline-none focus:border-teal"
              />
            </label>
          </div>
          {error && <p className="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
          <button
            disabled={busy}
            className="mt-5 inline-flex h-11 items-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white disabled:opacity-60"
          >
            <GitCompare size={17} />
            Compare
          </button>
        </form>
        <div className="rounded-md border border-line bg-white p-5 shadow-soft">
          <div className="flex items-center justify-between gap-3">
            <h2 className="font-semibold">Result</h2>
            {comparison && <span className="text-xs text-slate-500">Confidence {Math.round(confidence * 100)}%</span>}
          </div>
          <pre className="mt-5 min-h-[360px] whitespace-pre-wrap rounded-md border border-line bg-slate-50 p-4 text-sm leading-6 text-slate-800">
            {busy ? "Comparing retrieved documentation..." : comparison || "Run a comparison after indexing both documentation sets."}
          </pre>
          <CitationList citations={citations} />
        </div>
      </section>
    </div>
  );
}
