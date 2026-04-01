# Trading Skill - Development Guidelines

## Project Overview

This is a comprehensive trading analysis skill for Claude Code that provides professional-grade market analysis and explicit trading signals for multiple asset classes (crypto, stocks, forex, commodities).

## Architecture

### Core Components

```
trading-skill/
├── SKILL.md                 # Main skill definition (entry point)
├── agents/                  # Specialized analysis agents
│   ├── market-data-agent.md
│   ├── technical-analysis-agent.md
│   ├── fundamental-analysis-agent.md
│   ├── sentiment-analysis-agent.md
│   ├── pestle-analysis-agent.md
│   ├── risk-management-agent.md
│   ├── signal-generator-agent.md
│   ├── news-monitor-agent.md
│   ├── backtesting-agent.md
│   └── portfolio-manager-agent.md
├── references/              # Framework documentation
│   ├── pestle-framework.md
│   └── position-sizing.md
└── evals/                   # Test cases
    └── evals.json
```

### Agent Workflow

```
User Request (/trading BTC)
       ↓
┌─────────────────────────────────────┐
│  SKILL.md (orchestrates analysis)  │
└─────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────────────┐
│  1. market-data-agent → Price, volume, levels       │
│  2. technical-analysis-agent → Indicators, patterns │
│  3. fundamental-analysis-agent → Metrics, valuation │
│  4. sentiment-analysis-agent → Positioning, flows   │
│  5. pestle-analysis-agent → Macro factors           │
│  6. news-monitor-agent → Catalysts, events          │
└──────────────────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────────────────┐
│  7. risk-management-agent → Position sizing, stops │
│  8. signal-generator-agent → Synthesize all inputs │
└─────────────────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────────────────┐
│  Final Output: Trading Signal with entry, exit,    │
│  position size, thesis, and risk disclosure         │
└─────────────────────────────────────────────────────┘
```

## Development Principles

### 1. Analysis Quality

- **Multi-source verification**: Always cross-reference data from 2+ sources
- **Timestamp everything**: Market data must be current (<15 min for crypto, <1 day for stocks)
- **Explicit signals**: Never vague - always provide specific entry, stop, targets
- **Risk-first**: Every trade must have defined risk parameters before entry

### 2. Agent Design

Each agent must include:
- Clear `name` and `description` in YAML frontmatter
- Defined `Role` section
- `Responsibilities` list
- `Output Format` template (markdown tables)
- `Quality Checks` checklist
- `Example Invocation`

### 3. Data Sources

**Always prefer primary sources:**
- Crypto: CoinGecko, CoinMarketCap, Glassnode, DefiLlama
- Stocks: SEC EDGAR, Yahoo Finance, company investor relations
- Forex: Central bank websites, FRED, Trading Economics
- Commodities: EIA, USDA, CME Group

### 4. Risk Management

**Non-negotiable rules:**
- Every trade must have stop loss at technical level (not arbitrary %)
- Risk/reeward must be >= 1:2 (or explain why)
- Position size must be calculated (Kelly + fixed fractional)
- Correlation must be checked against existing positions
- Maximum 1-2% portfolio risk per trade

### 5. Disclaimer Requirements

**ALWAYS include at the end of any analysis:**

```markdown
---
**Disclaimer:** This analysis is for informational purposes only and does not 
constitute financial advice. Trading involves substantial risk of loss. Past 
performance does not guarantee future results. Always do your own research and 
consult with a licensed financial advisor before making investment decisions.
```

## Testing

### Running Tests

Test prompts are in `evals/evals.json`. To test the skill:

1. Install locally: `cp -r trading-skill ~/.claude/skills/trading`
2. Restart Claude Code
3. Run test prompts:
   - `/trading Bitcoin`
   - `Should I buy Apple stock?`
   - `Analyze EUR/USD for a swing trade`

### Expected Outputs

Each test should produce:
- Current market data with timestamp
- Technical analysis with indicator values
- Fundamental analysis with asset-specific metrics
- PESTLE+ scorecard
- Sentiment analysis with quantitative readings
- **Explicit trading signal** (direction, entry, stop, targets)
- Position sizing calculation
- Risk disclosure

## Code Style

### Markdown Formatting

- Use tables for structured data
- Use code blocks for formulas
- Use bold for emphasis on key values
- Include source links at end of each analysis

### Agent Templates

```markdown
---
name: agent-name
description: Clear, specific description of what agent does
---

# Agent Name

## Role

[Clear statement of responsibility]

## Responsibilities

1. **Category** - Description
2. **Category** - Description

## Output Format

[Markdown template with tables]

## Quality Checks

- [ ] Check 1
- [ ] Check 2

## Example Invocation

[Example task and expected output]
```

## Key Decisions

### Why Multiple Agents?

Separating concerns allows:
- Specialized expertise per domain
- Parallel execution when possible
- Easier testing and debugging
- Reusability across different analysis types

### Why PESTLE+?

Standard PESTLE + Sentiment + Technical provides:
- Comprehensive macro coverage
- Quantifiable scoring system
- Asset-class agnostic framework
- Clear signal generation

### Why Kelly Criterion?

- Mathematically optimal bet sizing
- Accounts for both win rate and payoff ratio
- Fractional Kelly reduces volatility
- Provides upper bound for position size

## Future Enhancements

Potential additions:
- Real-time price API integration
- Automated backtesting with historical data
- Portfolio optimization algorithms
- Machine learning signal enhancement
- Options flow analysis agent
- On-chain analysis agent (crypto-specific)

## Contact

Repository: https://github.com/moneymotive029-source/trading-skill
