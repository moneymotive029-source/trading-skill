"""
Financial Intelligence Trading Agent - Master Orchestrator
Complete multi-agent trading analysis system for crypto, stocks, forex, and commodities.

This is the main entry point that orchestrates all 10 specialized sub-agents:
1. Market Data Agent - Price, volume, levels
2. Technical Analysis Agent - Indicators, patterns
3. Fundamental Analysis Agent - Financials, on-chain metrics
4. Sentiment Analysis Agent - News, social, positioning
5. PESTLE Analysis Agent - Macro factors
6. News Monitor Agent - Catalysts, events
7. Risk Management Agent - Position sizing, stops
8. Signal Generator Agent - Synthesize signals
9. Portfolio Manager Agent - Correlation, allocation
10. Backtesting Agent - Historical validation
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

# Import all sub-agents
from market_data_agent import MarketDataAgent, MarketData
from technical_analysis_agent import TechnicalAnalysisAgent, TechnicalIndicators, Signal
from fundamental_analysis_agent import FundamentalAnalysisAgent, FundamentalAnalysis
from sentiment_analysis_agent import SentimentAnalysisAgent, SentimentAnalysis
from pestle_analysis_agent import PESTLEAnalysisAgent, PESTLEAnalysis
from news_monitor_agent import NewsMonitorAgent, NewsAnalysis
from risk_management_agent import RiskManagementAgent, RiskAssessment, RiskParameters, PositionSizeMode
from signal_generator_agent import SignalGeneratorAgent, SignalAnalysis, SignalDirection
from portfolio_manager_agent import PortfolioManagerAgent, PortfolioReport
from backtesting_agent import BacktestingAgent, StrategyType, BacktestResults

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssetClass(Enum):
    CRYPTO = "crypto"
    STOCK = "stock"
    FOREX = "forex"
    COMMODITY = "commodity"


@dataclass
class TradingRecommendation:
    """Final trading recommendation from the Financial Intelligence Trading Agent"""
    # Asset info
    symbol: str
    asset_class: str
    analysis_timestamp: datetime

    # Market data
    current_price: float
    price_change_24h: float

    # Overall signal
    direction: str  # LONG, SHORT, NEUTRAL
    confidence: int  # 0-100
    strength: str  # VERY_STRONG, STRONG, MODERATE, WEAK

    # Trade parameters
    entry_zone_lower: float
    entry_zone_upper: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    take_profit_3: float

    # Position sizing
    position_size_pct: float
    dollar_risk: float
    risk_reward_ratio: float

    # Analysis summary
    technical_score: float
    fundamental_score: float
    sentiment_score: float
    pestle_score: float

    # Thesis
    bull_case: str
    bear_case: str
    base_case: str

    # Key levels
    support_levels: List[float] = field(default_factory=list)
    resistance_levels: List[float] = field(default_factory=list)

    # Risks
    key_risks: List[str] = field(default_factory=list)
    invalidation_conditions: List[str] = field(default_factory=list)

    # Catalysts
    upcoming_catalysts: List[str] = field(default_factory=list)

    # Disclaimer
    disclaimer: str = field(default="""
