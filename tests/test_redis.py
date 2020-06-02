import pytest
import json

from links import RedisLinksConnector
from redis import Redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 1
REDIS_PASSWORD = None


class TestRedis:
    def setup_method(self):
        client = Redis(REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD)
        self.client = client

    def teardown_method(self):
        self.client.flushdb()

    def test_add(self):
        name_id = "test_id"
        name = "test"
        links = ["link1", "link2"]
        timestamp = 555

        test_id = self.client.get(name_id)
        if test_id is None:
            test_id = 0
        else:
            test_id = int(test_id)
        test_id += 1

        redis_conn = RedisLinksConnector(self.client, name, name_id)
        redis_conn.add(links, timestamp)

        assert test_id == int(self.client.get(name_id))
        assert test_id in [int(id) for id in self.client.zrangebyscore(name, timestamp, timestamp)]
        assert links == [link.decode() for link in self.client.lrange(test_id, 0, -1)]

    def test_get_by_range(self):
        name_id = "test_id"
        name = "test"

        min_t = 200
        max_t = 300

        exp_res = []

        for id, timestamp in enumerate(range(100, 401, 10)):
            self.client.zadd(name, {str(id):timestamp})
            self.client.rpush(str(id), "link1" + str(id))
            self.client.rpush(str(id), "link2" + str(id))

            if min_t <= timestamp <= max_t:
                exp_res.append("link1" + str(id))
                exp_res.append("link2" + str(id))

        redis_conn = RedisLinksConnector(self.client, name, name_id)
        res = redis_conn.get_by_range(min_t, max_t)

        assert res == exp_res