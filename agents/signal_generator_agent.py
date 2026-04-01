"""
Signal Generator Agent - Synthesizes all inputs into explicit trading signals
Combines technical, fundamental, sentiment, and PESTLE+ analysis into actionable trades.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalDirection(Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"


class SignalStrength(Enum):
    VERY_WEAK = 1
    WEAK = 2
    MODERATE = 3
    STRONG = 4
    VERY_STRONG = 5


class TradeTimeframe(Enum):
    SCALP = "Scalp (minutes-hours)"
    DAY_TRADE = "Day Trade (hours)"
    SWING = "Swing (days-weeks)"
    POSITION = "Position (weeks-months)"


@dataclass
class TradingSignal:
    """Complete trading signal with all parameters"""
    # Core signal
    direction: SignalDirection = SignalDirection.NEUTRAL
    strength: SignalStrength = SignalStrength.WEAK
    timeframe: TradeTimeframe = TradeTimeframe.SWING

    # Entry
    entry_zone_lower: float = 0.0
    entry_zone_upper: float = 0.0
    current_price: float = 0.0

    # Exit
    stop_loss: float = 0.0
    take_profit_1: float = 0.0
    take_profit_2: float = 0.0
    take_profit_3: float = 0.0

    # Position sizing
    position_size_pct: float = 0.0
    position_size_units: float = 0.0
    dollar_risk: float = 0.0

    # Risk/Reward
    risk_reward_ratio: float = 0.0
    expected_return: float = 0.0

    # Confidence
    confidence_score: int = 0  # 0-100
    confidence_level: str = "Medium"

    # Thesis
    thesis: str = ""
    catalyst: str = ""

    # Invalidation
    invalidation_conditions: List[str] = field(default_factory=list)

    # Risks
    key_risks: List[str] = field(default_factory=list)

    # Metadata
    symbol: str = ""
    asset_class: str = ""
    generated_at: datetime = None

    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.utcnow()

    @property
    def entry_avg(self) -> float:
        """Average entry price"""
        return (self.entry_zone_lower + self.entry_zone_upper) / 2

    @property
    def stop_distance_pct(self) -> float:
        """Stop loss distance from average entry"""
        if self.entry_avg == 0:
            return 0
        return abs(self.entry_avg - self.stop_loss) / self.entry_avg * 100

    @property
    def tp1_distance_pct(self) -> float:
        """Take profit 1 distance from average entry"""
        if self.entry_avg == 0:
            return 0
        return abs(self.take_profit_1 - self.entry_avg) / self.entry_avg * 100


@dataclass
class SignalComponents:
    """Component scores that feed into signal generation"""
    # Input scores (0-100)
    technical_score: float = 50.0
    fundamental_score: float = 50.0
    sentiment_score: float = 50.0
    pestle_score: float = 50.0

    # Weights (sum to 1.0)
    technical_weight: float = 0.30
    fundamental_weight: float = 0.25
    sentiment_weight: float = 0.25
    pestle_weight: float = 0.20

    # Agreement flag
    all_aligned: bool = False
    conflicting_signals: List[str] = field(default_factory=list)

    @property
    def weighted_score(self) -> float:
        """Calculate weighted composite score"""
        return (
            self.technical_score * self.technical_weight +
            self.fundamental_score * self.fundamental_weight +
            self.sentiment_score * self.sentiment_weight +
            self.pestle_score * self.pestle_weight
        )


@dataclass
class SignalAnalysis:
    """Complete signal analysis with components and final signal"""
    symbol: str
    asset_class: str
    timestamp: datetime = None

    # Component scores
    components: SignalComponents = None

    # Final signal
    signal: TradingSignal = None

    # Alternative scenarios
    bull_case: str = ""
    bear_case: str = ""
    base_case: str = ""

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.components is None:
            self.components = SignalComponents()
        if self.signal is None:
            self.signal = TradingSignal()


class SignalGeneratorAgent:
    """
    Signal Generator Agent for synthesizing trading signals.

    Process:
    1. Gather component scores (technical, fundamental, sentiment, PESTLE)
    2. Calculate weighted composite score
    3. Check for signal alignment
    4. Generate entry/exit levels
    5. Calculate position size
    6. Document thesis and risks
    """

    # Asset-class-specific thresholds
    SIGNAL_THRESHOLDS = {
        'crypto': {
            'strong_buy': 75,
            'buy': 60,
            'neutral_low': 40,
            'neutral_high': 60,
            'sell': 40,
            'strong_sell': 25
        },
        'stock': {
            'strong_buy': 80,
            'buy': 65,
            'neutral_low': 45,
            'neutral_high': 65,
            'sell': 45,
            'strong_sell': 30
        },
        'forex': {
            'strong_buy': 70,
            'buy': 55,
            'neutral_low': 45,
            'neutral_high': 55,
            'sell': 45,
            'strong_sell': 30
        },
        'commodity': {
            'strong_buy': 75,
            'buy': 60,
            'neutral_low': 40,
            'neutral_high': 60,
            'sell': 40,
            'strong_sell': 25
        }
    }

    def __init__(self):
        """Initialize the signal generator"""
        self.analysis: Optional[SignalAnalysis] = None

    def generate_signal(
        self,
        symbol: str,
        asset_class: str,
        current_price: float,
        technical_indicators: Dict = None,
        fundamental_data: Dict = None,
        sentiment_data: Dict = None,
        pestle_score: float = None,
        support_levels: List[float] = None,
        resistance_levels: List[float] = None
    ) -> SignalAnalysis:
        """
        Generate complete trading signal from all inputs.

        Args:
            symbol: Asset symbol
            asset_class: 'crypto', 'stock', 'forex', 'commodity'
            current_price: Current market price
            technical_indicators: Dict with RSI, MACD, MA signals, etc.
            fundamental_data: Dict with fundamental metrics
            sentiment_data: Dict with sentiment scores
            pestle_score: PESTLE+ overall score (0-100)
            support_levels: List of support price levels
            resistance_levels: List of resistance price levels

        Returns:
            SignalAnalysis with components and trading signal
        """
        analysis = SignalAnalysis(
            symbol=symbol.upper(),
            asset_class=asset_class.lower()
        )

        # Calculate component scores
        analysis.components = self._calculate_component_scores(
            technical_indicators or {},
            fundamental_data or {},
            sentiment_data or {},
            pestle_score or 50.0
        )

        # Generate signal
        analysis.signal = self._generate_trading_signal(
            symbol=symbol.upper(),
            asset_class=asset_class.lower(),
            current_price=current_price,
            components=analysis.components,
            support_levels=support_levels or [],
            resistance_levels=resistance_levels or []
        )

        # Generate scenarios
        analysis.bull_case = self._generate_bull_case(
            symbol, analysis.components, asset_class
        )
        analysis.bear_case = self._generate_bear_case(
            symbol, analysis.components, asset_class
        )
        analysis.base_case = self._generate_base_case(
            symbol, analysis.components, asset_class
        )

        self.analysis = analysis
        return analysis

    def _calculate_component_scores(
        self,
        technical: Dict,
        fundamental: Dict,
        sentiment: Dict,
        pestle: float
    ) -> SignalComponents:
        """Calculate component scores from input data"""
        components = SignalComponents()

        # Technical score (0-100)
        components.technical_score = self._calculate_technical_score(technical)

        # Fundamental score (0-100)
        components.fundamental_score = self._calculate_fundamental_score(fundamental)

        # Sentiment score (0-100)
        components.sentiment_score = self._calculate_sentiment_score(sentiment)

        # PESTLE score (already 0-100)
        components.pestle_score = pestle

        # Check alignment
        scores = [
            components.technical_score,
            components.fundamental_score,
            components.sentiment_score,
            components.pestle_score
        ]
        avg_score = sum(scores) / len(scores)
        max_deviation = max(abs(s - avg_score) for s in scores)

        components.all_aligned = max_deviation < 15

        if not components.all_aligned:
            # Identify conflicting signals
            if components.technical_score > 70 and components.sentiment_score < 30:
                components.conflicting_signals.append(
                    "Technical bullish but sentiment bearish"
                )
            if components.fundamental_score > 70 and components.technical_score < 30:
                components.conflicting_signals.append(
                    "Fundamental strength but technical weakness"
                )

        return components

    def _calculate_technical_score(self, indicators: Dict) -> float:
        """Calculate technical analysis score (0-100)"""
        score = 50.0  # Start neutral

        # RSI contribution (max 15 points)
        rsi = indicators.get('rsi_14', 50)
        if rsi < 30:
            score += 15  # Oversold
        elif rsi < 40:
            score += 10
        elif rsi > 70:
            score -= 15  # Overbought
        elif rsi > 60:
            score -= 10

        # MACD contribution (max 15 points)
        macd_histogram = indicators.get('macd_histogram', 0)
        if macd_histogram > 0:
            score += 10
            if indicators.get('macd_crossabove', False):
                score += 5  # Recent bullish cross

        # Moving average contribution (max 20 points)
        price = indicators.get('current_price', 100)
        sma_20 = indicators.get('sma_20', price)
        sma_50 = indicators.get('sma_50', price)
        sma_200 = indicators.get('sma_200', price)

        if price > sma_200:
            score += 10
        if price > sma_50:
            score += 5
        if price > sma_20:
            score += 3

        if sma_20 > sma_50 > sma_200:
            score += 5  # Golden arrangement

        # Bollinger Bands (max 10 points)
        bb_lower = indicators.get('bollinger_lower', price * 0.95)
        bb_upper = indicators.get('bollinger_upper', price * 1.05)
        if price < bb_lower:
            score += 10  # Mean reversion buy
        elif price > bb_upper:
            score -= 10  # Mean reversion sell

        # ADX trend strength (max 10 points)
        adx = indicators.get('adx', 20)
        if adx > 25:
            # Strong trend - amplify direction
            if price > sma_50:
                score += 5
            else:
                score -= 5

        # Stochastic (max 10 points)
        stoch_k = indicators.get('stochastic_k', 50)
        stoch_d = indicators.get('stochastic_d', 50)
        if stoch_k < 20 and stoch_k > stoch_d:
            score += 10  # Bullish cross in oversold
        elif stoch_k > 80 and stoch_k < stoch_d:
            score -= 10  # Bearish cross in overbought

        # Volume confirmation (max 10 points)
        if indicators.get('volume_above_average', False):
            score += 5  # Volume confirms move

        return max(0, min(100, score))

    def _calculate_fundamental_score(self, data: Dict) -> float:
        """Calculate fundamental analysis score (0-100)"""
        # Use provided fundamental score or calculate from metrics
        if 'fundamental_score' in data:
            return data['fundamental_score']

        score = 50.0

        # Valuation (max 25 points)
        pe_ratio = data.get('pe_ratio')
        if pe_ratio:
            if pe_ratio < 15:
                score += 25
            elif pe_ratio < 25:
                score += 15
            elif pe_ratio < 35:
                score += 5
            else:
                score -= 10

        # Growth (max 25 points)
        revenue_growth = data.get('revenue_growth_yoy', 0)
        if revenue_growth > 20:
            score += 25
        elif revenue_growth > 10:
            score += 15
        elif revenue_growth > 5:
            score += 5
        elif revenue_growth < 0:
            score -= 10

        # Profitability (max 25 points)
        roe = data.get('roe', 0)
        if roe > 20:
            score += 25
        elif roe > 15:
            score += 20
        elif roe > 10:
            score += 15
        elif roe < 0:
            score -= 10

        # Financial health (max 25 points)
        debt_to_equity = data.get('debt_to_equity', 0.5)
        if debt_to_equity < 0.5:
            score += 25
        elif debt_to_equity < 1.0:
            score += 15
        elif debt_to_equity < 2.0:
            score += 5
        else:
            score -= 10

        return max(0, min(100, score))

    def _calculate_sentiment_score(self, data: Dict) -> float:
        """Calculate sentiment score (0-100)"""
        if 'overall_sentiment_score' in data:
            # Convert from -1 to +1 scale to 0-100
            score = (data['overall_sentiment_score'] + 1) / 2 * 100
            return score

        score = 50.0

        # News sentiment (max 30 points)
        news_score = data.get('news_sentiment_score', 0)
        if isinstance(news_score, (int, float)):
            news_normalized = (news_score + 1) / 2 * 100
            if news_normalized > 70:
                score += 25
            elif news_normalized > 50:
                score += 15
            elif news_normalized < 30:
                score -= 25
            elif news_normalized < 50:
                score -= 15

        # Social sentiment (max 30 points)
        social_score = data.get('social_sentiment_score', 0)
        if isinstance(social_score, (int, float)):
            social_normalized = (social_score + 1) / 2 * 100
            if social_normalized > 70:
                score += 25
            elif social_normalized > 50:
                score += 15

        # Positioning (max 20 points)
        fear_greed = data.get('fear_greed_index', 50)
        if fear_greed < 25:
            score += 20  # Extreme fear - contrarian buy
        elif fear_greed > 75:
            score -= 20  # Extreme greed - contrarian sell

        return max(0, min(100, score))

    def _generate_trading_signal(
        self,
        symbol: str,
        asset_class: str,
        current_price: float,
        components: SignalComponents,
        support_levels: List[float],
        resistance_levels: List[float]
    ) -> TradingSignal:
        """Generate trading signal from component scores"""
        signal = TradingSignal(
            symbol=symbol,
            asset_class=asset_class,
            current_price=current_price
        )

        # Get thresholds for asset class
        thresholds = self.SIGNAL_THRESHOLDS.get(
            asset_class.lower(),
            self.SIGNAL_THRESHOLDS['crypto']
        )

        # Calculate weighted score
        weighted_score = components.weighted_score
        signal.confidence_score = int(weighted_score)

        # Determine direction
        if weighted_score >= thresholds['strong_buy']:
            signal.direction = SignalDirection.LONG
            signal.strength = SignalStrength.VERY_STRONG
        elif weighted_score >= thresholds['buy']:
            signal.direction = SignalDirection.LONG
            signal.strength = SignalStrength.STRONG
        elif weighted_score >= thresholds['neutral_high']:
            signal.direction = SignalDirection.LONG
            signal.strength = SignalStrength.WEAK
        elif weighted_score <= thresholds['strong_sell']:
            signal.direction = SignalDirection.SHORT
            signal.strength = SignalStrength.VERY_STRONG
        elif weighted_score <= thresholds['sell']:
            signal.direction = SignalDirection.SHORT
            signal.strength = SignalStrength.STRONG
        elif weighted_score <= thresholds['neutral_low']:
            signal.direction = SignalDirection.SHORT
            signal.strength = SignalStrength.WEAK
        else:
            signal.direction = SignalDirection.NEUTRAL
            signal.strength = SignalStrength.WEAK

        # Set entry zone
        signal.entry_zone_lower = current_price * 0.995  # 0.5% below
        signal.entry_zone_upper = current_price * 1.005  # 0.5% above

        # Calculate stop loss and take profit levels
        if signal.direction == SignalDirection.LONG:
            # Stop below nearest support
            if support_levels:
                valid_supports = [s for s in support_levels if s < current_price]
                if valid_supports:
                    signal.stop_loss = max(valid_supports) * 0.99  # 1% below support
                else:
                    signal.stop_loss = current_price * 0.95  # 5% hard stop
            else:
                signal.stop_loss = current_price * 0.95

            # Take profits at resistance levels
            if resistance_levels:
                valid_resistances = [r for r in resistance_levels if r > current_price]
                if valid_resistances:
                    signal.take_profit_1 = min(valid_resistances)
                    if len(valid_resistances) > 1:
                        signal.take_profit_2 = sorted(valid_resistances)[1]
                    if len(valid_resistances) > 2:
                        signal.take_profit_3 = sorted(valid_resistances)[2]

            # Fill in missing TP levels
            if not signal.take_profit_1:
                signal.take_profit_1 = current_price * 1.03
            if not signal.take_profit_2:
                signal.take_profit_2 = current_price * 1.06
            if not signal.take_profit_3:
                signal.take_profit_3 = current_price * 1.10

        elif signal.direction == SignalDirection.SHORT:
            # Stop above nearest resistance
            if resistance_levels:
                valid_resistances = [r for r in resistance_levels if r > current_price]
                if valid_resistances:
                    signal.stop_loss = min(valid_resistances) * 1.01  # 1% above resistance
                else:
                    signal.stop_loss = current_price * 1.05  # 5% hard stop
            else:
                signal.stop_loss = current_price * 1.05

            # Take profits at support levels
            if support_levels:
                valid_supports = [s for s in support_levels if s < current_price]
                if valid_supports:
                    signal.take_profit_1 = max(valid_supports)
                    if len(valid_supports) > 1:
                        signal.take_profit_2 = sorted(valid_supports, reverse=True)[1]
                    if len(valid_supports) > 2:
                        signal.take_profit_3 = sorted(valid_supports, reverse=True)[2]

            # Fill in missing TP levels
            if not signal.take_profit_1:
                signal.take_profit_1 = current_price * 0.97
            if not signal.take_profit_2:
                signal.take_profit_2 = current_price * 0.94
            if not signal.take_profit_3:
                signal.take_profit_3 = current_price * 0.90

        # Calculate position size (simplified - 1% risk)
        if signal.stop_loss > 0 and signal.entry_avg > 0:
            stop_distance = abs(signal.entry_avg - signal.stop_loss) / signal.entry_avg
            signal.dollar_risk = 100000 * 0.01  # 1% of $100k account
            signal.position_size_value = signal.dollar_risk / stop_distance
            signal.position_size_units = signal.position_size_value / signal.entry_avg
            signal.position_size_pct = (signal.position_size_value / 100000) * 100

        # Risk/Reward ratio
        if signal.stop_distance_pct > 0:
            signal.risk_reward_ratio = signal.tp1_distance_pct / signal.stop_distance_pct

        # Expected return (simplified)
        win_rate = 0.55 if signal.strength == SignalStrength.STRONG else 0.50
        signal.expected_return = (
            win_rate * signal.risk_reward_ratio - (1 - win_rate)
        ) * 100

        # Confidence level
        if signal.confidence_score >= 75:
            signal.confidence_level = "High"
        elif signal.confidence_score >= 55:
            signal.confidence_level = "Medium"
        else:
            signal.confidence_level = "Low"

        # Generate thesis
        signal.thesis = self._generate_thesis(symbol, components, signal.direction)

        # Invalidation conditions
        signal.invalidation_conditions = self._generate_invalidation_conditions(
            signal.direction, signal.stop_loss, components
        )

        # Key risks
        signal.key_risks = self._generate_key_risks(asset_class, components)

        return signal

    def _generate_thesis(
        self,
        symbol: str,
        components: SignalComponents,
        direction: SignalDirection
    ) -> str:
        """Generate trade thesis narrative"""
        direction_str = "bullish" if direction == SignalDirection.LONG else "bearish"

        thesis_parts = [f"The {direction_str} thesis for {symbol} is based on:"]

        if components.technical_score > 60 and direction == SignalDirection.LONG:
            thesis_parts.append("- Positive technical setup with momentum indicators turning higher")
        elif components.technical_score < 40 and direction == SignalDirection.SHORT:
            thesis_parts.append("- Weak technical structure with bearish momentum divergence")

        if components.fundamental_score > 60:
            thesis_parts.append("- Attractive fundamental valuation and growth prospects")
        elif components.fundamental_score < 40:
            thesis_parts.append("- Deteriorating fundamental conditions and overvaluation concerns")

        if components.sentiment_score > 60:
            thesis_parts.append("- Improving market sentiment and positioning")
        elif components.sentiment_score < 40:
            thesis_parts.append("- Negative sentiment creating headwinds")

        if components.pestle_score > 60:
            thesis_parts.append("- Favorable macro and regulatory environment")
        elif components.pestle_score < 40:
            thesis_parts.append("- Challenging macro backdrop and regulatory uncertainty")

        return " ".join(thesis_parts)

    def _generate_invalidation_conditions(
        self,
        direction: SignalDirection,
        stop_loss: float,
        components: SignalComponents
    ) -> List[str]:
        """Generate conditions that would invalidate the thesis"""
        conditions = []

        if direction == SignalDirection.LONG:
            conditions.append(f"Price closes below stop loss at ${stop_loss:.2f}")
            if components.technical_score > 60:
                conditions.append("Technical momentum reverses (RSI breaks below 40)")
        elif direction == SignalDirection.SHORT:
            conditions.append(f"Price closes above stop loss at ${stop_loss:.2f}")
            if components.technical_score < 40:
                conditions.append("Technical momentum improves (RSI breaks above 60)")

        if components.fundamental_score > 60:
            conditions.append("Fundamental deterioration (earnings miss, guidance cut)")
        elif components.fundamental_score < 40:
            conditions.append("Unexpected fundamental improvement")

        return conditions

    def _generate_key_risks(
        self,
        asset_class: str,
        components: SignalComponents
    ) -> List[str]:
        """Generate key risks for the trade"""
        risks = []

        # Asset-class-specific risks
        if asset_class.lower() == 'crypto':
            risks.append("Regulatory announcement risk")
            risks.append("Exchange/counterparty risk")
            risks.append("High volatility - position may gap")
        elif asset_class.lower() == 'stock':
            risks.append("Earnings announcement risk")
            risks.append("Sector rotation risk")
            risks.append("Market-wide correlation in stress")
        elif asset_class.lower() == 'forex':
            risks.append("Central bank surprise risk")
            risks.append("Geopolitical shock risk")
            risks.append("Low liquidity during off-hours")
        elif asset_class.lower() == 'commodity':
            risks.append("Supply shock risk")
            risks.append("Inventory report volatility")
            risks.append("Currency translation risk")

        # Signal conflict risk
        if not components.all_aligned:
            risks.append("Conflicting signals across analysis dimensions")

        return risks

    def _generate_bull_case(
        self,
        symbol: str,
        components: SignalComponents,
        asset_class: str
    ) -> str:
        """Generate bull case scenario"""
        return f"Bull case for {symbol}: Technical breakout above resistance, fundamental improvement in key metrics, positive sentiment shift, and favorable macro backdrop converge for significant upside. Target: +15-25% from current levels."

    def _generate_bear_case(
        self,
        symbol: str,
        components: SignalComponents,
        asset_class: str
    ) -> str:
        """Generate bear case scenario"""
        return f"Bear case for {symbol}: Technical breakdown below support, fundamental deterioration, negative sentiment spiral, and macro headwinds create downside pressure. Risk: -15-20% from current levels."

    def _generate_base_case(
        self,
        symbol: str,
        components: SignalComponents,
        asset_class: str
    ) -> str:
        """Generate base case scenario"""
        return f"Base case for {symbol}: Range-bound trading with gradual drift toward fair value. Expect {symbol} to trade within established support/resistance levels while fundamentals and sentiment stabilize."

    def format_output(self, analysis: SignalAnalysis) -> str:
        """Format signal analysis as markdown"""
        signal = analysis.signal

        # Direction emoji
        if signal.direction == SignalDirection.LONG:
            direction_emoji = "🟢"
        elif signal.direction == SignalDirection.SHORT:
            direction_emoji = "🔴"
        else:
            direction_emoji = "🟡"

        # Strength stars
        strength_stars = "⭐" * signal.strength.value

        output = f"""