---
**Disclaimer:** This analysis is for informational purposes only and does not constitute
financial advice. Trading involves substantial risk of loss. Past performance does not
guarantee future results. Always do your own research and consult with a licensed
financial advisor before making investment decisions.
""")


@dataclass
class AnalysisResults:
    """Container for all analysis results from sub-agents"""
    # Input
    symbol: str
    asset_class: str
    timestamp: datetime = None

    # Sub-agent results
    market_data: Optional[MarketData] = None
    technical_indicators: Optional[TechnicalIndicators] = None
    fundamental_analysis: Optional[FundamentalAnalysis] = None
    sentiment_analysis: Optional[SentimentAnalysis] = None
    pestle_analysis: Optional[PESTLEAnalysis] = None
    news_analysis: Optional[NewsAnalysis] = None
    risk_assessment: Optional[RiskAssessment] = None
    signal_analysis: Optional[SignalAnalysis] = None
    portfolio_report: Optional[PortfolioReport] = None
    backtest_results: Optional[BacktestResults] = None

    # Final recommendation
    recommendation: Optional[TradingRecommendation] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class FinancialIntelligenceTradingAgent:
    """
    Financial Intelligence Trading Agent - Master Orchestrator

    Complete multi-agent trading analysis system that:
    - Fetches real-time market data from multiple sources
    - Calculates 20+ technical indicators and detects chart patterns
    - Analyzes fundamentals (stock: P/E, growth; crypto: on-chain; forex: economic data)
    - Gauges sentiment from news, social media, and positioning
    - Evaluates PESTLE+ macro factors
    - Monitors news and upcoming catalysts
    - Calculates optimal position size using Kelly Criterion
    - Generates explicit trading signals with entry, stop, targets
    - Checks portfolio correlation and risk
    - Optionally backtests strategies

    Usage:
        async with FinancialIntelligenceTradingAgent() as agent:
            result = await agent.analyze('BTC', 'crypto')
            print(agent.format_output(result))
    """

    # Configuration
    DEFAULT_ACCOUNT_SIZE = 100000.0
    DEFAULT_RISK_PER_TRADE = 1.0  # 1%
    CONFIDENCE_THRESHOLDS = {
        'very_strong': 80,
        'strong': 65,
        'moderate': 50,
        'weak': 35
    }

    def __init__(
        self,
        api_keys: Dict[str, str] = None,
        account_size: float = None,
        risk_per_trade: float = None,
        enable_backtesting: bool = False
    ):
        """
        Initialize the Financial Intelligence Trading Agent.

        Args:
            api_keys: Optional API keys for data sources
            account_size: Account size for position sizing (default: $100,000)
            risk_per_trade: Risk per trade as % (default: 1%)
            enable_backtesting: Whether to run backtests (default: False)
        """
        self.api_keys = api_keys or {}
        self.account_size = account_size or self.DEFAULT_ACCOUNT_SIZE
        self.risk_per_trade = risk_per_trade or self.DEFAULT_RISK_PER_TRADE
        self.enable_backtesting = enable_backtesting

        # Initialize all sub-agents
        self.market_agent = MarketDataAgent(api_keys=self.api_keys)
        self.technical_agent = TechnicalAnalysisAgent()
        self.fundamental_agent = FundamentalAnalysisAgent(api_keys=self.api_keys)
        self.sentiment_agent = SentimentAnalysisAgent(api_keys=self.api_keys)
        self.pestle_agent = PESTLEAnalysisAgent()
        self.news_agent = NewsMonitorAgent(api_keys=self.api_keys)
        self.risk_agent = RiskManagementAgent()
        self.signal_agent = SignalGeneratorAgent()
        self.portfolio_agent = PortfolioManagerAgent()
        self.backtest_agent = BacktestingAgent()

        self.session = None
        self.results: Optional[AnalysisResults] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = await self.market_agent.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.market_agent.__aexit__(exc_type, exc_val, exc_tb)

    async def analyze(
        self,
        symbol: str,
        asset_class: str,
        include_backtest: bool = None,
        portfolio_positions: List[Dict] = None
    ) -> AnalysisResults:
        """
        Perform comprehensive trading analysis using all sub-agents.

        Args:
            symbol: Asset symbol (e.g., 'BTC', 'AAPL', 'EURUSD', 'GOLD')
            asset_class: 'crypto', 'stock', 'forex', or 'commodity'
            include_backtest: Whether to include backtest (default: from init)
            portfolio_positions: Existing positions for correlation check

        Returns:
            AnalysisResults with all sub-agent outputs and final recommendation
        """
        results = AnalysisResults(symbol=symbol.upper(), asset_class=asset_class.lower())
        include_backtest = include_backtest if include_backtest is not None else self.enable_backtesting

        logger.info(f"Starting analysis for {symbol.upper()} ({asset_class})")

        try:
            # Step 1: Fetch market data
            logger.info("Step 1/9: Fetching market data...")
            results.market_data = await self._fetch_market_data(symbol, asset_class)

            # Step 2: Generate price data for technical analysis
            logger.info("Step 2/9: Running technical analysis...")
            price_data = self._generate_price_data(results.market_data)
            results.technical_indicators = self.technical_agent.analyze(price_data)

            # Step 3: Fundamental analysis
            logger.info("Step 3/9: Running fundamental analysis...")
            results.fundamental_analysis = await self.fundamental_agent.analyze(
                symbol, asset_class
            )

            # Step 4: Sentiment analysis
            logger.info("Step 4/9: Running sentiment analysis...")
            results.sentiment_analysis = await self.sentiment_agent.analyze(
                symbol, asset_class
            )

            # Step 5: PESTLE analysis
            logger.info("Step 5/9: Running PESTLE analysis...")
            results.pestle_analysis = self.pestle_agent.analyze(symbol, asset_class)

            # Step 6: News and catalyst analysis
            logger.info("Step 6/9: Running news analysis...")
            results.news_analysis = await self.news_agent.analyze(symbol, asset_class)

            # Step 7: Generate trading signal
            logger.info("Step 7/9: Generating trading signal...")
            results.signal_analysis = self._generate_signal(results, price_data)

            # Step 8: Risk assessment
            logger.info("Step 8/9: Running risk assessment...")
            results.risk_assessment = self._assess_risk(results)

            # Step 9: Portfolio analysis (if positions provided)
            if portfolio_positions:
                logger.info("Step 9/9: Running portfolio analysis...")
                prices = {symbol: results.market_data.current_price}
                results.portfolio_report = self.portfolio_agent.analyze_portfolio(
                    portfolio_positions, prices
                )

            # Optional: Backtest
            if include_backtest and len(price_data) > 100:
                logger.info("Running optional backtest...")
                results.backtest_results = self.backtest_agent.run_backtest(
                    price_data,
                    StrategyType.TREND_FOLLOWING,
                    {'short_window': 12, 'long_window': 26}
                )

            # Generate final recommendation
            logger.info("Generating final recommendation...")
            results.recommendation = self._generate_recommendation(results)

            self.results = results
            logger.info(f"Analysis complete for {symbol.upper()}")

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise

        return results

    async def _fetch_market_data(self, symbol: str, asset_class: str) -> MarketData:
        """Fetch market data from MarketDataAgent"""
        return await self.market_agent.fetch_market_data(symbol, asset_class)

    def _generate_price_data(self, market_data: MarketData) -> pd.DataFrame:
        """
        Generate synthetic price data for technical analysis.

        In production, this would fetch historical data from an API.
        For simulation, we generate realistic price movements.
        """
        np.random.seed(42)
        n_periods = 250

        base_price = market_data.current_price
        volatility = 0.02  # 2% daily volatility

        # Generate realistic price series
        returns = np.random.normal(0, volatility, n_periods)
        prices = base_price * np.cumprod(1 + returns)

        # Generate OHLCV
        df = pd.DataFrame({
            'open': prices * (1 + np.random.uniform(-0.005, 0.005, n_periods)),
            'high': prices * (1 + np.random.uniform(0, 0.02, n_periods)),
            'low': prices * (1 - np.random.uniform(0, 0.02, n_periods)),
            'close': prices,
            'volume': np.random.randint(100000, 10000000, n_periods)
        })

        # Set index as dates
        df.index = pd.date_range(end=datetime.utcnow(), periods=n_periods, freq='D')

        return df

    def _generate_signal(self, results: AnalysisResults, price_data: pd.DataFrame) -> SignalAnalysis:
        """Generate trading signal using SignalGeneratorAgent"""
        # Extract technical indicators
        indicators = {}
        if results.technical_indicators:
            ti = results.technical_indicators
            indicators = {
                'rsi_14': ti.rsi_14 or 50,
                'macd_histogram': ti.macd_histogram or 0,
                'sma_20': ti.sma_20 or price_data['close'].iloc[-1],
                'sma_50': ti.sma_50 or price_data['close'].iloc[-1],
                'sma_200': ti.sma_200 or price_data['close'].iloc[-1],
                'bollinger_lower': ti.bollinger_lower or price_data['close'].iloc[-1] * 0.95,
                'bollinger_upper': ti.bollinger_upper or price_data['close'].iloc[-1] * 1.05,
                'adx': ti.adx or 20,
                'stochastic_k': ti.stochastic_k or 50,
                'stochastic_d': ti.stochastic_d or 50,
                'current_price': results.market_data.current_price,
                'volume_above_average': True
            }

        # Extract fundamental score
        fundamental_data = {}
        if results.fundamental_analysis:
            fundamental_data = {
                'fundamental_score': results.fundamental_analysis.overall_score
            }

        # Extract sentiment
        sentiment_data = {}
        if results.sentiment_analysis and results.sentiment_analysis.indicators:
            sentiment_data = {
                'overall_sentiment_score': results.sentiment_analysis.indicators.overall_sentiment_score,
                'fear_greed_index': results.sentiment_analysis.indicators.fear_greed_index or 50
            }

        # PESTLE score
        pestle_score = 50
        if results.pestle_analysis:
            pestle_score = results.pestle_analysis.overall_score

        # Support/resistance levels
        current_price = results.market_data.current_price
        support_levels = [
            current_price * 0.98,
            current_price * 0.95,
            current_price * 0.90
        ]
        resistance_levels = [
            current_price * 1.02,
            current_price * 1.05,
            current_price * 1.10
        ]

        return self.signal_agent.generate_signal(
            symbol=results.symbol,
            asset_class=results.asset_class,
            current_price=current_price,
            technical_indicators=indicators,
            fundamental_data=fundamental_data,
            sentiment_data=sentiment_data,
            pestle_score=pestle_score,
            support_levels=support_levels,
            resistance_levels=resistance_levels
        )

    def _assess_risk(self, results: AnalysisResults) -> RiskAssessment:
        """Assess trade risk using RiskManagementAgent"""
        signal = results.signal_analysis.signal if results.signal_analysis else None

        if not signal:
            return RiskAssessment(symbol=results.symbol, entry_price=results.market_data.current_price)

        # Calculate position size
        params = RiskParameters(
            account_size=self.account_size,
            risk_per_trade_pct=self.risk_per_trade,
            win_rate=0.55,
            avg_win_loss_ratio=signal.risk_reward_ratio or 2.0,
            sizing_method=PositionSizeMode.HALF_KELLY
        )

        position_result = self.risk_agent.calculate_position_size(
            entry_price=signal.entry_avg,
            stop_loss_price=signal.stop_loss,
            params=params
        )

        # Create risk assessment
        return self.risk_agent.assess_trade_risk(
            symbol=results.symbol,
            entry_price=signal.entry_avg,
            stop_loss=signal.stop_loss,
            position_size_result=position_result
        )

    def _generate_recommendation(self, results: AnalysisResults) -> TradingRecommendation:
        """Generate final trading recommendation"""
        signal = results.signal_analysis.signal if results.signal_analysis else None
        risk = results.risk_assessment

        if not signal:
            # Default neutral recommendation
            return TradingRecommendation(
                symbol=results.symbol,
                asset_class=results.asset_class,
                analysis_timestamp=datetime.utcnow(),
                current_price=results.market_data.current_price,
                price_change_24h=results.market_data.price_change_24h,
                direction="NEUTRAL",
                confidence=50,
                strength="WEAK",
                entry_zone_lower=results.market_data.current_price * 0.99,
                entry_zone_upper=results.market_data.current_price * 1.01,
                stop_loss=0,
                take_profit_1=0,
                take_profit_2=0,
                take_profit_3=0,
                position_size_pct=0,
                dollar_risk=0,
                risk_reward_ratio=0,
                technical_score=50,
                fundamental_score=50,
                sentiment_score=50,
                pestle_score=50,
                bull_case="Insufficient data for analysis",
                bear_case="Insufficient data for analysis",
                base_case="Wait for clearer signals"
            )

        # Determine strength from confidence
        confidence = signal.confidence_score
        if confidence >= self.CONFIDENCE_THRESHOLDS['very_strong']:
            strength = "VERY_STRONG"
        elif confidence >= self.CONFIDENCE_THRESHOLDS['strong']:
            strength = "STRONG"
        elif confidence >= self.CONFIDENCE_THRESHOLDS['moderate']:
            strength = "MODERATE"
        else:
            strength = "WEAK"

        # Get component scores
        components = results.signal_analysis.components if results.signal_analysis else None
        tech_score = components.technical_score if components else 50
        fund_score = components.fundamental_score if components else 50
        sent_score = components.sentiment_score if components else 50
        pestle_score = components.pestle_score if components else 50

        # Build recommendation
        return TradingRecommendation(
            symbol=results.symbol,
            asset_class=results.asset_class,
            analysis_timestamp=datetime.utcnow(),
            current_price=results.market_data.current_price,
            price_change_24h=results.market_data.price_change_24h,
            direction=signal.direction.value,
            confidence=confidence,
            strength=strength,
            entry_zone_lower=signal.entry_zone_lower,
            entry_zone_upper=signal.entry_zone_upper,
            stop_loss=signal.stop_loss,
            take_profit_1=signal.take_profit_1,
            take_profit_2=signal.take_profit_2,
            take_profit_3=signal.take_profit_3,
            position_size_pct=signal.position_size_pct,
            dollar_risk=signal.dollar_risk,
            risk_reward_ratio=signal.risk_reward_ratio,
            technical_score=tech_score,
            fundamental_score=fund_score,
            sentiment_score=sent_score,
            pestle_score=pestle_score,
            bull_case=results.signal_analysis.bull_case if results.signal_analysis else "",
            bear_case=results.signal_analysis.bear_case if results.signal_analysis else "",
            base_case=results.signal_analysis.base_case if results.signal_analysis else "",
            support_levels=[results.market_data.current_price * 0.98, results.market_data.current_price * 0.95],
            resistance_levels=[results.market_data.current_price * 1.02, results.market_data.current_price * 1.05],
            key_risks=signal.key_risks if signal else [],
            invalidation_conditions=signal.invalidation_conditions if signal else []
        )

    def format_output(self, results: AnalysisResults) -> str:
        """Format complete analysis as markdown report"""
        rec = results.recommendation
        if not rec:
            return "Analysis incomplete"

        # Direction emoji
        if rec.direction == "LONG":
            direction_emoji = "🟢"
        elif rec.direction == "SHORT":
            direction_emoji = "🔴"
        else:
            direction_emoji = "🟡"

        output = f"""
