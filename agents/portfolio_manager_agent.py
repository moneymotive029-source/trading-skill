"""
Portfolio Manager Agent - Portfolio-level risk, correlation, and allocation
Manages multi-asset portfolios with correlation analysis and optimization.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OptimizationMethod(Enum):
    MEAN_VARIANCE = "mean_variance"
    RISK_PARITY = "risk_parity"
    MAX_DIVERSIFICATION = "max_diversification"
    MIN_VARIANCE = "min_variance"


@dataclass
class Position:
    """Individual portfolio position"""
    symbol: str
    asset_class: str
    quantity: float
    entry_price: float
    current_price: float
    market_value: float
    weight: float  # % of portfolio

    # P&L
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0
    realized_pnl: float = 0.0

    # Risk
    position_var: float = 0.0  # Value at Risk
    position_beta: float = 1.0

    def calculate_pnl(self):
        """Calculate P&L"""
        self.unrealized_pnl = (self.current_price - self.entry_price) * self.quantity
        self.unrealized_pnl_pct = (self.current_price - self.entry_price) / self.entry_price * 100


@dataclass
class CorrelationMatrix:
    """Asset correlation data"""
    assets: List[str]
    matrix: List[List[float]]
    period: str  # e.g., "30D", "90D", "1Y"

    def get_correlation(self, asset1: str, asset2: str) -> Optional[float]:
        """Get correlation between two assets"""
        if asset1 not in self.assets or asset2 not in self.assets:
            return None
        i = self.assets.index(asset1)
        j = self.assets.index(asset2)
        return self.matrix[i][j]

    def get_high_correlations(self, threshold: float = 0.7) -> List[Tuple[str, str, float]]:
        """Find all pairs with correlation above threshold"""
        high_corr = []
        n = len(self.assets)
        for i in range(n):
            for j in range(i + 1, n):
                corr = self.matrix[i][j]
                if abs(corr) >= threshold:
                    high_corr.append((self.assets[i], self.assets[j], corr))
        return high_corr


@dataclass
class RiskMetrics:
    """Portfolio risk metrics"""
    # Value at Risk
    var_95_1d: float = 0.0
    var_99_1d: float = 0.0
    var_95_10d: float = 0.0

    # Expected Shortfall (CVaR)
    es_95: float = 0.0
    es_99: float = 0.0

    # Portfolio volatility
    portfolio_volatility: float = 0.0  # Annualized
    downside_volatility: float = 0.0

    # Beta and correlation
    portfolio_beta: float = 1.0
    correlation_to_benchmark: float = 0.0

    # Concentration
    herfindahl_index: float = 0.0
    top_3_concentration: float = 0.0
    effective_n: float = 0.0  # Effective number of uncorrelated bets

    # Diversification
    diversification_ratio: float = 1.0
    idiosyncratic_risk_pct: float = 0.0


@dataclass
class OptimizationResult:
    """Portfolio optimization result"""
    method: OptimizationMethod
    current_weights: Dict[str, float]
    optimized_weights: Dict[str, float]
    trades_required: List[Dict]

    # Improvement metrics
    current_sharpe: float
    optimized_sharpe: float
    current_volatility: float
    optimized_volatility: float
    current_return: float
    optimized_return: float

    # Constraints applied
    constraints: Dict = field(default_factory=dict)


@dataclass
class PortfolioReport:
    """Complete portfolio analysis report"""
    portfolio_name: str
    report_date: datetime = None

    # Portfolio summary
    total_value: float = 0.0
    cash_balance: float = 0.0
    positions: List[Position] = field(default_factory=list)

    # Returns
    total_return: float = 0.0
    total_return_pct: float = 0.0
    daily_return: float = 0.0
    ytd_return: float = 0.0

    # Risk
    risk_metrics: RiskMetrics = None

    # Correlation
    correlation_matrix: CorrelationMatrix = None

    # Asset allocation
    allocation_by_class: Dict[str, float] = field(default_factory=dict)
    allocation_by_sector: Dict[str, float] = field(default_factory=dict)
    allocation_by_region: Dict[str, float] = field(default_factory=dict)

    # Optimization
    optimization_result: Optional[OptimizationResult] = None

    # Alerts
    rebalancing_alerts: List[Dict] = field(default_factory=list)
    risk_alerts: List[str] = field(default_factory=list)

    # Drawdown
    current_drawdown: float = 0.0
    max_drawdown: float = 0.0
    drawdown_limit: float = 0.20

    def __post_init__(self):
        if self.report_date is None:
            self.report_date = datetime.utcnow()


class PortfolioManagerAgent:
    """
    Portfolio Manager Agent for portfolio-level analysis.

    Features:
    - Correlation analysis
    - Risk aggregation (VaR, CVaR)
    - Asset allocation
    - Portfolio optimization
    - Rebalancing recommendations
    """

    def __init__(self, benchmark: str = "SPY"):
        """
        Initialize portfolio manager.

        Args:
            benchmark: Benchmark symbol for beta calculation
        """
        self.benchmark = benchmark
        self.report: Optional[PortfolioReport] = None

    def analyze_portfolio(
        self,
        positions: List[Dict],
        prices: Dict[str, float],
        historical_returns: pd.DataFrame = None,
        initial_capital: float = None
    ) -> PortfolioReport:
        """
        Perform comprehensive portfolio analysis.

        Args:
            positions: List of position dicts with symbol, quantity, entry_price, asset_class
            prices: Dict of current prices by symbol
            historical_returns: DataFrame of historical returns for correlation/risk calc
            initial_capital: Initial capital for return calculation

        Returns:
            PortfolioReport with complete analysis
        """
        report = PortfolioReport(
            portfolio_name="Trading Portfolio"
        )

        # Calculate position values and weights
        total_value = sum(
            p['quantity'] * prices.get(p['symbol'], p['entry_price'])
            for p in positions
        )
        report.total_value = total_value

        # Build positions
        for p in positions:
            current_price = prices.get(p['symbol'], p['entry_price'])
            position = Position(
                symbol=p['symbol'],
                asset_class=p.get('asset_class', 'unknown'),
                quantity=p['quantity'],
                entry_price=p['entry_price'],
                current_price=current_price,
                market_value=current_price * p['quantity'],
                weight=0.0
            )
            position.calculate_pnl()
            position.weight = position.market_value / total_value * 100 if total_value > 0 else 0
            report.positions.append(position)

        # Calculate returns
        if initial_capital:
            report.total_return = total_value - initial_capital
            report.total_return_pct = report.total_return / initial_capital * 100

        # Asset allocation
        report.allocation_by_class = self._calculate_allocation_by_class(report.positions)

        # Risk metrics
        if historical_returns is not None:
            report.risk_metrics = self._calculate_risk_metrics(report.positions, historical_returns)
        else:
            report.risk_metrics = RiskMetrics()

        # Correlation matrix
        if historical_returns is not None:
            report.correlation_matrix = self._build_correlation_matrix(historical_returns)

        # Concentration metrics
        if report.risk_metrics:
            weights = [p.weight / 100 for p in report.positions]
            report.risk_metrics.herfindahl_index = sum(w ** 2 for w in weights)
            report.risk_metrics.top_3_concentration = sum(sorted(weights, reverse=True)[:3]) * 100
            report.risk_metrics.effective_n = 1 / sum(w ** 2 for w in weights) if sum(w ** 2 for w in weights) > 0 else len(positions)

        # Generate rebalancing alerts
        report.rebalancing_alerts = self._check_rebalancing_needs(report.positions)

        # Risk alerts
        report.risk_alerts = self._generate_risk_alerts(report.risk_metrics)

        # Drawdown analysis
        report.current_drawdown = self._calculate_current_drawdown(report, initial_capital)

        self.report = report
        return report

    def _calculate_allocation_by_class(self, positions: List[Position]) -> Dict[str, float]:
        """Calculate allocation by asset class"""
        allocation = {}
        for p in positions:
            asset_class = p.asset_class
            allocation[asset_class] = allocation.get(asset_class, 0) + p.weight
        return allocation

    def _calculate_risk_metrics(
        self,
        positions: List[Position],
        historical_returns: pd.DataFrame
    ) -> RiskMetrics:
        """Calculate portfolio risk metrics"""
        metrics = RiskMetrics()

        # Get weights
        weights = np.array([p.weight / 100 for p in positions])

        # Filter returns to only include portfolio assets
        symbols = [p.symbol for p in positions]
        available_symbols = [s for s in symbols if s in historical_returns.columns]

        if not available_symbols or len(historical_returns) < 10:
            return metrics

        portfolio_returns = historical_returns[available_symbols]

        # Realign weights to match available symbols
        aligned_weights = weights[:len(available_symbols)]

        # Portfolio volatility
        if len(portfolio_returns.columns) > 1:
            cov_matrix = portfolio_returns.cov() * 252  # Annualized
            portfolio_var = np.dot(aligned_weights.T, np.dot(cov_matrix, aligned_weights))
            metrics.portfolio_volatility = np.sqrt(portfolio_var) * 100
        else:
            metrics.portfolio_volatility = portfolio_returns.std().iloc[0] * np.sqrt(252) * 100

        # Daily volatility
        metrics.downside_volatility = portfolio_returns.min().std() * np.sqrt(252) * 100

        # Value at Risk (parametric)
        portfolio_mean = portfolio_returns.mean().sum() * 252
        metrics.var_95_1d = (portfolio_mean - 1.645 * metrics.portfolio_volatility / 100)
        metrics.var_99_1d = (portfolio_mean - 2.33 * metrics.portfolio_volatility / 100)
        metrics.var_95_10d = metrics.var_95_1d * np.sqrt(10)

        # Expected Shortfall (approximate)
        metrics.es_95 = metrics.var_95_1d * 1.2
        metrics.es_99 = metrics.var_99_1d * 1.15

        return metrics

    def _build_correlation_matrix(self, historical_returns: pd.DataFrame) -> CorrelationMatrix:
        """Build correlation matrix from historical returns"""
        corr_matrix = historical_returns.corr()

        assets = list(corr_matrix.columns)
        matrix = corr_matrix.values.tolist()

        return CorrelationMatrix(
            assets=assets,
            matrix=matrix,
            period="90D"
        )

    def _check_rebalancing_needs(self, positions: List[Position]) -> List[Dict]:
        """Check if any positions need rebalancing"""
        alerts = []

        # Target weights (simplified - equal weight for demo)
        n_positions = len(positions)
        target_weight = 100 / n_positions if n_positions > 0 else 0

        for p in positions:
            drift = p.weight - target_weight
            if abs(drift) > 5:  # 5% threshold
                alerts.append({
                    'symbol': p.symbol,
                    'current_weight': p.weight,
                    'target_weight': target_weight,
                    'drift': drift,
                    'action': 'sell' if drift > 0 else 'buy'
                })

        return alerts

    def _generate_risk_alerts(self, metrics: RiskMetrics) -> List[str]:
        """Generate risk alerts"""
        alerts = []

        if metrics.portfolio_volatility > 30:
            alerts.append(f"High portfolio volatility: {metrics.portfolio_volatility:.1f}%")

        if metrics.herfindahl_index > 0.25:
            alerts.append(f"High concentration (HHI: {metrics.herfindahl_index:.3f})")

        if metrics.top_3_concentration > 60:
            alerts.append(f"Top 3 positions = {metrics.top_3_concentration:.1f}% of portfolio")

        if metrics.effective_n < 3:
            alerts.append(f"Low diversification (effective N: {metrics.effective_n:.1f})")

        return alerts

    def _calculate_current_drawdown(
        self,
        report: PortfolioReport,
        initial_capital: float
    ) -> float:
        """Calculate current drawdown from peak"""
        if not initial_capital:
            return 0.0

        peak_value = max(initial_capital, report.total_value)
        if peak_value > 0:
            return (peak_value - report.total_value) / peak_value * 100
        return 0.0

    def optimize_portfolio(
        self,
        historical_returns: pd.DataFrame,
        method: OptimizationMethod = OptimizationMethod.MEAN_VARIANCE,
        constraints: Dict = None
    ) -> OptimizationResult:
        """
        Optimize portfolio allocation.

        Args:
            historical_returns: DataFrame of historical returns
            method: Optimization method to use
            constraints: Dict with constraints like max_weight, min_weight, etc.

        Returns:
            OptimizationResult with optimized weights
        """
        if constraints is None:
            constraints = {}

        result = OptimizationResult(
            method=method,
            current_weights={},
            optimized_weights={},
            trades_required=[]
        )

        if self.report:
            result.current_weights = {p.symbol: p.weight for p in self.report.positions}

        # Get available symbols
        symbols = list(historical_returns.columns)
        n_assets = len(symbols)

        # Calculate expected returns and covariance
        expected_returns = historical_returns.mean() * 252  # Annualized
        cov_matrix = historical_returns.cov() * 252

        # Simple optimization (equal weight as baseline)
        if method == OptimizationMethod.MEAN_VARIANCE:
            # Simplified mean-variance (not full efficient frontier)
            weights = self._mean_variance_optimize(
                expected_returns, cov_matrix, constraints
            )
        elif method == OptimizationMethod.RISK_PARITY:
            weights = self._risk_parity_optimize(cov_matrix, constraints)
        elif method == OptimizationMethod.MAX_DIVERSIFICATION:
            weights = self._max_diversification_optimize(cov_matrix, constraints)
        elif method == OptimizationMethod.MIN_VARIANCE:
            weights = self._min_variance_optimize(cov_matrix, constraints)
        else:
            # Equal weight
            weights = np.ones(n_assets) / n_assets

        # Apply constraints
        max_weight = constraints.get('max_weight', 0.25)
        min_weight = constraints.get('min_weight', 0.0)

        weights = np.clip(weights, min_weight, max_weight)
        weights = weights / weights.sum()  # Renormalize

        # Build result
        result.optimized_weights = {symbols[i]: weights[i] * 100 for i in range(n_assets)}

        # Calculate trades required
        if self.report:
            for symbol in symbols:
                current = result.current_weights.get(symbol, 0)
                target = result.optimized_weights.get(symbol, 0)
                if abs(current - target) > 1:  # 1% threshold
                    result.trades_required.append({
                        'symbol': symbol,
                        'action': 'buy' if target > current else 'sell',
                        'current_weight': current,
                        'target_weight': target,
                        'change': target - current
                    })

        # Estimate improvement (simplified)
        result.current_sharpe = 1.0  # Would calculate from actual data
        result.optimized_sharpe = result.current_sharpe * 1.1  # Assume 10% improvement
        result.current_volatility = 20.0
        result.optimized_volatility = 18.0

        return result

    def _mean_variance_optimize(
        self,
        expected_returns: pd.Series,
        cov_matrix: pd.DataFrame,
        constraints: Dict
    ) -> np.ndarray:
        """Mean-variance optimization (simplified)"""
        n = len(expected_returns)

        # Simplified: use inverse volatility weighting with return tilt
        vols = np.sqrt(np.diag(cov_matrix))
        inv_vols = 1 / vols
        weights = inv_vols * (1 + expected_returns.values)
        weights = weights / weights.sum()

        return weights

    def _risk_parity_optimize(
        self,
        cov_matrix: pd.DataFrame,
        constraints: Dict
    ) -> np.ndarray:
        """Risk parity optimization (equal risk contribution)"""
        n = cov_matrix.shape[0]
        vols = np.sqrt(np.diag(cov_matrix))

        # Risk parity: inverse volatility
        weights = 1 / vols
        weights = weights / weights.sum()

        return weights

    def _max_diversification_optimize(
        self,
        cov_matrix: pd.DataFrame,
        constraints: Dict
    ) -> np.ndarray:
        """Maximum diversification optimization"""
        n = cov_matrix.shape[0]
        vols = np.sqrt(np.diag(cov_matrix))

        # Max diversification tends toward equal risk
        weights = 1 / vols
        weights = weights / weights.sum()

        return weights

    def _min_variance_optimize(
        self,
        cov_matrix: pd.DataFrame,
        constraints: Dict
    ) -> np.ndarray:
        """Minimum variance portfolio"""
        n = cov_matrix.shape[0]

        # Simplified: use inverse covariance
        try:
            inv_cov = np.linalg.inv(cov_matrix)
            ones = np.ones(n)
            weights = np.dot(inv_cov, ones)
            weights = weights / weights.sum()
        except:
            # Fall back to equal weight
            weights = np.ones(n) / n

        return weights

    def format_output(self, report: PortfolioReport) -> str:
        """Format portfolio report as markdown"""
        output = f"""
