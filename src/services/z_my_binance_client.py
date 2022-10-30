from typing import Dict, Optional, List, Tuple
from binance.client import Client
from config import binance_api_key, binance_api_secret
from init import init
from icecream import ic


class MyBinanceClient(Client):
    def __init__(
        self, api_key: Optional[str] = None, api_secret: Optional[str] = None,
        requests_params: Optional[Dict[str, str]] = None, tld: str = 'com',
        testnet: bool = False
    ):

        super().__init__(api_key, api_secret, requests_params, tld, testnet)

    def get_flexible_product_position(self, **params):
        """Get account status detail.
        https://binance-docs.github.io/apidocs/spot/en/#account-status-sapi-user_data
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int
        :returns: API response
        .. code-block:: python
            {
                "data": "Normal"
            }
        """
        uri = 'sapi/v1/lending/daily/token/position'
        # 'account/status'
        return self._get(uri)
        # return self._request_margin_api('get', uri, True, data=params)
