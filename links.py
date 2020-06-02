import json
from urllib.parse import urlparse

LINKS_KEY = "links"
SCHEME_DELIMITER = "//"

ERROR_LINKS_LIST_OR_STR = "Links must be list or string"
ERROR_LINK_STR = "Link must be string"
ERROR_NO_DATA = "No data"
ERROR_BAD_DATA_FORMAT = "Not json data format"
ERROR_NO_KEY = f"'{LINKS_KEY}' key not found"
ERROR_BAD_RANGE_DATA = "range_data must be list"


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
            pipe.rpush(id, link)
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
            raise TypeError(ERROR_LINKS_LIST_OR_STR)

        if isinstance(links, str):
            links = [links]

        if not all([isinstance(link, str) for link in links]):
            raise TypeError(ERROR_LINK_STR)

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
            raise ValueError(ERROR_NO_DATA)
        if not isinstance(json, dict):
            raise TypeError(ERROR_BAD_DATA_FORMAT)
        if LINKS_KEY not in json:
            raise KeyError(ERROR_NO_KEY)

        links = json[LINKS_KEY]
        return Links(links)

    def get_domains(self):
        res = []

        for link in self.links:
            res.append(self.get_domain(link))

        return list(set(res))