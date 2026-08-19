# Webull Read-Only REST API Documentation

This is a **read-only** REST API wrapper for the Webull OpenAPI Python SDK. It allows you to safely query stock prices, market data, account balances, and order histories without exposing your real Webull trading keys to the internet.

Because it is read-only, **it is impossible to place or cancel trades through this API**, making it highly secure for use on your website.

---

## 🔐 Authentication

All API requests (except `/` and `/health`) require an API key to be passed in the headers.

**Header Name:** `X-API-Key`  
**Header Value:** The value you set for `API_SECRET_KEY` in your Render Environment Variables.

**Example Request (curl):**

```bash
curl -H "X-API-Key: your_secret_key_here" https://your-web-service.com/api/v1/trade/accounts
```

---

## 🚀 Endpoints (GET METHOD ONLY)

### 1. System & Health

Used to wake up the server on Render or check if it's online.

- **`GET /health`**
  - Returns `{"status": "ok", "service": "webull-api"}`

### 2. Market Data (Stock Prices & Info)

All market data endpoints use the `/api/v1/market` prefix.

- **`GET /api/v1/market/snapshot`**
  - **Description:** Get real-time or delayed snapshot quotes.
  - **Query Parameters:**
    - `symbols` (required): Comma-separated symbols (e.g., `GOOG,AAPL`)
    - `category` (optional, default `US_STOCK`): Market category (`US_STOCK`, etc.)

- **`GET /api/v1/market/bars`**
  - **Description:** Get historical candlestick (OHLCV) data.
  - **Query Parameters:**
    - `symbol` (required): Ticker symbol (e.g., `GOOG`)
    - `category` (optional, default `US_STOCK`)
    - `timespan` (optional, default `D`): `M1`, `M5`, `M15`, `D`, `W`, `M`, etc.
    - `count` (optional, default `200`): Number of bars to return.

- **`GET /api/v1/market/quotes`**
  - **Description:** Level-2 Order book depth (bids and asks).
  - **Query Parameters:** `symbol`, `category`, `depth`

- **`GET /api/v1/market/tick`**
  - **Description:** Tick-by-tick historical transaction data.
  - **Query Parameters:** `symbol`, `category`, `count`

- **`GET /api/v1/market/instruments`**
  - **Description:** Search and lookup instrument metadata.
  - **Query Parameters:** `symbols`, `category`

### 3. Trade Data (Account & Orders)

All trade data endpoints use the `/api/v1/trade` prefix.

- **`GET /api/v1/trade/accounts`**
  - **Description:** Lists all accounts linked to your Webull API keys.
  - **Returns:** An array of accounts containing `account_id`.

- **`GET /api/v1/trade/accounts/{account_id}/balance`**
  - **Description:** Returns the total cash balance, net liquidation value, and buying power for the specified account.
- **`GET /api/v1/trade/accounts/{account_id}/positions`**
  - **Description:** Returns a list of all currently held assets (open positions).

- **`GET /api/v1/trade/orders/open`**
  - **Description:** Returns all currently open (pending/working) orders.
  - **Query Parameters:**
    - `account_id` (required)
    - `page_size` (optional)

- **`GET /api/v1/trade/orders/history`**
  - **Description:** Returns the history of all completed, cancelled, and rejected orders.
  - **Query Parameters:**
    - `account_id` (required)
    - `page_size` (optional)
    - `start_date` (optional, format: `yyyy-MM-dd`)
    - `end_date` (optional, format: `yyyy-MM-dd`)

---