# Portfolio Management Report

**Portfolio:** {report.portfolio_name}
**Report Date:** {report.report_date.strftime('%Y-%m-%d %H:%M:%S UTC')}
**Total Value:** ${report.total_value:,.2f}

---

## Portfolio Summary

### Current Positions

| Asset | Position | Value | Weight | P&L | P&L % |
|-------|----------|-------|--------|-----|-------|
"""
        for p in report.positions:
            pnl_sign = "+" if p.unrealized_pnl >= 0 else ""
            output += f"| **{p.symbol}** | {p.quantity:,.4f} | ${p.market_value:,.2f} | {p.weight:.1f}% | {pnl_sign}${p.unrealized_pnl:,.2f} | {pnl_sign}{p.unrealized_pnl_pct:.2f}% |\n"

        # Add cash
        if report.cash_balance > 0:
            cash_weight = report.cash_balance / (report.total_value + report.cash_balance) * 100
            output += f"| **Cash** | - | ${report.cash_balance:,.2f} | {cash_weight:.1f}% | - | - |\n"

        total_weight = sum(p.weight for p in report.positions)
        output += f"| **TOTAL** | - | ${report.total_value:,.2f} | {total_weight:.1f}% | - | - |\n"

        # Asset allocation
        if report.allocation_by_class:
            output += "\n### Asset Allocation\n"
            output += "| Asset Class | Weight |\n"
            output += "|-------------|--------|\n"
            for asset_class, weight in sorted(report.allocation_by_class.items(), key=lambda x: x[1], reverse=True):
                output += f"| **{asset_class.title()}** | {weight:.1f}% |\n"

        # Returns
        output += f"""
