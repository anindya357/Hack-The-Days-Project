"use client";

import { FormEvent, useEffect, useState } from "react";
import { Play, RefreshCw } from "lucide-react";
import { ProgressPanel } from "@/components/ProgressPanel";
import { api, type JobStatus } from "@/lib/api";

export default function CrawlerPage() {
  const [url, setUrl] = useState("https://python.langchain.com");
  const [projectName, setProjectName] = useState("LangChain");
  const [version, setVersion] = useState("latest");
  const [maxPages, setMaxPages] = useState(32);
  const [jobs, setJobs] = useState<JobStatus[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadJobs = async () => {
    try {
      setJobs(await api.jobs());
    } catch {
      setJobs([]);
    }
  };

  useEffect(() => {
    loadJobs();
    const interval = window.setInterval(loadJobs, 2500);
    return () => window.clearInterval(interval);
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await api.crawl({ url, project_name: projectName, version, max_pages: maxPages });
      await loadJobs();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start crawler");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-normal">Crawler</h1>
        <p className="mt-1 text-sm text-slate-500">Discover pages, clean HTML, extract code blocks, chunk, embed, and store vectors.</p>
      </div>

      <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <form onSubmit={submit} className="rounded-md border border-line bg-white p-5 shadow-soft">
          <div className="grid gap-4">
            <label className="grid gap-2 text-sm font-medium">
              Documentation URL
              <input
                value={url}
                onChange={(event) => setUrl(event.target.value)}
                className="h-11 rounded-md border border-line px-3 text-sm outline-none focus:border-teal"
              />
            </label>
            <div className="grid gap-4 md:grid-cols-3">
              <label className="grid gap-2 text-sm font-medium md:col-span-1">
                Project
                <input
                  value={projectName}
                  onChange={(event) => setProjectName(event.target.value)}
                  className="h-11 rounded-md border border-line px-3 text-sm outline-none focus:border-teal"
                />
              </label>
              <label className="grid gap-2 text-sm font-medium">
                Version
                <input
                  value={version}
                  onChange={(event) => setVersion(event.target.value)}
                  className="h-11 rounded-md border border-line px-3 text-sm outline-none focus:border-teal"
                />
              </label>
              <label className="grid gap-2 text-sm font-medium">
                Max pages
                <input
                  type="number"
                  min={1}
                  max={500}
                  value={maxPages}
                  onChange={(event) => setMaxPages(Number(event.target.value))}
                  className="h-11 rounded-md border border-line px-3 text-sm outline-none focus:border-teal"
                />
              </label>
            </div>
            {error && <p className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
            <div className="flex flex-wrap gap-3">
              <button
                type="submit"
                disabled={busy}
                className="inline-flex h-11 items-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white disabled:opacity-60"
              >
                <Play size={17} />
                Start Crawl
              </button>
              <button
                type="button"
                onClick={loadJobs}
                className="inline-flex h-11 items-center gap-2 rounded-md border border-line bg-white px-4 text-sm font-semibold text-ink"
              >
                <RefreshCw size={17} />
                Refresh
              </button>
            </div>
          </div>
        </form>
        <ProgressPanel jobs={jobs} />
      </section>
    </div>
  );
}
