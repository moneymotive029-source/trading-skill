"""
Technical Analysis Agent - Chart patterns, indicators, and momentum analysis
Calculates technical indicators and identifies trading signals from price data.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Signal(Enum):
    """Trading signal enumeration"""
    STRONG_BUY = 2
    BUY = 1
    NEUTRAL = 0
    SELL = -1
    STRONG_SELL = -2


@dataclass
class TechnicalIndicators:
    """Container for all technical indicators"""
    # Moving Averages
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None

    # Momentum
    rsi_14: Optional[float] = None
    stochastic_k: Optional[float] = None
    stochastic_d: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    williams_r: Optional[float] = None
    cci: Optional[float] = None

    # Volatility
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    atr_14: Optional[float] = None
    standard_deviation: Optional[float] = None

    # Volume
    obv: Optional[float] = None
    volume_sma: Optional[float] = None

    # Trend
    adx: Optional[float] = None
    plus_di: Optional[float] = None
    minus_di: Optional[float] = None

    # Summary
    overall_signal: Signal = Signal.NEUTRAL
    signal_score: int = 0  # -10 to +10


@dataclass
class ChartPattern:
    """Detected chart pattern"""
    name: str
    type: str  # 'reversal' or 'continuation'
    status: str  # 'forming', 'complete', 'broken'
    breakout_level: Optional[float] = None
    target_price: Optional[float] = None
    confidence: float = 0.0  # 0-1


class TechnicalAnalysisAgent:
    """
    Technical Analysis Agent for calculating indicators and identifying patterns.

    Features:
    - Moving averages (SMA, EMA)
    - Momentum indicators (RSI, Stochastic, MACD)
    - Volatility indicators (Bollinger Bands, ATR)
    - Volume indicators (OBV)
    - Trend indicators (ADX)
    - Chart pattern recognition
    """

    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.patterns: List[ChartPattern] = []

    def analyze(self, prices: pd.DataFrame) -> TechnicalIndicators:
        """
        Perform complete technical analysis on price data.

        Args:
            prices: DataFrame with columns ['open', 'high', 'low', 'close', 'volume']

        Returns:
            TechnicalIndicators object with all calculated values
        """
        if len(prices) < 200:
            logger.warning("Insufficient data for full analysis (need 200+ periods)")

        # Calculate all indicators
        self._calculate_moving_averages(prices)
        self._calculate_momentum_indicators(prices)
        self._calculate_volatility_indicators(prices)
        self._calculate_volume_indicators(prices)
        self._calculate_trend_indicators(prices)

        # Generate overall signal
        self._generate_signal(prices)

        # Detect patterns
        self.patterns = self._detect_patterns(prices)

        return self.indicators

    def _calculate_moving_averages(self, prices: pd.DataFrame):
        """Calculate SMA and EMA moving averages"""
        close = prices['close']

        # Simple Moving Averages
        self.indicators.sma_20 = close.rolling(window=20).mean().iloc[-1]
        self.indicators.sma_50 = close.rolling(window=50).mean().iloc[-1]
        self.indicators.sma_200 = close.rolling(window=200).mean().iloc[-1]

        # Exponential Moving Averages
        self.indicators.ema_12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
        self.indicators.ema_26 = close.ewm(span=26, adjust=False).mean().iloc[-1]

    def _calculate_momentum_indicators(self, prices: pd.DataFrame):
        """Calculate RSI, Stochastic, MACD, Williams %R, CCI"""
        close = prices['close']
        high = prices['high']
        low = prices['low']

        # RSI (14-period)
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.indicators.rsi_14 = 100 - (100 / (1 + rs)).iloc[-1]

        # Stochastic Oscillator
        lowest_low = low.rolling(window=14).min()
        highest_high = high.rolling(window=14).max()
        self.indicators.stochastic_k = (100 * (close - lowest_low) / (highest_high - lowest_low)).iloc[-1]
        self.indicators.stochastic_d = self.indicators.stochastic_k.rolling(window=3).mean()

        # MACD
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        self.indicators.macd = (ema_12 - ema_26).iloc[-1]
        self.indicators.macd_signal = self.indicators.macd.ewm(span=9, adjust=False).mean()
        self.indicators.macd_histogram = self.indicators.macd - self.indicators.macd_signal

        # Williams %R
        highest_high_14 = high.rolling(window=14).max()
        lowest_low_14 = low.rolling(window=14).min()
        self.indicators.williams_r = (-100 * (highest_high_14 - close) / (highest_high_14 - lowest_low_14)).iloc[-1]

        # CCI (Commodity Channel Index)
        tp = (high + low + close) / 3
        sma_tp = tp.rolling(window=20).mean()
        mad = tp.rolling(window=20).apply(lambda x: np.abs(x - x.mean()).mean())
        self.indicators.cci = ((tp - sma_tp) / (0.015 * mad)).iloc[-1]

    def _calculate_volatility_indicators(self, prices: pd.DataFrame):
        """Calculate Bollinger Bands and ATR"""
        close = prices['close']
        high = prices['high']
        low = prices['low']

        # Bollinger Bands
        self.indicators.bollinger_middle = close.rolling(window=20).mean()
        self.indicators.standard_deviation = close.rolling(window=20).std()
        self.indicators.bollinger_upper = self.indicators.bollinger_middle + 2 * self.indicators.standard_deviation
        self.indicators.bollinger_lower = self.indicators.bollinger_middle - 2 * self.indicators.standard_deviation

        self.indicators.bollinger_upper = self.indicators.bollinger_upper.iloc[-1]
        self.indicators.bollinger_middle = self.indicators.bollinger_middle.iloc[-1]
        self.indicators.bollinger_lower = self.indicators.bollinger_lower.iloc[-1]
        self.indicators.standard_deviation = self.indicators.standard_deviation.iloc[-1]

        # ATR (Average True Range)
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        self.indicators.atr_14 = true_range.rolling(window=14).mean().iloc[-1]

    def _calculate_volume_indicators(self, prices: pd.DataFrame):
        """Calculate OBV and volume SMA"""
        close = prices['close']
        volume = prices['volume']

        # On-Balance Volume
        direction = np.sign(close.diff())
        direction.iloc[0] = 0
        self.indicators.obv = (direction * volume).cumsum().iloc[-1]

        # Volume SMA
        self.indicators.volume_sma = volume.rolling(window=20).mean().iloc[-1]

    def _calculate_trend_indicators(self, prices: pd.DataFrame):
        """Calculate ADX for trend strength"""
        high = prices['high']
        low = prices['low']
        close = prices['close']

        # +DM and -DM
        plus_dm = high.diff()
        minus_dm = -low.diff()

        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        plus_dm[plus_dm <= minus_dm] = 0
        minus_dm[minus_dm <= plus_dm] = 0

        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Smoothed values
        atr = tr.rolling(window=14).sum()
        plus_di = 100 * (plus_dm.rolling(window=14).sum() / atr)
        minus_di = 100 * (minus_dm.rolling(window=14).sum() / atr)

        # ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        self.indicators.adx = dx.rolling(window=14).mean().iloc[-1]
        self.indicators.plus_di = plus_di.iloc[-1]
        self.indicators.minus_di = minus_di.iloc[-1]

    def _generate_signal(self, prices: pd.DataFrame):
        """Generate overall technical signal based on all indicators"""
        score = 0
        close = prices['close'].iloc[-1]

        # Moving Average Signals
        if self.indicators.sma_20 and close > self.indicators.sma_20:
            score += 1
        if self.indicators.sma_50 and close > self.indicators.sma_50:
            score += 1
        if self.indicators.sma_200 and close > self.indicators.sma_200:
            score += 1

        # RSI Signals
        if self.indicators.rsi_14:
            if self.indicators.rsi_14 < 30:
                score += 2  # Oversold
            elif self.indicators.rsi_14 > 70:
                score -= 2  # Overbought

        # MACD Signals
        if self.indicators.macd_histogram and self.indicators.macd_histogram > 0:
            score += 1
        elif self.indicators.macd_histogram and self.indicators.macd_histogram < 0:
            score -= 1

        # Stochastic Signals
        if self.indicators.stochastic_k and self.indicators.stochastic_d:
            if self.indicators.stochastic_k < 20 and self.indicators.stochastic_k > self.indicators.stochastic_d:
                score += 1
            elif self.indicators.stochastic_k > 80 and self.indicators.stochastic_k < self.indicators.stochastic_d:
                score -= 1

        # Bollinger Band Signals
        if self.indicators.bollinger_lower and close < self.indicators.bollinger_lower:
            score += 1  # Price below lower band - potential bounce
        elif self.indicators.bollinger_upper and close > self.indicators.bollinger_upper:
            score -= 1  # Price above upper band - potential pullback

        # ADX Trend Strength
        if self.indicators.adx and self.indicators.adx > 25:
            # Strong trend - amplify existing signals
            score = int(score * 1.2)

        # Set overall signal
        self.indicators.signal_score = max(-10, min(10, score))

        if score >= 8:
            self.indicators.overall_signal = Signal.STRONG_BUY
        elif score >= 5:
            self.indicators.overall_signal = Signal.BUY
        elif score >= 2:
            self.indicators.overall_signal = Signal.NEUTRAL
        elif score >= -1:
            self.indicators.overall_signal = Signal.NEUTRAL
        elif score >= -4:
            self.indicators.overall_signal = Signal.SELL
        else:
            self.indicators.overall_signal = Signal.STRONG_SELL

    def _detect_patterns(self, prices: pd.DataFrame) -> List[ChartPattern]:
        """Detect chart patterns in price data"""
        patterns = []

        # Double Bottom Detection
        double_bottom = self._detect_double_bottom(prices)
        if double_bottom:
            patterns.append(double_bottom)

        # Double Top Detection
        double_top = self._detect_double_top(prices)
        if double_top:
            patterns.append(double_top)

        # Head and Shoulders
        hns = self._detect_head_and_shoulders(prices)
        if hns:
            patterns.append(hns)

        return patterns

    def _detect_double_bottom(self, prices: pd.DataFrame) -> Optional[ChartPattern]:
        """Detect double bottom reversal pattern"""
        low = prices['low'].iloc[-50:]

        # Find two lows within 5% of each other
        min1 = low.min()
        min1_idx = low.idxmin()

        # Mask out first low and find second
        low_masked = low.copy()
        low_masked.loc[max(0, min1_idx - 10):min(min1_idx + 10, len(low) - 1)] = np.inf
        min2 = low_masked.min()

        if abs(min1 - min2) / min1 < 0.05:  # Within 5%
            neckline = low.loc[max(0, min1_idx - 10):min1_idx].max()
            target = neckline + (neckline - min1)
            current_price = prices['close'].iloc[-1]

            return ChartPattern(
                name="Double Bottom",
                type="reversal",
                status="forming" if current_price < neckline else "complete",
                breakout_level=neckline,
                target_price=target,
                confidence=0.75
            )

        return None

    def _detect_double_top(self, prices: pd.DataFrame) -> Optional[ChartPattern]:
        """Detect double top reversal pattern"""
        high = prices['high'].iloc[-50:]

        # Find two highs within 5% of each other
        max1 = high.max()
        max1_idx = high.idxmax()

        high_masked = high.copy()
        high_masked.loc[max(0, max1_idx - 10):min(max1_idx + 10, len(high) - 1)] = -np.inf
        max2 = high_masked.max()

        if abs(max1 - max2) / max1 < 0.05:
            neckline = high.loc[max(0, max1_idx - 10):max1_idx].min()
            target = neckline - (max1 - neckline)
            current_price = prices['close'].iloc[-1]

            return ChartPattern(
                name="Double Top",
                type="reversal",
                status="forming" if current_price > neckline else "complete",
                breakout_level=neckline,
                target_price=target,
                confidence=0.75
            )

        return None

    def _detect_head_and_shoulders(self, prices: pd.DataFrame) -> Optional[ChartPattern]:
        """Detect head and shoulders pattern"""
        high = prices['high'].iloc[-100:]

        # Find local maxima
        from scipy.signal import argrelextrema
        peaks = argrelextrema(high.values, np.greater, order=5)[0]

        if len(peaks) >= 3:
            # Check for head and shoulders shape
            left_shoulder = high.iloc[peaks[0]]
            head = high.iloc[peaks[1]]
            right_shoulder = high.iloc[peaks[2]]

            # Head should be highest, shoulders roughly equal
            if head > left_shoulder and head > right_shoulder:
                if abs(left_shoulder - right_shoulder) / head < 0.05:
                    neckline = high.iloc[peaks[0]:peaks[2]].min()
                    target = neckline - (head - neckline)

                    return ChartPattern(
                        name="Head and Shoulders",
                        type="reversal",
                        status="forming",
                        breakout_level=neckline,
                        target_price=target,
                        confidence=0.70
                    )

        return None

    def format_output(self, indicators: TechnicalIndicators, patterns: List[ChartPattern] = None) -> str:
        """Format technical analysis as markdown"""
        signal_emoji = {
            Signal.STRONG_BUY: "🟢 Strong Buy",
            Signal.BUY: "🟢 Buy",
            Signal.NEUTRAL: "🟡 Neutral",
            Signal.SELL: "🔴 Sell",
            Signal.STRONG_SELL: "🔴 Strong Sell"
        }

        output = f"""
