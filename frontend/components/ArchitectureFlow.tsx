"use client";

import { Background, Controls, ReactFlow, type Edge, type Node } from "@xyflow/react";

const nodes: Node[] = [
  { id: "user", position: { x: 280, y: 0 }, data: { label: "User" } },
  { id: "frontend", position: { x: 250, y: 85 }, data: { label: "Next.js Frontend" } },
  { id: "backend", position: { x: 250, y: 170 }, data: { label: "FastAPI Backend" } },
  { id: "supervisor", position: { x: 230, y: 255 }, data: { label: "LangGraph Supervisor" } },
  { id: "crawler", position: { x: 0, y: 360 }, data: { label: "Crawler Agent" } },
  { id: "rag", position: { x: 180, y: 360 }, data: { label: "RAG Agent" } },
  { id: "search", position: { x: 360, y: 360 }, data: { label: "Search Agent" } },
  { id: "code", position: { x: 540, y: 360 }, data: { label: "Code Agent" } },
  { id: "openai", position: { x: 220, y: 470 }, data: { label: "OpenAI Responses API" } },
  { id: "chroma", position: { x: 250, y: 555 }, data: { label: "ChromaDB Vectors" } }
];

const edges: Edge[] = [
  { id: "e1", source: "user", target: "frontend" },
  { id: "e2", source: "frontend", target: "backend" },
  { id: "e3", source: "backend", target: "supervisor" },
  { id: "e4", source: "supervisor", target: "crawler" },
  { id: "e5", source: "supervisor", target: "rag" },
  { id: "e6", source: "supervisor", target: "search" },
  { id: "e7", source: "supervisor", target: "code" },
  { id: "e8", source: "rag", target: "openai" },
  { id: "e9", source: "code", target: "openai" },
  { id: "e10", source: "openai", target: "chroma" }
];

export function ArchitectureFlow() {
  return (
    <div className="h-[440px] rounded-md border border-line bg-white shadow-soft">
      <ReactFlow nodes={nodes} edges={edges} fitView nodesDraggable={false} panOnScroll>
        <Background />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}
