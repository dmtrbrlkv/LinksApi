import pytest
import datetime

from werkzeug.datastructures import ImmutableMultiDict

from utils import *




def test_now_timestamp():
    ts = now_timestamp()
    d1 = datetime.now()
    d2 = datetime.fromtimestamp(ts)

    d1 = d1.replace(second=0, microsecond=0)
    d2 = d2.replace(second=0, microsecond=0)

    assert d1 == d2


class TestMakeResponse:
    def test_empty_params(self):
        res = make_response()
        assert isinstance(res, tuple)
        assert len(res) == 2
        data, code = res
        assert code == HTTPStatus.OK
        assert isinstance(data, dict)
        assert STATUS_KEY in data

    def test_error_param(self):
        e_msg = "test msg"
        e = Exception(e_msg)
        res = make_response(error=e)
        assert isinstance(res, tuple)
        assert len(res) == 2
        data, code = res
        assert isinstance(data, dict)
        assert STATUS_KEY in data
        data[STATUS_KEY] = e_msg

    def test_data_param(self):
        key = "key"
        data = "data"
        res = make_response(key=key, data=data)
        assert isinstance(res, tuple)
        assert len(res) == 2
        data, code = res
        assert isinstance(data, dict)
        assert key in data
        data[key] = data


class TestVisitedParams:

    @pytest.mark.parametrize("args, exp_res", [
        pytest.param(
            (ImmutableMultiDict(), ("p1", )), ERROR_PARAM_NOT_PROVIDED.format("p1"), id="not provided one"
        ),

        pytest.param(
            (ImmutableMultiDict(), ("p1", "p2", "p3")), [ERROR_PARAM_NOT_PROVIDED.format(x) for x in ("p1", "p2", "p3")], id="not provided multi"
        ),

        pytest.param(
            (ImmutableMultiDict({"p1": "one"}), ("p1",)), ERROR_PARAM_INT.format("p1"), id="not integer"
        ),

        pytest.param(
            (ImmutableMultiDict({"p1": "one", "p2": "two",  "p3": "three"}), ("p1", "p2", "p3")), [ERROR_PARAM_INT.format(x) for x in ("p1", "p2", "p3")], id="not integer multi"
        ),

    ])
    def test_errors(self, args, exp_res):
        with pytest.raises(ValueError) as e:
            get_visited_domains_params(*args)

        if isinstance(exp_res, str):
            assert exp_res in str(e.value)
        if isinstance(exp_res, list):
            for res in exp_res:
                assert res in str(e.value)

    def test_params(self):
        p1 = 1
        p2 = 2
        assert (p1, p2) == get_visited_domains_params(ImmutableMultiDict({"p1": p1, "p2": p2}), ("p1", "p2"))
