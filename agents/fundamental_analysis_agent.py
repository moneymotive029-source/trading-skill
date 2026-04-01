"""
Fundamental Analysis Agent - Financial metrics, valuation, and on-chain analysis
Analyzes asset fundamentals across stocks, crypto, forex, and commodities.
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssetClass(Enum):
    STOCK = "stock"
    CRYPTO = "crypto"
    FOREX = "forex"
    COMMODITY = "commodity"


@dataclass
class StockFundamentals:
    """Stock-specific fundamental metrics"""
    # Valuation
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    peg_ratio: Optional[float] = None
    price_to_book: Optional[float] = None
    price_to_sales: Optional[float] = None
    ev_to_ebitda: Optional[float] = None

    # Profitability
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    roic: Optional[float] = None

    # Growth
    revenue_growth_yoy: Optional[float] = None
    earnings_growth_yoy: Optional[float] = None
    revenue_growth_3y: Optional[float] = None
    earnings_growth_3y: Optional[float] = None

    # Financial Health
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    free_cash_flow: Optional[float] = None
    operating_cash_flow: Optional[float] = None

    # Per Share
    eps_ttm: Optional[float] = None
    eps_forward: Optional[float] = None
    book_value_per_share: Optional[float] = None

    # Dividends
    dividend_yield: Optional[float] = None
    payout_ratio: Optional[float] = None
    dividend_growth_5y: Optional[float] = None

    # Analyst Data
    analyst_rating: Optional[str] = None  # Strong Buy, Buy, Hold, Sell, Strong Sell
    price_target_avg: Optional[float] = None
    price_target_high: Optional[float] = None
    price_target_low: Optional[float] = None
    num_analysts: Optional[int] = None

    # Overall
    fundamental_score: int = 0  # 0-100
    valuation_assessment: str = "Fair"  # Undervalued, Fair, Overvalued


@dataclass
class CryptoFundamentals:
    """Crypto-specific fundamental metrics"""
    # Market Metrics
    market_cap: Optional[float] = None
    fully_diluted_valuation: Optional[float] = None
    market_cap_rank: Optional[int] = None
    circulating_supply: Optional[float] = None
    total_supply: Optional[float] = None
    max_supply: Optional[float] = None

    # Volume & Liquidity
    volume_24h: Optional[float] = None
    volume_to_market_cap: Optional[float] = None
    liquidity_score: Optional[float] = None  # 0-100

    # On-Chain Metrics
    active_addresses_24h: Optional[int] = None
    active_addresses_7d_avg: Optional[float] = None
    transaction_count_24h: Optional[int] = None
    transaction_volume_24h: Optional[float] = None
    nvt_ratio: Optional[float] = None  # Network Value to Transactions

    # DeFi Metrics (for DeFi tokens)
    tvl: Optional[float] = None  # Total Value Locked
    tvl_change_7d: Optional[float] = None
    protocol_revenue_24h: Optional[float] = None
    fee_apr: Optional[float] = None

    # Development Activity
    github_commits_4w: Optional[int] = None
    github_contributors: Optional[int] = None
    development_score: Optional[float] = None  # 0-100

    # Holder Metrics
    holder_count: Optional[int] = None
    holder_change_7d: Optional[float] = None
    top_10_concentration: Optional[float] = None  # % held by top 10 wallets

    # Token Economics
    inflation_rate: Optional[float] = None
    next_unlock_date: Optional[str] = None
    next_unlock_amount: Optional[float] = None
    tokens_unlocked_pct: Optional[float] = None  # % already unlocked

    # Overall
    fundamental_score: int = 0  # 0-100
    tokenomics_score: int = 0  # 0-100


@dataclass
class ForexFundamentals:
    """Forex-specific fundamental metrics"""
    # Interest Rates
    central_bank_rate: Optional[float] = None
    rate_change_last_12m: Optional[float] = None
    next_meeting_date: Optional[str] = None
    market_implied_rate_next: Optional[float] = None

    # Economic Growth
    gdp_growth_yoy: Optional[float] = None
    gdp_growth_qoq: Optional[float] = None
    gdp_forecast_next_y: Optional[float] = None

    # Inflation
    cpi_yoy: Optional[float] = None
    core_cpi_yoy: Optional[float] = None
    pce_yoy: Optional[float] = None
    inflation_forecast: Optional[float] = None

    # Labor Market
    unemployment_rate: Optional[float] = None
    employment_change_mom: Optional[float] = None
    wage_growth_yoy: Optional[float] = None

    # Trade & Fiscal
    current_account_balance: Optional[float] = None  # % of GDP
    fiscal_balance: Optional[float] = None  # % of GDP
    debt_to_gdp: Optional[float] = None
    foreign_reserves: Optional[float] = None

    # Sentiment
    pmi_manufacturing: Optional[float] = None
    pmi_services: Optional[float] = None
    consumer_confidence: Optional[float] = None
    business_confidence: Optional[float] = None

    # Yield Differentials (vs counter currency)
    yield_2y_diff: Optional[float] = None
    yield_10y_diff: Optional[float] = None

    # Overall
    fundamental_score: int = 0  # 0-100
    rate_outlook: str = "Neutral"  # Hawkish, Neutral, Dovish


@dataclass
class CommodityFundamentals:
    """Commodity-specific fundamental metrics"""
    # Supply & Demand
    global_production: Optional[float] = None  # Annual
    global_consumption: Optional[float] = None  # Annual
    supply_demand_balance: Optional[float] = None  # Surplus (+) or deficit (-)
    production_growth_yoy: Optional[float] = None
    consumption_growth_yoy: Optional[float] = None

    # Inventory
    inventory_level: Optional[float] = None
    inventory_change_wow: Optional[float] = None
    inventory_days_forward: Optional[float] = None  # Days of supply
    inventory_location: Optional[str] = None  # e.g., "Cushing, OK" for oil

    # Production Costs
    marginal_cost_of_production: Optional[float] = None
    cash_cost_curve_p50: Optional[float] = None
    cash_cost_curve_p90: Optional[float] = None

    # Geopolitical & Structural
    top_producer: Optional[str] = None
    top_producer_pct: Optional[float] = None
    opec_quota_applicable: Optional[bool] = False
    strategic_reserve_level: Optional[float] = None

    # Forward Curve
    front_month_price: Optional[float] = None
    back_month_price: Optional[float] = None
    contango_backwardation: str = "Contango"  # Contango or Backwardation
    roll_yield: Optional[float] = None

    # Substitution & Alternatives
    substitute_available: Optional[bool] = False
    renewable_alternative: Optional[str] = None

    # Overall
    fundamental_score: int = 0  # 0-100
    supply_outlook: str = "Balanced"  # Tight, Balanced, Loose


@dataclass
class FundamentalAnalysis:
    """Container for all fundamental analysis results"""
    asset_class: AssetClass
    symbol: str

    # Asset-specific fundamentals
    stock: Optional[StockFundamentals] = None
    crypto: Optional[CryptoFundamentals] = None
    forex: Optional[ForexFundamentals] = None
    commodity: Optional[CommodityFundamentals] = None

    # Cross-asset comparison
    relative_value_score: int = 0  # 0-100 vs peers
    sector_rank: Optional[int] = None
    sector_total: Optional[int] = None

    # Overall
    overall_score: int = 0  # 0-100
    recommendation: str = "Hold"  # Strong Buy, Buy, Hold, Sell, Strong Sell


class FundamentalAnalysisAgent:
    """
    Fundamental Analysis Agent for analyzing asset fundamentals.

    Supports:
    - Stocks: Financial statements, ratios, analyst estimates
    - Crypto: On-chain metrics, tokenomics, development activity
    - Forex: Economic indicators, central bank policy
    - Commodities: Supply/demand, inventory, production costs
    """

    # API Endpoints
    ALPHA_VANTAGE_API = "https://www.alphavantage.co/query"
    COINGECKO_API = "https://api.coingecko.com/api/v3"
    FRED_API = "https://api.stlouisfed.org/fred"

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

    async def analyze(self, symbol: str, asset_class: str) -> FundamentalAnalysis:
        """
        Perform fundamental analysis on an asset.

        Args:
            symbol: Asset symbol (e.g., 'AAPL', 'BTC', 'EURUSD')
            asset_class: 'stock', 'crypto', 'forex', 'commodity'

        Returns:
            FundamentalAnalysis object with all metrics
        """
        asset_enum = AssetClass(asset_class.lower())

        analysis = FundamentalAnalysis(
            asset_class=asset_enum,
            symbol=symbol.upper()
        )

        if asset_class.lower() == 'stock':
            analysis.stock = await self._analyze_stock(symbol)
            analysis.overall_score = analysis.stock.fundamental_score
            analysis.recommendation = self._score_to_recommendation(analysis.overall_score)

        elif asset_class.lower() == 'crypto':
            analysis.crypto = await self._analyze_crypto(symbol)
            analysis.overall_score = analysis.crypto.fundamental_score
            analysis.recommendation = self._score_to_recommendation(analysis.overall_score)

        elif asset_class.lower() == 'forex':
            analysis.forex = await self._analyze_forex(symbol)
            analysis.overall_score = analysis.forex.fundamental_score
            analysis.recommendation = self._score_to_recommendation(analysis.overall_score)

        elif asset_class.lower() == 'commodity':
            analysis.commodity = await self._analyze_commodity(symbol)
            analysis.overall_score = analysis.commodity.fundamental_score
            analysis.recommendation = self._score_to_recommendation(analysis.overall_score)

        return analysis

    def _score_to_recommendation(self, score: int) -> str:
        """Convert numerical score to recommendation"""
        if score >= 80:
            return "Strong Buy"
        elif score >= 60:
            return "Buy"
        elif score >= 40:
            return "Hold"
        elif score >= 20:
            return "Sell"
        else:
            return "Strong Sell"

    async def _analyze_stock(self, symbol: str) -> StockFundamentals:
        """Analyze stock fundamentals"""
        fundamentals = StockFundamentals()

        # Mock data - in production, fetch from Alpha Vantage, Yahoo Finance, SEC
        # This simulates realistic fundamental data

        # Valuation metrics
        fundamentals.pe_ratio = 25.5
        fundamentals.forward_pe = 22.0
        fundamentals.peg_ratio = 1.8
        fundamentals.price_to_book = 5.2
        fundamentals.price_to_sales = 6.5
        fundamentals.ev_to_ebitda = 18.5

        # Profitability
        fundamentals.gross_margin = 42.5
        fundamentals.operating_margin = 28.0
        fundamentals.net_margin = 22.5
        fundamentals.roe = 25.0
        fundamentals.roa = 12.5
        fundamentals.roic = 18.0

        # Growth
        fundamentals.revenue_growth_yoy = 15.0
        fundamentals.earnings_growth_yoy = 20.0
        fundamentals.revenue_growth_3y = 18.0
        fundamentals.earnings_growth_3y = 22.0

        # Financial health
        fundamentals.debt_to_equity = 0.5
        fundamentals.current_ratio = 2.0
        fundamentals.quick_ratio = 1.5
        fundamentals.free_cash_flow = 50_000_000_000
        fundamentals.operating_cash_flow = 75_000_000_000

        # Per share
        fundamentals.eps_ttm = 6.50
        fundamentals.eps_forward = 7.25
        fundamentals.book_value_per_share = 32.00

        # Dividends
        fundamentals.dividend_yield = 0.5
        fundamentals.payout_ratio = 15.0
        fundamentals.dividend_growth_5y = 8.0

        # Analyst data
        fundamentals.analyst_rating = "Buy"
        fundamentals.price_target_avg = 185.00
        fundamentals.price_target_high = 220.00
        fundamentals.price_target_low = 150.00
        fundamentals.num_analysts = 45

        # Calculate fundamental score
        score = 0

        # Valuation (max 20 points)
        if fundamentals.pe_ratio and fundamentals.pe_ratio < 15:
            score += 20
        elif fundamentals.pe_ratio and fundamentals.pe_ratio < 25:
            score += 15
        elif fundamentals.pe_ratio and fundamentals.pe_ratio < 35:
            score += 10
        else:
            score += 5

        # Profitability (max 25 points)
        if fundamentals.roe and fundamentals.roe > 20:
            score += 25
        elif fundamentals.roe and fundamentals.roe > 15:
            score += 20
        elif fundamentals.roe and fundamentals.roe > 10:
            score += 15
        else:
            score += 5

        # Growth (max 25 points)
        if fundamentals.earnings_growth_yoy and fundamentals.earnings_growth_yoy > 20:
            score += 25
        elif fundamentals.earnings_growth_yoy and fundamentals.earnings_growth_yoy > 15:
            score += 20
        elif fundamentals.earnings_growth_yoy and fundamentals.earnings_growth_yoy > 10:
            score += 15
        else:
            score += 5

        # Financial health (max 15 points)
        if fundamentals.debt_to_equity and fundamentals.debt_to_equity < 0.5:
            score += 15
        elif fundamentals.debt_to_equity and fundamentals.debt_to_equity < 1.0:
            score += 10
        else:
            score += 5

        # Analyst sentiment (max 15 points)
        if fundamentals.analyst_rating == "Strong Buy":
            score += 15
        elif fundamentals.analyst_rating == "Buy":
            score += 12
        elif fundamentals.analyst_rating == "Hold":
            score += 5
        else:
            score += 0

        fundamentals.fundamental_score = min(100, score)

        # Valuation assessment
        if fundamentals.pe_ratio and fundamentals.pe_ratio < 20 and fundamentals.peg_ratio and fundamentals.peg_ratio < 1.5:
            fundamentals.valuation_assessment = "Undervalued"
        elif fundamentals.pe_ratio and fundamentals.pe_ratio > 35 or (fundamentals.peg_ratio and fundamentals.peg_ratio > 2.5):
            fundamentals.valuation_assessment = "Overvalued"
        else:
            fundamentals.valuation_assessment = "Fair"

        return fundamentals

    async def _analyze_crypto(self, symbol: str) -> CryptoFundamentals:
        """Analyze crypto fundamentals"""
        fundamentals = CryptoFundamentals()

        # Mock data - in production, fetch from CoinGecko, Glassnode, DefiLlama

        # Market metrics
        fundamentals.market_cap = 850_000_000_000
        fundamentals.fully_diluted_valuation = 900_000_000_000
        fundamentals.market_cap_rank = 1
        fundamentals.circulating_supply = 19_700_000
        fundamentals.total_supply = 21_000_000
        fundamentals.max_supply = 21_000_000

        # Volume & liquidity
        fundamentals.volume_24h = 25_000_000_000
        fundamentals.volume_to_market_cap = 0.029
        fundamentals.liquidity_score = 95.0

        # On-chain metrics
        fundamentals.active_addresses_24h = 950_000
        fundamentals.active_addresses_7d_avg = 920_000
        fundamentals.transaction_count_24h = 350_000
        fundamentals.transaction_volume_24h = 8_500_000_000
        fundamentals.nvt_ratio = 28.5

        # Development activity
        fundamentals.github_commits_4w = 250
        fundamentals.github_contributors = 45
        fundamentals.development_score = 85.0

        # Holder metrics
        fundamentals.holder_count = 50_000_000
        fundamentals.holder_change_7d = 2.5
        fundamentals.top_10_concentration = 12.0

        # Token economics
        fundamentals.inflation_rate = 1.75
        fundamentals.tokens_unlocked_pct = 93.8

        # Calculate fundamental score
        score = 0

        # Market maturity (max 20 points)
        if fundamentals.market_cap_rank and fundamentals.market_cap_rank <= 5:
            score += 20
        elif fundamentals.market_cap_rank and fundamentals.market_cap_rank <= 20:
            score += 15
        elif fundamentals.market_cap_rank and fundamentals.market_cap_rank <= 50:
            score += 10
        else:
            score += 5

        # Liquidity (max 20 points)
        if fundamentals.liquidity_score and fundamentals.liquidity_score > 80:
            score += 20
        elif fundamentals.liquidity_score and fundamentals.liquidity_score > 60:
            score += 15
        else:
            score += 5

        # Development (max 25 points)
        if fundamentals.development_score and fundamentals.development_score > 75:
            score += 25
        elif fundamentals.development_score and fundamentals.development_score > 50:
            score += 20
        else:
            score += 10

        # Tokenomics (max 20 points)
        if fundamentals.tokens_unlocked_pct and fundamentals.tokens_unlocked_pct > 80:
            score += 20  # Most tokens already unlocked
        elif fundamentals.tokens_unlocked_pct and fundamentals.tokens_unlocked_pct > 50:
            score += 15
        else:
            score += 5

        # On-chain activity (max 15 points)
        if fundamentals.active_addresses_7d_avg and fundamentals.active_addresses_7d_avg > 500_000:
            score += 15
        elif fundamentals.active_addresses_7d_avg and fundamentals.active_addresses_7d_avg > 100_000:
            score += 10
        else:
            score += 5

        fundamentals.fundamental_score = min(100, score)

        # Tokenomics score (separate from fundamental score)
        tokenomics_score = 0
        if fundamentals.max_supply and fundamentals.circulating_supply:
            unlocked_pct = fundamentals.circulating_supply / fundamentals.max_supply
            if unlocked_pct > 0.9:
                tokenomics_score += 50  # Low inflation risk
            else:
                tokenomics_score += int(unlocked_pct * 50)

        if fundamentals.inflation_rate and fundamentals.inflation_rate < 2:
            tokenomics_score += 30
        elif fundamentals.inflation_rate and fundamentals.inflation_rate < 5:
            tokenomics_score += 20
        else:
            tokenomics_score += 10

        if fundamentals.top_10_concentration and fundamentals.top_10_concentration < 20:
            tokenomics_score += 20  # Good distribution
        elif fundamentals.top_10_concentration and fundamentals.top_10_concentration < 40:
            tokenomics_score += 15
        else:
            tokenomics_score += 5

        fundamentals.tokenomics_score = min(100, tokenomics_score)

        return fundamentals

    async def _analyze_forex(self, symbol: str) -> ForexFundamentals:
        """Analyze forex fundamentals"""
        fundamentals = ForexFundamentals()

        # Mock data - in production, fetch from FRED, central banks, Trading Economics

        # Normalize symbol
        if '/' in symbol:
            base, quote = symbol.split('/')
        else:
            base, quote = symbol[:3], symbol[3:]

        # Base currency data (e.g., EUR)
        fundamentals.central_bank_rate = 4.50
        fundamentals.rate_change_last_12m = 0.75
        fundamentals.next_meeting_date = "2026-04-15"

        fundamentals.gdp_growth_yoy = 1.2
        fundamentals.gdp_growth_qoq = 0.3
        fundamentals.gdp_forecast_next_y = 1.5

        fundamentals.cpi_yoy = 2.8
        fundamentals.core_cpi_yoy = 3.2
        fundamentals.pce_yoy = 2.5

        fundamentals.unemployment_rate = 6.5
        fundamentals.employment_change_mom = 0.2
        fundamentals.wage_growth_yoy = 4.5

        fundamentals.current_account_balance = 2.5  # % of GDP
        fundamentals.fiscal_balance = -3.0  # % of GDP
        fundamentals.debt_to_gdp = 90.0
        fundamentals.foreign_reserves = 800_000_000_000

        fundamentals.pmi_manufacturing = 48.5
        fundamentals.pmi_services = 52.0
        fundamentals.consumer_confidence = 95.0
        fundamentals.business_confidence = 92.0

        fundamentals.yield_2y_diff = -0.50
        fundamentals.yield_10y_diff = -0.75

        # Calculate fundamental score
        score = 50  # Start neutral

        # Rate differential (max 25 points)
        if fundamentals.yield_10y_diff and fundamentals.yield_10y_diff > 0:
            score += 25  # Positive differential is bullish
        elif fundamentals.yield_10y_diff and fundamentals.yield_10y_diff > -0.5:
            score += 15
        elif fundamentals.yield_10y_diff and fundamentals.yield_10y_diff > -1.0:
            score += 5
        else:
            score -= 10

        # Growth outlook (max 20 points)
        if fundamentals.gdp_forecast_next_y and fundamentals.gdp_forecast_next_y > 2.0:
            score += 20
        elif fundamentals.gdp_forecast_next_y and fundamentals.gdp_forecast_next_y > 1.0:
            score += 15
        elif fundamentals.gdp_forecast_next_y and fundamentals.gdp_forecast_next_y > 0:
            score += 10
        else:
            score += 0

        # Inflation (max 15 points)
        if fundamentals.cpi_yoy and 1.5 < fundamentals.cpi_yoy < 3.0:
            score += 15  # Goldilocks zone
        elif fundamentals.cpi_yoy and fundamentals.cpi_yoy > 4.0:
            score -= 10  # Too high
        elif fundamentals.cpi_yoy and fundamentals.cpi_yoy < 1.0:
            score -= 5  # Deflation risk
        else:
            score += 5

        # Fiscal health (max 20 points)
        if fundamentals.debt_to_gdp and fundamentals.debt_to_gdp < 60:
            score += 20
        elif fundamentals.debt_to_gdp and fundamentals.debt_to_gdp < 100:
            score += 15
        elif fundamentals.debt_to_gdp and fundamentals.debt_to_gdp < 150:
            score += 10
        else:
            score += 0

        # Current account (max 20 points)
        if fundamentals.current_account_balance and fundamentals.current_account_balance > 0:
            score += 20  # Surplus is bullish
        elif fundamentals.current_account_balance and fundamentals.current_account_balance > -3:
            score += 10
        else:
            score += 0

        fundamentals.fundamental_score = max(0, min(100, score))

        # Rate outlook
        if fundamentals.rate_change_last_12m and fundamentals.rate_change_last_12m > 0.5:
            fundamentals.rate_outlook = "Hawkish"
        elif fundamentals.rate_change_last_12m and fundamentals.rate_change_last_12m < -0.5:
            fundamentals.rate_outlook = "Dovish"
        else:
            fundamentals.rate_outlook = "Neutral"

        return fundamentals

    async def _analyze_commodity(self, symbol: str) -> CommodityFundamentals:
        """Analyze commodity fundamentals"""
        fundamentals = CommodityFundamentals()

        # Mock data - in production, fetch from EIA, USDA, CME Group

        if symbol.upper() == 'GOLD':
            fundamentals.global_production = 3_600  # tonnes/year
            fundamentals.global_consumption = 4_500  # tonnes/year
            fundamentals.supply_demand_balance = -900  # Deficit
            fundamentals.production_growth_yoy = -1.5
            fundamentals.consumption_growth_yoy = 3.2

            fundamentals.inventory_level = 85_000  # tonnes
            fundamentals.inventory_change_wow = -0.5
            fundamentals.inventory_days_forward = 45

            fundamentals.marginal_cost_of_production = 1_850  # $/oz
            fundamentals.cash_cost_curve_p50 = 1_200
            fundamentals.cash_cost_curve_p90 = 1_600

            fundamentals.top_producer = "China"
            fundamentals.top_producer_pct = 10.0
            fundamentals.strategic_reserve_level = 8_133  # tonnes (US + official)

            fundamentals.front_month_price = 2_035
            fundamentals.back_month_price = 2_050
            fundamentals.contango_backwardation = "Contango"
            fundamentals.roll_yield = -0.7

            fundamentals.substitute_available = False

        elif symbol.upper() in ['CRUDE', 'BRENT']:
            fundamentals.global_production = 102_000_000  # barrels/day
            fundamentals.global_consumption = 101_500_000  # barrels/day
            fundamentals.supply_demand_balance = 500_000  # Surplus
            fundamentals.production_growth_yoy = 1.2
            fundamentals.consumption_growth_yoy = 0.8

            fundamentals.inventory_level = 850_000_000  # barrels (OECD)
            fundamentals.inventory_change_wow = 2.5
            fundamentals.inventory_days_forward = 60

            fundamentals.marginal_cost_of_production = 65  # $/barrel
            fundamentals.cash_cost_curve_p50 = 45
            fundamentals.cash_cost_curve_p90 = 80

            fundamentals.top_producer = "United States"
            fundamentals.top_producer_pct = 20.0
            fundamentals.opec_quota_applicable = True
            fundamentals.strategic_reserve_level = 650_000_000  # SPR

            fundamentals.front_month_price = 78.50
            fundamentals.back_month_price = 76.00
            fundamentals.contango_backwardation = "Backwardation"
            fundamentals.roll_yield = 3.2

            fundamentals.substitute_available = True
            fundamentals.renewable_alternative = "Solar, Wind, Nuclear"

        else:
            # Generic commodity
            fundamentals.supply_demand_balance = 0
            fundamentals.inventory_days_forward = 45
            fundamentals.contango_backwardation = "Contango"

        # Calculate fundamental score
        score = 50  # Start neutral

        # Supply/demand balance (max 30 points)
        if fundamentals.supply_demand_balance and fundamentals.supply_demand_balance < 0:
            # Deficit is bullish
            deficit_pct = abs(fundamentals.supply_demand_balance) / fundamentals.global_consumption
            if deficit_pct > 0.05:
                score += 30
            elif deficit_pct > 0.02:
                score += 20
            else:
                score += 10
        elif fundamentals.supply_demand_balance and fundamentals.supply_demand_balance > 0:
            # Surplus is bearish
            surplus_pct = fundamentals.supply_demand_balance / fundamentals.global_consumption
            if surplus_pct > 0.05:
                score -= 20
            elif surplus_pct > 0.02:
                score -= 10

        # Inventory trend (max 20 points)
        if fundamentals.inventory_change_wow and fundamentals.inventory_change_wow < 0:
            score += 20  # Drawdown is bullish
        elif fundamentals.inventory_change_wow and fundamentals.inventory_change_wow > 5:
            score -= 10  # Build is bearish
        else:
            score += 5

        # Forward curve (max 20 points)
        if fundamentals.contango_backwardation == "Backwardation":
            score += 20  # Tight spot market
        else:
            score += 5  # Contango is neutral/slightly bearish

        # Production cost support (max 15 points)
        if fundamentals.marginal_cost_of_production and fundamentals.front_month_price:
            cost_support_pct = (fundamentals.front_month_price - fundamentals.marginal_cost_of_production) / fundamentals.front_month_price
            if cost_support_pct > 0.3:
                score += 15  # High margin, sustainable
            elif cost_support_pct > 0.1:
                score += 10
            elif cost_support_pct > 0:
                score += 5
            else:
                score += 0  # Below cost, potential supply cut

        # Geopolitical (max 15 points)
        if fundamentals.top_producer_pct and fundamentals.top_producer_pct < 15:
            score += 15  # Diversified supply
        elif fundamentals.top_producer_pct and fundamentals.top_producer_pct < 25:
            score += 10
        else:
            score += 5

        fundamentals.fundamental_score = max(0, min(100, score))

        # Supply outlook
        if fundamentals.supply_demand_balance and fundamentals.supply_demand_balance < -0.03 * fundamentals.global_consumption:
            fundamentals.supply_outlook = "Tight"
        elif fundamentals.supply_demand_balance and fundamentals.supply_demand_balance > 0.03 * fundamentals.global_consumption:
            fundamentals.supply_outlook = "Loose"
        else:
            fundamentals.supply_outlook = "Balanced"

        return fundamentals

    def format_output(self, analysis: FundamentalAnalysis) -> str:
        """Format fundamental analysis as markdown"""
        output = f"""
