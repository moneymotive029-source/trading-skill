"""
Sentiment Analysis Agent - News, social media, and positioning sentiment
Analyzes market sentiment from multiple sources for trading signals.
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentCategory(Enum):
    VERY_BEARISH = -2
    BEARISH = -1
    NEUTRAL = 0
    BULLISH = 1
    VERY_BULLISH = 2


@dataclass
class NewsSentiment:
    """Sentiment from news sources"""
    total_articles: int = 0
    positive_articles: int = 0
    neutral_articles: int = 0
    negative_articles: int = 0

    sentiment_score: float = 0.0  # -1 to +1
    sentiment_category: SentimentCategory = SentimentCategory.NEUTRAL

    # Topic breakdown
    topics: Dict[str, int] = None

    # Recent headlines
    recent_headlines: List[Dict[str, str]] = None

    def __post_init__(self):
        if self.topics is None:
            self.topics = {}
        if self.recent_headlines is None:
            self.recent_headlines = []


@dataclass
class SocialSentiment:
    """Sentiment from social media"""
    platform: str
    total_mentions: int = 0
    sentiment_score: float = 0.0  # -1 to +1
    sentiment_category: SentimentCategory = SentimentCategory.NEUTRAL

    # Engagement metrics
    total_likes: int = 0
    total_shares: int = 0
    total_comments: int = 0

    # Influencer sentiment
    influencer_sentiment: float = 0.0  # -1 to +1

    # Trending metrics
    mention_change_24h: float = 0.0  # % change
    sentiment_momentum: str = "Stable"  # Improving, Stable, Deteriorating


@dataclass
class PositioningData:
    """Institutional positioning data"""
    # COT Report (Commitment of Traders)
    managed_money_long: Optional[int] = None
    managed_money_short: Optional[int] = None
    managed_money_net: Optional[int] = None
    dealer_long: Optional[int] = None
    dealer_short: Optional[int] = None
    leveraged_funds_long: Optional[int] = None
    leveraged_funds_short: Optional[int] = None

    # Calculated metrics
    net_positioning: str = "Neutral"  # Net Long, Neutral, Net Short
    positioning_extreme: bool = False
    positioning_change_wow: float = 0.0  # % change in net

    # Put/Call ratios (for equities)
    put_call_ratio: Optional[float] = None
    put_call_interpretation: str = "Neutral"  # Bullish, Neutral, Bearish

    # Short interest (for stocks)
    short_interest_pct: Optional[float] = None
    short_interest_ratio: Optional[float] = None  # Days to cover
    short_interest_change: Optional[float] = None  # % change


@dataclass
class SentimentIndicators:
    """Aggregate sentiment indicators"""
    # Fear & Greed (crypto-specific)
    fear_greed_index: Optional[int] = None  # 0-100
    fear_greed_classification: str = "Neutral"  # Extreme Fear, Fear, Neutral, Greed, Extreme Greed

    # Aggregate scores
    news_sentiment_score: float = 0.0  # -1 to +1
    social_sentiment_score: float = 0.0  # -1 to +1
    positioning_score: float = 0.0  # -1 to +1

    # Overall
    overall_sentiment_score: float = 0.0  # -1 to +1
    overall_sentiment_category: SentimentCategory = SentimentCategory.NEUTRAL
    confidence_level: str = "Medium"  # Low, Medium, High

    # Contrarian signals
    contrarian_signal: str = "None"  # Buy the Fear, Sell the Greed, None
    sentiment_divergence: bool = False


@dataclass
class SentimentAnalysis:
    """Complete sentiment analysis result"""
    symbol: str
    asset_class: str
    timestamp: datetime = None

    news: Optional[NewsSentiment] = None
    social: List[SocialSentiment] = None
    positioning: Optional[PositioningData] = None
    indicators: Optional[SentimentIndicators] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.social is None:
            self.social = []


class SentimentAnalysisAgent:
    """
    Sentiment Analysis Agent for analyzing market sentiment.

    Analyzes:
    - News sentiment from major financial sources
    - Social media sentiment (Reddit, Twitter, StockTwits)
    - Institutional positioning (COT, put/call, short interest)
    - Fear & Greed indicators
    """

    # API Endpoints
    NEWS_API = "https://newsapi.org/v2"
    REDDIT_API = "https://oauth.reddit.com"
    STOCKTWITS_API = "https://api.stocktwits.com/api/2"

    # Sentiment lexicons
    BULLISH_WORDS = [
        'bullish', 'surge', 'rally', 'breakout', 'moon', 'buy', 'long',
        'undervalued', 'opportunity', 'growth', 'beat', 'outperform',
        'upgrade', 'target raised', 'strong buy', 'accumulating'
    ]

    BEARISH_WORDS = [
        'bearish', 'crash', 'dump', 'sell-off', 'correction', 'short',
        'overvalued', 'risk', 'decline', 'miss', 'underperform',
        'downgrade', 'target cut', 'strong sell', 'distributing'
    ]

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

    async def analyze(self, symbol: str, asset_class: str) -> SentimentAnalysis:
        """
        Perform comprehensive sentiment analysis.

        Args:
            symbol: Asset symbol
            asset_class: 'crypto', 'stock', 'forex', 'commodity'

        Returns:
            SentimentAnalysis with all sentiment data
        """
        analysis = SentimentAnalysis(
            symbol=symbol.upper(),
            asset_class=asset_class.lower()
        )

        # Gather all sentiment data
        analysis.news = await self._analyze_news_sentiment(symbol, asset_class)
        analysis.social = await self._analyze_social_sentiment(symbol, asset_class)
        analysis.positioning = await self._analyze_positioning(symbol, asset_class)

        # Calculate aggregate indicators
        analysis.indicators = self._calculate_indicators(analysis)

        return analysis

    def _analyze_text_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of text using lexicon-based approach.
        Returns score from -1 (very bearish) to +1 (very bullish)
        """
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)

        bullish_count = sum(1 for word in words if word in self.BULLISH_WORDS)
        bearish_count = sum(1 for word in words if word in self.BEARISH_WORDS)

        total = bullish_count + bearish_count
        if total == 0:
            return 0.0

        # Normalize to -1 to +1
        return (bullish_count - bearish_count) / total

    def _score_to_category(self, score: float) -> SentimentCategory:
        """Convert numerical score to category"""
        if score >= 0.6:
            return SentimentCategory.VERY_BULLISH
        elif score >= 0.2:
            return SentimentCategory.BULLISH
        elif score >= -0.2:
            return SentimentCategory.NEUTRAL
        elif score >= -0.6:
            return SentimentCategory.BEARISH
        else:
            return SentimentCategory.VERY_BEARISH

    async def _analyze_news_sentiment(self, symbol: str, asset_class: str) -> NewsSentiment:
        """Analyze news sentiment"""
        news = NewsSentiment()

        # Mock data - in production, fetch from NewsAPI, Bloomberg, Reuters
        # Simulate realistic news sentiment data

        if asset_class.lower() == 'crypto':
            # Crypto tends to have more volatile sentiment
            news.total_articles = 156
            news.positive_articles = 72
            news.neutral_articles = 52
            news.negative_articles = 32

            news.topics = {
                'regulation': 45,
                'adoption': 38,
                'technology': 28,
                'price_action': 65,
                'defi': 24
            }

            news.recent_headlines = [
                {'title': 'Bitcoin ETF Sees Record Inflows', 'sentiment': 'positive', 'source': 'CoinDesk'},
                {'title': 'SEC Delays Decision on Crypto ETF', 'sentiment': 'negative', 'source': 'Bloomberg'},
                {'title': 'Major Bank Launches Crypto Custody', 'sentiment': 'positive', 'source': 'Reuters'},
                {'title': 'DeFi Protocol Suffers Exploit', 'sentiment': 'negative', 'source': 'The Block'},
                {'title': 'Institutional Adoption Continues', 'sentiment': 'positive', 'source': 'CoinTelegraph'}
            ]

        elif asset_class.lower() == 'stock':
            news.total_articles = 89
            news.positive_articles = 42
            news.neutral_articles = 35
            news.negative_articles = 12

            news.topics = {
                'earnings': 35,
                'analyst_ratings': 18,
                'product_news': 22,
                'management': 8,
                'sector_trends': 15
            }

            news.recent_headlines = [
                {'title': 'Company Beats Earnings Estimates', 'sentiment': 'positive', 'source': 'CNBC'},
                {'title': 'Analyst Raises Price Target', 'sentiment': 'positive', 'source': 'MarketWatch'},
                {'title': 'New Product Launch Announced', 'sentiment': 'positive', 'source': 'WSJ'},
                {'title': 'Sector Faces Headwinds', 'sentiment': 'negative', 'source': 'Bloomberg'},
                {'title': 'CEO Discusses Growth Strategy', 'sentiment': 'neutral', 'source': 'Reuters'}
            ]

        elif asset_class.lower() == 'forex':
            news.total_articles = 45
            news.positive_articles = 18
            news.neutral_articles = 20
            news.negative_articles = 7

            news.topics = {
                'central_bank': 22,
                'economic_data': 15,
                'geopolitics': 8
            }

            news.recent_headlines = [
                {'title': 'Central Bank Signals Rate Hold', 'sentiment': 'neutral', 'source': 'Reuters'},
                {'title': 'GDP Data Beats Expectations', 'sentiment': 'positive', 'source': 'Bloomberg'},
                {'title': 'Inflation Remains Elevated', 'sentiment': 'negative', 'source': 'FT'}
            ]

        else:  # commodity
            news.total_articles = 32
            news.positive_articles = 14
            news.neutral_articles = 12
            news.negative_articles = 6

            news.topics = {
                'supply_demand': 15,
                'inventory': 8,
                'geopolitics': 9
            }

        # Calculate sentiment score
        if news.total_articles > 0:
            news.sentiment_score = (
                (news.positive_articles - news.negative_articles) / news.total_articles
            )
        news.sentiment_category = self._score_to_category(news.sentiment_score)

        return news

    async def _analyze_social_sentiment(self, symbol: str, asset_class: str) -> List[SocialSentiment]:
        """Analyze social media sentiment from multiple platforms"""
        sentiments = []

        # Reddit sentiment
        reddit = SocialSentiment(platform='reddit')
        if asset_class.lower() == 'crypto':
            subreddit = f"r/{symbol.lower()}"
            reddit.total_mentions = 2450
            reddit.sentiment_score = 0.35
            reddit.total_likes = 45000
            reddit.total_shares = 8500
            reddit.total_comments = 12000
            reddit.influencer_sentiment = 0.40
            reddit.mention_change_24h = 15.5
            reddit.sentiment_momentum = "Improving"
        elif asset_class.lower() == 'stock':
            reddit.total_mentions = 1850
            reddit.sentiment_score = 0.25
            reddit.total_likes = 32000
            reddit.total_shares = 5200
            reddit.total_comments = 8500
            reddit.influencer_sentiment = 0.30
            reddit.mention_change_24h = 8.2
            reddit.sentiment_momentum = "Stable"
        else:
            reddit.total_mentions = 450
            reddit.sentiment_score = 0.10
            reddit.mention_change_24h = -5.0
            reddit.sentiment_momentum = "Stable"

        reddit.sentiment_category = self._score_to_category(reddit.sentiment_score)
        sentiments.append(reddit)

        # Twitter/X sentiment
        twitter = SocialSentiment(platform='twitter')
        if asset_class.lower() == 'crypto':
            twitter.total_mentions = 15600
            twitter.sentiment_score = 0.42
            twitter.total_likes = 125000
            twitter.total_shares = 35000
            twitter.total_comments = 28000
            twitter.influencer_sentiment = 0.55
            twitter.mention_change_24h = 22.0
            twitter.sentiment_momentum = "Improving"
        elif asset_class.lower() == 'stock':
            twitter.total_mentions = 8900
            twitter.sentiment_score = 0.28
            twitter.total_likes = 65000
            twitter.total_shares = 12000
            twitter.total_comments = 15000
            twitter.influencer_sentiment = 0.35
            twitter.mention_change_24h = 5.5
            twitter.sentiment_momentum = "Stable"
        else:
            twitter.total_mentions = 1200
            twitter.sentiment_score = 0.05
            twitter.mention_change_24h = -2.0
            twitter.sentiment_momentum = "Stable"

        twitter.sentiment_category = self._score_to_category(twitter.sentiment_score)
        sentiments.append(twitter)

        # StockTwits (for stocks/crypto)
        if asset_class.lower() in ['stock', 'crypto']:
            stocktwits = SocialSentiment(platform='stocktwits')
            stocktwits.total_mentions = 5600 if asset_class.lower() == 'crypto' else 3200
            stocktwits.sentiment_score = 0.38 if asset_class.lower() == 'crypto' else 0.22
            stocktwits.influencer_sentiment = 0.45 if asset_class.lower() == 'crypto' else 0.28
            stocktwits.mention_change_24h = 12.0 if asset_class.lower() == 'crypto' else 3.5
            stocktwits.sentiment_momentum = "Improving" if asset_class.lower() == 'crypto' else "Stable"
            stocktwits.sentiment_category = self._score_to_category(stocktwits.sentiment_score)
            sentiments.append(stocktwits)

        return sentiments

    async def _analyze_positioning(self, symbol: str, asset_class: str) -> PositioningData:
        """Analyze institutional positioning data"""
        positioning = PositioningData()

        if asset_class.lower() == 'crypto':
            # Crypto positioning (simulated from futures data)
            positioning.managed_money_long = 125000
            positioning.managed_money_short = 85000
            positioning.managed_money_net = 40000
            positioning.leveraged_funds_long = 280000
            positioning.leveraged_funds_short = 195000
            positioning.net_positioning = "Net Long"
            positioning.positioning_extreme = False
            positioning.positioning_change_wow = 8.5

        elif asset_class.lower() == 'stock':
            # Stock positioning
            positioning.put_call_ratio = 0.72
            positioning.put_call_interpretation = "Bullish"  # < 0.7 is bullish
            positioning.short_interest_pct = 3.5
            positioning.short_interest_ratio = 2.8
            positioning.short_interest_change = -0.5
            positioning.net_positioning = "Neutral"

        elif asset_class.lower() == 'forex':
            # COT report data for forex
            if 'EUR' in symbol.upper():
                positioning.managed_money_long = 185000
                positioning.managed_money_short = 125000
                positioning.managed_money_net = 60000
                positioning.dealer_long = 95000
                positioning.dealer_short = 145000
                positioning.leveraged_funds_long = 220000
                positioning.leveraged_funds_short = 165000
                positioning.net_positioning = "Net Long"
                positioning.positioning_change_wow = 5.2
            else:
                positioning.managed_money_long = 95000
                positioning.managed_money_short = 115000
                positioning.managed_money_net = -20000
                positioning.net_positioning = "Net Short"
                positioning.positioning_change_wow = -3.5

        elif asset_class.lower() == 'commodity':
            # COT report for commodities
            if symbol.upper() == 'GOLD':
                positioning.managed_money_long = 245000
                positioning.managed_money_short = 95000
                positioning.managed_money_net = 150000
                positioning.dealer_long = 85000
                positioning.dealer_short = 215000
                positioning.net_positioning = "Net Long"
                positioning.positioning_extreme = True
                positioning.positioning_change_wow = 12.5
            elif symbol.upper() in ['CRUDE', 'BRENT']:
                positioning.managed_money_long = 185000
                positioning.managed_money_short = 145000
                positioning.managed_money_net = 40000
                positioning.net_positioning = "Net Long"
                positioning.positioning_change_wow = -2.5
            else:
                positioning.net_positioning = "Neutral"

        return positioning

    def _calculate_indicators(self, analysis: SentimentAnalysis) -> SentimentIndicators:
        """Calculate aggregate sentiment indicators"""
        indicators = SentimentIndicators()

        # News sentiment score
        if analysis.news:
            indicators.news_sentiment_score = analysis.news.sentiment_score

        # Social sentiment score (weighted average across platforms)
        if analysis.social:
            total_weight = 0
            weighted_score = 0
            for social in analysis.social:
                weight = 1.0
                if social.platform == 'twitter':
                    weight = 1.5  # Higher weight for Twitter
                elif social.platform == 'stocktwits':
                    weight = 1.2
                weighted_score += social.sentiment_score * weight
                total_weight += weight
            indicators.social_sentiment_score = weighted_score / total_weight if total_weight > 0 else 0

        # Positioning score
        if analysis.positioning:
            if analysis.positioning.net_positioning == "Net Long":
                indicators.positioning_score = 0.5
            elif analysis.positioning.net_positioning == "Net Short":
                indicators.positioning_score = -0.5

            # Adjust for extreme positioning (contrarian signal)
            if analysis.positioning.positioning_extreme:
                if analysis.positioning.net_positioning == "Net Long":
                    indicators.positioning_score = 0.3  # Reduce bullish score
                else:
                    indicators.positioning_score = -0.3

            # Put/call interpretation
            if analysis.positioning.put_call_interpretation == "Bullish":
                indicators.positioning_score += 0.2
            elif analysis.positioning.put_call_interpretation == "Bearish":
                indicators.positioning_score -= 0.2

            # Clamp to -1 to +1
            indicators.positioning_score = max(-1, min(1, indicators.positioning_score))

        # Calculate overall sentiment (weighted average)
        weights = {'news': 0.35, 'social': 0.35, 'positioning': 0.30}
        indicators.overall_sentiment_score = (
            indicators.news_sentiment_score * weights['news'] +
            indicators.social_sentiment_score * weights['social'] +
            indicators.positioning_score * weights['positioning']
        )

        indicators.overall_sentiment_category = self._score_to_category(
            indicators.overall_sentiment_score
        )

        # Fear & Greed index (crypto-specific)
        if analysis.asset_class.lower() == 'crypto':
            # Calculate from component scores
            base_score = indicators.overall_sentiment_score
            indicators.fear_greed_index = int((base_score + 1) * 50)  # Convert -1 to +1 into 0-100

            if indicators.fear_greed_index >= 75:
                indicators.fear_greed_classification = "Extreme Greed"
            elif indicators.fear_greed_index >= 55:
                indicators.fear_greed_classification = "Greed"
            elif indicators.fear_greed_index >= 45:
                indicators.fear_greed_classification = "Neutral"
            elif indicators.fear_greed_index >= 25:
                indicators.fear_greed_classification = "Fear"
            else:
                indicators.fear_greed_classification = "Extreme Fear"

            # Contrarian signal
            if indicators.fear_greed_classification == "Extreme Fear":
                indicators.contrarian_signal = "Buy the Fear"
            elif indicators.fear_greed_classification == "Extreme Greed":
                indicators.contrarian_signal = "Sell the Greed"

        # Confidence level based on data convergence
        scores = [
            indicators.news_sentiment_score,
            indicators.social_sentiment_score,
            indicators.positioning_score
        ]
        score_range = max(scores) - min(scores)
        if score_range < 0.3:
            indicators.confidence_level = "High"  # All sources agree
        elif score_range < 0.6:
            indicators.confidence_level = "Medium"
        else:
            indicators.confidence_level = "Low"  # Sources disagree significantly
            indicators.sentiment_divergence = True

        return indicators

    def format_output(self, analysis: SentimentAnalysis) -> str:
        """Format sentiment analysis as markdown"""
        output = f"""
## Sentiment Analysis: {analysis.symbol}

**Timestamp:** {analysis.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

### Overall Sentiment
| Metric | Value |
|--------|-------|
| **Overall Score** | {analysis.indicators.overall_sentiment_score:+.2f} |
| **Classification** | {analysis.indicators.overall_sentiment_category.name} |
| **Confidence** | {analysis.indicators.confidence_level} |
"""

        if analysis.indicators.fear_greed_index:
            output += f"""
### Fear & Greed Index
| Metric | Value |
|--------|-------|
| **Index** | {analysis.indicators.fear_greed_index}/100 |
| **Classification** | {analysis.indicators.fear_greed_classification} |
| **Contrarian Signal** | {analysis.indicators.contrarian_signal} |
"""

        if analysis.news:
            news = analysis.news
            output += f"""
### News Sentiment
| Metric | Value |
|--------|-------|
| **Total Articles** | {news.total_articles} |
| **Positive** | {news.positive_articles} ({news.positive_articles/news.total_articles*100:.1f}%) |
| **Neutral** | {news.neutral_articles} ({news.neutral_articles/news.total_articles*100:.1f}%) |
| **Negative** | {news.negative_articles} ({news.negative_articles/news.total_articles*100:.1f}%) |
| **Sentiment Score** | {news.sentiment_score:+.2f} |

**Topic Breakdown:**
"""
            for topic, count in news.topics.items():
                output += f"- {topic.title()}: {count} articles\n"

            if news.recent_headlines:
                output += "\n**Recent Headlines:**\n"
                for headline in news.recent_headlines[:5]:
                    emoji = "🟢" if headline['sentiment'] == 'positive' else "🔴" if headline['sentiment'] == 'negative' else "🟡"
                    output += f"- {emoji} {headline['title']} ({headline['source']})\n"

        if analysis.social:
            output += "\n### Social Media Sentiment\n"
            output += "| Platform | Mentions | Sentiment | Momentum |\n"
            output += "|----------|----------|-----------|----------|\n"
            for social in analysis.social:
                output += f"| {social.platform.title()} | {social.total_mentions:,} | {social.sentiment_score:+.2f} | {social.sentiment_momentum} |\n"

        if analysis.positioning:
            pos = analysis.positioning
            output += f"""
### Institutional Positioning
| Metric | Value |
|--------|-------|
| **Net Positioning** | {pos.net_positioning} |
| **Positioning Change (WoW)** | {pos.positioning_change_wow:+.1f}% |
| **Extreme Positioning** | {'Yes ⚠️' if pos.positioning_extreme else 'No'} |
"""
            if pos.put_call_ratio:
                output += f"""
| Metric | Value |
|--------|-------|
| **Put/Call Ratio** | {pos.put_call_ratio:.2f} |
| **Interpretation** | {pos.put_call_interpretation} |
| **Short Interest** | {pos.short_interest_pct:.2f}% |
| **Days to Cover** | {pos.short_interest_ratio:.1f} |
"""
            if pos.managed_money_net is not None:
                output += f"""
**COT Report:**
- Managed Money Net: {pos.managed_money_net:+,}
- Leveraged Funds Net: {(pos.leveraged_funds_long - pos.leveraged_funds_short):+,}
"""

        if analysis.indicators.sentiment_divergence:
            output += """
⚠️ **Sentiment Divergence Detected**
Different sentiment sources are showing conflicting signals. Exercise caution.
"""

        return output


async def main():
    """Example usage of SentimentAnalysisAgent"""
    async with SentimentAnalysisAgent() as agent:
        # Analyze Bitcoin sentiment
        btc_sentiment = await agent.analyze('BTC', 'crypto')
        print(agent.format_output(btc_sentiment))

        # Analyze stock sentiment
        aapl_sentiment = await agent.analyze('AAPL', 'stock')
        print(agent.format_output(aapl_sentiment))


if __name__ == '__main__':
    asyncio.run(main())
