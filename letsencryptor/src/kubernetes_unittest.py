#!/usr/bin/env python2

from unittest import TestCase, main
from kubernetes_wrapper import _set_dict_path


class KubernetesUnitTest(TestCase):
    def test_set_dict_path_empty(self):
        d = {}
        _set_dict_path(d, ["one", "two"], "val")
        self.assertEquals(d["one"]["two"], "val")

    def test_set_dict_path_notempty(self):
        d = {"one": {"foo": "bar"}}
        _set_dict_path(d, ["one", "two"], "val")
        self.assertEquals(d["one"]["foo"], "bar")
        self.assertEquals(d["one"]["two"], "val")

    def test_set_dict_path_overwrites(self):
        d = {"one": {"two": "OLD"}}
        _set_dict_path(d, ["one", "two"], "val")
        self.assertEquals(d["one"]["two"], "val")

if __name__ == "__main__":
    main()