## Fundamental Analysis: {analysis.symbol}

### Overall Assessment
| Metric | Value |
|--------|-------|
| **Fundamental Score** | {analysis.overall_score}/100 |
| **Recommendation** | {analysis.recommendation} |
| **Asset Class** | {analysis.asset_class.value} |
"""

        if analysis.stock:
            stock = analysis.stock
            output += f"""
### Valuation Metrics
| Metric | Value | Assessment |
|--------|-------|------------|
| **P/E Ratio** | {stock.pe_ratio:.1f}x | {stock.valuation_assessment} |
| **Forward P/E** | {stock.forward_pe:.1f}x | - |
| **PEG Ratio** | {stock.peg_ratio:.2f} | - |
| **Price/Book** | {stock.price_to_book:.2f}x | - |
| **EV/EBITDA** | {stock.ev_to_ebitda:.1f}x | - |

### Profitability
| Metric | Value |
|--------|-------|
| **Gross Margin** | {stock.gross_margin:.1f}% |
| **Operating Margin** | {stock.operating_margin:.1f}% |
| **Net Margin** | {stock.net_margin:.1f}% |
| **ROE** | {stock.roe:.1f}% |
| **ROIC** | {stock.roic:.1f}% |

### Growth Rates
| Metric | Value |
|--------|-------|
| **Revenue Growth (YoY)** | {stock.revenue_growth_yoy:.1f}% |
| **Earnings Growth (YoY)** | {stock.earnings_growth_yoy:.1f}% |
| **3Y Revenue CAGR** | {stock.revenue_growth_3y:.1f}% |
| **3Y Earnings CAGR** | {stock.earnings_growth_3y:.1f}% |

