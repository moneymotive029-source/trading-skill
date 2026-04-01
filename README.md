# Financial Intelligence Trading Agent

**The most comprehensive AI-powered trading analysis system on Claude Code.**

Professional-grade multi-agent trading system that orchestrates 10 specialized AI agents to deliver explicit trading signals with technical, fundamental, sentiment, and macro analysis.

![Trading Dashboard](https://img.shields.io/badge/Status-Production_Ready-green)
![Assets](https://img.shields.io/badge/assets-crypto%2C%20stocks%2C%20forex%2C%20commodities-blue)
![License](https://img.shields.io/badge/license-MIT-yellow)

## Features

### Multi-Agent Architecture

10 specialized Python agents orchestrated by a master agent:

| Agent | Purpose |
|-------|---------|
| **Market Data** | Real-time prices, volume, support/resistance |
| **Technical Analysis** | RSI, MACD, Bollinger Bands, chart patterns |
| **Fundamental Analysis** | P/E, TVL, on-chain metrics, yield differentials |
| **Sentiment Analysis** | News sentiment, social media, fear/greed |
| **PESTLE Analysis** | Political, Economic, Social, Tech, Legal, Environmental |
| **News Monitor** | Catalysts, earnings, regulatory events |
| **Risk Management** | Kelly Criterion, VaR, CVaR, position sizing |
| **Signal Generator** | Multi-factor signal synthesis |
| **Portfolio Manager** | Correlation matrix, optimization |
| **Backtesting** | Walk-forward analysis, strategy grading |
| **Broker Execution** | Alpaca/Binance integration for live trading |
| **WebSocket Feed** | Real-time price streaming |

### Vercel Dashboard

Modern Next.js dashboard with:

- **Live Trading Signals** - Real-time signals from all agents
- **Detailed Analysis Modal** - Full breakdown of technicals, fundamentals, sentiment
- **Portfolio Overview** - P&L tracking, risk exposure, position summary
- **Live Price Feeds** - WebSocket/SSE streaming prices
- **Activity Feed** - New signals, alerts, updates
- **Automated Cron Updates** - 15-minute auto-refresh via Vercel Cron

### Asset Class Support

| Asset Class | Examples | Data Sources |
|-------------|----------|--------------|
| **Crypto** | BTC, ETH, SOL | CoinGecko, Binance |
| **Stocks** | AAPL, TSLA, NVDA | Yahoo Finance, Alpaca |
| **Forex** | EUR/USD, GBP/JPY | Central bank rates |
| **Commodities** | XAU/USD, Oil | COMEX, NYMEX |

## Quick Start

### Install Python Dependencies

```bash
cd agents
pip install -r requirements.txt
```

### Run the Trading Agent

```bash
# JSON output for dashboard/API
python financial_intelligence_trading_agent.py --symbol BTC --asset-class crypto --json

# Human-readable output
python financial_intelligence_trading_agent.py --symbol AAPL --asset-class stock

# WebSocket price feed
python websocket_price_feed.py --symbols BTC,ETH --feed binance

# Broker execution (paper trading)
python broker_execution_agent.py --broker alpaca --paper --symbol AAPL --side buy --qty 10
```

### Run the Dashboard

```bash
cd dashboard
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Deploy on Vercel

```bash
npm install -g vercel
cd dashboard
vercel deploy
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `PYTHON_ENABLED` | Set to `1` to enable Python runtime |
| `CRON_SECRET` | Secret token for cron authentication |
| `ALPACA_API_KEY` | Alpaca API key (for broker integration) |
| `ALPACA_API_SECRET` | Alpaca API secret |
| `BINANCE_API_KEY` | Binance API key |
| `BINANCE_API_SECRET` | Binance API secret |

## Usage with Claude Code

Install as a Claude Code skill:

```bash
# Clone to skills directory
git clone https://github.com/moneymotive029-source/trading-skill.git
cd trading-skill
cp -r . ~/.claude/skills/trading
```

Then use in Claude Code:

```bash
/trading Bitcoin
/trading BTC
/trading Apple stock
/trading AAPL
/trading EUR/USD
Should I buy Tesla?
Analyze gold for a swing trade
```

## Trading Signal Output

Every signal includes:

```markdown
## Trading Signal: Bitcoin (BTC/USD)

| Parameter | Value |
|-----------|-------|
| **Direction** | LONG |
| **Confidence** | High |
| **Timeframe** | Swing (3-7 days) |
| **Entry Zone** | $94,200 - $95,500 |
| **Stop Loss** | $91,800 (-2.8%) |
| **Take Profit 1** | $98,000 (+4.0%) |
| **Take Profit 2** | $102,000 (+8.5%) |
| **Risk/Reward** | 1:3.2 |

### Position Sizing
- **Kelly Criterion:** 4.2%
- **Recommended:** 2.1% (Half-Kelly for safety)

### Trade Thesis
Bitcoin breaking above key resistance with strong momentum...

### Key Risks
1. Regulatory headwinds
2. Exchange concentration risk
3. Liquidity gaps

### Invalidation
- Daily close below $91,800
```

## Project Structure

```
trading-skill/
├── agents/
│   ├── financial_intelligence_trading_agent.py  # Master orchestrator
│   ├── market_data_agent.py
│   ├── technical_analysis_agent.py
│   ├── fundamental_analysis_agent.py
│   ├── sentiment_analysis_agent.py
│   ├── pestle_analysis_agent.py
│   ├── news_monitor_agent.py
│   ├── risk_management_agent.py
│   ├── signal_generator_agent.py
│   ├── portfolio_manager_agent.py
│   ├── backtesting_agent.py
│   ├── broker_execution_agent.py        # Live trading
│   ├── websocket_price_feed.py          # Real-time streaming
│   └── requirements.txt
├── dashboard/
│   ├── src/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   ├── signals/route.ts
│   │   │   │   ├── analyze/route.ts
│   │   │   │   ├── ws/prices/route.ts
│   │   │   │   └── cron/signals/route.ts
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   └── components/
│   │       ├── signal-table.tsx
│   │       ├── analysis-detail.tsx
│   │       ├── live-prices.tsx
│   │       └── ...
│   ├── package.json
│   ├── vercel.json
│   └── README.md
├── evals/
│   └── evals.json
├── references/
│   ├── pestle-framework.md
│   └── position-sizing.md
├── CLAUDE.md
├── SKILL.md
├── LICENSE
└── README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/signals` | GET | Get all trading signals |
| `/api/signals` | POST | Get signal for specific symbol |
| `/api/analyze` | POST | Run full multi-agent analysis |
| `/api/ws/prices` | GET | WebSocket/SSE price stream |
| `/api/cron/signals` | GET | Scheduled signal refresh (Cron) |

## Broker Integration

### Supported Brokers

- **Alpaca** - Stocks/ETFs (paper + live trading)
- **Binance** - Crypto (testnet + live)
- **Interactive Brokers** - Coming soon

### Example: Submit Order

```bash
# Alpaca paper trading
python broker_execution_agent.py \
  --broker alpaca \
  --paper \
  --api-key $ALPACA_KEY \
  --api-secret $ALPACA_SECRET \
  --symbol AAPL \
  --side buy \
  --qty 10 \
  --type market
```

## Risk Disclaimer

**This software is for educational and informational purposes only.**

- Trading involves substantial risk of loss
- Past performance does not guarantee future results
- Never risk more than you can afford to lose
- Consult with a licensed financial advisor before trading
- The authors are not responsible for any trading losses

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Areas for improvement:

- Additional broker integrations (IBKR, TD Ameritrade)
- Options/futures support
- Advanced backtesting features
- Machine learning signal enhancement
- Mobile app integration

## Acknowledgments

Built with:
- [Next.js](https://nextjs.org/)
- [Vercel Functions](https://vercel.com/docs/functions)
- [Python](https://python.org/)
- [Claude Code](https://claude.ai/code)
