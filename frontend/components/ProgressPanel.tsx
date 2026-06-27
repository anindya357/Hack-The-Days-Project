import { CheckCircle2, Loader2, XCircle } from "lucide-react";
import type { JobStatus } from "@/lib/api";

export function ProgressPanel({ jobs }: { jobs: JobStatus[] }) {
  return (
    <div className="rounded-md border border-line bg-white p-5 shadow-soft">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Crawler Jobs</h2>
      </div>
      <div className="mt-4 space-y-3">
        {jobs.length === 0 ? (
          <p className="text-sm text-slate-500">No jobs yet.</p>
        ) : (
          jobs.map((job) => (
            <div key={job.job_id} className="rounded-md border border-line p-3">
              <div className="flex items-center gap-2">
                {job.status === "completed" && <CheckCircle2 className="text-teal" size={18} />}
                {job.status === "failed" && <XCircle className="text-red-600" size={18} />}
                {["queued", "running"].includes(job.status) && <Loader2 className="animate-spin text-saffron" size={18} />}
                <span className="text-sm font-medium">{job.message}</span>
                <span className="ml-auto text-xs text-slate-500">{job.progress}%</span>
              </div>
              <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
                <div className="h-full bg-teal transition-all" style={{ width: `${job.progress}%` }} />
              </div>
              <p className="mt-2 text-xs text-slate-500">
                {job.pages_found} found · {job.pages_indexed} indexed · {job.stage}
              </p>
              {job.error && <p className="mt-2 text-xs text-red-600">{job.error}</p>}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
