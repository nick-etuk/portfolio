from portfolio.utils.config import bitquery_api_key
from icecream import ic
from requests import post


def bitquery_api(query: str):
    headers = {'X-API-KEY': bitquery_api_key}
    request = post('https://graphql.bitquery.io/',
                   json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception('Query failed and return code is {}.      {}'.format(request.status_code,
                        query))


def get_wallet_balances(address: str):

    query = f'''
    query{{
        ethereum_network: ethereum(network: ethereum){{
            address(address: {{is: "{address}"}}) {{
                balances {{
                    value
                    currency {{
                    symbol
                    name
                    address
                    }}
                }}
            }}
        }}
        bsc_network: ethereum(network: bsc) {{
            address(address: {{is: "{address}"}}) {{
                balances {{
                    value
                    currency {{
                    symbol
                    name
                    address
                    }}
                }}
            }}
        }}
        matic_network: ethereum(network: matic) {{
            address(address: {{is: "{address}"}}) {{
                balances {{
                    value
                    currency {{
                        symbol
                        name
                        address
                    }}
                }}
            }}
        }}
        fantom_network: ethereum(network: fantom) {{
            address(address: {{is: "{address}"}}) {{
                balances {{
                    value
                    currency {{
                        symbol
                        name
                        address
                    }}
                }}
            }}
        }}
        avalanche_network: ethereum(network: avalanche) {{
            address(address: {{is: "{address}"}}) {{
                balances {{
                    value
                    currency {{
                        symbol
                        name
                        address
                    }}
                }}
            }}
        }}
        moonbeam_network: ethereum(network: moonbeam) {{
            address(address: {{is: "{address}"}}) {{
                balances {{
                    value
                    currency {{
                        symbol
                        name
                        address
                    }}
                }}
            }}
        }}
    }}
    '''
    return bitquery_api(query)


if __name__ == "__main__":

    sol_med = '0x3Cb83df6CF19831ca241159137b75C71D9087294'
    sol_high = '0xEc10A8061dAeBdA85386dBf16E9880706bC9f1b9'
    """
    Solomon LTC
    0x6b707Ab93B8153c930aBfaa709087772DDCcc8e6

    Peronsal Med
    0x5B19bAeb7491Ad1890dD6F1A41b935aa11C0cFf7

    Personal High
    0xb9CD1949B934897ABA4EB107853C3D2BfcB225De

    Personal LTC
    0x541A1f804aC641A07DD719CC0A9Ca89a7F8F756E
    """
    print(get_wallet_balances(sol_high))
