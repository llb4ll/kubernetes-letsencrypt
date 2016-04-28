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

    def test_set_get_dict_path(self):
        d = {}
        k8s._set_dict_path(d, [1,2,3], 4)
        self.assertEqual(d, {1:{2:{3:4}}})
        self.assertEqual(k8s._get_dict_path(d, (1,2,3)), 4)

    def test_set_get_dict_path_simple(self):
        d = {}
        k8s._set_dict_path(d, 'key', 'val')
        self.assertEqual(k8s._get_dict_path(d, 'key'), 'val')

    def test_compare_data(self):
        a = {'foo': 'bar'}
        b = {'foo': 'not bar'}
        k8s.set_data(a, 'key', 'binary')
        k8s.set_data(b, 'key', 'binary')
        self.assertTrue(k8s.compare_data(a, b, 'key'))

    def test_set_get_secret(self):
        d = {}
        expected= "test-secret"
        k8s.set_tls_secret_name(d, expected)
        output = k8s.get_tls_secret_name(d)
        self.assertEqual(expected, output)


if __name__ == "__main__":
    main()