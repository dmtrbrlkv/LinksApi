from datetime import datetime
from http import HTTPStatus
from argparse import ArgumentParser

from flask import jsonify

OK = "ok"

REDIS_LINKS_KEY = "links"
REDIS_LINKS_ID = "links_id"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None


def load_config():
    ap = ArgumentParser()
    ap.add_argument("--host", action="store", default=REDIS_HOST)
    ap.add_argument("--port", action="store", default=REDIS_PORT)
    ap.add_argument("--db", action="store", default=REDIS_DB)
    ap.add_argument("--password", action="store", default=REDIS_PASSWORD)
    ap.add_argument("--lkey", action="store", default=REDIS_LINKS_KEY)
    ap.add_argument("--lid", action="store", default=REDIS_LINKS_ID)
    ap.add_argument("--debug", action="store_true", default=False)
    options = ap.parse_args()
    return options


def make_json_response(key=None, data=None, code=None, status=None, error=None):
    if error:
        status = error
    if status is None:
        status = OK
    if code is None:
        code = HTTPStatus.OK

    res = {}
    if key is not None:
        res[key] = data

    res["status"] = status

    return jsonify(res), code


def now_timestamp():
    return int(datetime.timestamp(datetime.now()))


def get_visited_domains_params(request, params):
    def add_err(err, e):
        if err:
            err += ", "
        err += e

        return err

    err = ""
    res = []
    for param in params:
        v = request.args.get(param, default=None)
        if v is None:
            err = add_err(err, f"'{param}' parameter not provided")
            continue
        try:
            v = int(v)
        except:
            err = add_err(err, f"'{param}' must be integer")
            continue

        res.append(v)

    if err:
        raise ValueError(err)

    return tuple(res)
