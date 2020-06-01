from http import HTTPStatus

from flask import Flask, request
from redis import Redis

from links import RedisLinksConnector, Links
from utils import load_config, make_json_response, now_timestamp, get_visited_domains_params


app = Flask(__name__)


@app.route("/visited_links",methods=["POST"])
def visited_links():
    try:
        json = request.json
    except Exception as e:
        return make_json_response(status=e.description, code=HTTPStatus.BAD_REQUEST)

    try:
        links = Links.from_json(json)
    except Exception as e:
        return make_json_response(status=", ".join(e.args), code=HTTPStatus.BAD_REQUEST)

    try:
        redis_connector.add(links.links, now_timestamp())
    except Exception as e:
        return make_json_response(status="Internal error", code=HTTPStatus.INTERNAL_SERVER_ERROR)

    return make_json_response()


@app.route("/visited_domains/", methods=["GET"])
def visited_domains():
    try:
        frm, to = get_visited_domains_params(request, ("from", "to"))
    except Exception as e:
        return make_json_response(status=", ".join(e.args), code=HTTPStatus.BAD_REQUEST)

    try:
        data = redis_connector.get_by_range(frm, to)
    except Exception as e:
        return make_json_response(status="Internal error", code=HTTPStatus.INTERNAL_SERVER_ERROR)

    links = Links(data)
    return make_json_response(key="domains", data=links.get_domains())


if __name__ == "__main__":
    options = load_config()
    client = Redis(options.host, options.port, options.db, options.password)
    redis_connector = RedisLinksConnector(client, options.lkey, options.lid)
    app.run(debug=options.debug)