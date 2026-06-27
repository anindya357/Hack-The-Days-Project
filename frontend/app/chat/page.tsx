"use client";

import { FormEvent, useState } from "react";
import { Bot, Send, Sparkles } from "lucide-react";
import { CitationList } from "@/components/CitationList";
import { api, type ChatResponse } from "@/lib/api";

const examples = ["How do I create an Agent?", "Explain LangGraph.", "Summarize LangGraph documentation in 5 minutes."];

export default function ChatPage() {
  const [question, setQuestion] = useState("How do I create an Agent?");
  const [mode, setMode] = useState<"answer" | "summarize">("answer");
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      setResponse(await api.chat({ question, mode }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat request failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-normal">Chat</h1>
        <p className="mt-1 text-sm text-slate-500">Ask questions and receive grounded answers with code examples, citations, and confidence.</p>
      </div>

      <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <form onSubmit={submit} className="rounded-md border border-line bg-white p-5 shadow-soft">
          <div className="mb-4 flex rounded-md border border-line p-1">
            <button
              type="button"
              onClick={() => setMode("answer")}
              className={`h-10 flex-1 rounded px-3 text-sm font-medium ${mode === "answer" ? "bg-ink text-white" : "text-slate-600"}`}
            >
              Answer
            </button>
            <button
              type="button"
              onClick={() => setMode("summarize")}
              className={`h-10 flex-1 rounded px-3 text-sm font-medium ${mode === "summarize" ? "bg-ink text-white" : "text-slate-600"}`}
            >
              Summarize
            </button>
          </div>
          <label className="grid gap-2 text-sm font-medium">
            Question
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              rows={8}
              className="resize-none rounded-md border border-line p-3 text-sm outline-none focus:border-teal"
            />
          </label>
          <div className="mt-4 flex flex-wrap gap-2">
            {examples.map((example) => (
              <button
                key={example}
                type="button"
                onClick={() => setQuestion(example)}
                className="rounded-md border border-line px-3 py-2 text-xs font-medium text-slate-600 hover:border-teal"
              >
                {example}
              </button>
            ))}
          </div>
          {error && <p className="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
          <button
            disabled={busy}
            className="mt-5 inline-flex h-11 items-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white disabled:opacity-60"
          >
            <Send size={17} />
            Ask
          </button>
        </form>

        <div className="rounded-md border border-line bg-white p-5 shadow-soft">
          <div className="flex items-center gap-2">
            <span className="grid h-9 w-9 place-items-center rounded-md bg-teal text-white">
              {mode === "summarize" ? <Sparkles size={18} /> : <Bot size={18} />}
            </span>
            <div>
              <h2 className="font-semibold">Response</h2>
              {response && (
                <p className="text-xs text-slate-500">
                  Confidence {Math.round(response.confidence * 100)}% · {response.retrieved_chunks} chunks
                </p>
              )}
            </div>
          </div>
          <pre className="mt-5 min-h-[320px] whitespace-pre-wrap rounded-md border border-line bg-slate-50 p-4 text-sm leading-6 text-slate-800">
            {busy ? "Thinking with retrieved documentation..." : response?.answer || "Run a query after indexing documentation."}
          </pre>
          {response && <CitationList citations={response.citations} />}
        </div>
      </section>
    </div>
  );
}
