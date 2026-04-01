"use client";

const activities = [
  {
    id: 1,
    type: "signal",
    message: "New LONG signal on BTC/USD",
    time: "2m ago",
    color: "green",
  },
  {
    id: 2,
    type: "alert",
    message: "AAPL hit entry zone ($228-230)",
    time: "8m ago",
    color: "red",
  },
  {
    id: 3,
    type: "update",
    message: "EUR/USD analysis refreshed",
    time: "15m ago",
    color: "blue",
  },
  {
    id: 4,
    type: "signal",
    message: "XAU/USD moved to NEUTRAL",
    time: "32m ago",
    color: "slate",
  },
  {
    id: 5,
    type: "risk",
    message: "Portfolio VaR updated: $4,200",
    time: "1h ago",
    color: "yellow",
  },
];

const colors = {
  green: "text-green-400",
  red: "text-red-400",
  blue: "text-blue-400",
  slate: "text-slate-400",
  yellow: "text-yellow-400",
};

export function ActivityFeed() {
  return (
    <div className="space-y-4">
      {activities.map((activity) => (
        <div key={activity.id} className="flex items-start gap-3">
          <div
            className={`w-2 h-2 rounded-full mt-2 ${colors[activity.color as keyof typeof colors]}`}
          />
          <div className="flex-1">
            <p className="text-sm text-slate-300">{activity.message}</p>
            <p className="text-xs text-slate-500 mt-0.5">{activity.time}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