## Technical Analysis Summary

### Overall Signal: {signal_emoji.get(indicators.overall_signal, 'Neutral')}
**Score:** {indicators.signal_score}/10

### Moving Averages
| Indicator | Value | Signal |
|-----------|-------|--------|
| SMA 20 | ${indicators.sma_20:,.2f} if indicators.sma_20 else 'N/A' | {'Bullish' if indicators.sma_20 else 'N/A'} |
| SMA 50 | ${indicators.sma_50:,.2f} if indicators.sma_50 else 'N/A' | {'Bullish' if indicators.sma_50 else 'N/A'} |
| SMA 200 | ${indicators.sma_200:,.2f} if indicators.sma_200 else 'N/A' | {'Bullish' if indicators.sma_200 else 'N/A'} |

### Momentum Indicators
| Indicator | Value | Signal |
|-----------|-------|--------|
| RSI (14) | {indicators.rsi_14:.2f} if indicators.rsi_14 else 'N/A' | {'Oversold' if indicators.rsi_14 and indicators.rsi_14 < 30 else 'Overbought' if indicators.rsi_14 and indicators.rsi_14 > 70 else 'Neutral'} |
| Stochastic K | {indicators.stochastic_k:.2f} if indicators.stochastic_k else 'N/A' | - |
| MACD | {indicators.macd:.4f} if indicators.macd else 'N/A' | {'Bullish' if indicators.macd and indicators.macd > 0 else 'Bearish'} |
| Williams %R | {indicators.williams_r:.2f} if indicators.williams_r else 'N/A' | - |

