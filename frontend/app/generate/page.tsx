"use client";

import { FormEvent, useState } from "react";
import { FileCode2, Send } from "lucide-react";
import { CitationList } from "@/components/CitationList";
import { api, type ChatResponse } from "@/lib/api";

export default function GeneratePage() {
  const [request, setRequest] = useState("Create a LangChain RAG pipeline.");
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      setResponse(await api.generate({ request }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generate request failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-normal">Generate Code</h1>
        <p className="mt-1 text-sm text-slate-500">Create code examples from indexed documentation only, with citations for the APIs used.</p>
      </div>

      <section className="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
        <form onSubmit={submit} className="rounded-md border border-line bg-white p-5 shadow-soft">
          <label className="grid gap-2 text-sm font-medium">
            Request
            <textarea
              value={request}
              onChange={(event) => setRequest(event.target.value)}
              rows={10}
              className="resize-none rounded-md border border-line p-3 text-sm outline-none focus:border-teal"
            />
          </label>
          {error && <p className="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
          <button
            disabled={busy}
            className="mt-5 inline-flex h-11 items-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white disabled:opacity-60"
          >
            <Send size={17} />
            Generate
          </button>
        </form>

        <div className="rounded-md border border-line bg-white p-5 shadow-soft">
          <div className="flex items-center gap-2">
            <span className="grid h-9 w-9 place-items-center rounded-md bg-plum text-white">
              <FileCode2 size={18} />
            </span>
            <div>
              <h2 className="font-semibold">Code Output</h2>
              {response && (
                <p className="text-xs text-slate-500">
                  Confidence {Math.round(response.confidence * 100)}% · {response.retrieved_chunks} chunks
                </p>
              )}
            </div>
          </div>
          <pre className="mt-5 min-h-[420px] whitespace-pre-wrap rounded-md border border-line bg-slate-50 p-4 text-sm leading-6 text-slate-800">
            {busy ? "Generating from retrieved documentation..." : response?.answer || "Index documentation, then generate code from it."}
          </pre>
          {response && <CitationList citations={response.citations} />}
        </div>
      </section>
    </div>
  );
}
