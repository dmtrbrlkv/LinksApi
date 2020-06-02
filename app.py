from http import HTTPStatus

from flask import Flask, request
from redis import Redis

from links import RedisLinksConnector, Links
from utils import load_config, make_json_response, now_timestamp, get_visited_domains_params, ERROR_INTERNAL, DOMAINS_KEY

app = Flask(__name__)


@app.route("/visited_links",methods=["POST"])
def visited_links():
    try:
        json = request.json
    except Exception as e:
        return make_json_response(error=e, code=HTTPStatus.BAD_REQUEST)

    try:
        links = Links.from_json(json)
    except Exception as e:
        return make_json_response(error=e, code=HTTPStatus.BAD_REQUEST)

    try:
        redis_connector.add(links.links, now_timestamp())
    except Exception as e:
        return make_json_response(error=ERROR_INTERNAL, code=HTTPStatus.INTERNAL_SERVER_ERROR)

    return make_json_response()


@app.route("/visited_domains/", methods=["GET"])
def visited_domains():
    try:
        frm, to = get_visited_domains_params(request.args, ("from", "to"))
    except Exception as e:
        return make_json_response(error=e, code=HTTPStatus.BAD_REQUEST)

    try:
        data = redis_connector.get_by_range(frm, to)
    except Exception as e:
        return make_json_response(status=ERROR_INTERNAL, code=HTTPStatus.INTERNAL_SERVER_ERROR)

    links = Links(data)
    return make_json_response(key=DOMAINS_KEY, data=links.get_domains())


if __name__ == "__main__":
    options = load_config()
    client = Redis(options.host, options.port, options.db, options.password)
    redis_connector = RedisLinksConnector(client, options.lkey, options.lid)
    app.run(debug=options.debug)