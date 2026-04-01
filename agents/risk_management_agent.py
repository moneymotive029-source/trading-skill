"""
Risk Management Agent - Position sizing, stop loss, and portfolio risk
Calculates optimal position sizes and risk parameters for trades.
"""

import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskTolerance(Enum):
    CONSERVATIVE = 0.5  # 0.5% risk per trade
    MODERATE = 1.0      # 1% risk per trade
    AGGRESSIVE = 2.0    # 2% risk per trade


class PositionSizeMode(Enum):
    FIXED_FRACTIONAL = "fixed_fractional"
    KELLY_CRITERION = "kelly"
    HALF_KELLY = "half_kelly"
    QUARTER_KELLY = "quarter_kelly"
    ATR_BASED = "atr_based"
    VOLATILITY_TARGET = "volatility_target"


@dataclass
class RiskParameters:
    """Risk parameters for a trade"""
    # Input parameters
    account_size: float = 100000.0
    risk_per_trade_pct: float = 1.0
    win_rate: float = 0.50  # Historical win rate
    avg_win_loss_ratio: float = 2.0  # Average winner / Average loser

    # Position sizing method
    sizing_method: PositionSizeMode = PositionSizeMode.FIXED_FRACTIONAL

    # ATR for volatility-based sizing
    atr: Optional[float] = None
    atr_multiple: float = 2.0

    # Volatility target
    target_volatility: float = 0.15  # 15% annual volatility
    asset_volatility: float = 0.30   # 30% annual volatility


@dataclass
class PositionSizeResult:
    """Result of position size calculation"""
    # Position size
    position_size_units: float = 0.0
    position_size_value: float = 0.0
    position_size_pct: float = 0.0  # % of portfolio

    # Risk metrics
    dollar_risk: float = 0.0
    risk_reward_ratio: float = 0.0
    expected_value: float = 0.0

    # Kelly metrics
    kelly_fraction: float = 0.0
    kelly_recommended_pct: float = 0.0
    actual_fraction_of_kelly: float = 0.0

    # Stop loss
    stop_loss_price: float = 0.0
    stop_loss_distance_pct: float = 0.0
    stop_loss_distance_atr: float = 0.0

    # Take profit
    take_profit_1: float = 0.0
    take_profit_2: float = 0.0
    take_profit_3: float = 0.0

    # Method used
    method: str = ""
    confidence: str = "Medium"


@dataclass
class PortfolioRiskMetrics:
    """Portfolio-level risk metrics"""
    # Value at Risk
    var_95_1d: float = 0.0  # 95% 1-day VaR
    var_99_1d: float = 0.0  # 99% 1-day VaR
    var_95_10d: float = 0.0  # 95% 10-day VaR

    # Expected Shortfall (CVaR)
    es_95: float = 0.0
    es_99: float = 0.0

    # Portfolio metrics
    total_exposure: float = 0.0
    net_exposure: float = 0.0
    gross_exposure: float = 0.0
    leverage: float = 1.0

    # Concentration
    top_position_pct: float = 0.0
    top_3_positions_pct: float = 0.0
    herfindahl_index: float = 0.0

    # Correlation
    avg_correlation: float = 0.0
    diversification_ratio: float = 1.0

    # Drawdown
    current_drawdown: float = 0.0
    max_drawdown: float = 0.0
    drawdown_limit: float = 0.20  # 20% max drawdown

    # Risk limits
    risk_utilization: float = 0.0  # % of risk budget used
    risk_status: str = "Green"  # Green, Yellow, Red