### Financial Health
| Metric | Value |
|--------|-------|
| **Debt/Equity** | {stock.debt_to_equity:.2f} |
| **Current Ratio** | {stock.current_ratio:.2f} |
| **Free Cash Flow** | ${stock.free_cash_flow:,.0f} |

### Analyst Consensus
| Metric | Value |
|--------|-------|
| **Rating** | {stock.analyst_rating} |
| **Price Target** | ${stock.price_target_avg:,.2f} |
| **Upside/Downside** | {((stock.price_target_avg - stock.eps_ttm * stock.pe_ratio) / (stock.eps_ttm * stock.pe_ratio) * 100):+.1f}% |
| **Num Analysts** | {stock.num_analysts} |
"""

        elif analysis.crypto:
            crypto = analysis.crypto
            output += f"""
### Market Metrics
| Metric | Value |
|--------|-------|
| **Market Cap** | ${crypto.market_cap:,.0f} |
| **FDV** | ${crypto.fully_diluted_valuation:,.0f} |
| **Market Cap Rank** | #{crypto.market_cap_rank} |
| **Circulating Supply** | {crypto.circulating_supply:,.0f} |
| **Max Supply** | {crypto.max_supply:,.0f} |
| **Unlocked** | {crypto.tokens_unlocked_pct:.1f}% |

