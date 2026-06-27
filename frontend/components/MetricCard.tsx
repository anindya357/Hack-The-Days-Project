import type { LucideIcon } from "lucide-react";

export function MetricCard({
  label,
  value,
  icon: Icon,
  tone = "ink"
}: {
  label: string;
  value: string | number;
  icon: LucideIcon;
  tone?: "ink" | "teal" | "saffron" | "plum";
}) {
  const tones = {
    ink: "bg-ink text-white",
    teal: "bg-teal text-white",
    saffron: "bg-saffron text-white",
    plum: "bg-plum text-white"
  };
  return (
    <div className="rounded-md border border-line bg-white p-5 shadow-soft">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm text-slate-500">{label}</p>
          <p className="mt-2 text-3xl font-semibold tracking-normal">{value}</p>
        </div>
        <span className={`grid h-11 w-11 place-items-center rounded-md ${tones[tone]}`}>
          <Icon size={20} />
        </span>
      </div>
    </div>
  );
}
