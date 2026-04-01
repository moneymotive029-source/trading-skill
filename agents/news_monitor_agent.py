"""
News Monitor Agent - Real-time news and catalyst tracking
Monitors news sources, economic calendars, and upcoming catalysts.
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsImpact(Enum):
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5


class NewsCategory(Enum):
    EARNINGS = "earnings"
    PRODUCT = "product"
    REGULATORY = "regulatory"
    MACRO = "macro"
    GEOPOLITICAL = "geopolitical"
    MARKET_MOVING = "market_moving"
    MANAGEMENT = "management"
    PARTNERSHIP = "partnership"
    LITIGATION = "litigation"
    OTHER = "other"


@dataclass
class NewsItem:
    """Individual news item"""
    headline: str
    summary: str
    source: str
    url: str
    published_at: datetime
    category: NewsCategory = NewsCategory.OTHER
    impact: NewsImpact = NewsImpact.MEDIUM
    sentiment: float = 0.0  # -1 to +1
    related_symbols: List[str] = field(default_factory=list)
    is_verified: bool = True
    is_breaking: bool = False

    @property
    def age_minutes(self) -> int:
        """Calculate age in minutes"""
        return int((datetime.utcnow() - self.published_at).total_seconds() / 60)

    @property
    def is_fresh(self) -> bool:
        """Check if news is fresh (< 30 minutes old)"""
        return self.age_minutes < 30


@dataclass
class EconomicEvent:
    """Economic calendar event"""
    event_name: str
    country: str
    date: datetime
    actual: Optional[str] = None
    forecast: Optional[str] = None
    previous: Optional[str] = None
    impact: NewsImpact = NewsImpact.MEDIUM
    currency: str = "USD"
    importance: int = 3  # 1-3 scale

    @property
    def surprise(self) -> Optional[float]:
        """Calculate surprise vs forecast"""
        if self.actual and self.forecast:
            try:
                actual_val = float(self.actual.replace('%', ''))
                forecast_val = float(self.forecast.replace('%', ''))
                return actual_val - forecast_val
            except ValueError:
                return None
        return None

    @property
    def is_upcoming(self) -> bool:
        """Check if event is in the future"""
        return self.date > datetime.utcnow()


@dataclass
class CorporateEvent:
    """Corporate event (earnings, dividends, etc.)"""
    event_type: str  # earnings, dividend, split, shareholder_meeting
    symbol: str
    date: datetime
    time: Optional[str] = None  # "BMO" (before market open), "AMC" (after market close)
    estimate: Optional[str] = None
    actual: Optional[str] = None
    fiscal_quarter: Optional[str] = None
    fiscal_year: Optional[str] = None

    @property
    def is_upcoming(self) -> bool:
        return self.date > datetime.utcnow()


@dataclass
class CatalystCalendar:
    """Collection of upcoming catalysts"""
    symbol: str
    news: List[NewsItem] = field(default_factory=list)
    economic_events: List[EconomicEvent] = field(default_factory=list)
    corporate_events: List[CorporateEvent] = field(default_factory=list)

    # Summary
    high_impact_count: int = 0
    fresh_news_count: int = 0
    next_major_catalyst: Optional[str] = None
    next_catalyst_date: Optional[datetime] = None

    def calculate_summary(self):
        """Calculate summary statistics"""
        self.high_impact_count = sum(
            1 for n in self.news if n.impact in [NewsImpact.HIGH, NewsImpact.VERY_HIGH]
        )
        self.fresh_news_count = sum(1 for n in self.news if n.is_fresh)

        # Find next catalyst
        all_dates = []

        for event in self.economic_events:
            if event.is_upcoming:
                all_dates.append((event.date, event.event_name))

        for event in self.corporate_events:
            if event.is_upcoming:
                all_dates.append((event.date, f"{event.symbol} {event.event_type.title()}"))

        if all_dates:
            all_dates.sort(key=lambda x: x[0])
            self.next_catalyst_date, self.next_major_catalyst = all_dates[0]


@dataclass
class NewsAnalysis:
    """Complete news analysis result"""
    symbol: str
    asset_class: str
    timestamp: datetime = None

    # News items
    recent_news: List[NewsItem] = field(default_factory=list)
    breaking_news: List[NewsItem] = field(default_factory=list)

    # Sentiment aggregate
    news_sentiment_score: float = 0.0  # -1 to +1
    news_sentiment_category: str = "Neutral"

    # Catalysts
    catalysts: CatalystCalendar = None

    # Topic analysis
    topic_distribution: Dict[str, int] = field(default_factory=dict)

    # Alerts
    high_priority_alerts: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.catalysts is None:
            self.catalysts = CatalystCalendar(symbol=self.symbol)


class NewsMonitorAgent:
    """
    News Monitor Agent for tracking news and catalysts.

    Features:
    - Real-time news aggregation
    - Economic calendar tracking
    - Corporate event monitoring
    - Sentiment analysis
    - Catalyst identification
    """

    # API Endpoints
    NEWS_API = "https://newsapi.org/v2"
    FINNHUB_API = "https://finnhub.io/api/v1"
    ECONOMIC_CALENDAR_API = "https://api.polygon.io/v1/indicators"

    def __init__(self, api_keys: Dict[str, str] = None):
        """Initialize with optional API keys"""
        self.api_keys = api_keys or {}
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def analyze(self, symbol: str, asset_class: str) -> NewsAnalysis:
        """
        Perform comprehensive news and catalyst analysis.

        Args:
            symbol: Asset symbol
            asset_class: 'crypto', 'stock', 'forex', 'commodity'

        Returns:
            NewsAnalysis with news items and catalyst calendar
        """
        analysis = NewsAnalysis(
            symbol=symbol.upper(),
            asset_class=asset_class.lower()
        )

        # Fetch recent news
        analysis.recent_news = await self._fetch_news(symbol, asset_class)

        # Identify breaking news
        analysis.breaking_news = [
            n for n in analysis.recent_news if n.is_breaking
        ]

        # Fetch economic events
        analysis.catalysts.economic_events = await self._fetch_economic_events(
            asset_class
        )

        # Fetch corporate events
        analysis.catalysts.corporate_events = await self._fetch_corporate_events(
            symbol, asset_class
        )

        # Calculate summary
        analysis.catalysts.calculate_summary()

        # Calculate sentiment
        if analysis.recent_news:
            analysis.news_sentiment_score = sum(
                n.sentiment for n in analysis.recent_news
            ) / len(analysis.recent_news)
            analysis.news_sentiment_category = self._sentiment_to_category(
                analysis.news_sentiment_score
            )

        # Topic distribution
        analysis.topic_distribution = self._analyze_topics(analysis.recent_news)

        # Generate alerts
        analysis.high_priority_alerts = self._generate_alerts(analysis)

        return analysis

    async def _fetch_news(
        self,
        symbol: str,
        asset_class: str
    ) -> List[NewsItem]:
        """Fetch recent news for symbol"""
        news_items = []

        # Mock data - in production, fetch from NewsAPI, Bloomberg, Reuters
        if asset_class.lower() == 'crypto':
            news_items = [
                NewsItem(
                    headline=f"{symbol} ETF Sees Record Daily Inflows",
                    summary="Major institutional investors continue accumulating as ETF records highest single-day inflow since launch.",
                    source="CoinDesk",
                    url="https://coindesk.com/example",
                    published_at=datetime.utcnow() - timedelta(minutes=15),
                    category=NewsCategory.MARKET_MOVING,
                    impact=NewsImpact.HIGH,
                    sentiment=0.75,
                    related_symbols=[symbol],
                    is_breaking=True
                ),
                NewsItem(
                    headline="SEC Delays Decision on Crypto Regulation Framework",
                    summary="Securities and Exchange Commission postpones announcement of comprehensive crypto regulatory framework.",
                    source="Bloomberg",
                    url="https://bloomberg.com/example",
                    published_at=datetime.utcnow() - timedelta(hours=2),
                    category=NewsCategory.REGULATORY,
                    impact=NewsImpact.VERY_HIGH,
                    sentiment=-0.25,
                    related_symbols=[symbol, 'ETH']
                ),
                NewsItem(
                    headline="Major Bank Launches Crypto Custody Service",
                    summary="Leading financial institution announces institutional-grade custody solution for digital assets.",
                    source="Reuters",
                    url="https://reuters.com/example",
                    published_at=datetime.utcnow() - timedelta(hours=4),
                    category=NewsCategory.PARTNERSHIP,
                    impact=NewsImpact.HIGH,
                    sentiment=0.60,
                    related_symbols=[symbol]
                ),
                NewsItem(
                    headline="Network Upgrade Successfully Deployed",
                    summary="Latest protocol upgrade goes live without issues, bringing scalability improvements.",
                    source="The Block",
                    url="https://theblock.co/example",
                    published_at=datetime.utcnow() - timedelta(hours=6),
                    category=NewsCategory.PRODUCT,
                    impact=NewsImpact.MEDIUM,
                    sentiment=0.40,
                    related_symbols=[symbol]
                ),
                NewsItem(
                    headline="Whale Alert: Large Transfer to Exchange Detected",
                    summary="On-chain data shows significant token transfer to major exchange, sparking speculation.",
                    source="Whale Alert",
                    url="https://whalealert.io/example",
                    published_at=datetime.utcnow() - timedelta(hours=8),
                    category=NewsCategory.MARKET_MOVING,
                    impact=NewsImpact.MEDIUM,
                    sentiment=-0.30,
                    related_symbols=[symbol]
                )
            ]

        elif asset_class.lower() == 'stock':
            news_items = [
                NewsItem(
                    headline=f"{symbol} Beats Q4 Earnings Estimates",
                    summary="Company reports quarterly earnings above analyst expectations, raises full-year guidance.",
                    source="CNBC",
                    url="https://cnbc.com/example",
                    published_at=datetime.utcnow() - timedelta(minutes=45),
                    category=NewsCategory.EARNINGS,
                    impact=NewsImpact.VERY_HIGH,
                    sentiment=0.80,
                    related_symbols=[symbol],
                    is_breaking=True
                ),
                NewsItem(
                    headline="Analyst Upgrades Stock to Overweight",
                    summary="Wall Street analyst cites improving fundamentals and attractive valuation.",
                    source="MarketWatch",
                    url="https://marketwatch.com/example",
                    published_at=datetime.utcnow() - timedelta(hours=3),
                    category=NewsCategory.MARKET_MOVING,
                    impact=NewsImpact.MEDIUM,
                    sentiment=0.50,
                    related_symbols=[symbol]
                ),
                NewsItem(
                    headline="New Product Line Announced at Company Event",
                    summary="Unveils next-generation products with AI integration and improved features.",
                    source="WSJ",
                    url="https://wsj.com/example",
                    published_at=datetime.utcnow() - timedelta(hours=5),
                    category=NewsCategory.PRODUCT,
                    impact=NewsImpact.HIGH,
                    sentiment=0.45,
                    related_symbols=[symbol]
                ),
                NewsItem(
                    headline="CEO Discusses Growth Strategy at Conference",
                    summary="Management outlines expansion plans and capital allocation priorities.",
                    source="Reuters",
                    url="https://reuters.com/example",
                    published_at=datetime.utcnow() - timedelta(hours=12),
                    category=NewsCategory.MANAGEMENT,
                    impact=NewsImpact.LOW,
                    sentiment=0.20,
                    related_symbols=[symbol]
                )
            ]

        elif asset_class.lower() == 'forex':
            # For forex, news is about the currencies
            currency = symbol[:3] if '/' in symbol else symbol[:3]
            news_items = [
                NewsItem(
                    headline=f"{currency} Central Bank Signals Rate Hold",
                    summary="Central bank governor indicates pause in rate hiking cycle amid cooling inflation.",
                    source="Reuters",
                    url="https://reuters.com/example",
                    published_at=datetime.utcnow() - timedelta(hours=1),
                    category=NewsCategory.MACRO,
                    impact=NewsImpact.VERY_HIGH,
                    sentiment=0.10,
                    related_symbols=[symbol]
                ),
                NewsItem(
                    headline="GDP Data Beats Expectations",
                    summary="Economic growth accelerates more than forecast in latest quarter.",
                    source="Bloomberg",
                    url="https://bloomberg.com/example",
                    published_at=datetime.utcnow() - timedelta(hours=4),
                    category=NewsCategory.MACRO,
                    impact=NewsImpact.HIGH,
                    sentiment=0.55,
                    related_symbols=[symbol]
                ),
                NewsItem(
                    headline="Political Tensions Ease After Trade Talks",
                    summary="Diplomatic progress reduces geopolitical risk premium.",
                    source="FT",
                    url="https://ft.com/example",
                    published_at=datetime.utcnow() - timedelta(hours=8),
                    category=NewsCategory.GEOPOLITICAL,
                    impact=NewsImpact.MEDIUM,
                    sentiment=0.35,
                    related_symbols=[symbol]
                )
            ]

        else:  # commodity
            news_items = [
                NewsItem(
                    headline=f"{symbol} Inventory Data Shows Unexpected Draw",
                    summary="Weekly inventory report reveals larger-than-expected decline in stockpiles.",
                    source="Reuters",
                    url="https://reuters.com/example",
                    published_at=datetime.utcnow() - timedelta(hours=2),
                    category=NewsCategory.MARKET_MOVING,
                    impact=NewsImpact.HIGH,
                    sentiment=0.65,
                    related_symbols=[symbol],
                    is_breaking=True
                ),
                NewsItem(
                    headline="OPEC+ Maintains Production Quotas",
                    summary="Producer group agrees to keep output levels unchanged at monthly meeting.",
                    source="Bloomberg",
                    url="https://bloomberg.com/example",
                    published_at=datetime.utcnow() - timedelta(hours=6),
                    category=NewsCategory.GEOPOLITICAL,
                    impact=NewsImpact.VERY_HIGH,
                    sentiment=0.30,
                    related_symbols=[symbol, 'BRENT']
                ),
                NewsItem(
                    headline="Demand Forecast Raised for Next Quarter",
                    summary="Industry body increases consumption outlook amid strong economic data.",
                    source="S&P Global",
                    url="https://spglobal.com/example",
                    published_at=datetime.utcnow() - timedelta(hours=10),
                    category=NewsCategory.MACRO,
                    impact=NewsImpact.MEDIUM,
                    sentiment=0.45,
                    related_symbols=[symbol]
                )
            ]

        return news_items

    async def _fetch_economic_events(self, asset_class: str) -> List[EconomicEvent]:
        """Fetch upcoming economic events"""
        events = []

        if asset_class.lower() == 'forex':
            events = [
                EconomicEvent(
                    event_name="Federal Reserve Interest Rate Decision",
                    country="US",
                    date=datetime.utcnow() + timedelta(days=5),
                    forecast="5.50%",
                    previous="5.50%",
                    impact=NewsImpact.VERY_HIGH,
                    currency="USD",
                    importance=3
                ),
                EconomicEvent(
                    event_name="Non-Farm Payrolls",
                    country="US",
                    date=datetime.utcnow() + timedelta(days=12),
                    forecast="185K",
                    previous="210K",
                    impact=NewsImpact.VERY_HIGH,
                    currency="USD",
                    importance=3
                ),
                EconomicEvent(
                    event_name="Consumer Price Index (YoY)",
                    country="US",
                    date=datetime.utcnow() + timedelta(days=18),
                    forecast="3.2%",
                    previous="3.5%",
                    impact=NewsImpact.VERY_HIGH,
                    currency="USD",
                    importance=3
                ),
                EconomicEvent(
                    event_name="ECB Interest Rate Decision",
                    country="EU",
                    date=datetime.utcnow() + timedelta(days=8),
                    forecast="4.50%",
                    previous="4.50%",
                    impact=NewsImpact.VERY_HIGH,
                    currency="EUR",
                    importance=3
                ),
                EconomicEvent(
                    event_name="Retail Sales (MoM)",
                    country="US",
                    date=datetime.utcnow() + timedelta(days=22),
                    forecast="0.3%",
                    previous="0.6%",
                    impact=NewsImpact.HIGH,
                    currency="USD",
                    importance=2
                )
            ]

        elif asset_class.lower() == 'stock':
            events = [
                EconomicEvent(
                    event_name="FOMC Meeting Minutes",
                    country="US",
                    date=datetime.utcnow() + timedelta(days=3),
                    impact=NewsImpact.HIGH,
                    currency="USD",
                    importance=3
                ),
                EconomicEvent(
                    event_name="GDP Growth Rate (QoQ)",
                    country="US",
                    date=datetime.utcnow() + timedelta(days=15),
                    forecast="2.5%",
                    previous="3.0%",
                    impact=NewsImpact.HIGH,
                    currency="USD",
                    importance=3
                ),
                EconomicEvent(
                    event_name="ISM Manufacturing PMI",
                    country="US",
                    date=datetime.utcnow() + timedelta(days=7),
                    forecast="48.5",
                    previous="47.8",
                    impact=NewsImpact.MEDIUM,
                    currency="USD",
                    importance=2
                )
            ]

        return events

    async def _fetch_corporate_events(
        self,
        symbol: str,
        asset_class: str
    ) -> List[CorporateEvent]:
        """Fetch upcoming corporate events"""
        events = []

        if asset_class.lower() == 'stock':
            events = [
                CorporateEvent(
                    event_type="earnings",
                    symbol=symbol,
                    date=datetime.utcnow() + timedelta(days=10),
                    time="AMC",
                    estimate="$1.85",
                    fiscal_quarter="Q1",
                    fiscal_year="2026"
                ),
                CorporateEvent(
                    event_type="dividend",
                    symbol=symbol,
                    date=datetime.utcnow() + timedelta(days=25),
                    estimate="$0.25"
                ),
                CorporateEvent(
                    event_type="shareholder_meeting",
                    symbol=symbol,
                    date=datetime.utcnow() + timedelta(days=45)
                )
            ]

        elif asset_class.lower() == 'crypto':
            # Token unlocks, protocol upgrades
            events = [
                CorporateEvent(
                    event_type="token_unlock",
                    symbol=symbol,
                    date=datetime.utcnow() + timedelta(days=14),
                    estimate="50M tokens"
                ),
                CorporateEvent(
                    event_type="protocol_upgrade",
                    symbol=symbol,
                    date=datetime.utcnow() + timedelta(days=30)
                )
            ]

        return events

    def _analyze_topics(self, news: List[NewsItem]) -> Dict[str, int]:
        """Analyze topic distribution in news"""
        topics = {}
        for item in news:
            category = item.category.value
            topics[category] = topics.get(category, 0) + 1
        return topics

    def _sentiment_to_category(self, score: float) -> str:
        """Convert sentiment score to category"""
        if score >= 0.5:
            return "Very Positive"
        elif score >= 0.2:
            return "Positive"
        elif score >= -0.2:
            return "Neutral"
        elif score >= -0.5:
            return "Negative"
        else:
            return "Very Negative"

    def _generate_alerts(self, analysis: NewsAnalysis) -> List[str]:
        """Generate high-priority alerts"""
        alerts = []

        # Breaking news alert
        if analysis.breaking_news:
            for news in analysis.breaking_news:
                alerts.append(
                    f"🚨 BREAKING: {news.headline} ({news.age_minutes} min ago)"
                )

        # High impact regulatory news
        regulatory = [
            n for n in analysis.recent_news
            if n.category == NewsCategory.REGULATORY and n.impact >= NewsImpact.HIGH
        ]
        if regulatory:
            for n in regulatory:
                alerts.append(f"⚖️ REGULATORY: {n.headline}")

        # Earnings surprise (if recent earnings)
        earnings = [
            n for n in analysis.recent_news
            if n.category == NewsCategory.EARNINGS and n.is_fresh
        ]
        if earnings:
            for e in earnings:
                alerts.append(f"📊 EARNINGS: {e.headline}")

        # Multiple high-impact events
        if analysis.catalysts.high_impact_count >= 3:
            alerts.append(
                f"⚠️ High catalyst density: {analysis.catalysts.high_impact_count} "
                f"high-impact events in monitoring period"
            )

        # Next major catalyst
        if analysis.catalysts.next_major_catalyst:
            days_until = (
                analysis.catalysts.next_catalyst_date - datetime.utcnow()
            ).days if analysis.catalysts.next_catalyst_date else 0
            alerts.append(
                f"📅 Next Catalyst: {analysis.catalysts.next_major_catalyst} "
                f"in {days_until} days"
            )

        return alerts

    def format_output(self, analysis: NewsAnalysis) -> str:
        """Format news analysis as markdown"""
        output = f"""
