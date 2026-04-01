"""
Market Data Agent - Real-time price, volume, and level data collection
Fetches market data from multiple sources for crypto, stocks, forex, and commodities.
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MarketData:
    """Standardized market data structure"""
    symbol: str
    asset_class: str
    current_price: float
    price_change_24h: float
    price_change_7d: float
    price_change_30d: float
    volume_24h: float
    market_cap: float
    high_24h: float
    low_24h: float
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    spread: Optional[float] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class MarketDataAgent:
    """
    Market Data Agent for collecting real-time market data.

    Supports:
    - Cryptocurrencies (CoinGecko, CoinMarketCap)
    - Stocks (Yahoo Finance, Alpha Vantage)
    - Forex (FXCM, OANDA APIs)
    - Commodities (Kitco, EIA)
    """

    # API Endpoints
    COINGECKO_API = "https://api.coingecko.com/api/v3"
    YAHOO_FINANCE_API = "https://query1.finance.yahoo.com/v8/finance/chart"

    # Crypto ID mappings
    CRYPTO_IDS = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'SOL': 'solana',
        'BNB': 'binancecoin',
        'XRP': 'ripple',
        'ADA': 'cardano',
        'DOGE': 'dogecoin',
        'MATIC': 'matic-network',
        'LINK': 'chainlink',
        'AVAX': 'avalanche-2'
    }

    def __init__(self, api_keys: Dict[str, str] = None):
        """Initialize with optional API keys"""
        self.api_keys = api_keys or {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Tuple[MarketData, datetime]] = {}
        self.cache_ttl = timedelta(minutes=5)  # Cache valid for 5 minutes

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_market_data(self, symbol: str, asset_class: str = 'crypto') -> MarketData:
        """
        Fetch market data for a given symbol.

        Args:
            symbol: Asset symbol (e.g., 'BTC', 'AAPL', 'EURUSD')
            asset_class: 'crypto', 'stock', 'forex', 'commodity'

        Returns:
            MarketData object with current price and metrics
        """
        # Check cache first
        if symbol in self.cache:
            cached_data, cached_time = self.cache[symbol]
            if datetime.utcnow() - cached_time < self.cache_ttl:
                logger.info(f"Cache hit for {symbol}")
                return cached_data

        # Fetch based on asset class
        if asset_class == 'crypto':
            data = await self._fetch_crypto_data(symbol)
        elif asset_class == 'stock':
            data = await self._fetch_stock_data(symbol)
        elif asset_class == 'forex':
            data = await self._fetch_forex_data(symbol)
        elif asset_class == 'commodity':
            data = await self._fetch_commodity_data(symbol)
        else:
            raise ValueError(f"Unknown asset class: {asset_class}")

        # Cache the result
        self.cache[symbol] = (data, datetime.utcnow())

        return data

    async def _fetch_crypto_data(self, symbol: str) -> MarketData:
        """Fetch cryptocurrency data from CoinGecko"""
        coin_id = self.CRYPTO_IDS.get(symbol.upper())
        if not coin_id:
            raise ValueError(f"Unknown crypto symbol: {symbol}")

        url = f"{self.COINGECKO_API}/coins/{coin_id}"
        params = {
            'localization': 'false',
            'tickers': 'false',
            'community_data': 'false',
            'developer_data': 'false'
        }

        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                market_data = data.get('market_data', {})

                return MarketData(
                    symbol=symbol.upper(),
                    asset_class='crypto',
                    current_price=market_data.get('current_price', {}).get('usd', 0),
                    price_change_24h=market_data.get('price_change_percentage_24h', 0),
                    price_change_7d=market_data.get('price_change_percentage_7d', 0),
                    price_change_30d=market_data.get('price_change_percentage_30d', 0),
                    volume_24h=market_data.get('total_volume', {}).get('usd', 0),
                    market_cap=market_data.get('market_cap', {}).get('usd', 0),
                    high_24h=market_data.get('high_24h', {}).get('usd', 0),
                    low_24h=market_data.get('low_24h', {}).get('usd', 0),
                    timestamp=datetime.utcnow()
                )
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching crypto data: {e}")
            raise

    async def _fetch_stock_data(self, symbol: str) -> MarketData:
        """Fetch stock data from Yahoo Finance"""
        url = f"{self.YAHOO_FINANCE_API}/{symbol}"
        params = {'interval': '1d', 'range': '1y'}

        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                result = data.get('chart', {}).get('result', [{}])[0]
                if not result:
                    raise ValueError(f"No data found for {symbol}")

                meta = result.get('meta', {})
                quote = result.get('indicators', {}).get('quote', [{}])[0]

                # Calculate 52-week high/low from historical data
                timestamps = result.get('timestamp', [])
                highs = quote.get('high', [])
                lows = quote.get('low', [])

                high_52w = max(highs) if highs else None
                low_52w = min(lows) if lows else None

                current_price = meta.get('regularMarketPrice', 0)
                prev_close = meta.get('chartPreviousClose', current_price)
                price_change_24h = ((current_price - prev_close) / prev_close) * 100 if prev_close else 0

                return MarketData(
                    symbol=symbol.upper(),
                    asset_class='stock',
                    current_price=current_price,
                    price_change_24h=price_change_24h,
                    price_change_7d=0,  # Would need more calculation
                    price_change_30d=0,
                    volume_24h=quote.get('volume', [0])[-1] if quote.get('volume') else 0,
                    market_cap=meta.get('marketCap', 0),
                    high_24h=meta.get('regularMarketDayHigh', 0),
                    low_24h=meta.get('regularMarketDayLow', 0),
                    high_52w=high_52w,
                    low_52w=low_52w,
                    timestamp=datetime.utcnow()
                )
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching stock data: {e}")
            raise

    async def _fetch_forex_data(self, symbol: str) -> MarketData:
        """Fetch forex data (simplified - would use OANDA/FXCM in production)"""
        # Normalize symbol (e.g., 'EURUSD' -> 'EUR/USD')
        if '/' not in symbol:
            symbol = symbol[:3] + '/' + symbol[3:]

        # Mock data - in production, use real forex API
        base_rates = {
            'EUR/USD': 1.0850,
            'GBP/USD': 1.2650,
            'USD/JPY': 151.50,
            'USD/CHF': 0.9050,
            'AUD/USD': 0.6550,
            'USD/CAD': 1.3550,
        }

        current_price = base_rates.get(symbol, 1.0)

        return MarketData(
            symbol=symbol,
            asset_class='forex',
            current_price=current_price,
            price_change_24h=0.15,  # Mock
            price_change_7d=-0.3,
            price_change_30d=1.2,
            volume_24h=0,  # Forex doesn't have volume in same way
            market_cap=0,
            high_24h=current_price * 1.002,
            low_24h=current_price * 0.998,
            timestamp=datetime.utcnow()
        )

    async def _fetch_commodity_data(self, symbol: str) -> MarketData:
        """Fetch commodity data (simplified - would use Kitco/EIA in production)"""
        # Mock data - in production, use real commodity API
        commodity_prices = {
            'GOLD': 2035.50,
            'SILVER': 22.85,
            'CRUDE': 78.50,
            'BRENT': 82.30,
            'NATGAS': 1.85,
            'COPPER': 3.85,
            'WHEAT': 6.25,
            'CORN': 4.35,
        }

        current_price = commodity_prices.get(symbol.upper(), 0)

        return MarketData(
            symbol=symbol.upper(),
            asset_class='commodity',
            current_price=current_price,
            price_change_24h=-0.5,
            price_change_7d=2.1,
            price_change_30d=-3.2,
            volume_24h=0,
            market_cap=0,
            high_24h=current_price * 1.01,
            low_24h=current_price * 0.99,
            timestamp=datetime.utcnow()
        )

    async def fetch_multiple(self, symbols: List[Tuple[str, str]]) -> Dict[str, MarketData]:
        """
        Fetch market data for multiple symbols concurrently.

        Args:
            symbols: List of (symbol, asset_class) tuples

        Returns:
            Dict mapping symbol to MarketData
        """
        tasks = [self.fetch_market_data(sym, ac) for sym, ac in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        data = {}
        for (symbol, _), result in zip(symbols, results):
            if isinstance(result, MarketData):
                data[symbol] = result
            else:
                logger.error(f"Failed to fetch {symbol}: {result}")

        return data

    def get_key_levels(self, data: MarketData) -> Dict[str, float]:
        """
        Calculate key support/resistance levels from market data.

        Returns:
            Dict with support and resistance levels
        """
        price = data.current_price

        # Pivot points
        high = data.high_24h
        low = data.low_24h

        pivot = (high + low + price) / 3
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        r3 = high + 2 * (pivot - low)
        s3 = low - 2 * (high - pivot)

        return {
            'pivot': pivot,
            'resistance_1': r1,
            'resistance_2': r2,
            'resistance_3': r3,
            'support_1': s1,
            'support_2': s2,
            'support_3': s3,
            'high_24h': high,
            'low_24h': low,
        }

    def format_output(self, data: MarketData, include_levels: bool = True) -> str:
        """
        Format market data as markdown table for display.

        Args:
            data: MarketData object
            include_levels: Whether to include support/resistance levels

        Returns:
            Formatted markdown string
        """
        output = f"""
