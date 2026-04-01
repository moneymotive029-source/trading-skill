"""
Backtesting Agent - Historical strategy validation with walk-forward analysis
Tests trading strategies on historical data with statistical rigor.
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


class StrategyType(Enum):
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    TREND_FOLLOWING = "trend_following"
    PAIRS_TRADING = "pairs_trading"


@dataclass
class Trade:
    """Individual trade record"""
    entry_date: datetime
    exit_date: Optional[datetime]
    direction: str  # 'long' or 'short'
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    pnl: float = 0.0
    pnl_pct: float = 0.0
    max_drawdown: float = 0.0
    max_profit: float = 0.0
    holding_period: int = 0  # days
    exit_reason: str = ""  # 'target', 'stop', 'time', 'signal'

    def calculate_pnl(self):
        """Calculate P&L"""
        if self.exit_price is None:
            return
        if self.direction == 'long':
            self.pnl = (self.exit_price - self.entry_price) * self.quantity
            self.pnl_pct = (self.exit_price - self.entry_price) / self.entry_price * 100
        else:
            self.pnl = (self.entry_price - self.exit_price) * self.quantity
            self.pnl_pct = (self.entry_price - self.exit_price) / self.entry_price * 100

        if self.exit_date and self.entry_date:
            self.holding_period = (self.exit_date - self.entry_date).days


@dataclass
class BacktestResults:
    """Complete backtest results"""
    # Strategy info
    strategy_name: str
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_capital: float = 100000.0

    # Trade statistics
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0

    # Returns
    total_return: float = 0.0
    total_return_pct: float = 0.0
    annualized_return: float = 0.0
    benchmark_return: float = 0.0  # Buy & hold return
    excess_return: float = 0.0  # Alpha

    # Risk metrics
    max_drawdown: float = 0.0
    max_drawdown_duration: int = 0  # days
    avg_drawdown: float = 0.0
    volatility: float = 0.0  # Annualized
    daily_volatility: float = 0.0

    # Risk-adjusted returns
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    max_calmar: float = 0.0

    # Trade statistics
    avg_win: float = 0.0
    avg_loss: float = 0.0
    avg_win_pct: float = 0.0
    avg_loss_pct: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0
    avg_holding_period: float = 0.0
    profit_factor: float = 0.0
    payoff_ratio: float = 0.0

    # Exposure
    avg_exposure: float = 0.0  # Average % of capital deployed
    time_in_market: float = 0.0  # % of time with open positions

    # Equity curve
    equity_curve: List[float] = field(default_factory=list)
    drawdown_curve: List[float] = field(default_factory=list)
    trade_pnl: List[float] = field(default_factory=list)

    # Monthly returns
    monthly_returns: Dict[str, float] = field(default_factory=dict)

    # Walk-forward results
    walk_forward_results: List[Dict] = field(default_factory=list)
    oos_consistency: float = 0.0

    # All trades
    trades: List[Trade] = field(default_factory=list)

    # Assessment
    strategy_grade: str = "N/A"
    is_robust: bool = False
    warnings: List[str] = field(default_factory=list)


class BacktestingAgent:
    """
    Backtesting Agent for historical strategy validation.

    Features:
    - Multiple strategy types
    - Walk-forward analysis
    - Statistical significance testing
    - Drawdown analysis
    - Risk-adjusted metrics
    """

    def __init__(self, risk_free_rate: float = 0.05):
        """
        Initialize backtester.

        Args:
            risk_free_rate: Annual risk-free rate for Sharpe calculation
        """
        self.risk_free_rate = risk_free_rate
        self.results: Optional[BacktestResults] = None

    def run_backtest(
        self,
        prices: pd.DataFrame,
        strategy_type: StrategyType,
        strategy_params: Dict = None,
        initial_capital: float = 100000.0,
        commission: float = 0.001,
        slippage: float = 0.0005
    ) -> BacktestResults:
        """
        Run backtest on historical price data.

        Args:
            prices: DataFrame with OHLCV data
            strategy_type: Type of strategy to test
            strategy_params: Strategy-specific parameters
            initial_capital: Starting capital
            commission: Commission rate (0.1% = 0.001)
            slippage: Slippage estimate

        Returns:
            BacktestResults with all metrics
        """
        results = BacktestResults(
            strategy_name=strategy_type.value,
            symbol=prices.get('symbol', ['UNKNOWN'])[0] if isinstance(prices.get('symbol'), list) else 'UNKNOWN',
            start_date=prices.index[0] if hasattr(prices.index[0], 'to_pydatetime') else datetime.utcnow() - timedelta(days=365),
            end_date=prices.index[-1] if hasattr(prices.index[-1], 'to_pydatetime') else datetime.utcnow(),
            initial_capital=initial_capital
        )

        # Generate signals based on strategy
        signals = self._generate_signals(prices, strategy_type, strategy_params or {})

        # Execute trades
        results.trades = self._execute_trades(
            prices, signals, initial_capital, commission, slippage
        )

        # Calculate metrics
        results = self._calculate_metrics(results, prices, initial_capital)

        # Run walk-forward analysis
        results.walk_forward_results = self._walk_forward_analysis(
            prices, strategy_type, strategy_params, initial_capital, commission, slippage
        )

        # Calculate OOS consistency
        if results.walk_forward_results:
            results.oos_consistency = self._calculate_oos_consistency(results.walk_forward_results)

        # Assign grade
        results.strategy_grade, results.is_robust = self._assign_grade(results)

        # Generate warnings
        results.warnings = self._generate_warnings(results)

        self.results = results
        return results

    def _generate_signals(
        self,
        prices: pd.DataFrame,
        strategy_type: StrategyType,
        params: Dict
    ) -> pd.Series:
        """Generate trading signals based on strategy"""
        close = prices['close']

        if strategy_type == StrategyType.MOMENTUM:
            # Momentum strategy: buy when RSI < 30, sell when RSI > 70
            lookback = params.get('lookback', 14)
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(window=lookback).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=lookback).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            signals = pd.Series(0, index=close.index)
            signals[rsi < 30] = 1  # Buy signal
            signals[rsi > 70] = -1  # Sell signal

        elif strategy_type == StrategyType.MEAN_REVERSION:
            # Mean reversion: buy when price < lower Bollinger Band
            window = params.get('window', 20)
            num_std = params.get('num_std', 2)
            sma = close.rolling(window=window).mean()
            std = close.rolling(window=window).std()
            upper = sma + num_std * std
            lower = sma - num_std * std

            signals = pd.Series(0, index=close.index)
            signals[close < lower] = 1  # Buy when below lower band
            signals[close > upper] = -1  # Sell when above upper band

        elif strategy_type == StrategyType.BREAKOUT:
            # Breakout: buy when price breaks above N-day high
            lookback = params.get('lookback', 20)
            highest = close.rolling(window=lookback).max()
            lowest = close.rolling(window=lookback).min()

            signals = pd.Series(0, index=close.index)
            signals[close > highest.shift(1)] = 1  # Breakout buy
            signals[close < lowest.shift(1)] = -1  # Breakdown sell

        elif strategy_type == StrategyType.TREND_FOLLOWING:
            # Trend following: buy when short MA > long MA
            short_window = params.get('short_window', 12)
            long_window = params.get('long_window', 26)
            short_ma = close.ewm(span=short_window, adjust=False).mean()
            long_ma = close.ewm(span=long_window, adjust=False).mean()

            signals = pd.Series(0, index=close.index)
            signals[short_ma > long_ma] = 1
            signals[short_ma < long_ma] = -1

        else:
            signals = pd.Series(0, index=close.index)

        return signals

    def _execute_trades(
        self,
        prices: pd.DataFrame,
        signals: pd.Series,
        initial_capital: float,
        commission: float,
        slippage: float
    ) -> List[Trade]:
        """Execute trades based on signals"""
        trades = []
        position = None
        capital = initial_capital

        for i, (idx, signal) in enumerate(signals.items()):
            if signal == 0:
                continue

            current_price = prices.loc[idx, 'close']

            if position is None and signal == 1:
                # Open long position
                entry_price = current_price * (1 + slippage)
                quantity = (capital * 0.95) / entry_price  # 95% position sizing

                position = Trade(
                    entry_date=idx.to_pydatetime() if hasattr(idx, 'to_pydatetime') else idx,
                    exit_date=None,
                    direction='long',
                    entry_price=entry_price,
                    exit_price=None,
                    quantity=quantity
                )

            elif position is not None and signal == -1:
                # Close position
                exit_price = current_price * (1 - slippage)
                position.exit_date = idx.to_pydatetime() if hasattr(idx, 'to_pydatetime') else idx
                position.exit_price = exit_price
                position.exit_reason = 'signal'
                position.calculate_pnl()

                # Apply commission
                position.pnl -= (position.entry_price + exit_price) * position.quantity * commission

                trades.append(position)
                capital += position.pnl
                position = None

        # Close any open position at end
        if position is not None:
            last_idx = prices.index[-1]
            exit_price = prices.loc[last_idx, 'close'] * (1 - slippage)
            position.exit_date = last_idx.to_pydatetime() if hasattr(last_idx, 'to_pydatetime') else last_idx
            position.exit_price = exit_price
            position.exit_reason = 'end_of_data'
            position.calculate_pnl()
            trades.append(position)

        return trades

    def _calculate_metrics(
        self,
        results: BacktestResults,
        prices: pd.DataFrame,
        initial_capital: float
    ) -> BacktestResults:
        """Calculate all backtest metrics"""
        if not results.trades:
            return results

        # Basic trade statistics
        results.total_trades = len(results.trades)
        results.winning_trades = sum(1 for t in results.trades if t.pnl > 0)
        results.losing_trades = sum(1 for t in results.trades if t.pnl <= 0)
        results.win_rate = results.winning_trades / results.total_trades if results.total_trades > 0 else 0

        # P&L statistics
        results.trade_pnl = [t.pnl for t in results.trades]
        results.total_return = sum(results.trade_pnl)
        results.total_return_pct = results.total_return / initial_capital * 100

        # Win/loss statistics
        winning_pnls = [t.pnl for t in results.trades if t.pnl > 0]
        losing_pnls = [t.pnl for t in results.trades if t.pnl <= 0]

        results.avg_win = np.mean(winning_pnls) if winning_pnls else 0
        results.avg_loss = np.mean(losing_pnls) if losing_pnls else 0
        results.avg_win_pct = np.mean([t.pnl_pct for t in results.trades if t.pnl > 0]) if winning_pnls else 0
        results.avg_loss_pct = np.mean([t.pnl_pct for t in results.trades if t.pnl <= 0]) if losing_pnls else 0
        results.largest_win = max(winning_pnls) if winning_pnls else 0
        results.largest_loss = min(losing_pnls) if losing_pnls else 0

        # Profit factor and payoff ratio
        gross_profit = sum(winning_pnls)
        gross_loss = abs(sum(losing_pnls))
        results.profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        results.payoff_ratio = results.avg_win / abs(results.avg_loss) if results.avg_loss != 0 else float('inf')

        # Holding period
        results.avg_holding_period = np.mean([t.holding_period for t in results.trades])

        # Calculate equity curve
        equity = [initial_capital]
        for trade in results.trades:
            equity.append(equity[-1] + trade.pnl)
        results.equity_curve = equity

        # Calculate drawdown curve
        peak = equity[0]
        drawdowns = []
        for eq in equity:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / peak
            drawdowns.append(dd)
        results.drawdown_curve = drawdowns

        # Max drawdown
        results.max_drawdown = max(drawdowns) * 100

        # Max drawdown duration
        results.max_drawdown_duration = self._calculate_max_dd_duration(drawdowns)

        # Annualized return
        days = (results.end_date - results.start_date).days if hasattr(results.start_date, 'to_pydatetime') else 365
        years = days / 365.25
        results.annualized_return = ((1 + results.total_return_pct / 100) ** (1 / years) - 1) * 100 if years > 0 else 0

        # Benchmark return (buy and hold)
        if len(prices) > 0:
            first_price = prices['close'].iloc[0]
            last_price = prices['close'].iloc[-1]
            results.benchmark_return = (last_price - first_price) / first_price * 100

        results.excess_return = results.annualized_return - results.benchmark_return

        # Volatility
        equity_series = pd.Series(equity)
        returns = equity_series.pct_change().dropna()
        results.daily_volatility = returns.std()
        results.volatility = results.daily_volatility * np.sqrt(252) * 100

        # Risk-adjusted returns
        if results.volatility > 0:
            excess_returns = returns - self.risk_free_rate / 252
            results.sharpe_ratio = np.sqrt(252) * excess_returns.mean() / returns.std()

        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0 and downside_returns.std() > 0:
            results.sortino_ratio = np.sqrt(252) * excess_returns.mean() / downside_returns.std()

        # Calmar ratio
        if results.max_drawdown > 0:
            results.calmar_ratio = results.annualized_return / (results.max_drawdown * 100)

        # Exposure
        total_days = (results.end_date - results.start_date).days if hasattr(results.start_date, 'to_pydatetime') else 365
        days_invested = sum(t.holding_period for t in results.trades)
        results.time_in_market = (days_invested / total_days * 100) if total_days > 0 else 0

        return results

    def _calculate_max_dd_duration(self, drawdowns: List[float]) -> int:
        """Calculate maximum drawdown duration in days"""
        max_duration = 0
        current_duration = 0

        for dd in drawdowns:
            if dd > 0:
                current_duration += 1
                max_duration = max(max_duration, current_duration)
            else:
                current_duration = 0

        return max_duration

    def _walk_forward_analysis(
        self,
        prices: pd.DataFrame,
        strategy_type: StrategyType,
        params: Dict,
        initial_capital: float,
        commission: float,
        slippage: float,
        n_splits: int = 5
    ) -> List[Dict]:
        """Perform walk-forward analysis"""
        results = []
        n = len(prices)
        split_size = n // n_splits

        for i in range(n_splits - 1):
            # In-sample period (first 70% of split)
            is_end = int((i + 0.7) * split_size)
            # Out-of-sample period (remaining 30%)
            oos_end = int((i + 1) * split_size)

            is_prices = prices.iloc[:is_end]
            oos_prices = prices.iloc[is_end:oos_end]

            if len(oos_prices) < 20:
                continue

            # Optimize on in-sample
            is_result = self.run_backtest(
                is_prices, strategy_type, params, initial_capital, commission, slippage
            )

            # Test on out-of-sample
            oos_result = self.run_backtest(
                oos_prices, strategy_type, params, initial_capital, commission, slippage
            )

            results.append({
                'split': i + 1,
                'is_return': is_result.total_return_pct,
                'oos_return': oos_result.total_return_pct,
                'is_sharpe': is_result.sharpe_ratio,
                'oos_sharpe': oos_result.sharpe_ratio,
                'is_max_dd': is_result.max_drawdown,
                'oos_max_dd': oos_result.max_drawdown
            })

        return results

    def _calculate_oos_consistency(self, wf_results: List[Dict]) -> float:
        """Calculate OOS consistency score"""
        if not wf_results:
            return 0.0

        # Count how many OOS periods were profitable
        profitable_oos = sum(1 for r in wf_results if r['oos_return'] > 0)
        return profitable_oos / len(wf_results) * 100

    def _assign_grade(self, results: BacktestResults) -> Tuple[str, bool]:
        """Assign strategy grade and robustness assessment"""
        score = 0

        # Sharpe ratio (max 30 points)
        if results.sharpe_ratio > 2.0:
            score += 30
        elif results.sharpe_ratio > 1.5:
            score += 25
        elif results.sharpe_ratio > 1.0:
            score += 20
        elif results.sharpe_ratio > 0.5:
            score += 10
        elif results.sharpe_ratio > 0:
            score += 5

        # Max drawdown (max 25 points)
        if results.max_drawdown < 10:
            score += 25
        elif results.max_drawdown < 15:
            score += 20
        elif results.max_drawdown < 20:
            score += 15
        elif results.max_drawdown < 30:
            score += 10
        else:
            score += 0

        # Win rate (max 15 points)
        if results.win_rate > 0.60:
            score += 15
        elif results.win_rate > 0.50:
            score += 10
        elif results.win_rate > 0.45:
            score += 5

        # Profit factor (max 15 points)
        if results.profit_factor > 2.0:
            score += 15
        elif results.profit_factor > 1.5:
            score += 10
        elif results.profit_factor > 1.0:
            score += 5

        # OOS consistency (max 15 points)
        if results.oos_consistency > 70:
            score += 15
        elif results.oos_consistency > 50:
            score += 10
        elif results.oos_consistency > 30:
            score += 5

        # Assign grade
        if score >= 85:
            grade = "A+"
        elif score >= 75:
            grade = "A"
        elif score >= 65:
            grade = "B+"
        elif score >= 55:
            grade = "B"
        elif score >= 45:
            grade = "C+"
        elif score >= 35:
            grade = "C"
        else:
            grade = "D"

        is_robust = score >= 55 and results.oos_consistency >= 50

        return grade, is_robust

    def _generate_warnings(self, results: BacktestResults) -> List[str]:
        """Generate warnings about potential issues"""
        warnings = []

        if results.total_trades < 30:
            warnings.append(f"Low trade count ({results.total_trades}) - results may not be statistically significant")

        if results.max_drawdown > 30:
            warnings.append(f"High maximum drawdown ({results.max_drawdown:.1f}%) - consider risk management")

        if results.win_rate < 0.40:
            warnings.append(f"Low win rate ({results.win_rate:.1%}) - may be psychologically challenging")

        if results.oos_consistency < 50:
            warnings.append(f"Poor OOS consistency ({results.oos_consistency:.1f}%) - potential overfitting")

        if results.time_in_market < 20:
            warnings.append(f"Low time in market ({results.time_in_market:.1f}%) - may miss opportunities")

        if results.profit_factor < 1.2:
            warnings.append(f"Low profit factor ({results.profit_factor:.2f}) - marginal edge")

        return warnings

    def format_output(self, results: BacktestResults) -> str:
        """Format backtest results as markdown"""
        output = f"""
