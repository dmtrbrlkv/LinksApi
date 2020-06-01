from datetime import datetime
from http import HTTPStatus
from urllib.parse import urlparse

from flask import Flask, request, jsonify


class RedisConnector:
    def __init__(self):
        self.data = []

    def add(self, link, timestamp):
        self.data.append((link, timestamp))

    def get_by_range(self, frm, to):
        res = []

        for link, timestamp in self.data:
            if frm <= timestamp <= to:
                res.append(link)

        return res


LINKS_KEY = "links"
app = Flask(__name__)
redis = RedisConnector()

class Links:
    def __init__(self, links, timestamp=None):
        self.links = links
        if timestamp is None:
            timestamp = int(datetime.timestamp(datetime.now()))
        self.timestamp = timestamp

    @staticmethod
    def get_domain(url):
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

        if not isinstance(links, (list, str)):
            raise TypeError

        if isinstance(links, str):
            links = [str]

        return Links(links)

    @classmethod
    def from_list(cls, lst):
        if not lst:
            raise ValueError("No data")
        if not isinstance(lst, list):
            raise TypeError("Not list instance")

        return Links(lst)

    def get_domains(self):
        res = []

        for link in self.links:
            res.append(self.get_domain(link))

        return list(set(res))

    def save(self, db_connector):
        for link in self.links:
            db_connector.add(link, self.timestamp)


@app.route("/visited_links",methods=["POST"])
def add_links():
    try:
        json = request.json
    except Exception as e:
        return jsonify({'status': e.description}), HTTPStatus.BAD_REQUEST

    try:
        links = Links.from_json(json)
    except Exception as e:
        return jsonify({'status': ", ".join(e.args)}), HTTPStatus.BAD_REQUEST

    try:
        links.save(redis)
    except Exception as e:
        return jsonify({'status': HTTPStatus.INTERNAL_SERVER_ERROR}), HTTPStatus.INTERNAL_SERVER_ERROR

    return jsonify({'status': "OK"}), HTTPStatus.OK


@app.route("/visited_domains/", methods=["GET"])
def get_domains_by_range():
    frm = request.args.get("from", default=None, type=int)
    to = request.args.get("to", default=None, type=int)
    data = redis.get_by_range(frm, to)
    links = Links.from_list(data)
    return jsonify({"domains": links.get_domains(),
                    'status': "OK"}), HTTPStatus.OK


if __name__ == "__main__":
    app.run(debug=True)