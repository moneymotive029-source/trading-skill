# Trading Skill for Claude Code

A comprehensive Financial Intelligence Trading Agent for Claude Code that provides professional-grade market analysis and explicit trading signals.

## Features

- **Multi-Asset Support**: Cryptocurrencies, Stocks, Forex, Commodities
- **Comprehensive Analysis**: Technical, Fundamental, PESTLE+ macro factors
- **Explicit Trading Signals**: Clear direction, entry zones, stops, and targets
- **Position Sizing**: Kelly Criterion and risk-based position calculations
- **Risk Management**: Stop loss strategies, take profit levels, correlation checks

## Installation

### Option 1: Clone to Skills Directory

```bash
git clone https://github.com/YOUR_USERNAME/trading-skill.git
cd trading-skill
cp -r . ~/.claude/skills/trading
```

### Option 2: Manual Install

1. Download this repository
2. Copy the `trading` folder to `~/.claude/skills/`
3. Restart Claude Code

## Usage

Once installed, the skill activates automatically when you ask about trading or mention assets:

```bash
/trading Bitcoin
/trading BTC
/trading Apple stock
/trading AAPL
/trading EUR/USD
/trading Gold
/trading XAU/USD
```

You can also use natural language:
- "Should I buy Tesla?"
- "Analyze Bitcoin for a swing trade"
- "What's your view on gold?"
- "Best position size for a $50k portfolio trading ETH?"

## Output Structure

Every analysis includes:

1. **Executive Summary** - Quick take on the asset
2. **Current Market Data** - Price, changes, key levels
3. **Technical Analysis** - Trend, momentum, volatility indicators
4. **Fundamental Analysis** - Asset-specific metrics (P/E for stocks, TVL for crypto, etc.)
5. **PESTLE+ Factors** - Political, Economic, Social, Technological, Legal, Environmental, Sentiment
6. **Sentiment Analysis** - Quantitative and qualitative sentiment data
7. **Trading Signal** - Explicit LONG/SHORT/NEUTRAL with entry, stop, targets
8. **Risk Management** - Position sizing, key risks, invalidation conditions
9. **Sources** - All data sources used

## Example Output

```markdown
## Trading Signal: Bitcoin (BTC/USD)

| Parameter | Value |
|-----------|-------|
| **Direction** | LONG |
| **Confidence** | Medium |
| **Timeframe** | Swing (3-7 days) |
| **Entry Zone** | $67,000 - $68,500 |
| **Stop Loss** | $64,200 (-5.2%) |
| **Take Profit 1** | $72,000 (+6.5%) |
| **Take Profit 2** | $75,500 (+11.2%) |
| **Risk/Reward** | 1:2.3 |

### Position Sizing

**Recommended Position:** 2.5% of portfolio
**Kelly Criterion:** 3.1% (using 55% win rate, 2.3:1 R/R)

### Trade Thesis

Bitcoin is breaking above the 50-day MA with improving on-chain metrics. 
ETF inflows remain positive and the technical setup suggests a move to 
$72k+ if $69k resistance clears.

### Key Risks

1. Mt. Gox repayment overhang
2. Strong USD headwind
3. Weekend liquidity gaps

### Invalidation

This thesis is invalidated if:
- Price closes below $64,200 on daily timeframe
- ETF flows turn negative for 3+ consecutive days
```

## Reference Documentation

The skill includes bundled reference files:

- `references/pestle-framework.md` - Complete PESTLE+ analysis methodology
- `references/position-sizing.md` - Position sizing methods and risk management

## Test Cases

Run these to validate the skill is working:

```bash
# In Claude Code with the skill installed
/trading Bitcoin
/trading AAPL
Analyze EUR/USD for a swing trade
What's your view on gold?
```

## Disclaimer

**This skill provides analysis and educational content only. It does not constitute financial advice.**

Trading involves substantial risk of loss. Past performance does not guarantee future results. Always:
- Do your own research
- Consult with a licensed financial advisor
- Never risk more than you can afford to lose
- Use proper position sizing and risk management

## Development

### Directory Structure

```
trading-skill/
├── SKILL.md              # Main skill definition
├── README.md             # This file
├── evals/
│   └── evals.json        # Test prompts for evaluation
└── references/
    ├── pestle-framework.md    # PESTLE+ analysis guide
    └── position-sizing.md     # Risk management guide
```

### Improving the Skill

To test and improve the skill:

1. Run test prompts from `evals/evals.json`
2. Compare outputs against expected results
3. Update `SKILL.md` based on findings
4. Add new test cases for edge cases discovered

## License

MIT License - Feel free to use, modify, and distribute.

## Contributing

Contributions welcome! Areas for improvement:
- Additional asset class support (bonds, options, futures)
- Backtesting integration
- Portfolio correlation analysis
- Real-time alert system
