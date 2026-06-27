import { KeyRound, Network, Server } from "lucide-react";

const settings = [
  { label: "Backend", value: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api", icon: Server },
  { label: "Embedding", value: "text-embedding-3-large", icon: Network },
  { label: "Answering", value: "OpenAI Responses API", icon: KeyRound }
];

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-normal">Settings</h1>
        <p className="mt-1 text-sm text-slate-500">Runtime configuration is driven by environment variables and Docker Compose.</p>
      </div>
      <section className="grid gap-4 md:grid-cols-3">
        {settings.map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.label} className="rounded-md border border-line bg-white p-5 shadow-soft">
              <span className="grid h-10 w-10 place-items-center rounded-md bg-ink text-white">
                <Icon size={18} />
              </span>
              <p className="mt-4 text-sm text-slate-500">{item.label}</p>
              <p className="mt-1 break-words text-base font-semibold">{item.value}</p>
            </div>
          );
        })}
      </section>
      <section className="rounded-md border border-line bg-white p-5 shadow-soft">
        <h2 className="text-lg font-semibold">Environment</h2>
        <pre className="mt-4 overflow-auto rounded-md border border-line bg-slate-50 p-4 text-sm text-slate-800">{`OPENAI_API_KEY=
TAVILY_API_KEY=
DATABASE_URL=postgresql+psycopg://devdocs:devdocs@postgres:5432/devdocs
CHROMA_HOST=chromadb
CHROMA_PORT=8000
NEXT_PUBLIC_API_URL=http://localhost:8000/api`}</pre>
      </section>
    </div>
  );
}
