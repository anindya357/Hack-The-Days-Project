import { BrainCircuit, Boxes, Workflow } from "lucide-react";

export default function AboutPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-normal">About</h1>
        <p className="mt-1 text-sm text-slate-500">DevDocs AI is an agentic documentation assistant for software teams and hackathon demos.</p>
      </div>
      <section className="grid gap-4 md:grid-cols-3">
        <div className="rounded-md border border-line bg-white p-5 shadow-soft">
          <BrainCircuit className="text-teal" size={28} />
          <h2 className="mt-4 font-semibold">Grounded Answers</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">Retrieves documentation chunks, answers only from context, and returns URLs as citations.</p>
        </div>
        <div className="rounded-md border border-line bg-white p-5 shadow-soft">
          <Workflow className="text-plum" size={28} />
          <h2 className="mt-4 font-semibold">Agentic Flow</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">LangGraph supervises crawler, retriever, search, and code generation responsibilities.</p>
        </div>
        <div className="rounded-md border border-line bg-white p-5 shadow-soft">
          <Boxes className="text-saffron" size={28} />
          <h2 className="mt-4 font-semibold">Deployable Stack</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">FastAPI, Next.js, ChromaDB, PostgreSQL, Docker Compose, Nginx, and CI are included.</p>
        </div>
      </section>
    </div>
  );
}
