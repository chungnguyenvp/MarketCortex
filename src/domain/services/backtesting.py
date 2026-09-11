"""Simple, reproducible long-only backtest used by the public API."""

from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from src.domain.services.financial_calc import calculate_rsi


def run_ma_rsi_backtest(
    prices: pd.DataFrame,
    initial_capital: float = 100_000.0,
    fee_bps: float = 10.0,
) -> Dict[str, Any]:
    """Backtest a MA20/MA50 trend strategy with an RSI confirmation filter."""

    if prices is None or prices.empty or "close" not in prices.columns:
        raise ValueError("Price data must contain a non-empty 'close' column.")
    if initial_capital <= 0 or fee_bps < 0:
        raise ValueError("Initial capital must be positive and fee_bps cannot be negative.")

    frame = prices[["close"]].copy().sort_index()
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    frame = frame.dropna()
    if len(frame) < 2:
        raise ValueError("At least two valid price observations are required.")

    frame["ma20"] = frame["close"].rolling(20, min_periods=1).mean()
    frame["ma50"] = frame["close"].rolling(50, min_periods=1).mean()
    frame["rsi"] = calculate_rsi(frame["close"], period=14).fillna(50.0)
    desired_position = ((frame["ma20"] > frame["ma50"]) & (frame["rsi"] >= 50)).astype(float)
    position = desired_position.shift(1).fillna(0.0)
    turnover = position.diff().abs().fillna(position.abs())
    fee_rate = fee_bps / 10_000.0
    market_returns = frame["close"].pct_change().fillna(0.0)
    strategy_returns = position * market_returns - turnover * fee_rate
    benchmark_returns = market_returns
    frame["equity"] = initial_capital * (1.0 + strategy_returns).cumprod()
    frame["benchmark_equity"] = initial_capital * (1.0 + benchmark_returns).cumprod()

    periods = max(len(frame) - 1, 1)
    annual_factor = 252 / periods
    total_return = frame["equity"].iloc[-1] / initial_capital - 1.0
    benchmark_return = frame["benchmark_equity"].iloc[-1] / initial_capital - 1.0
    annualized_return = (1.0 + total_return) ** annual_factor - 1.0 if total_return > -1 else -1.0
    volatility = strategy_returns.std(ddof=0) * (252**0.5)
    sharpe = ((strategy_returns.mean() / strategy_returns.std(ddof=0)) * (252**0.5)) if strategy_returns.std(ddof=0) else 0.0
    drawdown = frame["equity"] / frame["equity"].cummax() - 1.0

    curve = []
    for index, row in frame.tail(250).iterrows():
        date = index.strftime("%Y-%m-%d") if hasattr(index, "strftime") else str(index)
        curve.append({
            "date": date,
            "equity": round(float(row.equity), 2),
            "benchmark_equity": round(float(row.benchmark_equity), 2),
        })
    return {
        "strategy": "MA20/MA50 crossover + RSI14 confirmation",
        "initial_capital": round(initial_capital, 2),
        "final_equity": round(float(frame["equity"].iloc[-1]), 2),
        "total_return": round(float(total_return), 6),
        "annualized_return": round(float(annualized_return), 6),
        "benchmark_return": round(float(benchmark_return), 6),
        "volatility": round(float(volatility), 6),
        "sharpe_ratio": round(float(sharpe), 4),
        "max_drawdown": round(float(drawdown.min()), 6),
        "trades": int((turnover > 0).sum()),
        "equity_curve": curve,
    }