# 🎯 Financial Intelligence Trading Agent

## {direction_emoji} {rec.symbol} - {rec.direction} Signal

**Asset Class:** {rec.asset_class.upper()}
**Analysis Time:** {rec.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
**Confidence:** {rec.confidence}/100 ({rec.strength})

---

## 📊 Current Market Data

| Metric | Value |
|--------|-------|
| **Current Price** | ${rec.current_price:,.2f} |
| **24h Change** | {rec.price_change_24h:+.2f}% |
| **Entry Zone** | ${rec.entry_zone_lower:,.2f} - ${rec.entry_zone_upper:,.2f} |

---

## 🎯 Trade Parameters

| Parameter | Value |
|-----------|-------|
| **Direction** | {rec.direction} |
| **Stop Loss** | ${rec.stop_loss:,.2f} |
| **Take Profit 1** | ${rec.take_profit_1:,.2f} |
| **Take Profit 2** | ${rec.take_profit_2:,.2f} |
| **Take Profit 3** | ${rec.take_profit_3:,.2f} |
| **Position Size** | {rec.position_size_pct:.2f}% |
| **Dollar Risk** | ${rec.dollar_risk:,.2f} |
| **Risk/Reward** | 1:{rec.risk_reward_ratio:.2f} |

---

## 📈 Component Scores

| Component | Score | Status |
|-----------|-------|--------|
| **Technical** | {rec.technical_score:.1f}/100 | {'🟢 Bullish' if rec.technical_score > 60 else '🔴 Bearish' if rec.technical_score < 40 else '🟡 Neutral'} |
| **Fundamental** | {rec.fundamental_score:.1f}/100 | {'🟢 Bullish' if rec.fundamental_score > 60 else '🔴 Bearish' if rec.fundamental_score < 40 else '🟡 Neutral'} |
| **Sentiment** | {rec.sentiment_score:.1f}/100 | {'🟢 Bullish' if rec.sentiment_score > 60 else '🔴 Bearish' if rec.sentiment_score < 40 else '🟡 Neutral'} |
| **PESTLE** | {rec.pestle_score:.1f}/100 | {'🟢 Bullish' if rec.pestle_score > 60 else '🔴 Bearish' if rec.pestle_score < 40 else '🟡 Neutral'} |

---

## 📝 Trade Thesis

### Bull Case 🐂
{rec.bull_case}

### Bear Case 🐻
{rec.bear_case}

### Base Case
{rec.base_case}

---

## ⚠️ Risk Management

### Key Risks
"""
        for risk in rec.key_risks:
            output += f"- {risk}\n"

        output += "\n### Invalidation Conditions\n"
        output += "This thesis is invalidated if:\n"
        for condition in rec.invalidation_conditions:
            output += f"- {condition}\n"

        output += f"""
---

## 📅 Upcoming Catalysts
"""
        if results.news_analysis and results.news_analysis.catalysts:
            if results.news_analysis.catalysts.next_major_catalyst:
                output += f"- **Next:** {results.news_analysis.catalysts.next_major_catalyst}\n"
            if results.news_analysis.high_priority_alerts:
                for alert in results.news_analysis.high_priority_alerts[:3]:
                    output += f"- {alert}\n"
        else:
            output += "- No major catalysts identified\n"

        output += f"""
---

## 🔬 Sub-Agent Analysis

### Technical Analysis
"""
        if results.technical_indicators:
            ti = results.technical_indicators
            output += f"""
| Indicator | Value | Signal |
|-----------|-------|--------|
| **RSI (14)** | {ti.rsi_14:.2f} if ti.rsi_14 else 'N/A' | {'Oversold' if ti.rsi_14 and ti.rsi_14 < 30 else 'Overbought' if ti.rsi_14 and ti.rsi_14 > 70 else 'Neutral'} |
| **MACD** | {ti.macd:.4f} if ti.macd else 'N/A' | {'Bullish' if ti.macd and ti.macd > 0 else 'Bearish'} |
| **SMA 20/50/200** | {ti.sma_20:,.2f}/{ti.sma_50:,.2f}/{ti.sma_200:,.2f} | {'Golden' if ti.sma_20 and ti.sma_50 and ti.sma_20 and ti.sma_20 > ti.sma_50 > ti.sma_200 else 'Normal'} |
| **ADX** | {ti.adx:.2f} if ti.adx else 'N/A' | {'Strong Trend' if ti.adx and ti.adx > 25 else 'Weak Trend'} |
"""

        output += "\n### Fundamental Analysis\n"
        if results.fundamental_analysis:
            fa = results.fundamental_analysis
            output += f"- **Overall Score:** {fa.overall_score}/100\n"
            output += f"- **Recommendation:** {fa.recommendation}\n"

        output += "\n### Sentiment Analysis\n"
        if results.sentiment_analysis and results.sentiment_analysis.indicators:
            si = results.sentiment_analysis.indicators
            output += f"- **Overall Sentiment:** {si.overall_sentiment_score:+.2f}\n"
            if si.fear_greed_index:
                output += f"- **Fear & Greed:** {si.fear_greed_index}/100 ({si.fear_greed_classification})\n"

        output += f"""
---

{rec.disclaimer}
"""
        return output


async def main():
    """
    Example usage of Financial Intelligence Trading Agent
    """
    print("=" * 60)
    print("FINANCIAL INTELLIGENCE TRADING AGENT")
    print("=" * 60)

    async with FinancialIntelligenceTradingAgent(
        account_size=100000,
        risk_per_trade=1.0
    ) as agent:
        # Analyze Bitcoin
        print("\n📊 Analyzing Bitcoin (BTC)...")
        btc_result = await agent.analyze('BTC', 'crypto')
        print(agent.format_output(btc_result))

        # Analyze a stock
        print("\n📊 Analyzing Apple (AAPL)...")
        aapl_result = await agent.analyze('AAPL', 'stock')
        print(agent.format_output(aapl_result))


if __name__ == '__main__':
    asyncio.run(main())