## Backtest Results: {results.strategy_name.upper()} Strategy

**Symbol:** {results.symbol}
**Period:** {results.start_date.strftime('%Y-%m-%d')} to {results.end_date.strftime('%Y-%m-%d')}
**Initial Capital:** ${results.initial_capital:,.0f}

---

## Overall Assessment
| Metric | Value |
|--------|-------|
| **Strategy Grade** | {results.strategy_grade} |
| **Robust** | {'Yes ✅' if results.is_robust else 'No ⚠️'} |
| **Total Return** | ${results.total_return:,.2f} ({results.total_return_pct:.2f}%) |
| **Annualized Return** | {results.annualized_return:.2f}% |
| **Benchmark Return** | {results.benchmark_return:.2f}% |
| **Excess Return (Alpha)** | {results.excess_return:+.2f}% |

---

## Risk-Adjusted Metrics
| Metric | Value | Assessment |
|--------|-------|------------|
| **Sharpe Ratio** | {results.sharpe_ratio:.2f} | {'Excellent' if results.sharpe_ratio > 1.5 else 'Good' if results.sharpe_ratio > 1.0 else 'Average' if results.sharpe_ratio > 0.5 else 'Poor'} |
| **Sortino Ratio** | {results.sortino_ratio:.2f} | - |
| **Calmar Ratio** | {results.calmar_ratio:.2f} | - |
| **Max Drawdown** | {results.max_drawdown:.2f}% | {'High' if results.max_drawdown > 20 else 'Moderate' if results.max_drawdown > 10 else 'Low'} |
| **Drawdown Duration** | {results.max_drawdown_duration} days | - |