### On-Chain Metrics
| Metric | Value |
|--------|-------|
| **Active Addresses (24h)** | {crypto.active_addresses_24h:,} |
| **Active Addresses (7D Avg)** | {crypto.active_addresses_7d_avg:,.0f} |
| **Transaction Count (24h)** | {crypto.transaction_count_24h:,} |
| **NVT Ratio** | {crypto.nvt_ratio:.2f} |

### Development Activity
| Metric | Value |
|--------|-------|
| **GitHub Commits (4W)** | {crypto.github_commits_4w} |
| **Contributors** | {crypto.github_contributors} |
| **Development Score** | {crypto.development_score:.1f}/100 |

### Tokenomics
| Metric | Value |
|--------|-------|
| **Tokenomics Score** | {crypto.tokenomics_score:.1f}/100 |
| **Inflation Rate** | {crypto.inflation_rate:.2f}% |
| **Top 10 Concentration** | {crypto.top_10_concentration:.1f}% |
| **Holder Count** | {crypto.holder_count:,} |
"""

        elif analysis.forex:
            forex = analysis.forex
            base = analysis.symbol[:3] if '/' not in analysis.symbol else analysis.symbol.split('/')[0]
            output += f"""
### {base} Economic Indicators
| Category | Indicator | Value |
|----------|-----------|-------|
| **Monetary** | Central Bank Rate | {forex.central_bank_rate:.2f}% |
| | Rate Change (12M) | {forex.rate_change_last_12m:+.2f}% |
| | Rate Outlook | {forex.rate_outlook} |
| **Growth** | GDP Growth (YoY) | {forex.gdp_growth_yoy:.2f}% |
| | GDP Forecast (Next Y) | {forex.gdp_forecast_next_y:.2f}% |
| **Inflation** | CPI (YoY) | {forex.cpi_yoy:.2f}% |
| | Core CPI (YoY) | {forex.core_cpi_yoy:.2f}% |
| **Labor** | Unemployment Rate | {forex.unemployment_rate:.2f}% |
| | Wage Growth (YoY) | {forex.wage_growth_yoy:.2f}% |
| **Fiscal** | Debt/GDP | {forex.debt_to_gdp:.1f}% |
| | Current Account | {forex.current_account_balance:+.2f}% of GDP |

