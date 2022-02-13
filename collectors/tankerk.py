import requests
from prometheus_client.metrics_core import GaugeMetricFamily

from collector_base import CollectorBase


class TankerKCollector(CollectorBase):
    ENV_PREFIX = "TANKERK"
    BASE_URL = "https://creativecommons.tankerkoenig.de/json/"

    def __init__(self, env):
        super().__init__(env)
        self.token = self.env_get_raise("API_KEY")
        id_list = self.env_get_raise("ID_LIST")
        self.ids = id_list.replace(",", " ").split()

    def collect(self):
        g = GaugeMetricFamily("price", "fuel price", labels=["station_id", "fuel_type"])
        for id_, prices in self.request_prices().items():
            for fuel_type, value in prices.items():
                g.add_metric([id_, fuel_type], value)
        yield g

    def request_prices(self):
        prices = {}
        for i in range(len(self.ids)):
            target_ids = self.ids[i:i + 10]
            r = requests.get(
                f"{self.BASE_URL}/prices.php",
                params={
                    "ids": ",".join(target_ids),
                    "apikey": self.token
                }
            )
            if not r.json().get("ok"):
                continue
            for id_, data in r.json().get("prices").items():
                if data.get("status") != "open":
                    continue
                del data["status"]
                prices[id_] = data
        return prices
