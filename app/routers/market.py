"""
Market / Quote endpoints – backed by webull.data.DataClient
GET /api/v1/market/snapshot          – snapshot quotes for given symbols
GET /api/v1/market/bars              – OHLCV historical bars
GET /api/v1/market/quotes            – Level-2 order book quotes
GET /api/v1/market/tick              – tick-by-tick transactions
GET /api/v1/market/instruments       – instrument search
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional

from app.security import require_api_key
from app.webull_client import get_data_client

router = APIRouter(prefix="/api/v1/market", tags=["Market Data"])


def _ok(res):
    """Raise HTTP 502 if the upstream Webull call failed."""
    if res.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail={"webull_status": res.status_code, "body": res.text},
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
    symbol: str = Query(..., description="Ticker symbol, e.g. PTT"),
    category: str = Query("TH_STOCK", description="Security category, e.g. TH_STOCK, US_STOCK"),
    timespan: str = Query("d1", description="Bar size: m1 m5 m15 m30 h1 h2 h4 d1 w1 mn1"),
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
