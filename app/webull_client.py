"""
Singleton Webull API clients – shared across all requests.
Uses DataClient for market data and TradeClient for trading.
"""
import logging
from webull.core.client import ApiClient
from webull.trade.trade_client import TradeClient
from webull.data.data_client import DataClient

from app.config import WEBULL_APP_KEY, WEBULL_APP_SECRET, WEBULL_REGION, WEBULL_ENDPOINT

logger = logging.getLogger(__name__)

_api_client: ApiClient | None = None
_trade_client: TradeClient | None = None
_data_client: DataClient | None = None


def get_api_client() -> ApiClient:
    global _api_client
    if _api_client is None:
        logger.info("Initialising Webull ApiClient (region=%s, endpoint=%s)", WEBULL_REGION, WEBULL_ENDPOINT)
        _api_client = ApiClient(WEBULL_APP_KEY, WEBULL_APP_SECRET, WEBULL_REGION)
        _api_client.add_endpoint(WEBULL_REGION, WEBULL_ENDPOINT)
    return _api_client


def get_trade_client() -> TradeClient:
    global _trade_client
    if _trade_client is None:
        _trade_client = TradeClient(get_api_client())
    return _trade_client


def get_data_client() -> DataClient:
    global _data_client
    if _data_client is None:
        _data_client = DataClient(get_api_client())
    return _data_client