---

## Performance

| Metric | Value |
|--------|-------|
| **Total Return** | ${report.total_return:,.2f} ({report.total_return_pct:.2f}%) |
| **Daily Return** | ${report.daily_return:,.2f} |
| **YTD Return** | {report.ytd_return:.2f}% |
"""

        # Risk metrics
        if report.risk_metrics:
            rm = report.risk_metrics
            output += f"""
---

## Risk Analysis

### Value at Risk (VaR)
| Confidence | 1-Day VaR | 10-Day VaR |
|------------|-----------|------------|
| **95%** | {rm.var_95_1d:.2f}% | {rm.var_95_10d:.2f}% |
| **99%** | {rm.var_99_1d:.2f}% | - |

### Portfolio Volatility
| Metric | Value |
|--------|-------|
| **Annualized Volatility** | {rm.portfolio_volatility:.1f}% |
| **Downside Volatility** | {rm.downside_volatility:.1f}% |

### Concentration
| Metric | Value | Assessment |
|--------|-------|------------|
| **Herfindahl Index** | {rm.herfindahl_index:.3f} | {'High' if rm.herfindahl_index > 0.25 else 'Moderate' if rm.herfindahl_index > 0.15 else 'Low'} |
| **Top 3 Concentration** | {rm.top_3_concentration:.1f}% | {'High' if rm.top_3_concentration > 60 else 'Moderate'} |
| **Effective N** | {rm.effective_n:.1f} | {'Low' if rm.effective_n < 3 else 'Adequate'} |
| **Diversification Ratio** | {rm.diversification_ratio:.2f} | - |
"""

        # Correlation matrix
        if report.correlation_matrix:
            output += "\n### Correlation Matrix\n"
            assets = report.correlation_matrix.assets
            matrix = report.correlation_matrix.matrix

            # Header
            output += "| | " + " | ".join(f"{a[:6]}" for a in assets) + " |\n"
            output += "|" + "|".join(["---"] * (len(assets) + 1)) + "|\n"

            # Rows
            for i, asset in enumerate(assets):
                row = [f"{matrix[i][j]:.2f}" if i != j else "1.00" for j in range(len(assets))]
                output += f"| **{asset[:6]}** | " + " | ".join(row) + " |\n"

            # High correlations
            high_corr = report.correlation_matrix.get_high_correlations(0.7)
            if high_corr:
                output += "\n**High Correlation Pairs (⚠️):**\n"
                for a1, a2, corr in high_corr:
                    output += f"- {a1} - {a2}: {corr:.2f}\n"

        # Rebalancing alerts
        if report.rebalancing_alerts:
            output += "\n---\n\n## Rebalancing Alerts\n"
            output += "| Symbol | Current | Target | Drift | Action |\n"
            output += "|--------|---------|--------|-------|--------|\n"
            for alert in report.rebalancing_alerts:
                action_emoji = "🔴" if alert['action'] == 'sell' else "🟢"
                output += f"| {alert['symbol']} | {alert['current_weight']:.1f}% | {alert['target_weight']:.1f}% | {alert['drift']:+.1f}% | {action_emoji} {alert['action'].upper()} |\n"

        # Risk alerts
        if report.risk_alerts:
            output += "\n---\n\n## ⚠️ Risk Alerts\n"
            for alert in report.risk_alerts:
                output += f"- {alert}\n"

        # Drawdown
        output += f"""