## News & Catalyst Analysis: {analysis.symbol}

**Asset Class:** {analysis.asset_class.upper()}
**Generated:** {analysis.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

### News Sentiment: {analysis.news_sentiment_category}
| Metric | Value |
|--------|-------|
| **Sentiment Score** | {analysis.news_sentiment_score:+.2f} |
| **Recent Articles** | {len(analysis.recent_news)} |
| **Breaking News** | {len(analysis.breaking_news)} |
| **High Impact** | {analysis.catalysts.high_impact_count} |
"""

        # Topic distribution
        if analysis.topic_distribution:
            output += "\n### Topic Distribution\n"
            output += "| Category | Count |\n"
            output += "|----------|-------|\n"
            for category, count in sorted(
                analysis.topic_distribution.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                output += f"| {category.title()} | {count} |\n"

        # Recent news
        if analysis.recent_news:
            output += "\n### Recent News\n"
            output += "| Time | Headline | Source | Impact |\n"
            output += "|------|----------|--------|--------|\n"
            for news in analysis.recent_news[:10]:
                time_str = f"{news.age_minutes}m ago" if news.age_minutes < 60 else f"{news.age_minutes // 60}h ago"
                impact_emoji = "🔴" if news.impact == NewsImpact.VERY_HIGH else \
                               "🟠" if news.impact == NewsImpact.HIGH else \
                               "🟡" if news.impact == NewsImpact.MEDIUM else "🟢"
                breaking = " 🚨" if news.is_breaking else ""
                sentiment_emoji = "🟢" if news.sentiment > 0.3 else \
                                  "🔴" if news.sentiment < -0.3 else "🟡"
                output += f"| {time_str} | {news.headline[:50]}... | {news.source} | {impact_emoji}{sentiment_emoji}{breaking} |\n"

        # Alerts
        if analysis.high_priority_alerts:
            output += "\n### 🚨 Alerts\n"
            for alert in analysis.high_priority_alerts:
                output += f"- {alert}\n"

        # Economic calendar
        if analysis.catalysts.economic_events:
            output += "\n### Economic Calendar\n"
            output += "| Date | Event | Country | Impact | Forecast | Previous |\n"
            output += "|------|-------|---------|--------|----------|----------|\n"
            for event in analysis.catalysts.economic_events[:5]:
                date_str = event.date.strftime('%Y-%m-%d')
                impact_emoji = "🔴" if event.impact == NewsImpact.VERY_HIGH else \
                               "🟠" if event.impact == NewsImpact.HIGH else "🟡"
                output += f"| {date_str} | {event.event_name} | {event.country} | {impact_emoji} | {event.forecast or '-'} | {event.previous or '-'} |\n"

        # Corporate events
        if analysis.catalysts.corporate_events:
            output += "\n### Corporate Events\n"
            output += "| Date | Event | Symbol | Details |\n"
            output += "|------|-------|--------|---------|\n"
            for event in analysis.catalysts.corporate_events[:5]:
                date_str = event.date.strftime('%Y-%m-%d')
                details = event.estimate or event.actual or '-'
                output += f"| {date_str} | {event.event_type.title()} | {event.symbol} | {details} |\n"

        return output


async def main():
    """Example usage of NewsMonitorAgent"""
    async with NewsMonitorAgent() as agent:
        # Analyze Bitcoin news
        btc_news = await agent.analyze('BTC', 'crypto')
        print(agent.format_output(btc_news))

        # Analyze stock news
        aapl_news = await agent.analyze('AAPL', 'stock')
        print(agent.format_output(aapl_news))


if __name__ == '__main__':
    asyncio.run(main())