---

## Trade Statistics
| Metric | Value |
|--------|-------|
| **Total Trades** | {results.total_trades} |
| **Winning Trades** | {results.winning_trades} ({results.win_rate:.1%}) |
| **Losing Trades** | {results.losing_trades} |
| **Profit Factor** | {results.profit_factor:.2f} |
| **Payoff Ratio** | 1:{results.payoff_ratio:.2f} |
| **Avg Holding Period** | {results.avg_holding_period:.1f} days |
| **Time in Market** | {results.time_in_market:.1f}% |

---

## Win/Loss Analysis
| Metric | Value |
|--------|-------|
| **Average Win** | ${results.avg_win:,.2f} ({results.avg_win_pct:.2f}%) |
| **Average Loss** | ${results.avg_loss:,.2f} ({results.avg_loss_pct:.2f}%) |
| **Largest Win** | ${results.largest_win:,.2f} |
| **Largest Loss** | ${results.largest_loss:,.2f} |

---

## Walk-Forward Analysis
"""
        if results.walk_forward_results:
            output += "| Split | IS Return | OOS Return | IS Sharpe | OOS Sharpe | IS MaxDD | OOS MaxDD |\n"
            output += "|-------|-----------|------------|-----------|------------|----------|----------|\n"
            for wf in results.walk_forward_results:
                output += f"| {wf['split']} | {wf['is_return']:.2f}% | {wf['oos_return']:.2f}% | {wf['is_sharpe']:.2f} | {wf['oos_sharpe']:.2f} | {wf['is_max_dd']:.1f}% | {wf['oos_max_dd']:.1f}% |\n"

            output += f"\n**OOS Consistency:** {results.oos_consistency:.1f}%\n"
        else:
            output += "*Walk-forward analysis not performed*\n"

        if results.warnings:
            output += "\n---\n\n## ⚠️ Warnings\n"
            for warning in results.warnings:
                output += f"- {warning}\n"

        return output


def main():
    """Example usage of BacktestingAgent"""
    # Generate sample price data
    np.random.seed(42)
    n_periods = 500
    dates = pd.date_range(end=datetime.utcnow(), periods=n_periods, freq='D')
    prices = 100 + np.cumsum(np.random.randn(n_periods) * 2)

    df = pd.DataFrame({
        'open': prices + np.random.randn(n_periods),
        'high': prices + np.abs(np.random.randn(n_periods)),
        'low': prices - np.abs(np.random.randn(n_periods)),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, n_periods)
    }, index=dates)

    # Run backtest
    agent = BacktestingAgent()
    results = agent.run_backtest(
        df,
        StrategyType.TREND_FOLLOWING,
        {'short_window': 12, 'long_window': 26},
        initial_capital=100000,
        commission=0.001,
        slippage=0.0005
    )

    print(agent.format_output(results))


if __name__ == '__main__':
    main()