## Market Data: {data.symbol} ({data.asset_class.upper()})
**Timestamp:** {data.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

### Price Data
| Metric | Value |
|--------|-------|
| Current Price | ${data.current_price:,.2f} |
| 24h Change | {data.price_change_24h:+.2f}% |
| 7D Change | {data.price_change_7d:+.2f}% |
| 30D Change | {data.price_change_30d:+.2f}% |

### Volume & Market Cap
| Metric | Value |
|--------|-------|
| 24h Volume | ${data.volume_24h:,.0f} |
| Market Cap | ${data.market_cap:,.0f} |

### 24h Range
| Metric | Value |
|--------|-------|
| High | ${data.high_24h:,.2f} |
| Low | ${data.low_24h:,.2f} |
"""

        if include_levels and data.asset_class in ['crypto', 'stock']:
            levels = self.get_key_levels(data)
            output += f"""
### Key Levels
| Type | Level | Price |
|------|-------|-------|
| **Resistance 3** | R3 | ${levels['resistance_3']:,.2f} |
| **Resistance 2** | R2 | ${levels['resistance_2']:,.2f} |
| **Resistance 1** | R1 | ${levels['resistance_1']:,.2f} |
| **Pivot** | - | ${levels['pivot']:,.2f} |
| **Support 1** | S1 | ${levels['support_1']:,.2f} |
| **Support 2** | S2 | ${levels['support_2']:,.2f} |
| **Support 3** | S3 | ${levels['support_3']:,.2f} |
"""

        return output


async def main():
    """Example usage of MarketDataAgent"""
    async with MarketDataAgent() as agent:
        # Fetch Bitcoin data
        btc_data = await agent.fetch_market_data('BTC', 'crypto')
        print(agent.format_output(btc_data))

        # Fetch multiple assets
        symbols = [
            ('ETH', 'crypto'),
            ('AAPL', 'stock'),
            ('GOLD', 'commodity'),
        ]
        multi_data = await agent.fetch_multiple(symbols)

        for symbol, data in multi_data.items():
            print(f"\n{symbol}: ${data.current_price:,.2f} ({data.price_change_24h:+.2f}%)")


if __name__ == '__main__':
    asyncio.run(main())
