# Getting Started (After u got open api from webull)

Welcome to the Webull Read-Only REST API! This guide will help you run the API locally for development and deploy it to Render.com for production.

---

## 💻 Local Development (Testing on your computer)

### Prerequisites

1. Python 3.11 or newer installed.
2. A Webull Developer account and API keys (`WEBULL_APP_KEY`, `WEBULL_APP_SECRET`).

### Setup Instructions

1. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the project folder and fill in your details:

   ```env
   WEBULL_APP_KEY=your_app_key_here
   WEBULL_APP_SECRET=your_app_secret_here
   WEBULL_REGION=th
   WEBULL_ENDPOINT=api.webull.co.th
   API_SECRET_KEY=ur-chosen-strong-secret
   PORT=8000
   ```

3. **Generate Webull Token (One-time setup):**
   Update getToken.py with your details. And run the following command to log into Webull.

   ```bash
   python getToken.py
   ```

   > 📱 **Check your phone:** Open the Webull Mobile app, go to your Messages/Notifications, and click **Confirm/Approve** for the OpenAPI Login.

   This will generate a file at `conf/token.txt`.

4. **Start the API Server:**
   ```bash
   uvicorn server:app --reload
   ```
   Your API is now running at `http://localhost:8000`! You can test it using the Postman collection provided.

---

## 🚀 **OPTIONAL** Production Deployment (Render.com)

### Step 1: Push code to GitHub

```bash
git add .
git commit -m "update project"
git push
```

### Step 2: Create a Web Service on Render

1. Go to [Render.com](https://render.com/) and click **New -> Web Service**.
2. Connect your GitHub repository.
3. Select **Docker** as the Runtime environment.

### Step 3: Configure Environment Variables on Render

In the Render dashboard, go to the **Environment** tab and add the following variables:

| Key                 | Value                                                                  |
| ------------------- | ---------------------------------------------------------------------- |
| `WEBULL_APP_KEY`    | Your Webull App Key                                                    |
| `WEBULL_APP_SECRET` | Your Webull App Secret                                                 |
| `WEBULL_REGION`     | `th`                                                                   |
| `WEBULL_ENDPOINT`   | `api.webull.co.th`                                                     |
| `API_SECRET_KEY`    | A strong, random string (you will send this in the `X-API-Key` header) |

### Step 4: Add the Webull Token (OTP Bypass)

Because Render is ephemeral (it deletes local files every time it restarts), you need to inject your token so Webull doesn't ask for mobile confirmation every day.

1. Open `conf/token.txt` on your local computer.
2. Copy the **3 lines** of text exactly as they appear.
3. In Render -> Environment Variables, create a new variable:
   - **Key:** `WEBULL_TOKEN_CONTENT`
   - **Value:** _(Paste the 3 lines you copied)_
4. Click **Save Changes**.

Render will automatically deploy your application, and it will be permanently authenticated with Webull!

---

## 📚 Next Steps

Read the [API_DOCS.md](API_DOCS.md) file to see the exact endpoints and how to make requests from your website or application.
