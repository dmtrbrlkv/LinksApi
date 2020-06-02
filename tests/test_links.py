import pytest

from links import *


class TestLinks:
    @pytest.mark.parametrize("args, exp_res", [
        pytest.param(
            [], [], id="empty list"
        ),

        pytest.param(
            ["s1", "s2"], ["s1", "s2"], id="list"
        ),

        pytest.param(
            "string", ["string"], id="string"
        ),

    ])
    def test_init(self, args, exp_res):
        links = Links(args)
        assert links.links == exp_res

    @pytest.mark.parametrize("args, exp_res", [
        pytest.param(
            {}, ERROR_LINKS_LIST_OR_STR, id="dict"
        ),

        pytest.param(
            1, ERROR_LINKS_LIST_OR_STR, id="int"
        ),

        pytest.param(
            ["s1", 2], ERROR_LINK_STR, id="int link"
        ),

    ])
    def test_init_error(self, args, exp_res):
        with pytest.raises(TypeError) as e:
            links = Links(args)
        assert exp_res == str(e.value)

    @pytest.mark.parametrize("args, exp_res", [
        pytest.param(
            "funbox.ru", "funbox.ru", id="no schema"
        ),

        pytest.param(
            "https://ya.ru", "ya.ru", id="only domain"
        ),

        pytest.param(
            "https://ya.ru?q=123", "ya.ru", id="domain with params"
        ),

        pytest.param(
            "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor", "stackoverflow.com", id="with path"
        ),

    ])
    def test_get_domain(self, args, exp_res):
        assert exp_res == Links.get_domain(args)

    def test_get_domains(self):
        l = [
            "https://ya.ru",
            "https://ya.ru?q=123",
            "funbox.ru",
            "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor"
        ]

        domains = list(set([
                    "ya.ru",
                    "funbox.ru",
                    "stackoverflow.com"
        ]))

        links = Links(l)
        assert domains == links.get_domains()

    @pytest.mark.parametrize("args, exp_res", [
        pytest.param(
            {LINKS_KEY: []}, [], id="empty list"
        ),

        pytest.param(
            {LINKS_KEY: ["s1", "s2"]}, ["s1", "s2"], id="list"
        ),

        pytest.param(
            {LINKS_KEY: "string"}, ["string"], id="string"
        ),

    ])
    def test_from_json(self, args, exp_res):
        links = Links.from_json(args)
        assert links.links == exp_res

    @pytest.mark.parametrize("args, error_type, error_msg", [
        pytest.param(
            None, ValueError, ERROR_NO_DATA, id="None"
        ),

        pytest.param(
            ["s1", "s2"], TypeError, ERROR_BAD_DATA_FORMAT, id="list"
        ),

        pytest.param(
            {"wrong key": "string"}, KeyError, ERROR_NO_KEY, id="wrong key"
        ),

    ])
    def test_from_json_error(self, args, error_type, error_msg):
        with pytest.raises(error_type) as e:
            links = Links.from_json(args)
        assert error_msg in str(e.value)