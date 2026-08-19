"""
Trade endpoints – backed by webull.trade.TradeClient
GET  /api/v1/trade/accounts              – list accounts
GET  /api/v1/trade/accounts/{id}/balance – account balance
GET  /api/v1/trade/accounts/{id}/positions – open positions
GET  /api/v1/trade/orders/open           – open/pending orders
GET  /api/v1/trade/orders/history        – order history
GET  /api/v1/trade/orders/{id}           – single order detail
"""
from fastapi import APIRouter, Depends, Query, HTTPException, Path
from pydantic import BaseModel
from typing import Optional, List, Any, Dict

from app.security import require_api_key
from app.webull_client import get_trade_client

router = APIRouter(prefix="/api/v1/trade", tags=["Trade"])


def _ok(res):
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


# ── Accounts ──────────────────────────────────────────────────────────────────

@router.get("/accounts", summary="List all linked accounts")
async def list_accounts(_: str = Depends(require_api_key)):
    """Returns all accounts linked to the API key."""
    tc = get_trade_client()
    res = tc.account_v2.get_account_list()
    return _ok(res)


@router.get("/accounts/{account_id}/balance", summary="Account balance")
async def get_account_balance(
    account_id: str = Path(..., description="Account ID from /accounts"),
    _: str = Depends(require_api_key),
):
    """Returns cash balance, net liquidation value, and buying power."""
    tc = get_trade_client()
    res = tc.account_v2.get_account_balance(account_id)
    return _ok(res)


@router.get("/accounts/{account_id}/positions", summary="Open positions")
async def get_positions(
    account_id: str = Path(..., description="Account ID from /accounts"),
    _: str = Depends(require_api_key),
):
    """Returns all current open positions for the account."""
    tc = get_trade_client()
    res = tc.account_v2.get_account_position(account_id)
    return _ok(res)


# ── Orders ────────────────────────────────────────────────────────────────────

@router.get("/orders/open", summary="Pending / open orders")
async def get_open_orders(
    account_id: str = Query(..., description="Account ID"),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    last_order_id: Optional[str] = Query(None),
    last_client_order_id: Optional[str] = Query(None),
    _: str = Depends(require_api_key),
):
    """Returns all pending/working orders for the account (cursor-based paging)."""
    tc = get_trade_client()
    res = tc.order_v2.get_order_open(
        account_id=account_id,
        page_size=page_size,
        last_order_id=last_order_id,
        last_client_order_id=last_client_order_id,
    )
    return _ok(res)


@router.get("/orders/history", summary="Historical orders")
async def get_order_history(
    account_id: str = Query(..., description="Account ID"),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    start_date: Optional[str] = Query(None, description="yyyy-MM-dd"),
    end_date: Optional[str] = Query(None, description="yyyy-MM-dd"),
    last_order_id: Optional[str] = Query(None),
    last_client_order_id: Optional[str] = Query(None),
    _: str = Depends(require_api_key),
):
    """Returns historical orders with optional date range and cursor paging."""
    tc = get_trade_client()
    res = tc.order_v2.get_order_history(
        account_id=account_id,
        page_size=page_size,
        start_date=start_date,
        end_date=end_date,
        last_order_id=last_order_id,
        last_client_order_id=last_client_order_id,
    )
    return _ok(res)