# Trading Signal: {analysis.symbol}

## {direction_emoji} {signal.direction.value} | {signal.strength.name} {strength_stars}

**Asset Class:** {analysis.asset_class.upper()}
**Generated:** {analysis.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
**Confidence:** {signal.confidence_score}/100 ({signal.confidence_level})

---

## Trade Parameters

| Parameter | Value |
|-----------|-------|
| **Direction** | {signal.direction.value} |
| **Timeframe** | {signal.timeframe.value} |
| **Entry Zone** | ${signal.entry_zone_lower:,.2f} - ${signal.entry_zone_upper:,.2f} |
| **Current Price** | ${signal.current_price:,.2f} |
| **Stop Loss** | ${signal.stop_loss:,.2f} |
| **Take Profit 1** | ${signal.take_profit_1:,.2f} |
| **Take Profit 2** | ${signal.take_profit_2:,.2f} |
| **Take Profit 3** | ${signal.take_profit_3:,.2f} |

---

## Position Sizing

| Metric | Value |
|--------|-------|
| **Position Size** | {signal.position_size_pct:.2f}% of portfolio |
| **Units** | {signal.position_size_units:,.4f} |
| **Dollar Risk** | ${signal.dollar_risk:,.2f} |
| **Risk/Reward** | 1:{signal.risk_reward_ratio:.2f} |
| **Expected Return** | {signal.expected_return:+.1f}% |

---

## Component Scores

| Component | Score | Weight | Contribution |
|-----------|-------|--------|--------------|
| **Technical** | {analysis.components.technical_score:.1f} | {analysis.components.technical_weight:.0%} | {analysis.components.technical_score * analysis.components.technical_weight:.1f} |
| **Fundamental** | {analysis.components.fundamental_score:.1f} | {analysis.components.fundamental_weight:.0%} | {analysis.components.fundamental_score * analysis.components.fundamental_weight:.1f} |
| **Sentiment** | {analysis.components.sentiment_score:.1f} | {analysis.components.sentiment_weight:.0%} | {analysis.components.sentiment_score * analysis.components.sentiment_weight:.1f} |
| **PESTLE** | {analysis.components.pestle_score:.1f} | {analysis.components.pestle_weight:.0%} | {analysis.components.pestle_score * analysis.components.pestle_weight:.1f} |

**Weighted Score:** {analysis.components.weighted_score:.1f}/100

{'**All Signals Aligned** ✅' if analysis.components.all_aligned else f'**Conflicting Signals:** {", ".join(analysis.components.conflicting_signals)}'}

---

## Trade Thesis

{signal.thesis}

### Bull Case
{analysis.bull_case}

### Bear Case
{analysis.bear_case}

### Base Case
{analysis.base_case}

---

## Risk Management

### Invalidation Conditions
This thesis is invalidated if:
"""
        for condition in signal.invalidation_conditions:
            output += f"- {condition}\n"

        output += "\n### Key Risks\n"
        for risk in signal.key_risks:
            output += f"- {risk}\n"

        return output


def main():
    """Example usage of SignalGeneratorAgent"""
    agent = SignalGeneratorAgent()

    # Example inputs
    analysis = agent.generate_signal(
        symbol='BTC',
        asset_class='crypto',
        current_price=45000,
        technical_indicators={
            'rsi_14': 35,
            'macd_histogram': 150,
            'sma_20': 44000,
            'sma_50': 42000,
            'sma_200': 38000,
            'bollinger_lower': 43000,
            'bollinger_upper': 47000,
            'adx': 28,
            'stochastic_k': 25,
            'stochastic_d': 22,
            'current_price': 45000,
            'volume_above_average': True
        },
        fundamental_data={
            'fundamental_score': 72,
            'market_cap': 880_000_000_000,
            'active_addresses': 950000
        },
        sentiment_data={
            'overall_sentiment_score': 0.35,
            'news_sentiment_score': 0.25,
            'social_sentiment_score': 0.40,
            'fear_greed_index': 35
        },
        pestle_score=65,
        support_levels=[42000, 40000, 38000],
        resistance_levels=[47000, 50000, 55000]
    )

    print(agent.format_output(analysis))


if __name__ == '__main__':
    main()
