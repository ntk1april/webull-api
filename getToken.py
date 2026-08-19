import json
from webull.core.client import ApiClient
from webull.trade.trade_client import TradeClient

api_client = ApiClient("<your_app_key>", "<your_app_secret>", "th")
api_client.add_endpoint("th", "api.webull.co.th")

trade_client = TradeClient(api_client)
res = trade_client.account_v2.get_account_list()
if res.status_code == 200:
    print("Success!", json.dumps(res.json(), indent=2))
else:
    print("Error:", res.status_code, res.text)