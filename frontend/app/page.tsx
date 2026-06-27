"use client";

import { useEffect, useState } from "react";
import { Blocks, Database, FileText, MessageSquare, WalletCards } from "lucide-react";
import { ArchitectureFlow } from "@/components/ArchitectureFlow";
import { MetricCard } from "@/components/MetricCard";
import { ProgressPanel } from "@/components/ProgressPanel";
import { api, type DashboardStats, type JobStatus, type ProjectSummary } from "@/lib/api";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [jobs, setJobs] = useState<JobStatus[]>([]);
  const [projects, setProjects] = useState<ProjectSummary[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        const [nextStats, nextJobs, nextProjects] = await Promise.all([api.stats(), api.jobs(), api.projects()]);
        setStats(nextStats);
        setJobs(nextJobs);
        setProjects(nextProjects);
      } catch {
        setStats({ projects: 0, documents: 0, chunks: 0, questions: 0, embeddings: 0, token_usage: 0 });
      }
    };
    load();
    const interval = window.setInterval(load, 4000);
    return () => window.clearInterval(interval);
  }, []);

  const values = stats ?? { projects: 0, documents: 0, chunks: 0, questions: 0, embeddings: 0, token_usage: 0 };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-normal">Dashboard</h1>
          <p className="mt-1 text-sm text-slate-500">Index docs, retrieve citations, compare frameworks, and generate grounded code.</p>
        </div>
        <div className="rounded-md border border-line bg-white px-3 py-2 text-sm text-slate-600">
          Agent mode: <span className="font-semibold text-teal">LangGraph supervisor</span>
        </div>
      </div>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <MetricCard label="Indexed Pages" value={values.documents} icon={FileText} tone="teal" />
        <MetricCard label="Embeddings" value={values.embeddings} icon={Database} />
        <MetricCard label="Questions" value={values.questions} icon={MessageSquare} tone="plum" />
        <MetricCard label="Documents" value={values.projects} icon={Blocks} tone="saffron" />
        <MetricCard label="Token Usage" value={values.token_usage} icon={WalletCards} />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.5fr_1fr]">
        <div>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Architecture</h2>
            <span className="text-sm text-slate-500">Frontend · Backend · Agents · ChromaDB</span>
          </div>
          <ArchitectureFlow />
        </div>
        <ProgressPanel jobs={jobs} />
      </section>

      <section className="rounded-md border border-line bg-white p-5 shadow-soft">
        <h2 className="text-lg font-semibold">Recently Indexed</h2>
        <div className="mt-4 overflow-hidden rounded-md border border-line">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500">
              <tr>
                <th className="px-4 py-3 font-medium">Project</th>
                <th className="px-4 py-3 font-medium">Version</th>
                <th className="px-4 py-3 font-medium">Pages</th>
                <th className="px-4 py-3 font-medium">Chunks</th>
              </tr>
            </thead>
            <tbody>
              {projects.length === 0 ? (
                <tr>
                  <td className="px-4 py-6 text-slate-500" colSpan={4}>
                    Paste a documentation URL in Crawler to begin.
                  </td>
                </tr>
              ) : (
                projects.map((project) => (
                  <tr key={project.id} className="border-t border-line">
                    <td className="px-4 py-3 font-medium">{project.name}</td>
                    <td className="px-4 py-3 text-slate-600">{project.version}</td>
                    <td className="px-4 py-3 text-slate-600">{project.document_count}</td>
                    <td className="px-4 py-3 text-slate-600">{project.chunk_count}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