### Volatility
| Indicator | Value |
|-----------|-------|
| Bollinger Upper | ${indicators.bollinger_upper:,.2f} if indicators.bollinger_upper else 'N/A' |
| Bollinger Middle | ${indicators.bollinger_middle:,.2f} if indicators.bollinger_middle else 'N/A' |
| Bollinger Lower | ${indicators.bollinger_lower:,.2f} if indicators.bollinger_lower else 'N/A' |
| ATR (14) | ${indicators.atr_14:,.2f} if indicators.atr_14 else 'N/A' |

### Trend Strength
| Indicator | Value | Interpretation |
|-----------|-------|----------------|
| ADX | {indicators.adx:.2f} if indicators.adx else 'N/A' | {'Strong Trend' if indicators.adx and indicators.adx > 25 else 'Weak Trend'} |
"""

        if patterns:
            output += "\n### Detected Patterns\n"
            for pattern in patterns:
                output += f"- **{pattern.name}** ({pattern.type}): {pattern.status}, Target: ${pattern.target_price:,.2f}\n"

        return output


def main():
    """Example usage with simulated data"""
    # Generate sample price data
    np.random.seed(42)
    n_periods = 250
    prices = 100 + np.cumsum(np.random.randn(n_periods) * 2)

    # Create DataFrame
    df = pd.DataFrame({
        'open': prices + np.random.randn(n_periods),
        'high': prices + np.abs(np.random.randn(n_periods)),
        'low': prices - np.abs(np.random.randn(n_periods)),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, n_periods)
    })

    # Run analysis
    agent = TechnicalAnalysisAgent()
    indicators = agent.analyze(df)

    print(agent.format_output(indicators, agent.patterns))


if __name__ == '__main__':
    main()
