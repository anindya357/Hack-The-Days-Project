import { ExternalLink } from "lucide-react";
import type { Citation } from "@/lib/api";

export function CitationList({ citations }: { citations: Citation[] }) {
  if (!citations.length) {
    return null;
  }
  return (
    <div className="mt-5 border-t border-line pt-4">
      <h3 className="text-sm font-semibold uppercase text-slate-500">Citations</h3>
      <div className="mt-3 space-y-2">
        {citations.map((citation) => (
          <a
            key={`${citation.url}-${citation.chunk_id}`}
            href={citation.url}
            target="_blank"
            rel="noreferrer"
            className="flex items-start gap-2 rounded-md border border-line bg-white p-3 text-sm text-slate-700 hover:border-teal"
          >
            <ExternalLink className="mt-0.5 shrink-0" size={16} />
            <span className="min-w-0">
              <span className="block truncate font-medium text-ink">{citation.title || citation.url}</span>
              <span className="block truncate text-xs text-slate-500">{citation.url}</span>
            </span>
          </a>
        ))}
      </div>
    </div>
  );
}
