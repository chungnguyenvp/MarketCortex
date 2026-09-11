import pandas as pd

from src.domain.services.backtesting import run_ma_rsi_backtest


def test_backtest_returns_metrics_and_equity_curve():
    prices = pd.DataFrame({"close": [100 + i * 0.5 for i in range(90)]})
    result = run_ma_rsi_backtest(prices, initial_capital=10_000)
    assert result["final_equity"] > 0
    assert "sharpe_ratio" in result
    assert result["equity_curve"]
    assert result["trades"] >= 0


def test_backtest_rejects_invalid_prices():
    try:
        run_ma_rsi_backtest(pd.DataFrame())
    except ValueError as exc:
        assert "close" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing price data")
