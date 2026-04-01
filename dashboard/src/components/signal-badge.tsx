export function SignalBadge({ signal }: { signal: "LONG" | "SHORT" | "NEUTRAL" }) {
  const colors = {
    LONG: "bg-green-500/20 text-green-400 border-green-500/30",
    SHORT: "bg-red-500/20 text-red-400 border-red-500/30",
    NEUTRAL: "bg-slate-500/20 text-slate-400 border-slate-500/30",
  };

  return (
    <span
      className={`px-2.5 py-0.5 text-xs font-medium rounded-full border ${colors[signal]}`}
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
    High: "bg-emerald-500/20 text-emerald-400",
    Medium: "bg-yellow-500/20 text-yellow-400",
    Low: "bg-slate-500/20 text-slate-400",
  };

  return (
    <span
      className={`px-2 py-0.5 text-xs rounded-full ${colors[confidence]}`}
    >
      {confidence} confidence
    </span>
  );
}
