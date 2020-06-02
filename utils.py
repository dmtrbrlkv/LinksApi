from datetime import datetime
from http import HTTPStatus
from argparse import ArgumentParser

from flask import jsonify

OK = "ok"
DOMAINS_KEY = "domains"
STATUS_KEY = "status"

REDIS_LINKS_KEY = "links"
REDIS_LINKS_ID = "links_id"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None

ERROR_PARAM_NOT_PROVIDED = "'{}' parameter not provided"
ERROR_PARAM_INT = "'{}' parameter must be integer"

ERROR_INTERNAL = "Internal error"


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


def make_response(key=None, data=None, code=None, status=None, error=None):
    if error:
        status = str(error)
        if status.startswith('"'):
            status = status[1:]
        if status.endswith('"'):
            status = status[:-1]
    if status is None:
        status = OK
    if code is None:
        code = HTTPStatus.OK

    res = {}
    if key is not None:
        res[key] = data

    res[STATUS_KEY] = status

    return res, code


def make_json_response(key=None, data=None, code=None, status=None, error=None):
    data, code = make_response(key, data, code, status, error)
    return jsonify(data), code


def now_timestamp():
    return int(datetime.timestamp(datetime.now()))


def get_visited_domains_params(args, params):
    def add_err(err, e):
        if err:
            err += ", "
        err += e
        return err

    err = ""
    res = []
    for param in params:
        v = args.get(param, default=None)
        if v is None:
            err = add_err(err, ERROR_PARAM_NOT_PROVIDED.format(param))
            continue
        try:
            v = int(v)
        except:
            err = add_err(err, ERROR_PARAM_INT.format(param))
            continue

        res.append(v)

    if err:
        raise ValueError(err)

    return tuple(res)
