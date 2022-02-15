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
        ids = id_list.replace(",", " ").split()
        self.id_to_name = {}
        for id_ in ids:
            self.id_to_name[id_] = self.request_name(id_)

    def collect(self):
        g = GaugeMetricFamily("fuel_price", "fuel price", labels=["station_id", "station_name", "fuel_type"])
        for id_, prices in self.request_prices(list(self.id_to_name)).items():
            for fuel_type, value in prices.items():
                g.add_metric([id_, self.id_to_name[id_], fuel_type], value)
        yield g

    def request_name(self, id_):
        r = requests.get(
            f"{self.BASE_URL}/detail.php",
            params={
                "id": id_,
                "apikey": self.token
            }
        )
        assert r.status_code == 200
        assert r.json().get("status") == "ok"
        return r.json().get("station").get("name")

    def request_prices(self, ids):
        prices = {}
        for i in range(len(ids)):
            target_ids = ids[i:i + 10]
            r = requests.get(
                f"{self.BASE_URL}/prices.php",
                params={
                    "ids": ",".join(target_ids),
                    "apikey": self.token
                }
            )
            assert r.status_code == 200
            assert r.json().get("ok")
            for id_, data in r.json().get("prices").items():
                if data.get("status") != "open":
                    continue
                del data["status"]
                prices[id_] = data
        return prices
