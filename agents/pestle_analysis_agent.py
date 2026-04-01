"""
PESTLE Analysis Agent - Macro factor analysis with weighted scoring
Analyzes Political, Economic, Social, Technological, Legal, Environmental factors.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImpactDirection(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class ImpactMagnitude(Enum):
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5


@dataclass
class PESTLEFactor:
    """Individual PESTLE factor"""
    name: str
    category: str  # Political, Economic, Social, Technological, Legal, Environmental
    description: str
    impact_direction: ImpactDirection = ImpactDirection.NEUTRAL
    impact_magnitude: ImpactMagnitude = ImpactMagnitude.MEDIUM
    confidence: float = 0.5  # 0-1, how confident we are in this assessment
    sources: List[str] = field(default_factory=list)
    last_updated: datetime = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()

    @property
    def weighted_score(self) -> float:
        """Calculate weighted score: -5 to +5"""
        direction_mult = {
            ImpactDirection.POSITIVE: 1.0,
            ImpactDirection.NEGATIVE: -1.0,
            ImpactDirection.NEUTRAL: 0.0
        }
        return direction_mult[self.impact_direction] * self.impact_magnitude.value * self.confidence


@dataclass
class PESTLECategoryScore:
    """Score for each PESTLE category"""
    category: str
    factors: List[PESTLEFactor] = field(default_factory=list)
    raw_score: float = 0.0  # -5 to +5
    normalized_score: float = 0.0  # 0-100
    assessment: str = "Neutral"

    def calculate(self):
        """Calculate category score from factors"""
        if not self.factors:
            return

        # Weighted average of factor scores
        total_weight = sum(f.confidence for f in self.factors)
        if total_weight > 0:
            self.raw_score = sum(f.weighted_score * f.confidence for f in self.factors) / total_weight

        # Normalize to 0-100
        self.normalized_score = (self.raw_score + 5) / 10 * 100

        # Assessment
        if self.normalized_score >= 80:
            self.assessment = "Very Favorable"
        elif self.normalized_score >= 60:
            self.assessment = "Favorable"
        elif self.normalized_score >= 40:
            self.assessment = "Neutral"
        elif self.normalized_score >= 20:
            self.assessment = "Unfavorable"
        else:
            self.assessment = "Very Unfavorable"


@dataclass
class PESTLEPlusScore:
    """Complete PESTLE+ scoring including Sentiment and Technical"""
    # PESTLE categories
    political: PESTLECategoryScore = field(default_factory=lambda: PESTLECategoryScore(category="Political"))
    economic: PESTLECategoryScore = field(default_factory=lambda: PESTLECategoryScore(category="Economic"))
    social: PESTLECategoryScore = field(default_factory=lambda: PESTLECategoryScore(category="Social"))
    technological: PESTLECategoryScore = field(default_factory=lambda: PESTLECategoryScore(category="Technological"))
    legal: PESTLECategoryScore = field(default_factory=lambda: PESTLECategoryScore(category="Legal"))
    environmental: PESTLECategoryScore = field(default_factory=lambda: PESTLECategoryScore(category="Environmental"))

    # Additional categories
    sentiment: PESTLECategoryScore = field(default_factory=lambda: PESTLECategoryScore(category="Sentiment"))
    technical: PESTLECategoryScore = field(default_factory=lambda: PESTLECategoryScore(category="Technical"))

    # Overall
    overall_score: float = 0.0  # 0-100
    recommendation: str = "Hold"
    confidence_level: str = "Medium"


@dataclass
class PESTLEAnalysis:
    """Complete PESTLE+ analysis result"""
    symbol: str
    asset_class: str
    timestamp: datetime = None

    scores: PESTLEPlusScore = None
    all_factors: List[PESTLEFactor] = None

    # Asset-specific weightings
    weights: Dict[str, float] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.scores is None:
            self.scores = PESTLEPlusScore()
        if self.all_factors is None:
            self.all_factors = []
        if self.weights is None:
            self.weights = self._get_default_weights()

    def _get_default_weights(self) -> Dict[str, float]:
        """Get default weights based on asset class"""
        if self.asset_class.lower() == 'crypto':
            return {
                'Political': 0.15,
                'Economic': 0.10,
                'Social': 0.10,
                'Technological': 0.20,
                'Legal': 0.20,
                'Environmental': 0.05,
                'Sentiment': 0.15,
                'Technical': 0.05
            }
        elif self.asset_class.lower() == 'stock':
            return {
                'Political': 0.10,
                'Economic': 0.20,
                'Social': 0.10,
                'Technological': 0.15,
                'Legal': 0.10,
                'Environmental': 0.10,
                'Sentiment': 0.10,
                'Technical': 0.15
            }
        elif self.asset_class.lower() == 'forex':
            return {
                'Political': 0.20,
                'Economic': 0.30,
                'Social': 0.05,
                'Technological': 0.05,
                'Legal': 0.10,
                'Environmental': 0.05,
                'Sentiment': 0.10,
                'Technical': 0.15
            }
        elif self.asset_class.lower() == 'commodity':
            return {
                'Political': 0.15,
                'Economic': 0.20,
                'Social': 0.05,
                'Technological': 0.10,
                'Legal': 0.10,
                'Environmental': 0.15,
                'Sentiment': 0.10,
                'Technical': 0.15
            }
        else:
            # Equal weights
            return {k: 0.125 for k in ['Political', 'Economic', 'Social', 'Technological',
                                       'Legal', 'Environmental', 'Sentiment', 'Technical']}


class PESTLEAnalysisAgent:
    """
    PESTLE Analysis Agent for macro factor analysis.

    Analyzes:
    - Political: Government policy, trade, geopolitics
    - Economic: GDP, inflation, employment, central bank
    - Social: Demographics, culture, consumer behavior
    - Technological: Innovation, disruption, R&D
    - Legal: Regulation, litigation, compliance
    - Environmental: Climate, ESG, natural resources
    - + Sentiment: Market positioning, news flow
    - + Technical: Price action, indicators
    """

    def __init__(self):
        """Initialize the agent"""
        self.analysis: Optional[PESTLEAnalysis] = None

    def analyze(self, symbol: str, asset_class: str,
                context: Dict[str, any] = None) -> PESTLEAnalysis:
        """
        Perform PESTLE+ analysis on an asset.

        Args:
            symbol: Asset symbol
            asset_class: 'crypto', 'stock', 'forex', 'commodity'
            context: Optional context data (news, economic data, etc.)

        Returns:
            PESTLEAnalysis with all factors and scores
        """
        analysis = PESTLEAnalysis(
            symbol=symbol.upper(),
            asset_class=asset_class.lower()
        )

        # Generate factors for each category
        analysis.all_factors = self._generate_factors(symbol, asset_class, context or {})

        # Populate category scores
        analysis.scores = self._calculate_scores(analysis.all_factors)

        # Calculate overall score with asset-class weights
        analysis.overall_score = self._calculate_overall_score(analysis.scores, analysis.weights)

        # Generate recommendation
        analysis.scores.overall_score = analysis.overall_score
        analysis.scores.recommendation = self._score_to_recommendation(analysis.overall_score)

        # Set confidence level
        analysis.scores.confidence_level = self._calculate_confidence(analysis.all_factors)

        self.analysis = analysis
        return analysis

    def _generate_factors(self, symbol: str, asset_class: str,
                          context: Dict[str, any]) -> List[PESTLEFactor]:
        """Generate PESTLE factors based on asset class and context"""
        factors = []

        if asset_class.lower() == 'crypto':
            factors = self._generate_crypto_factors(symbol, context)
        elif asset_class.lower() == 'stock':
            factors = self._generate_stock_factors(symbol, context)
        elif asset_class.lower() == 'forex':
            factors = self._generate_forex_factors(symbol, context)
        elif asset_class.lower() == 'commodity':
            factors = self._generate_commodity_factors(symbol, context)

        return factors

    def _generate_crypto_factors(self, symbol: str, context: Dict) -> List[PESTLEFactor]:
        """Generate PESTLE factors for cryptocurrency"""
        factors = []

        # Political factors
        factors.append(PESTLEFactor(
            name="Regulatory Clarity",
            category="Political",
            description="Government stance on cryptocurrency regulation and classification",
            impact_direction=ImpactDirection.NEUTRAL,
            impact_magnitude=ImpactMagnitude.HIGH,
            confidence=0.7,
            sources=["SEC.gov", "Treasury.gov"]
        ))

        factors.append(PESTLEFactor(
            name="Geopolitical Adoption",
            category="Political",
            description="Nation-state adoption and strategic reserves",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.HIGH,
            confidence=0.6,
            sources=["Government announcements", "IMF reports"]
        ))

        # Economic factors
        factors.append(PESTLEFactor(
            name="Inflation Hedge Narrative",
            category="Economic",
            description="Bitcoin as digital gold and inflation hedge",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.MEDIUM,
            confidence=0.5,
            sources=["Market analysis", "Correlation data"]
        ))

        factors.append(PESTLEFactor(
            name="Interest Rate Environment",
            category="Economic",
            description="Impact of Fed rates on risk assets",
            impact_direction=ImpactDirection.NEGATIVE,
            impact_magnitude=ImpactMagnitude.MEDIUM,
            confidence=0.8,
            sources=["Federal Reserve", "CME FedWatch"]
        ))

        # Social factors
        factors.append(PESTLEFactor(
            name="Retail Adoption",
            category="Social",
            description="Growing retail and institutional adoption",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.HIGH,
            confidence=0.7,
            sources=["Wallet data", "Exchange flows"]
        ))

        # Technological factors
        factors.append(PESTLEFactor(
            name="Network Security",
            category="Technological",
            description="Hash rate and network security trends",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.HIGH,
            confidence=0.9,
            sources=["Blockchain data", "Mining pools"]
        ))

        factors.append(PESTLEFactor(
            name="Layer 2 Development",
            category="Technological",
            description="Scaling solutions and ecosystem growth",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.MEDIUM,
            confidence=0.7,
            sources=["GitHub", "L2Beat"]
        ))

        # Legal factors
        factors.append(PESTLEFactor(
            name="ETF Approval Status",
            category="Legal",
            description="Spot ETF approvals and institutional access",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.VERY_HIGH,
            confidence=0.9,
            sources=["SEC filings", "BlackRock", "Fidelity"]
        ))

        factors.append(PESTLEFactor(
            name="Compliance Requirements",
            category="Legal",
            description="KYC/AML and travel rule compliance",
            impact_direction=ImpactDirection.NEGATIVE,
            impact_magnitude=ImpactMagnitude.LOW,
            confidence=0.8,
            sources=["FinCEN", "FATF"]
        ))

        # Environmental factors
        factors.append(PESTLEFactor(
            name="Energy Mix",
            category="Environmental",
            description="Bitcoin mining renewable energy usage",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.LOW,
            confidence=0.6,
            sources=["Bitcoin Mining Council", "Cambridge CBECI"]
        ))

        # Sentiment factors
        factors.append(PESTLEFactor(
            name="Media Sentiment",
            category="Sentiment",
            description="Overall media and social sentiment",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.MEDIUM,
            confidence=0.7,
            sources=["NewsAPI", "Social media"]
        ))

        # Technical factors
        factors.append(PESTLEFactor(
            name="Price Trend",
            category="Technical",
            description="Technical trend direction and momentum",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.MEDIUM,
            confidence=0.6,
            sources=["Price data", "Technical indicators"]
        ))

        return factors

    def _generate_stock_factors(self, symbol: str, context: Dict) -> List[PESTLEFactor]:
        """Generate PESTLE factors for stocks"""
        factors = []

        # Political
        factors.append(PESTLEFactor(
            name="Trade Policy",
            category="Political",
            description="Impact of trade policies and tariffs",
            impact_direction=ImpactDirection.NEUTRAL,
            impact_magnitude=ImpactMagnitude.MEDIUM,
            confidence=0.6
        ))

        # Economic
        factors.append(PESTLEFactor(
            name="Economic Growth",
            category="Economic",
            description="GDP growth and consumer spending impact",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.HIGH,
            confidence=0.7
        ))

        factors.append(PESTLEFactor(
            name="Interest Rates",
            category="Economic",
            description="Fed policy impact on valuation",
            impact_direction=ImpactDirection.NEGATIVE,
            impact_magnitude=ImpactMagnitude.HIGH,
            confidence=0.8
        ))

        # Social
        factors.append(PESTLEFactor(
            name="Consumer Trends",
            category="Social",
            description="Shifting consumer preferences",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.MEDIUM,
            confidence=0.6
        ))

        # Technological
        factors.append(PESTLEFactor(
            name="Innovation Pipeline",
            category="Technological",
            description="R&D and product innovation",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.HIGH,
            confidence=0.7
        ))

        # Legal
        factors.append(PESTLEFactor(
            name="Regulatory Compliance",
            category="Legal",
            description="Industry-specific regulations",
            impact_direction=ImpactDirection.NEUTRAL,
            impact_magnitude=ImpactMagnitude.MEDIUM,
            confidence=0.7
        ))

        # Environmental
        factors.append(PESTLEFactor(
            name="ESG Initiatives",
            category="Environmental",
            description="Environmental and social governance",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.LOW,
            confidence=0.5
        ))

        # Sentiment
        factors.append(PESTLEFactor(
            name="Analyst Sentiment",
            category="Sentiment",
            description="Wall Street analyst ratings",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.MEDIUM,
            confidence=0.7
        ))

        # Technical
        factors.append(PESTLEFactor(
            name="Technical Setup",
            category="Technical",
            description="Chart patterns and momentum",
            impact_direction=ImpactDirection.NEUTRAL,
            impact_magnitude=ImpactMagnitude.MEDIUM,
            confidence=0.6
        ))

        return factors

    def _generate_forex_factors(self, symbol: str, context: Dict) -> List[PESTLEFactor]:
        """Generate PESTLE factors for forex"""
        factors = []

        # Political (high weight for forex)
        factors.append(PESTLEFactor(
            name="Political Stability",
            category="Political",
            description="Government stability and policy continuity",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.HIGH,
            confidence=0.8
        ))

        factors.append(PESTLEFactor(
            name="Geopolitical Tensions",
            category="Political",
            description="International relations and conflicts",
            impact_direction=ImpactDirection.NEGATIVE,
            impact_magnitude=ImpactMagnitude.MEDIUM,
            confidence=0.6
        ))

        # Economic (highest weight for forex)
        factors.append(PESTLEFactor(
            name="Central Bank Policy",
            category="Economic",
            description="Monetary policy divergence",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.VERY_HIGH,
            confidence=0.9
        ))

        factors.append(PESTLEFactor(
            name="Economic Data",
            category="Economic",
            description="GDP, employment, inflation trends",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.HIGH,
            confidence=0.8
        ))

        factors.append(PESTLEFactor(
            name="Yield Differential",
            category="Economic",
            description="Bond yield spread between currencies",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.HIGH,
            confidence=0.85
        ))

        # Legal
        factors.append(PESTLEFactor(
            name="Capital Controls",
            category="Legal",
            description="Currency controls and restrictions",
            impact_direction=ImpactDirection.NEUTRAL,
            impact_magnitude=ImpactMagnitude.LOW,
            confidence=0.7
        ))

        # Sentiment
        factors.append(PESTLEFactor(
            name="Risk Sentiment",
            category="Sentiment",
            description="Risk-on/risk-off environment",
            impact_direction=ImpactDirection.NEUTRAL,
            impact_magnitude=ImpactMagnitude.MEDIUM,
            confidence=0.6
        ))

        # Technical
        factors.append(PESTLEFactor(
            name="Technical Levels",
            category="Technical",
            description="Key support/resistance levels",
            impact_direction=ImpactDirection.NEUTRAL,
            impact_magnitude=ImpactMagnitude.MEDIUM,
            confidence=0.7
        ))

        return factors

    def _generate_commodity_factors(self, symbol: str, context: Dict) -> List[PESTLEFactor]:
        """Generate PESTLE factors for commodities"""
        factors = []

        # Political
        factors.append(PESTLEFactor(
            name="OPEC+ Policy",
            category="Political",
            description="Production quotas and supply management",
            impact_direction=ImpactDirection.NEUTRAL,
            impact_magnitude=ImpactMagnitude.VERY_HIGH,
            confidence=0.9
        ))

        factors.append(PESTLEFactor(
            name="Geopolitical Supply Risk",
            category="Political",
            description="Supply disruption from conflicts",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.HIGH,
            confidence=0.7
        ))

        # Economic
        factors.append(PESTLEFactor(
            name="Global Demand",
            category="Economic",
            description="Economic growth and consumption",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.HIGH,
            confidence=0.7
        ))

        # Environmental (higher weight for commodities)
        factors.append(PESTLEFactor(
            name="Climate Policy",
            category="Environmental",
            description="Energy transition impact",
            impact_direction=ImpactDirection.NEGATIVE,
            impact_magnitude=ImpactMagnitude.HIGH,
            confidence=0.6
        ))

        factors.append(PESTLEFactor(
            name="Supply Constraints",
            category="Environmental",
            description="Resource depletion and extraction costs",
            impact_direction=ImpactDirection.POSITIVE,
            impact_magnitude=ImpactMagnitude.MEDIUM,
            confidence=0.6
        ))

        # Sentiment
        factors.append(PESTLEFactor(
            name="Market Sentiment",
            category="Sentiment",
            description="Speculative positioning",
            impact_direction=ImpactDirection.NEUTRAL,
            impact_magnitude=ImpactMagnitude.MEDIUM,
            confidence=0.6
        ))

        # Technical
        factors.append(PESTLEFactor(
            name="Price Momentum",
            category="Technical",
            description="Trend and momentum indicators",
            impact_direction=ImpactDirection.NEUTRAL,
            impact_magnitude=ImpactMagnitude.MEDIUM,
            confidence=0.6
        ))

        return factors

    def _calculate_scores(self, factors: List[PESTLEFactor]) -> PESTLEPlusScore:
        """Calculate category scores from factors"""
        scores = PESTLEPlusScore()

        # Group factors by category
        category_factors = {}
        for factor in factors:
            if factor.category not in category_factors:
                category_factors[factor.category] = []
            category_factors[factor.category].append(factor)

        # Calculate each category score
        category_map = {
            'Political': scores.political,
            'Economic': scores.economic,
            'Social': scores.social,
            'Technological': scores.technological,
            'Legal': scores.legal,
            'Environmental': scores.environmental,
            'Sentiment': scores.sentiment,
            'Technical': scores.technical
        }

        for category, score_obj in category_map.items():
            if category in category_factors:
                score_obj.factors = category_factors[category]
                score_obj.calculate()

        return scores

    def _calculate_overall_score(self, scores: PESTLEPlusScore,
                                  weights: Dict[str, float]) -> float:
        """Calculate weighted overall score"""
        category_scores = {
            'Political': scores.political.normalized_score,
            'Economic': scores.economic.normalized_score,
            'Social': scores.social.normalized_score,
            'Technological': scores.technological.normalized_score,
            'Legal': scores.legal.normalized_score,
            'Environmental': scores.environmental.normalized_score,
            'Sentiment': scores.sentiment.normalized_score,
            'Technical': scores.technical.normalized_score
        }

        weighted_sum = 0
        total_weight = 0

        for category, score in category_scores.items():
            weight = weights.get(category, 0.125)
            weighted_sum += score * weight
            total_weight += weight

        if total_weight > 0:
            return weighted_sum / total_weight
        return 50.0

    def _score_to_recommendation(self, score: float) -> str:
        """Convert overall score to recommendation"""
        if score >= 80:
            return "Strong Buy"
        elif score >= 65:
            return "Buy"
        elif score >= 55:
            return "Overweight"
        elif score >= 45:
            return "Hold"
        elif score >= 35:
            return "Underweight"
        elif score >= 20:
            return "Sell"
        else:
            return "Strong Sell"

    def _calculate_confidence(self, factors: List[PESTLEFactor]) -> str:
        """Calculate overall confidence level"""
        if not factors:
            return "Low"

        avg_confidence = sum(f.confidence for f in factors) / len(factors)

        if avg_confidence >= 0.75:
            return "High"
        elif avg_confidence >= 0.5:
            return "Medium"
        else:
            return "Low"

    def format_output(self, analysis: PESTLEAnalysis) -> str:
        """Format PESTLE+ analysis as markdown"""
        output = f"""