### Yield Differentials
| Metric | Value |
|--------|-------|
| **2Y Yield Diff** | {forex.yield_2y_diff:+.2f}% |
| **10Y Yield Diff** | {forex.yield_10y_diff:+.2f}% |

### Sentiment Indicators
| Indicator | Value |
|-----------|-------|
| **PMI Manufacturing** | {forex.pmi_manufacturing:.1f} |
| **PMI Services** | {forex.pmi_services:.1f} |
| **Consumer Confidence** | {forex.consumer_confidence:.1f} |
"""

        elif analysis.commodity:
            commodity = analysis.commodity
            output += f"""
### Supply & Demand
| Metric | Value |
|--------|-------|
| **Global Production** | {commodity.global_production:,.0f} |
| **Global Consumption** | {commodity.global_consumption:,.0f} |
| **Supply/Demand Balance** | {commodity.supply_demand_balance:+,.0f} |
| **Supply Outlook** | {commodity.supply_outlook} |

### Inventory
| Metric | Value |
|--------|-------|
| **Inventory Level** | {commodity.inventory_level:,.0f} |
| **Week-over-Week Change** | {commodity.inventory_change_wow:+.2f}% |
| **Days of Supply** | {commodity.inventory_days_forward:.0f} |

### Production Costs
| Metric | Value |
|--------|-------|
| **Marginal Cost of Production** | ${commodity.marginal_cost_of_production:,.2f} |
| **P50 Cash Cost** | ${commodity.cash_cost_curve_p50:,.2f} |
| **P90 Cash Cost** | ${commodity.cash_cost_curve_p90:,.2f} |

### Forward Curve
| Metric | Value |
|--------|-------|
| **Front Month** | ${commodity.front_month_price:,.2f} |
| **Back Month** | ${commodity.back_month_price:,.2f} |
| **Structure** | {commodity.contango_backwardation} |
| **Roll Yield** | {commodity.roll_yield:+.2f}% |

### Supply Concentration
| Metric | Value |
|--------|-------|
| **Top Producer** | {commodity.top_producer} |
| **Market Share** | {commodity.top_producer_pct:.1f}% |
"""

        return output


async def main():
    """Example usage of FundamentalAnalysisAgent"""
    async with FundamentalAnalysisAgent() as agent:
        # Analyze a stock
        aapl_analysis = await agent.analyze('AAPL', 'stock')
        print(agent.format_output(aapl_analysis))

        # Analyze crypto
        btc_analysis = await agent.analyze('BTC', 'crypto')
        print(agent.format_output(btc_analysis))


if __name__ == '__main__':
    asyncio.run(main())