---

## Drawdown Analysis

| Metric | Value |
|--------|-------|
| **Current Drawdown** | {report.current_drawdown:.2f}% |
| **Max Drawdown** | {report.max_drawdown:.2f}% |
| **Drawdown Limit** | {report.drawdown_limit * 100:.0f}% |
| **Status** | {'🔴 BREACHED' if report.current_drawdown > report.drawdown_limit * 100 else '🟡 WARNING' if report.current_drawdown > report.drawdown_limit * 100 * 0.5 else '🟢 OK'} |
"""

        return output


def main():
    """Example usage of PortfolioManagerAgent"""
    # Sample positions
    positions = [
        {'symbol': 'BTC', 'asset_class': 'crypto', 'quantity': 1.5, 'entry_price': 42000},
        {'symbol': 'ETH', 'asset_class': 'crypto', 'quantity': 10.0, 'entry_price': 2800},
        {'symbol': 'AAPL', 'asset_class': 'stock', 'quantity': 50.0, 'entry_price': 175},
        {'symbol': 'GOOGL', 'asset_class': 'stock', 'quantity': 20.0, 'entry_price': 140},
        {'symbol': 'GOLD', 'asset_class': 'commodity', 'quantity': 10.0, 'entry_price': 2000},
    ]

    # Current prices
    prices = {
        'BTC': 45000,
        'ETH': 3100,
        'AAPL': 185,
        'GOOGL': 155,
        'GOLD': 2050,
    }

    # Generate sample historical returns
    np.random.seed(42)
    dates = pd.date_range(end=datetime.utcnow(), periods=252, freq='D')
    returns = pd.DataFrame({
        'BTC': np.random.randn(252) * 0.04,
        'ETH': np.random.randn(252) * 0.05,
        'AAPL': np.random.randn(252) * 0.02,
        'GOOGL': np.random.randn(252) * 0.022,
        'GOLD': np.random.randn(252) * 0.012,
    }, index=dates)

    # Analyze portfolio
    agent = PortfolioManagerAgent()
    report = agent.analyze_portfolio(
        positions=positions,
        prices=prices,
        historical_returns=returns,
        initial_capital=250000
    )

    print(agent.format_output(report))


if __name__ == '__main__':
    main()
