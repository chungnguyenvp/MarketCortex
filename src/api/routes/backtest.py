import logging

from fastapi import APIRouter, HTTPException, Query

from src.api.schemas import BacktestResponse
from src.domain.services.backtesting import run_ma_rsi_backtest
from src.domain.services.validation_service import ValidationService
from src.infrastructure.adapters.vnstock_adapter import VnStockAdapter
from src.infrastructure.adapters.yfinance_adapter import YFinanceAdapter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Backtesting"])


@router.get("/backtest", response_model=BacktestResponse)
async def run_backtest(
    ticker: str = Query(..., min_length=3, max_length=5),
    market: str = Query("VN", pattern="^(VN|US)$"),
    days: int = Query(730, ge=60, le=3650),
):
    """Run the deterministic MA/RSI strategy without invoking an LLM."""
    clean_ticker = ticker.strip().upper()
    valid, error = ValidationService.validate_ticker(clean_ticker, market)
    if not valid:
        raise HTTPException(status_code=400, detail=error)
    provider = YFinanceAdapter() if market == "US" else VnStockAdapter()
    try:
        prices = provider.get_historical_prices(clean_ticker, days=days)
        metrics = run_ma_rsi_backtest(prices)
        return BacktestResponse(
            ticker=clean_ticker,
            market=market,
            start_date=str(prices.index.min().date()) if not prices.empty else "",
            end_date=str(prices.index.max().date()) if not prices.empty else "",
            metrics=metrics,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Backtest failed for %s", clean_ticker)
        raise HTTPException(status_code=502, detail=f"Unable to fetch backtest data: {exc}") from exc
