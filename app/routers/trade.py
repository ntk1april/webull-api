"""
Trade endpoints – backed by webull.trade.TradeClient
GET  /api/v1/trade/accounts              – list accounts
GET  /api/v1/trade/accounts/{id}/balance – account balance
GET  /api/v1/trade/accounts/{id}/positions – open positions
GET  /api/v1/trade/orders/open           – open/pending orders
GET  /api/v1/trade/orders/history        – order history
GET  /api/v1/trade/orders/{id}           – single order detail
POST /api/v1/trade/orders               – place order(s)
DELETE /api/v1/trade/orders/{id}        – cancel an order
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
            detail={"webull_status": res.status_code, "body": res.text},
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


@router.get("/orders/{client_order_id}", summary="Order detail")
async def get_order_detail(
    client_order_id: str = Path(..., description="Client order ID (your reference)"),
    account_id: str = Query(..., description="Account ID"),
    _: str = Depends(require_api_key),
):
    """Returns detailed information for a single order."""
    tc = get_trade_client()
    res = tc.order_v2.get_order_detail(account_id=account_id, client_order_id=client_order_id)
    return _ok(res)


class SingleOrder(BaseModel):
    """
    Webull v2 order object.  See SDK docs for full field reference.
    Required fields: symbol, market, side, order_type, qty.
    """
    symbol: str
    market: str                         # e.g. "TH"
    side: str                           # BUY | SELL
    order_type: str                     # LMT | MKT | STP | STP_LMT
    qty: str                            # quantity as string
    limit_price: Optional[str] = None
    stop_price: Optional[str] = None
    tif: Optional[str] = "DAY"         # DAY | GTC | IOC | FOK
    client_order_id: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None   # pass-through for any other fields


class PlaceOrderRequest(BaseModel):
    account_id: str
    orders: List[SingleOrder]
    client_combo_order_id: Optional[str] = None


@router.post("/orders", summary="Place one or more orders", status_code=201)
async def place_order(
    body: PlaceOrderRequest,
    _: str = Depends(require_api_key),
):
    """
    Places one or more stock orders using the Webull v2 API.

    Each order in `orders` maps to a Webull `new_order` dict.
    The `market` field sets the header category (e.g. `market: "TH"` → category `TH_STOCK`).
    """
    tc = get_trade_client()

    new_orders = []
    for o in body.orders:
        order_dict: Dict[str, Any] = {
            "symbol": o.symbol,
            "market": o.market,
            "side": o.side,
            "order_type": o.order_type,
            "qty": o.qty,
            "tif": o.tif,
        }
        if o.limit_price is not None:
            order_dict["limit_price"] = o.limit_price
        if o.stop_price is not None:
            order_dict["stop_price"] = o.stop_price
        if o.client_order_id is not None:
            order_dict["client_order_id"] = o.client_order_id
        if o.extra:
            order_dict.update(o.extra)
        new_orders.append(order_dict)

    res = tc.order_v2.place_order(
        account_id=body.account_id,
        new_orders=new_orders,
        client_combo_order_id=body.client_combo_order_id,
    )
    return _ok(res)


@router.delete("/orders/{client_order_id}", summary="Cancel an order")
async def cancel_order(
    client_order_id: str = Path(..., description="Client order ID to cancel"),
    account_id: str = Query(..., description="Account ID that owns the order"),
    _: str = Depends(require_api_key),
):
    """Cancels a pending order by client_order_id."""
    tc = get_trade_client()
    res = tc.order_v2.cancel_order(account_id=account_id, client_order_id=client_order_id)
    return _ok(res)
