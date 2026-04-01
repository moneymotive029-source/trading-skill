# Trading Dashboard

Next.js dashboard for the Financial Intelligence Trading Agent.

## Features

- **Live Trading Signals** - Real-time signals from multi-agent AI analysis
- **Detailed Analysis** - Click "Analyze" to see full breakdown:
  - Technical indicators (RSI, MACD, Moving Averages, Bollinger Bands)
  - Fundamental metrics
  - Sentiment analysis
  - PESTLE+ factors
  - Risk metrics (VaR, CVaR, Kelly position sizing)
- **Portfolio Overview** - Track total value, P&L, positions, and risk exposure
- **Activity Feed** - Stay updated on new signals and alerts
- **Automated Cron Updates** - Signals refresh every 15 minutes via Vercel Cron

## Getting Started

### Install dependencies

```bash
npm install
```

### Run development server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Deploy on Vercel

```bash
npm install -g vercel
vercel deploy
```

### Environment Variables

Set these in Vercel dashboard:

| Variable | Description |
|----------|-------------|
| `PYTHON_ENABLED` | Set to `1` to enable Python runtime |
| `CRON_SECRET` | Secret token for cron authentication |

## Project Structure

```
dashboard/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   ├── signals/route.ts    # GET/POST signals
│   │   │   ├── analyze/route.ts    # Run Python agent
│   │   │   └── cron/signals/route.ts  # Scheduled updates
│   │   ├── layout.tsx
│   │   └── page.tsx                # Main dashboard
│   └── components/
│       ├── ui/card.tsx
│       ├── signal-badge.tsx
│       ├── signal-table.tsx
│       ├── asset-search.tsx
│       ├── portfolio-overview.tsx
│       ├── activity-feed.tsx
│       └── analysis-detail.tsx     # Full analysis modal
├── vercel.json                     # Vercel config + cron
└── package.json
```

## Integration with Python Agents

The dashboard calls the Python trading agents via subprocess:

```ts
// src/app/api/analyze/route.ts
import { spawn } from "child_process";

const pythonProcess = spawn("python", [
  "../../agents/financial_intelligence_trading_agent.py",
  "--symbol", symbol,
  "--asset-class", assetClass,
]);
```

On Vercel, Python runtime is enabled via `vercel.json`:

```json
{
  "functions": {
    "src/app/api/analyze/route.ts": {
      "runtime": "python3.9",
      "maxDuration": 60
    }
  }
}
```

## Cron Jobs

Signals auto-refresh every 15 minutes:

```json
{
  "crons": [
    {
      "path": "/api/cron/signals",
      "schedule": "0 */15 * * * *"
    }
  ]
}
```

The cron job:
1. Authenticates via `CRON_SECRET`
2. Runs analysis on all tracked assets
3. Stores results (integrate with DB in production)
4. Triggers alerts for high-conviction signals
