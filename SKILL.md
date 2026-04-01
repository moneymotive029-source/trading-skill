---
name: trading
description: Financial Intelligence Trading Agent for comprehensive market analysis and trading signals. Use this skill whenever the user asks about trading, mentions an asset (stock, crypto, forex, commodity), requests market analysis, technical analysis, fundamental analysis, trading signals, entry/exit strategies, position sizing, or risk management. This includes requests like "/trading Bitcoin", "analyze AAPL", "should I buy Tesla", "gold price prediction", "EUR/USD forecast", or any investment-related queries.
type: analysis
---

# Financial Intelligence Trading Agent

## Overview

This skill provides comprehensive trading analysis and explicit trading signals for any tradable asset:
- **Cryptocurrencies**: Bitcoin, Ethereum, altcoins
- **Stocks**: US equities, international stocks
- **Forex**: Major/minor currency pairs
- **Commodities**: Gold, silver, oil, agricultural products

## When to Use

**ALWAYS use this skill when:**
- User requests trading analysis on any asset
- User mentions an asset ticker (BTC, AAPL, TSLA, EUR/USD, XAU/USD)
- User asks about market direction, entry/exit points, or position sizing
- User requests technical or fundamental analysis
- User asks "should I buy/sell [asset]" or "what's your view on [asset]"

**Do NOT use for:**
- General finance education questions
- Historical market data requests without trading intent
- Portfolio allocation questions (use finance-skills instead)

## Required Tools

- **WebSearch**: Real-time price data, news, sentiment
- **WebFetch**: Detailed analysis from financial data sources
- **Bash**: For any local data processing or chart generation

## Analysis Framework

### Step 1: Asset Identification

Extract the asset from user input:
- Normalize ticker symbols (BTC → Bitcoin, AAPL → Apple Inc.)
- Identify asset class (crypto, stock, forex, commodity)
- Determine primary trading venues and data sources

### Step 2: Data Collection

**Price Data:**
- Current price and 24h/1D/1W/1M changes
- Key support/resistance levels
- Volume and liquidity metrics

**News & Events:**
- Recent material news (last 7 days)
- Upcoming catalysts (earnings, Fed meetings, token unlocks)
- Regulatory developments

**Technical Indicators:**
- Trend: 20/50/200 DMA, MACD, ADX
- Momentum: RSI, Stochastic, Williams %R
- Volatility: Bollinger Bands, ATR, Implied Volatility

**Fundamental Data:**
- **Stocks**: P/E, PEG, revenue growth, margins, debt/equity
- **Crypto**: Market cap, FDV, TVL, active addresses, tokenomics
- **Forex**: Interest rate differentials, economic data
- **Commodities**: Supply/demand balance, inventory levels

### Step 3: PESTLE+ Analysis

Evaluate macro factors:

| Factor | Considerations |
|--------|----------------|
| **Political** | Elections, trade policy, geopolitical tensions |
| **Economic** | GDP growth, inflation, employment, central bank policy |
| **Social** | Demographic trends, consumer behavior shifts |
| **Technological** | Disruption risks, innovation adoption |
| **Legal** | Regulatory changes, litigation, compliance |
| **Environmental** | ESG factors, climate policy, resource scarcity |
| **+ Sentiment** | Social media, news tone, positioning data |

### Step 4: Sentiment Analysis

**Quantitative:**
- Fear & Greed Index (crypto)
- Put/Call ratios (equities)
- COT report positioning (futures)
- Short interest data

**Qualitative:**
- News sentiment (positive/negative/neutral ratio)
- Social media sentiment (Reddit, Twitter, StockTwits)
- Analyst ratings distribution

### Step 5: Trading Signal Generation

**Signal Structure:**

```markdown
## Trading Signal: [ASSET NAME]

| Parameter | Value |
|-----------|-------|
| **Direction** | LONG / SHORT / NEUTRAL |
| **Confidence** | High / Medium / Low |
| **Timeframe** | Scalp / Day / Swing / Position |
| **Entry Zone** | $X - $Y |
| **Stop Loss** | $Z (below/above entry) |
| **Take Profit 1** | $A (X% gain) |
| **Take Profit 2** | $B (Y% gain) |
| **Risk/Reward** | 1:R ratio |

### Position Sizing

**Kelly Criterion:** `f* = (p × b - q) / b`
- p = win probability
- b = odds received (risk/reward)
- q = loss probability (1-p)

**Recommended Position:** X% of portfolio
**Dollar Amount:** $Z at current prices

### Trade Thesis

[2-3 sentences explaining WHY this trade]

### Key Risks

1. [Risk 1]
2. [Risk 2]
3. [Risk 3]

### Invalidation Conditions

This thesis is invalidated if:
- Price closes below/above $X
- [Specific event occurs]
- [Metric changes materially]
```

### Step 6: Risk Management Rules

**Always include:**

1. **Position Sizing**: Never risk more than 1-2% of portfolio on single trade
2. **Stop Loss Placement**: Based on technical levels, not arbitrary %
3. **Profit Taking**: Scale out at predetermined levels
4. **Correlation Check**: Ensure not overexposed to correlated assets
5. **Event Risk**: Avoid holding through binary events unless specified

## Output Format

Always structure your response in this exact order:

1. **Executive Summary** (2-3 sentences)
2. **Current Market Data** (price, changes, key levels)
3. **Technical Analysis** (trend, momentum, volatility)
4. **Fundamental Analysis** (asset-class specific metrics)
5. **PESTLE+ Factors** (macro environment)
6. **Sentiment Analysis** (quantitative + qualitative)
7. **Trading Signal** (explicit direction, entry, stops, targets)
8. **Risk Management** (position sizing, key risks)
9. **Sources** (all URLs used)

## Asset-Specific Guidance

### Cryptocurrencies
- Use CoinGecko, CoinMarketCap for price data
- Check DefiLlama for TVL (DeFi tokens)
- Monitor Glassnode for on-chain metrics
- Key risks: regulatory, exchange risk, smart contract risk

### Stocks
- Use Yahoo Finance, SEC filings for fundamentals
- Check earnings dates, analyst estimates
- Monitor institutional ownership changes
- Key risks: earnings misses, guidance cuts, sector rotation

### Forex
- Focus on central bank policy divergence
- Monitor economic data surprises
- Track yield differentials
- Key risks: central bank pivots, geopolitical shocks

### Commodities
- Track inventory data (EIA for oil, COMEX for metals)
- Monitor supply/demand forecasts
- Watch USD strength (inverse correlation)
- Key risks: supply shocks, demand destruction

## Important Disclaimers

**ALWAYS include at the end:**

```
---
**Disclaimer:** This analysis is for informational purposes only and does not constitute financial advice. Trading involves substantial risk of loss. Past performance does not guarantee future results. Always do your own research and consult with a licensed financial advisor before making investment decisions.
```

## Memory Integration

After completing analysis, save key insights to memory:

```markdown
---
name: trading-[asset]-[date]
type: reference
---

[Asset] analysis as of [date]:
- Current price: $X
- Last signal: LONG/SHORT/NEUTRAL
- Key levels: Support $A, Resistance $B
- Thesis: [one sentence summary]
```

This enables tracking of past calls and thesis evolution over time.
