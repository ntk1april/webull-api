"""
Market / Quote endpoints – backed by webull.data.DataClient
GET /api/v1/market/snapshot          – snapshot quotes for given symbols
GET /api/v1/market/bars              – OHLCV historical bars
GET /api/v1/market/quotes            – Level-2 order book quotes
GET /api/v1/market/tick              – tick-by-tick transactions
GET /api/v1/market/instruments       – instrument search
GET /api/v1/market/debug             – test Webull connection and show exact error
"""
import traceback
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional

from app.security import require_api_key
from app.webull_client import get_data_client

router = APIRouter(prefix="/api/v1/market", tags=["Market Data"])


def _ok(res):
    """Raise HTTP 502 with full Webull error detail if the call failed."""
    if res.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Webull API returned an error",
                "webull_status": res.status_code,
                "webull_body": res.text,
            },
        )
    return res.json()


@router.get("/snapshot", summary="Real-time snapshot quotes")
async def get_snapshot(
    symbols: str = Query(..., description="Comma-separated symbols, e.g. PTT,AOT,KBANK"),
    category: str = Query("TH_STOCK", description="Security category, e.g. TH_STOCK, US_STOCK, HK_STOCK"),
    extend_hour_required: Optional[bool] = Query(None),
    _: str = Depends(require_api_key),
):
    """
    Returns real-time snapshot data for one or more symbols.
    """
    dc = get_data_client()
    symbol_list = [s.strip() for s in symbols.split(",") if s.strip()]
    res = dc.market_data.get_snapshot(
        symbols=symbol_list,
        category=category,
        extend_hour_required=extend_hour_required,
    )
    return _ok(res)


@router.get("/bars", summary="OHLCV historical candlestick bars")
async def get_history_bars(
    symbol: str = Query(..., description="Ticker symbol, e.g. GOOG"),
    category: str = Query("US_STOCK", description="Security category, e.g. TH_STOCK, US_STOCK"),
    timespan: str = Query("D", description="Bar size: M1, M5, M15, M30, M60, M120, M240, D, W, M, Y"),
    count: int = Query(200, ge=1, le=1200, description="Number of bars"),
    _: str = Depends(require_api_key),
):
    """
    Returns historical OHLCV bars for a symbol.
    """
    dc = get_data_client()
    res = dc.market_data.get_history_bar(
        symbol=symbol,
        category=category,
        timespan=timespan,
        count=str(count),
    )
    return _ok(res)


@router.get("/quotes", summary="Level-2 order book / quote depth")
async def get_quotes(
    symbol: str = Query(..., description="Ticker symbol, e.g. PTT"),
    category: str = Query("TH_STOCK", description="Security category"),
    depth: Optional[int] = Query(None, description="Order book depth levels"),
    _: str = Depends(require_api_key),
):
    """
    Returns Level-2 order book (bid/ask depth) for a symbol.
    """
    dc = get_data_client()
    res = dc.market_data.get_quotes(symbol=symbol, category=category, depth=depth)
    return _ok(res)


@router.get("/tick", summary="Tick-by-tick transaction data")
async def get_tick(
    symbol: str = Query(..., description="Ticker symbol, e.g. PTT"),
    category: str = Query("TH_STOCK", description="Security category"),
    count: int = Query(200, ge=1, le=1000, description="Number of ticks"),
    _: str = Depends(require_api_key),
):
    """
    Returns recent tick-by-tick trade transactions.
    """
    dc = get_data_client()
    res = dc.market_data.get_tick(symbol=symbol, category=category, count=str(count))
    return _ok(res)


@router.get("/instruments", summary="Search instruments / tickers")
async def get_instruments(
    symbols: str = Query(..., description="Symbol(s) to look up, comma-separated, e.g. PTT,AOT"),
    category: str = Query("TH_STOCK", description="Security category"),
    _: str = Depends(require_api_key),
):
    """
    Returns instrument metadata for given symbols.
    """
    dc = get_data_client()
    symbol_list = [s.strip() for s in symbols.split(",") if s.strip()]
    res = dc.instrument.get_instrument(symbols=symbol_list, category=category)
    return _ok(res)


@router.get("/debug", summary="Debug: test Webull connection", tags=["Debug"])
async def debug_connection(
    symbol: str = Query("PTT", description="Symbol to test with"),
    category: str = Query("TH_STOCK", description="Category to test with"),
    _: str = Depends(require_api_key),
):
    """
    Tests the Webull SDK connection and returns the raw response or full error detail.
    Use this endpoint first in Postman to diagnose 500/502 errors.
    """
    result = {"symbol": symbol, "category": category}
    try:
        dc = get_data_client()
        res = dc.market_data.get_snapshot(
            symbols=[symbol],
            category=category,
        )
        result["webull_status"] = res.status_code
        result["webull_body"] = res.json() if res.status_code == 200 else res.text
        result["success"] = res.status_code == 200
    except Exception as e:
        result["success"] = False
        result["exception_type"] = type(e).__name__
        result["exception_message"] = str(e)
        result["traceback"] = traceback.format_exc()
    return result
