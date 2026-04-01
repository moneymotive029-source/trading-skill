# PESTLE+ Analysis Framework for Trading

## Overview

PESTLE+ is a strategic analysis framework that evaluates macro-environmental factors affecting asset prices. The "+" adds Sentiment and Technical factors to the traditional six.

## Factor Breakdown

### Political (P)

**What to analyze:**
- Government stability and policy continuity
- Trade policies and tariffs
- Geopolitical tensions and conflicts
- Election cycles and outcomes
- Regulatory body compositions

**Trading implications:**
| Event | Typical Impact |
|-------|----------------|
| Trade war escalation | Risk-off, USD up, EM down |
| Election uncertainty | Volatility up, defensive sectors outperform |
| Regulatory crackdown | Sector-specific selloffs |
| Geopolitical crisis | Oil up, gold up, equities down |

**Data sources:**
- Reuters Politics, Bloomberg Government
- Official government statements
- Think tank reports

### Economic (E)

**What to analyze:**
- GDP growth rates and revisions
- Inflation (CPI, PCE, PPI)
- Employment data (NFP, unemployment rate)
- Central bank policy (rates, QE/QT)
- Yield curve shape and movements
- Currency strength (DXY for USD)

**Trading implications:**
| Indicator | Bullish for | Bearish for |
|-----------|-------------|-------------|
| Rising rates | USD, financials | Growth stocks, gold |
| High inflation | Commodities, TIPS | Bonds, growth stocks |
| Recession signals | Defensive sectors, USD | Cyclical stocks, EM |
| Yield curve inversion | Bonds | Banks, equities |

**Data sources:**
- FRED Economic Data
- Central bank websites (Fed, ECB, BOJ)
- Trading Economics

### Social (S)

**What to analyze:**
- Demographic shifts (aging populations)
- Consumer behavior changes
- Income inequality trends
- Urbanization rates
- Education levels

**Trading implications:**
- Aging Japan → healthcare stocks, bond demand
- Millennial wealth transfer → crypto adoption
- Remote work trend → commercial real estate headwinds

**Data sources:**
- Census bureaus
- Pew Research
- Consumer survey data

### Technological (T)

**What to analyze:**
- Disruptive innovation adoption curves
- R&D spending trends
- Patent filings
- Tech transfer policies
- Digital infrastructure development

**Trading implications:**
| Trend | Beneficiaries | Losers |
|-------|---------------|--------|
| AI adoption | NVDA, MSFT, cloud | Traditional software |
| EV transition | TSLA, lithium miners | Oil, ICE automakers |
| Fintech | Digital payments | Traditional banks |

**Data sources:**
- WIPO patent database
- Industry research reports
- Gartner hype cycles

### Legal (L)

**What to analyze:**
- Regulatory changes pending
- Major litigation outcomes
- Compliance requirements
- Intellectual property rulings
- Antitrust actions

**Trading implications:**
- Crypto regulation → exchange compliance costs
- Pharma patents → generic competition cliffs
- Antitrust → big tech breakup risk

**Data sources:**
- SEC filings (10-K risk factors)
- Court dockets
- Regulatory agency announcements

### Environmental (E)

**What to analyze:**
- Climate policy changes
- Carbon pricing mechanisms
- Resource scarcity indicators
- Natural disaster frequency
- ESG investment flows

**Trading implications:**
| Policy | Winners | Losers |
|--------|---------|--------|
| Carbon tax | Renewables, nuclear | Coal, oil |
| Water restrictions | Water tech | Agriculture, beverages |
| Mining bans | Recycling | Commodity producers |

**Data sources:**
- EPA reports
- IEA energy outlook
- Climate risk models

### + Sentiment

**What to analyze:**
- News sentiment (positive/negative ratio)
- Social media sentiment
- Analyst rating changes
- Positioning data (COT, short interest)
- Flow data (ETF inflows/outflows)

**Quantitative measures:**
| Metric | Interpretation |
|--------|----------------|
| RSI < 30 | Oversold, potential bounce |
| Put/Call > 1.2 | Bearish extreme, contrarian buy |
| Short interest > 20% | Squeeze potential |
| AAII bulls < 25% | Contrarian bullish |

**Data sources:**
- Sentiment analysis APIs
- CFTC COT reports
- ETF flow trackers

### + Technical

**What to analyze:**
- Price trends (higher highs/lows)
- Volume patterns
- Key support/resistance levels
- Moving average relationships
- Momentum indicators

**Key levels to identify:**
- 52-week highs/lows
- All-time highs (for crypto)
- Major round numbers
- Fibonacci retracement levels
- Volume nodes (VWAP, POC)

## Integration with Trading Signals

### Step 1: Factor Scoring

Score each factor from -2 to +2:
- **-2**: Strongly negative for asset
- **-1**: Moderately negative
- **0**: Neutral / mixed signals
- **+1**: Moderately positive
- **+2**: Strongly positive

### Step 2: Weighted Composite

Not all factors are equally important for every asset:

| Asset Class | Primary Factors | Secondary Factors |
|-------------|-----------------|-------------------|
| **Growth Stocks** | Economic, Technological | Legal, Sentiment |
| **Value Stocks** | Economic, Political | Environmental |
| **Crypto** | Political, Legal, Sentiment | Economic |
| **Forex** | Economic, Political | Social |
| **Commodities** | Environmental, Economic | Political |

### Step 3: Signal Generation

**Composite Score Interpretation:**

| Score | Action |
|-------|--------|
| +8 to +10 | Strong Buy |
| +5 to +7 | Buy |
| +2 to +4 | Cautious Buy |
| -1 to +1 | Neutral / Wait |
| -2 to -4 | Cautious Sell |
| -5 to -7 | Sell |
| -8 to -10 | Strong Sell |

## Example Analysis Template

```markdown
### PESTLE+ Scorecard: [Asset]

| Factor | Score | Rationale |
|--------|-------|-----------|
| Political | +1 | Stable government, no major policy risks |
| Economic | +2 | Rate cuts expected, growth accelerating |
| Social | 0 | Neutral demographics |
| Technological | +2 | AI tailwind, strong R&D pipeline |
| Legal | -1 | Antitrust overhang |
| Environmental | +1 | ESG-friendly operations |
| Sentiment | +1 | Improving analyst revisions |
| Technical | +2 | Breaking out above resistance |
| **Composite** | **+8** | **Strong Buy** |
```

## Updating PESTLE+ Over Time

Re-evaluate factors when:
- Major news events occur
- Economic data surprises
- Earnings releases
- Central bank meetings
- Technical breakouts/breakdowns

Track score changes to identify inflection points.
