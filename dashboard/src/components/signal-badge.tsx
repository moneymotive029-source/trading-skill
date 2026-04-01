export function SignalBadge({ signal }: { signal: "LONG" | "SHORT" | "NEUTRAL" }) {
  const colors = {
    LONG: "bg-green-500/20 text-green-400 border-green-500/30",
    SHORT: "bg-red-500/20 text-red-400 border-red-500/30",
    NEUTRAL: "bg-slate-500/20 text-slate-400 border-slate-500/30",
  };

  return (
    <span
      className={`px-2.5 py-1 text-xs font-medium rounded-lg border ${colors[signal]}`}
    >
      {signal}
    </span>
  );
}

export function ConfidenceBadge({
  confidence,
}: {
  confidence: "High" | "Medium" | "Low";
}) {
  const colors = {
    High: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
    Medium: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    Low: "bg-slate-500/20 text-slate-400 border-slate-500/30",
  };

  return (
    <span
      className={`px-2.5 py-1 text-xs rounded-lg border ${colors[confidence]}`}
    >
      {confidence}
    </span>
  );
}
