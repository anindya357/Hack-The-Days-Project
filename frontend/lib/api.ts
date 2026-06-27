export type ProjectSummary = {
  id: string;
  name: string;
  root_url: string;
  version: string;
  document_count: number;
  chunk_count: number;
  updated_at?: string | null;
};

export type DashboardStats = {
  projects: number;
  documents: number;
  chunks: number;
  questions: number;
  embeddings: number;
  token_usage: number;
};

export type JobStatus = {
  job_id: string;
  status: "queued" | "running" | "completed" | "failed";
  stage: string;
  progress: number;
  message: string;
  pages_found: number;
  pages_indexed: number;
  error?: string | null;
};

export type Citation = {
  url: string;
  title?: string | null;
  chunk_id?: string | null;
  score?: number | null;
};

export type ChatResponse = {
  answer: string;
  citations: Citation[];
  confidence: number;
  retrieved_chunks: number;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  stats: () => request<DashboardStats>("/stats"),
  projects: () => request<ProjectSummary[]>("/docs"),
  jobs: () => request<JobStatus[]>("/status"),
  crawl: (body: { url: string; project_name?: string; version?: string; max_pages?: number }) =>
    request<{ job_id: string; project_id: string; status: string; message: string }>("/crawl", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  chat: (body: { question: string; project_ids?: string[]; version?: string; mode?: "answer" | "summarize" }) =>
    request<ChatResponse>("/chat", { method: "POST", body: JSON.stringify(body) }),
  compare: (body: { left: string; right: string; project_ids?: string[]; version?: string }) =>
    request<{ comparison: string; citations: Citation[]; confidence: number }>("/compare", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  generate: (body: { request: string; project_ids?: string[]; version?: string }) =>
    request<ChatResponse>("/generate", { method: "POST", body: JSON.stringify(body) }),
  update: (body: { project_id?: string; url?: string; max_pages?: number }) =>
    request<{ job_id: string; project_id: string; status: string; message: string }>("/update", {
      method: "POST",
      body: JSON.stringify(body)
    })
};
