from utils.dotenv import CERTNAME

import requests


class Connector:
    _session = requests.Session()
    json_rpc_url = "https://api.betfair.com/exchange/betting/json-rpc/v1"
    REST_url = "https://api.betfair.com/exchange/betting/rest/v1.0/"

    def __init__(self):
        self._session.cert = (f"./certs/{CERTNAME}.crt", f"./certs/{CERTNAME}.pem")

