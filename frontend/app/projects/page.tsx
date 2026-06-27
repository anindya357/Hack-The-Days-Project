"use client";

import { useEffect, useState } from "react";
import { RefreshCw, RotateCcw } from "lucide-react";
import { api, type ProjectSummary } from "@/lib/api";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      setProjects(await api.projects());
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-3xl font-semibold tracking-normal">Projects</h1>
          <p className="mt-1 text-sm text-slate-500">Documentation sets indexed into ChromaDB and tracked in PostgreSQL.</p>
        </div>
        <button onClick={load} className="inline-flex h-10 items-center gap-2 rounded-md border border-line bg-white px-3 text-sm font-semibold">
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      <section className="rounded-md border border-line bg-white shadow-soft">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Root URL</th>
                <th className="px-4 py-3 font-medium">Version</th>
                <th className="px-4 py-3 font-medium">Pages</th>
                <th className="px-4 py-3 font-medium">Chunks</th>
                <th className="px-4 py-3 font-medium">Update</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td className="px-4 py-6 text-slate-500" colSpan={6}>
                    Loading projects...
                  </td>
                </tr>
              ) : projects.length === 0 ? (
                <tr>
                  <td className="px-4 py-6 text-slate-500" colSpan={6}>
                    No indexed projects yet.
                  </td>
                </tr>
              ) : (
                projects.map((project) => (
                  <tr key={project.id} className="border-t border-line">
                    <td className="px-4 py-3 font-medium">{project.name}</td>
                    <td className="max-w-[320px] truncate px-4 py-3 text-slate-600">{project.root_url}</td>
                    <td className="px-4 py-3 text-slate-600">{project.version}</td>
                    <td className="px-4 py-3 text-slate-600">{project.document_count}</td>
                    <td className="px-4 py-3 text-slate-600">{project.chunk_count}</td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => api.update({ project_id: project.id })}
                        className="grid h-9 w-9 place-items-center rounded-md border border-line text-slate-600 hover:border-teal"
                        title="Run incremental update"
                        aria-label="Run incremental update"
                      >
                        <RotateCcw size={16} />
                      </button>
                    </td>
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
