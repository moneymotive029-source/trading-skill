# Position Sizing and Risk Management

## Core Principles

### The 1-2% Rule

**Never risk more than 1-2% of your total portfolio on a single trade.**

This is the golden rule that keeps you alive long enough to compound.

**Calculation:**
```
Risk Amount = Portfolio Value × Risk %
Position Size = Risk Amount / (Entry Price - Stop Loss)
```

**Example:**
- Portfolio: $100,000
- Risk per trade: 1% = $1,000
- Entry: $50, Stop Loss: $45
- Position Size: $1,000 / ($50 - $45) = 200 shares
- Dollar Position: 200 × $50 = $10,000 (10% of portfolio)

### Kelly Criterion

**Formula:**
```
f* = (p × b - q) / b

Where:
- f* = fraction of capital to bet
- p = probability of winning
- q = probability of losing (1 - p)
- b = net odds received (profit/loss ratio)
```

**Example:**
- Win rate: 55% (p = 0.55)
- Risk/Reward: 1:2 (b = 2)
- f* = (0.55 × 2 - 0.45) / 2 = 0.325 = 32.5%

**Fractional Kelly:**
Most traders use 1/2 or 1/4 Kelly to reduce volatility:
- Half-Kelly: 32.5% / 2 = 16.25%
- Quarter-Kelly: 32.5% / 4 = 8.125%

### Risk of Ruin

**Formula:**
```
Risk of Ruin = ((1 - Edge) / (1 + Edge)) ^ N

Where:
- Edge = win rate - (1 - win rate)
- N = number of trades to ruin threshold
```

**Key insight:** Even with an edge, oversized positions lead to ruin.

## Position Sizing Methods

### 1. Fixed Fractional

Risk a fixed % of current equity on each trade.

**Pros:** Simple, automatically adjusts to account size
**Cons:** Can lead to overtrading in small accounts

```python
def fixed_fractional(equity, risk_pct, entry, stop):
    risk_amount = equity * (risk_pct / 100)
    risk_per_share = entry - stop
    shares = risk_amount / risk_per_share
    return int(shares)
```

### 2. Fixed Ratio

Increase position size by fixed amount for each "delta" of profits.

**Pros:** Accelerates growth during winning streaks
**Cons:** Can give back profits quickly

### 3. Volatility-Adjusted

Size positions based on asset volatility (ATR).

```python
def volatility_adjusted(equity, risk_pct, atr, multiplier=2):
    risk_amount = equity * (risk_pct / 100)
    stop_distance = atr * multiplier
    shares = risk_amount / stop_distance
    return int(shares)
```

**Pros:** Equalizes risk across volatile and stable assets
**Cons:** Reduces position size in high volatility (may miss opportunities)

### 4. Optimal f

Mathematical optimization based on historical trade distribution.

**Pros:** Maximizes geometric growth
**Cons:** Requires large sample size, sensitive to outliers

## Stop Loss Strategies

### Technical Stop Losses

| Method | Placement | Best For |
|--------|-----------|----------|
| **Support/Resistance** | Below support (long) / Above resistance (short) | Swing trading |
| **Moving Average** | Below key MA (20/50/200 DMA) | Trend following |
| **ATR-Based** | Entry - (ATR × multiplier) | Volatile assets |
| **Percentage** | Fixed % below entry | Simple rules-based |
| **Volatility** | Below Bollinger Band | Mean reversion |

### Stop Loss Psychology

**Common mistakes:**
- Moving stops wider (hope)
- Moving stops tighter (fear)
- No stop at all (denial)

**Best practices:**
- Set stop BEFORE entering trade
- Make stop logical (technical level), not arbitrary
- Document invalidation thesis
- Accept that stops = insurance, not failure

## Take Profit Strategies

### Scaling Out

**Example structure:**
| Target | % of Position | R Multiple |
|--------|---------------|------------|
| TP1 | 25% | 1R |
| TP2 | 25% | 2R |
| TP3 | 25% | 3R |
| Runner | 25% | Trail |

**Benefits:**
- Locks in profits
- Reduces regret if price reverses
- Lets winners run with portion

### Trailing Stops

**Methods:**
- **Fixed % trail:** Trail by X% from high
- **ATR trail:** Trail by ATR × multiplier
- **Moving average:** Exit when price closes below MA
- **Parabolic SAR:** Use SAR indicator

### Risk-Free Trades

After price reaches 1R or 2R, move stop to breakeven.

**Pros:** Eliminates risk of winner turning into loser
**Cons:** May get stopped out before continuation

## Correlation and Portfolio Risk

### Position Correlation Matrix

Avoid multiple positions with >0.7 correlation.

**Example:**
| Position | Correlation to BTC |
|----------|-------------------|
| ETH | 0.85 |
| SOL | 0.78 |
| Gold | 0.15 |
| USD Index | -0.65 |

**Rule:** If holding BTC, reduce or skip ETH position.

### Total Portfolio Risk

**Maximum risk exposure:**
- Single position: 1-2%
- Single sector: 5-6%
- Total portfolio at risk: 10-15%

### Leverage Considerations

**Leverage multiplies both gains AND losses:**

```
Effective Risk = Position Risk × Leverage
```

**Example:**
- 3x leverage on 2% risk = 6% effective risk
- This exceeds safe limits for most traders

**Leverage guidelines:**
| Account Size | Max Leverage |
|--------------|--------------|
| <$10k | 1-2x |
| $10k-$100k | 2-3x |
| $100k+ | 3-5x |

## Risk Management Checklist

Before entering ANY trade:

- [ ] Defined entry zone
- [ ] Defined stop loss level
- [ ] Defined take profit target(s)
- [ ] Calculated position size
- [ ] Checked correlation with existing positions
- [ ] Verified no major events (earnings, Fed) before exit
- [ ] Documented trade thesis
- [ ] Set alert for stop/target levels

## Drawdown Management

### Drawdown Stages

| Drawdown | Action |
|----------|--------|
| 5% | Review recent trades, no action needed |
| 10% | Reduce position sizes by 25% |
| 15% | Reduce position sizes by 50%, pause new trades |
| 20% | Stop trading, full strategy review |

### Recovery Math

**To recover from drawdown:**

| Loss | Gain Needed to Recover |
|------|------------------------|
| 10% | 11% |
| 20% | 25% |
| 30% | 43% |
| 40% | 67% |
| 50% | 100% |

**Key insight:** Losses hurt more than gains help. Protect capital first.

## Trade Journal Template

```markdown
## Trade Log: [Asset] - [Date]

| Field | Value |
|-------|-------|
| Direction | Long / Short |
| Entry | $X |
| Stop Loss | $Y |
| Target | $Z |
| Position Size | N shares |
| Risk % | X% |
| R Multiple | 1:R |

### Thesis
[Why this trade?]

### Outcome
- Exit price: $X
- P&L: $Y (Z%)
- R realized: N

### Lessons
[What worked, what didn't]
```

## Emergency Exits

**Exit immediately if:**
- Thesis is invalidated (specific conditions met)
- Black swan event occurs
- Personal circumstances change (need the money)
- System failure (can't monitor position)

**Never:**
- Exit due to boredom
- Exit due to small loss without thesis break
- Add to losing position (unless planned scale-in)