@dataclass
class RiskAssessment:
    """Complete risk assessment for a trade"""
    symbol: str
    entry_price: float
    timestamp: datetime = None

    # Position sizing
    position_size: PositionSizeResult = None

    # Portfolio impact
    portfolio_metrics: PortfolioRiskMetrics = None

    # Risk assessment
    risk_rating: str = "Medium"  # Low, Medium, High, Very High
    risk_adjusted_return: float = 0.0
    sharpe_ratio: float = 0.0

    # Warnings and alerts
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class RiskManagementAgent:
    """
    Risk Management Agent for position sizing and risk calculation.

    Features:
    - Multiple position sizing methods (Kelly, Fixed Fractional, ATR-based)
    - Stop loss calculation based on technical levels
    - Portfolio risk metrics (VaR, CVaR, concentration)
    - Correlation analysis
    - Drawdown monitoring
    """

    def __init__(self, default_risk_tolerance: RiskTolerance = RiskTolerance.MODERATE):
        """Initialize with default risk tolerance"""
        self.default_risk_tolerance = default_risk_tolerance
        self.portfolio_positions: List[Dict] = []

    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss_price: float,
        params: RiskParameters = None
    ) -> PositionSizeResult:
        """
        Calculate optimal position size based on risk parameters.

        Args:
            entry_price: Entry price for the trade
            stop_loss_price: Stop loss price level
            params: Risk parameters (uses defaults if not provided)

        Returns:
            PositionSizeResult with size and risk metrics
        """
        if params is None:
            params = RiskParameters()

        result = PositionSizeResult()
        result.method = params.sizing_method.value

        # Calculate stop loss distance
        stop_distance_pct = abs(entry_price - stop_loss_price) / entry_price
        result.stop_loss_price = stop_loss_price
        result.stop_loss_distance_pct = stop_distance_pct

        # Calculate ATR multiple if ATR provided
        if params.atr:
            result.stop_loss_distance_atr = abs(entry_price - stop_loss_price) / params.atr

        # Calculate position size based on method
        if params.sizing_method == PositionSizeMode.FIXED_FRACTIONAL:
            result = self._fixed_fractional_size(entry_price, stop_distance_pct, params, result)
        elif params.sizing_method in [
            PositionSizeMode.KELLY_CRITERION,
            PositionSizeMode.HALF_KELLY,
            PositionSizeMode.QUARTER_KELLY
        ]:
            result = self._kelly_size(entry_price, stop_distance_pct, params, result)
        elif params.sizing_method == PositionSizeMode.ATR_BASED:
            result = self._atr_based_size(entry_price, params, result)
        elif params.sizing_method == PositionSizeMode.VOLATILITY_TARGET:
            result = self._volatility_target_size(entry_price, params, result)

        # Calculate risk/reward
        if stop_distance_pct > 0:
            # Assume 2:1 reward for initial calculation
            reward_distance = stop_distance_pct * 2
            result.risk_reward_ratio = reward_distance / stop_distance_pct
            result.take_profit_1 = entry_price * (1 + reward_distance)
            result.take_profit_2 = entry_price * (1 + reward_distance * 1.5)
            result.take_profit_3 = entry_price * (1 + reward_distance * 2)

        # Expected value
        result.expected_value = (
            params.win_rate * (result.risk_reward_ratio * result.dollar_risk) -
            (1 - params.win_rate) * result.dollar_risk
        )

        # Set confidence
        if result.kelly_fraction > 0.25:
            result.confidence = "High"
        elif result.kelly_fraction > 0.10:
            result.confidence = "Medium"
        else:
            result.confidence = "Low"

        return result

    def _fixed_fractional_size(
        self,
        entry_price: float,
        stop_distance_pct: float,
        params: RiskParameters,
        result: PositionSizeResult
    ) -> PositionSizeResult:
        """Calculate position size using fixed fractional method"""
        # Dollar amount to risk
        result.dollar_risk = params.account_size * (params.risk_per_trade_pct / 100)

        # Position size = Risk Amount / Stop Distance
        if stop_distance_pct > 0:
            result.position_size_value = result.dollar_risk / stop_distance_pct
        else:
            # No stop loss - use maximum position based on risk %
            result.position_size_value = params.account_size * (params.risk_per_trade_pct / 100) * 10

        result.position_size_units = result.position_size_value / entry_price
        result.position_size_pct = (result.position_size_value / params.account_size) * 100

        # Kelly calculation for reference
        result.kelly_fraction = self._calculate_kelly(params.win_rate, params.avg_win_loss_ratio)
        result.kelly_recommended_pct = result.kelly_fraction * 100
        if result.kelly_fraction > 0:
            result.actual_fraction_of_kelly = result.position_size_pct / result.kelly_recommended_pct

        return result

    def _kelly_size(
        self,
        entry_price: float,
        stop_distance_pct: float,
        params: RiskParameters,
        result: PositionSizeResult
    ) -> PositionSizeResult:
        """Calculate position size using Kelly Criterion"""
        # Calculate Kelly fraction
        kelly = self._calculate_kelly(params.win_rate, params.avg_win_loss_ratio)

        # Apply fractional Kelly
        if params.sizing_method == PositionSizeMode.HALF_KELLY:
            kelly = kelly / 2
            result.method = "Half Kelly"
        elif params.sizing_method == PositionSizeMode.QUARTER_KELLY:
            kelly = kelly / 4
            result.method = "Quarter Kelly"
        else:
            result.method = "Full Kelly"

        # Cap Kelly at reasonable level
        max_kelly = 0.25  # Max 25% of portfolio
        kelly = min(kelly, max_kelly)

        result.kelly_fraction = kelly
        result.kelly_recommended_pct = kelly * 100
        result.actual_fraction_of_kelly = 1.0

        # Position size value
        result.position_size_value = params.account_size * kelly
        result.position_size_units = result.position_size_value / entry_price
        result.position_size_pct = kelly * 100

        # Dollar risk (position size * stop distance)
        result.dollar_risk = result.position_size_value * stop_distance_pct

        return result

    def _atr_based_size(
        self,
        entry_price: float,
        params: RiskParameters,
        result: PositionSizeResult
    ) -> PositionSizeResult:
        """Calculate position size using ATR-based method"""
        if not params.atr:
            # Fall back to fixed fractional
            return self._fixed_fractional_size(entry_price, 0.02, params, result)

        # Position size = (Account * Risk%) / (ATR * Multiple)
        risk_amount = params.account_size * (params.risk_per_trade_pct / 100)
        stop_distance = params.atr * params.atr_multiple

        if stop_distance > 0:
            result.position_size_value = risk_amount / (stop_distance / entry_price)
        else:
            result.position_size_value = params.account_size * 0.10

        result.position_size_units = result.position_size_value / entry_price
        result.position_size_pct = (result.position_size_value / params.account_size) * 100
        result.dollar_risk = risk_amount
        result.stop_loss_distance_atr = params.atr_multiple

        # Kelly for reference
        result.kelly_fraction = self._calculate_kelly(params.win_rate, params.avg_win_loss_ratio)
        result.kelly_recommended_pct = result.kelly_fraction * 100

        return result

    def _volatility_target_size(
        self,
        entry_price: float,
        params: RiskParameters,
        result: PositionSizeResult
    ) -> PositionSizeResult:
        """Calculate position size using volatility targeting"""
        # Target weight = Target Vol / Asset Vol
        if params.asset_volatility > 0:
            target_weight = params.target_volatility / params.asset_volatility
        else:
            target_weight = 0.10

        # Cap at reasonable level
        target_weight = min(target_weight, 0.25)

        result.position_size_value = params.account_size * target_weight
        result.position_size_units = result.position_size_value / entry_price
        result.position_size_pct = target_weight * 100

        # Estimate risk
        daily_vol = params.asset_volatility / math.sqrt(252)
        result.dollar_risk = result.position_size_value * daily_vol * 2.33  # 99% VaR

        # Kelly for reference
        result.kelly_fraction = self._calculate_kelly(params.win_rate, params.avg_win_loss_ratio)
        result.kelly_recommended_pct = result.kelly_fraction * 100

        return result

    def _calculate_kelly(self, win_rate: float, win_loss_ratio: float) -> float:
        """
        Calculate Kelly Criterion fraction.

        Formula: f* = (p * b - q) / b
        Where:
        - p = probability of winning
        - q = probability of losing (1 - p)
        - b = odds received (win/loss ratio)
        """
        p = win_rate
        q = 1 - win_rate
        b = win_loss_ratio

        if b <= 0:
            return 0.0

        kelly = (p * b - q) / b

        # Kelly can be negative (don't take the trade)
        return max(0, kelly)

    def calculate_portfolio_risk(
        self,
        positions: List[Dict],
        correlations: Dict[Tuple[str, str], float] = None,
        volatilities: Dict[str, float] = None
    ) -> PortfolioRiskMetrics:
        """
        Calculate portfolio-level risk metrics.

        Args:
            positions: List of position dicts with symbol, size, value, entry_price
            correlations: Dict of (symbol1, symbol2) -> correlation
            volatilities: Dict of symbol -> annual volatility

        Returns:
            PortfolioRiskMetrics
        """
        metrics = PortfolioRiskMetrics()

        if not positions:
            return metrics

        # Calculate exposures
        total_value = sum(p.get('value', 0) for p in positions)
        long_value = sum(p.get('value', 0) for p in positions if p.get('side', 'long') == 'long')
        short_value = abs(sum(p.get('value', 0) for p in positions if p.get('side') == 'short'))

        metrics.gross_exposure = long_value + short_value
        metrics.net_exposure = long_value - short_value
        metrics.total_exposure = total_value
        metrics.leverage = metrics.gross_exposure / total_value if total_value > 0 else 1.0

        # Concentration
        position_values = [p.get('value', 0) for p in positions]
        position_pcts = [v / total_value * 100 for v in position_values] if total_value > 0 else []

        if position_pcts:
            metrics.top_position_pct = max(position_pcts)
            metrics.top_3_positions_pct = sum(sorted(position_pcts, reverse=True)[:3])

            # Herfindahl Index (concentration measure)
            metrics.herfindahl_index = sum(p ** 2 for p in position_pcts) / 10000

        # Average correlation
        if correlations and len(positions) > 1:
            corr_values = []
            symbols = [p.get('symbol') for p in positions]
            for i, s1 in enumerate(symbols):
                for s2 in symbols[i + 1:]:
                    key = (s1, s2) if s1 < s2 else (s2, s1)
                    if key in correlations:
                        corr_values.append(correlations[key])
            if corr_values:
                metrics.avg_correlation = sum(corr_values) / len(corr_values)

        # Diversification ratio
        if volatilities and correlations:
            metrics.diversification_ratio = self._calculate_diversification_ratio(
                positions, volatilities, correlations
            )

        # VaR calculations (simplified parametric VaR)
        if volatilities:
            portfolio_vol = self._calculate_portfolio_volatility(
                positions, volatilities, correlations
            )
            daily_vol = portfolio_vol / math.sqrt(252)

            # Parametric VaR
            metrics.var_95_1d = total_value * daily_vol * 1.645
            metrics.var_99_1d = total_value * daily_vol * 2.33
            metrics.var_95_10d = metrics.var_95_1d * math.sqrt(10)

            # Expected Shortfall (CVaR) - approximate
            metrics.es_95 = metrics.var_95_1d * 1.2
            metrics.es_99 = metrics.var_99_1d * 1.15

        # Risk status
        if metrics.top_3_positions_pct > 60 or metrics.herfindahl_index > 0.25:
            metrics.risk_status = "Yellow"
        if metrics.top_3_positions_pct > 80 or metrics.herfindahl_index > 0.40:
            metrics.risk_status = "Red"

        return metrics

    def _calculate_portfolio_volatility(
        self,
        positions: List[Dict],
        volatilities: Dict[str, float],
        correlations: Dict[Tuple[str, str], float]
    ) -> float:
        """Calculate portfolio volatility using covariance matrix"""
        if not positions:
            return 0.0

        n = len(positions)
        total_value = sum(p.get('value', 0) for p in positions)

        if total_value == 0:
            return 0.0

        # Weights
        weights = [p.get('value', 0) / total_value for p in positions]
        symbols = [p.get('symbol') for p in positions]

        # Portfolio variance = w' * Σ * w
        portfolio_var = 0.0

        for i in range(n):
            sym_i = symbols[i]
            vol_i = volatilities.get(sym_i, 0.20)

            # Variance contribution
            portfolio_var += (weights[i] ** 2) * (vol_i ** 2)

            # Covariance contributions
            for j in range(i + 1, n):
                sym_j = symbols[j]
                vol_j = volatilities.get(sym_j, 0.20)

                # Get correlation
                key = (sym_i, sym_j) if sym_i < sym_j else (sym_j, sym_i)
                corr = correlations.get(key, 0.5)  # Default 0.5 correlation

                # Covariance = corr * vol_i * vol_j
                cov = corr * vol_i * vol_j
                portfolio_var += 2 * weights[i] * weights[j] * cov

        return math.sqrt(portfolio_var)

    def _calculate_diversification_ratio(
        self,
        positions: List[Dict],
        volatilities: Dict[str, float],
        correlations: Dict[Tuple[str, str], float]
    ) -> float:
        """Calculate diversification ratio"""
        if not positions:
            return 1.0

        total_value = sum(p.get('value', 0) for p in positions)
        if total_value == 0:
            return 1.0

        # Weighted average volatility
        weighted_vol = 0.0
        for p in positions:
            weight = p.get('value', 0) / total_value
            vol = volatilities.get(p.get('symbol'), 0.20)
            weighted_vol += weight * vol

        # Portfolio volatility
        portfolio_vol = self._calculate_portfolio_volatility(positions, volatilities, correlations)

        if portfolio_vol > 0:
            return weighted_vol / portfolio_vol
        return 1.0

    def assess_trade_risk(
        self,
        symbol: str,
        entry_price: float,
        stop_loss: float,
        position_size_result: PositionSizeResult,
        portfolio_metrics: PortfolioRiskMetrics = None
    ) -> RiskAssessment:
        """
        Assess overall risk of a proposed trade.

        Args:
            symbol: Asset symbol
            entry_price: Proposed entry price
            stop_loss: Stop loss level
            position_size_result: Position size calculation result
            portfolio_metrics: Current portfolio risk metrics

        Returns:
            RiskAssessment with rating and recommendations
        """
        assessment = RiskAssessment(
            symbol=symbol,
            entry_price=entry_price,
            position_size=position_size_result
        )

        if portfolio_metrics:
            assessment.portfolio_metrics = portfolio_metrics
        else:
            assessment.portfolio_metrics = PortfolioRiskMetrics()

        # Determine risk rating
        risk_factors = 0

        # Position size risk
        if position_size_result.position_size_pct > 20:
            risk_factors += 2
        elif position_size_result.position_size_pct > 10:
            risk_factors += 1

        # Stop loss distance risk
        if position_size_result.stop_loss_distance_pct > 0.15:
            risk_factors += 1

        # Kelly fraction risk
        if position_size_result.kelly_fraction > 0.25:
            risk_factors += 1

        # Portfolio concentration risk
        if portfolio_metrics:
            if portfolio_metrics.top_3_positions_pct > 60:
                risk_factors += 1
            if portfolio_metrics.avg_correlation > 0.7:
                risk_factors += 2
            if portfolio_metrics.risk_status == "Red":
                risk_factors += 2
            elif portfolio_metrics.risk_status == "Yellow":
                risk_factors += 1

        # Assign rating
        if risk_factors >= 5:
            assessment.risk_rating = "Very High"
        elif risk_factors >= 3:
            assessment.risk_rating = "High"
        elif risk_factors >= 1:
            assessment.risk_rating = "Medium"
        else:
            assessment.risk_rating = "Low"

        # Generate warnings
        if position_size_result.position_size_pct > 25:
            assessment.warnings.append(
                f"Position size ({position_size_result.position_size_pct:.1f}%) exceeds 25% concentration limit"
            )

        if position_size_result.stop_loss_distance_pct > 0.20:
            assessment.warnings.append(
                f"Stop loss distance ({position_size_result.stop_loss_distance_pct:.1f}%) is very wide"
            )

        if portfolio_metrics and portfolio_metrics.avg_correlation > 0.7:
            assessment.warnings.append(
                "High portfolio correlation - consider diversifying"
            )

        # Generate recommendations
        if position_size_result.position_size_pct > 15:
            assessment.recommendations.append(
                "Consider reducing position size to limit concentration risk"
            )

        if position_size_result.kelly_fraction > 0.20:
            assessment.recommendations.append(
                "Consider using Half-Kelly or Quarter-Kelly to reduce volatility"
            )

        if portfolio_metrics and portfolio_metrics.top_3_positions_pct > 50:
            assessment.recommendations.append(
                "Portfolio is concentrated - consider adding uncorrelated assets"
            )

        # Calculate risk-adjusted return (simplified Sharpe)
        if position_size_result.expected_value != 0:
            assessment.risk_adjusted_return = (
                position_size_result.expected_value /
                (position_size_result.dollar_risk or 1)
            )
            assessment.sharpe_ratio = max(-2, min(2, assessment.risk_adjusted_return))

        return assessment

    def format_output(self, assessment: RiskAssessment) -> str:
        """Format risk assessment as markdown"""
        output = f"""
## Risk Assessment: {assessment.symbol}

**Entry Price:** ${assessment.entry_price:,.2f}
**Timestamp:** {assessment.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

### Risk Rating: {assessment.risk_rating}
"""
        if assessment.position_size:
            ps = assessment.position_size
            output += f"""
### Position Sizing ({ps.method})
| Metric | Value |
|--------|-------|
| **Position Size** | {ps.position_size_units:,.2f} units |
| **Position Value** | ${ps.position_size_value:,.2f} |
| **Position %** | {ps.position_size_pct:.2f}% |
| **Dollar Risk** | ${ps.dollar_risk:,.2f} |

### Stop Loss
| Metric | Value |
|--------|-------|
| **Stop Price** | ${ps.stop_loss_price:,.2f} |
| **Stop Distance** | {ps.stop_loss_distance_pct:.2f}% |
| **Stop Distance (ATR)** | {ps.stop_loss_distance_atr:.2f}x ATR |

### Take Profit Levels
| Level | Price | Distance |
|-------|-------|----------|
| **TP1** | ${ps.take_profit_1:,.2f} | - |
| **TP2** | ${ps.take_profit_2:,.2f} | - |
| **TP3** | ${ps.take_profit_3:,.2f} | - |

### Kelly Analysis
| Metric | Value |
|--------|-------|
| **Kelly Fraction** | {ps.kelly_fraction:.2%} |
| **Recommended %** | {ps.kelly_recommended_pct:.2f}% |
| **Fraction of Kelly** | {ps.actual_fraction_of_kelly:.2%} |

### Risk/Reward
| Metric | Value |
|--------|-------|
| **Risk/Reward Ratio** | 1:{ps.risk_reward_ratio:.2f} |
| **Expected Value** | ${ps.expected_value:,.2f} |
"""

        if assessment.portfolio_metrics:
            pm = assessment.portfolio_metrics
            output += f"""
### Portfolio Impact
| Metric | Value |
|--------|-------|
| **Gross Exposure** | ${pm.gross_exposure:,.2f} |
| **Net Exposure** | ${pm.net_exposure:,.2f} |
| **Leverage** | {pm.leverage:.2f}x |
| **Top 3 Concentration** | {pm.top_3_positions_pct:.1f}% |
| **Herfindahl Index** | {pm.herfindahl_index:.3f} |
| **Avg Correlation** | {pm.avg_correlation:.2f} |
| **Diversification Ratio** | {pm.diversification_ratio:.2f} |

### VaR Metrics
| Confidence | 1-Day VaR | 10-Day VaR |
|------------|-----------|------------|
| **95%** | ${pm.var_95_1d:,.2f} | ${pm.var_95_10d:,.2f} |
| **99%** | ${pm.var_99_1d:,.2f} | - |

### Risk Status: {pm.risk_status}
"""

        if assessment.warnings:
            output += "\n### ⚠️ Warnings\n"
            for warning in assessment.warnings:
                output += f"- {warning}\n"

        if assessment.recommendations:
            output += "\n### 💡 Recommendations\n"
            for rec in assessment.recommendations:
                output += f"- {rec}\n"

        return output


def main():
    """Example usage of RiskManagementAgent"""
    agent = RiskManagementAgent()

    # Example position size calculation
    params = RiskParameters(
        account_size=100000,
        risk_per_trade_pct=1.0,
        win_rate=0.55,
        avg_win_loss_ratio=2.0,
        sizing_method=PositionSizeMode.HALF_KELLY,
        atr=2500,
        atr_multiple=2.0
    )

    result = agent.calculate_position_size(
        entry_price=45000,
        stop_loss_price=42000,
        params=params
    )

    # Assess trade risk
    assessment = agent.assess_trade_risk(
        symbol='BTC',
        entry_price=45000,
        stop_loss=42000,
        position_size_result=result
    )

    print(agent.format_output(assessment))


if __name__ == '__main__':
    main()
