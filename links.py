import json
from urllib.parse import urlparse

LINKS_KEY = "links"
SCHEME_DELIMITER = "//"


class RedisLinksConnector:
    def __init__(self, client, name, id_name):
        self.client = client
        self.name = name
        self.id_name = id_name

    def add(self, links, timestamp):
        id = self.client.incr(self.id_name)

        pipe = self.client.pipeline(True)
        pipe.zadd(self.name, {id: timestamp})
        for link in links:
            pipe.lpush(id, link)
        pipe.execute()

    def get_by_range(self, min, max):
        ids = self.client.zrangebyscore(self.name, min, max)
        res = []
        for id in ids:
            links = self.client.lrange(id, 0, -1)
            res.extend([link.decode() for link in links])
        return res


class Links:
    def __init__(self, links):
        if not isinstance(links, (list, str)):
            raise TypeError("Links must be list or string")

        if isinstance(links, str):
            links = [links]

        if not all([isinstance(link, str) for link in links]):
            raise TypeError("Link must be string")

        self.links = links

    @staticmethod
    def get_domain(url):
        if SCHEME_DELIMITER not in url:
            url = SCHEME_DELIMITER + url
        parse = urlparse(url)
        return parse.netloc

    @classmethod
    def from_json(cls, json):
        if not json:
            raise ValueError("No data")
        if not isinstance(json, dict):
            raise TypeError("Not json data format")
        if LINKS_KEY not in json:
            raise KeyError(f"'{LINKS_KEY}' key not found")

        links = json[LINKS_KEY]
        return Links(links)

    @classmethod
    def from_range_data(cls, range_data):
        if not isinstance(range_data, list):
            raise TypeError("mapping must be list")

        links = []

        for data in range_data:
            data = json.loads(data)
            try:
                links.extend(data.values())
            except:
                continue

        return Links(links)

    def get_domains(self):
        res = []

        for link in self.links:
            res.append(self.get_domain(link))

        return list(set(res))