## PESTLE+ Analysis: {analysis.symbol}

**Asset Class:** {analysis.asset_class.upper()}
**Timestamp:** {analysis.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

### Overall Assessment
| Metric | Value |
|--------|-------|
| **Overall Score** | {analysis.overall_score:.1f}/100 |
| **Recommendation** | {analysis.scores.recommendation} |
| **Confidence** | {analysis.scores.confidence_level} |

### Category Scores
| Category | Score | Assessment | Weight |
|----------|-------|------------|--------|
"""
        categories = [
            analysis.scores.political,
            analysis.scores.economic,
            analysis.scores.social,
            analysis.scores.technological,
            analysis.scores.legal,
            analysis.scores.environmental,
            analysis.scores.sentiment,
            analysis.scores.technical
        ]

        for cat in categories:
            weight = analysis.weights.get(cat.category, 0)
            output += f"| **{cat.category}** | {cat.normalized_score:.1f} | {cat.assessment} | {weight:.0%} |\n"

        output += "\n### Key Factors\n\n"

        # Group factors by category
        by_category = {}
        for factor in analysis.all_factors:
            if factor.category not in by_category:
                by_category[factor.category] = []
            by_category[factor.category].append(factor)

        for category, factors in by_category.items():
            output += f"#### {category}\n"
            for factor in factors:
                emoji = "🟢" if factor.impact_direction == ImpactDirection.POSITIVE else \
                        "🔴" if factor.impact_direction == ImpactDirection.NEGATIVE else "🟡"
                output += f"- {emoji} **{factor.name}**: {factor.description}\n"
                output += f"  - Impact: {factor.impact_magnitude.name} | Confidence: {factor.confidence:.0%}\n"

        return output


def main():
    """Example usage of PESTLEAnalysisAgent"""
    agent = PESTLEAnalysisAgent()

    # Analyze Bitcoin
    btc_analysis = agent.analyze('BTC', 'crypto')
    print(agent.format_output(btc_analysis))

    # Analyze stock
    aapl_analysis = agent.analyze('AAPL', 'stock')
    print(agent.format_output(aapl_analysis))


if __name__ == '__main__':
    main()
