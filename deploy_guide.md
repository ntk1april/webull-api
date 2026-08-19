# Webull REST API – Render.com Deployment Guide

## 📁 Project Structure

```
webull-api/
├── app/
│   ├── __init__.py
│   ├── config.py           ← all env-var settings
│   ├── main.py             ← FastAPI app + CORS
│   ├── security.py         ← X-API-Key auth dependency
│   ├── webull_client.py    ← singleton SDK clients
│   └── routers/
│       ├── market.py       ← /api/v1/market/*
│       └── trade.py        ← /api/v1/trade/*
├── server.py               ← gunicorn/uvicorn entry-point
├── requirements.txt
├── Dockerfile
└── .dockerignore
```

---

## ⚙️ Environment Variables (set in Render → Environment tab)

| Variable | Description | Example |
|---|---|---|
| `WEBULL_APP_KEY` | Your Webull OpenAPI app key | `de0e228bbd...` |
| `WEBULL_APP_SECRET` | Your Webull OpenAPI app secret | `abc123secret` |
| `WEBULL_REGION` | Region code | `th` |
| `WEBULL_ENDPOINT` | Webull API host | `api.webull.co.th` |
| `API_SECRET_KEY` | Secret your website sends as `X-API-Key` header | `my-super-secret-key` |
| `PORT` | Port (Render sets this automatically) | `8000` |

> [!CAUTION]
> **Never commit real secrets to Git.** The `.gitignore` already excludes `conf/token.txt` and `.env`.

---

## 🚀 Deploying to Render.com

### Option A – Deploy with Dockerfile (recommended)

1. Push this project to GitHub / GitLab (make sure `.gitignore` excludes secrets).
2. In Render dashboard → **New → Web Service**.
3. Connect your repository.
4. Set **Runtime** → `Docker`.
5. Add the 5 environment variables above.
6. Click **Create Web Service**.

Your API will be live at: `https://<your-service>.onrender.com`

### Option B – Deploy as Python service (no Docker)

1. Set **Runtime** → `Python 3`
2. Set **Build Command** → `pip install -r requirements.txt`
3. Set **Start Command**:
   ```
   gunicorn server:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --workers 2
   ```
4. Add all 5 environment variables.

---

## 🌐 API Endpoints

All endpoints require: **`X-API-Key: <your API_SECRET_KEY>`** header.

### Market Data  (`/api/v1/market/`)

| Method | Path | Key Parameters | Description |
|---|---|---|---|
| `GET` | `/api/v1/market/snapshot` | `symbols=PTT,AOT`, `category=TH_STOCK` | Real-time snapshot quotes |
| `GET` | `/api/v1/market/bars` | `symbol=PTT`, `timespan=d1`, `count=200` | OHLCV candlestick bars |
| `GET` | `/api/v1/market/quotes` | `symbol=PTT`, `category=TH_STOCK`, `depth=5` | Level-2 order book |
| `GET` | `/api/v1/market/tick` | `symbol=PTT`, `count=200` | Tick-by-tick transactions |
| `GET` | `/api/v1/market/instruments` | `symbols=PTT,AOT`, `category=TH_STOCK` | Instrument metadata |

**Timespan values:** `m1 m5 m15 m30 h1 h2 h4 d1 w1 mn1`

### Trade  (`/api/v1/trade/`)

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/trade/accounts` | List all linked accounts |
| `GET` | `/api/v1/trade/accounts/{id}/balance` | Account cash & buying power |
| `GET` | `/api/v1/trade/accounts/{id}/positions` | Open positions |
| `GET` | `/api/v1/trade/orders/open?account_id=xxx` | Pending/open orders |
| `GET` | `/api/v1/trade/orders/history?account_id=xxx` | Order history |
| `GET` | `/api/v1/trade/orders/{client_order_id}?account_id=xxx` | Single order detail |
| `POST` | `/api/v1/trade/orders` | Place order(s) |
| `DELETE` | `/api/v1/trade/orders/{client_order_id}?account_id=xxx` | Cancel an order |

### System

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check (no auth required) |
| `GET` | `/docs` | Swagger UI (interactive docs) |
| `GET` | `/redoc` | ReDoc API docs |

---

## 💻 Calling from Your Website (JavaScript)

```js
const API_BASE = "https://<your-service>.onrender.com";
const API_KEY  = "my-super-secret-key";  // store this securely!

// ── Market snapshot ───────────────────────────────────────────────────────
const snapshot = await fetch(
  `${API_BASE}/api/v1/market/snapshot?symbols=PTT,AOT&category=TH_STOCK`,
  { headers: { "X-API-Key": API_KEY } }
).then(r => r.json());

// ── OHLCV bars ────────────────────────────────────────────────────────────
const bars = await fetch(
  `${API_BASE}/api/v1/market/bars?symbol=PTT&timespan=d1&count=100&category=TH_STOCK`,
  { headers: { "X-API-Key": API_KEY } }
).then(r => r.json());

// ── List accounts ─────────────────────────────────────────────────────────
const accounts = await fetch(
  `${API_BASE}/api/v1/trade/accounts`,
  { headers: { "X-API-Key": API_KEY } }
).then(r => r.json());

// ── Place a buy order ─────────────────────────────────────────────────────
const placed = await fetch(`${API_BASE}/api/v1/trade/orders`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
  },
  body: JSON.stringify({
    account_id: "your-account-id",
    orders: [{
      symbol: "PTT",
      market: "TH",
      side: "BUY",
      order_type: "LMT",
      qty: "100",
      limit_price: "30.50",
      tif: "DAY"
    }]
  })
}).then(r => r.json());

// ── Cancel an order ───────────────────────────────────────────────────────
await fetch(
  `${API_BASE}/api/v1/trade/orders/my-order-id-001?account_id=your-account-id`,
  { method: "DELETE", headers: { "X-API-Key": API_KEY } }
);
```

---

## 🔒 Production Security Hardening

In [`app/main.py`](file:///c:/Users/User/Desktop/webull-api/app/main.py), replace the CORS wildcard with your exact domain:

```python
allow_origins=["https://your-website.com"],
```

---

## 🔧 Local Development

```powershell
# Activate venv
.\venv\Scripts\Activate

# Set env vars
$env:WEBULL_APP_KEY    = "your_app_key"
$env:WEBULL_APP_SECRET = "your_app_secret"
$env:WEBULL_REGION     = "th"
$env:WEBULL_ENDPOINT   = "api.webull.co.th"
$env:API_SECRET_KEY    = "test-secret"

# Start dev server
uvicorn server:app --reload
```

Then open **http://localhost:8000/docs** for the interactive Swagger UI.
