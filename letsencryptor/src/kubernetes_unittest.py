#!/usr/bin/env python2

from unittest import TestCase, main
import kubernetes_wrapper as k8s
import pykube


class KubernetesUnitTest(TestCase):
    def test_set_dict_path_empty(self):
        d = {}
        k8s._set_dict_path(d, ["one", "two"], "val")
        self.assertEquals(d["one"]["two"], "val")

    def test_set_dict_path_notempty(self):
        d = {"one": {"foo": "bar"}}
        k8s._set_dict_path(d, ["one", "two"], "val")
        self.assertEquals(d["one"]["foo"], "bar")
        self.assertEquals(d["one"]["two"], "val")

    def test_set_dict_path_overwrites(self):
        d = {"one": {"two": "OLD"}}
        k8s._set_dict_path(d, ["one", "two"], "val")
        self.assertEquals(d["one"]["two"], "val")

    def test_name(self):
        obj = {}
        name = "testname"
        k8s.set_name(obj, name)
        secret = pykube.Secret(None, obj)
        self.assertEquals(secret.name, name)

if __name__ == "__main__":
    main()