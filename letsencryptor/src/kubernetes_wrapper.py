import base64
from copy import copy
from pykube import Ingress, KubeConfig, HTTPClient, Secret
import logging


log = logging.getLogger("Kubenertes")

SECRET_LABEL = "letsencryptor-tls"
SECRET_BASENAME = SECRET_LABEL
INGRESS_NAME = "letsencryptor"
SERVICE_ACCOUNT_PATH="/var/run/secrets/kubernetes.io/serviceaccount"
NAMESPACE_FILE=SERVICE_ACCOUNT_PATH + "/namespace"
TOKEN_FILE=SERVICE_ACCOUNT_PATH + "/token"


class Kubernetes(object):
    def __init__(self, api_client, kube_config, namespace):
        self.api_client = api_client
        self.namespace = namespace
        self.kube_config = kube_config

    @classmethod
    def create_from_secrets(cls):
        logging.info("Using service account from kubernetes secrets")
        kube_config = KubeConfig.from_service_account()
        api_client = HTTPClient(kube_config)
        namespace = _get_namespace_from_secrets()
        return Kubernetes(api_client=api_client, kube_config=kube_config, namespace=namespace)

    def fetch_pykube_ingress(self, name=INGRESS_NAME):
        return self._fetch_pykube(Ingress, name=name)

    def fetch_pykube_secret(self, name):
        return self._fetch_pykube(Secret, name=name)

    def _fetch_pykube(self, pykube_type, name=INGRESS_NAME):
        try:
            for p in pykube_type.objects(self.api_client).filter(namespace=self.namespace):
                if p.name == name:
                    return p
        except Exception as exception:
            log.exception(exception)
            log.info("Failed to fetch {} objects in namespace {}".format(pykube_type, self.namespace))
            return None
        log.info("Failed to find {} object in namespace {} with name {}".format(pykube_type, self.namespace, name))
        return None

    def fetch_pykube_secrets(self, label=SECRET_LABEL):
        return list(Secret.objects(self.api_client).filter(selector=label, namespace=self.namespace))

    def create_secret(self, secret_obj):
        self.set_namespace(secret_obj)
        pykube_secret = Secret(self.api_client, secret_obj)
        pykube_secret.create()
        return pykube_secret

    def set_namespace(self, k8s_obj):
        set_namespace(k8s_obj, self.namespace)

    def fetch_pykube_secret_from_pykube_ingress(self, pykube_ingress):
        pykube_ingress = Ingress()
        secret_name = get_tls_secret_name_from_pykube_ingress(pykube_ingress)
        return self.fetch_pykube_secret(name = secret_name)



def _sanitize_name(name):
    return str(name).lower()


def set_name(k8s_obj, name):
    name = _sanitize_name(name)
    _set_dict_path(k8s_obj, ('metadata', 'name'), name)
    return name


def get_name(k8s_obj):
    return _get_dict_path(k8s_obj, ('metadata', 'name'))



def set_namespace(k8s_obj, namespace):
    _set_dict_path(k8s_obj, ('metadata', 'namespace'), namespace)


def set_label(k8s_obj, key, val):
    _set_dict_path(k8s_obj, ('metadata', 'labels', key), val)


def set_data(k8s_obj, key, binary):
    encoded = base64.b64encode(binary)
    _set_dict_path(k8s_obj, _get_data_path(key), encoded)


def _get_data_path(key):
    return ['data', key]


def get_hosts_from_pykube_ingress(pykube_ingress):
    rules = _get_dict_path(unwrap(pykube_ingress), ('spec', 'rules'))
    return _map_to_value(rules, 'host')


def _isiterable(obj):
    return hasattr(obj, '__iter__')


def _map_to_value(list_of_dicts, key):
    if _isiterable(list_of_dicts):
        return (rule[key] for rule in list_of_dicts)
    return []


def get_tls_secret_name_from_pykube_ingress(pykube_ingress):
    return _get_dict_path(unwrap(pykube_ingress), ('spec', 'tls', 'secretName'))


def set_secret_name(ingress_obj, secret_name):
    _set_dict_path(ingress_obj, ('spec', 'tls', 'secretName'), secret_name)


def _get_namespace_from_secrets(namespace_filename=NAMESPACE_FILE):
        try:
            with open(namespace_filename) as namespace_file:
                namespace = namespace_file.read()
                logging.info("Using namespace {} read from {}".format(namespace, namespace_filename))
                return namespace
        except Exception as exception:
            logging.exception(exception)
        logging.info("Fallback to default namespace")
        return "default"


def _set_dict_path(dict, path, value):
    first, remaining = _get_first(path)
    if len(remaining) == 0:
        dict[first] = value
    else:
        dict[first] = dict.get(first, {})
        _set_dict_path(dict[first], remaining, value)


def _get_dict_path(d, path):
    if not isinstance(d, dict):
        raise AssertionError("Expected dict with path {}, got {} {}".format(path, type(d), d))
    first, remaining = _get_first(path)
    d = d.get(first)
    if len(remaining) == 0:
        return d
    elif d is None:
        return None
    else:
        return _get_dict_path(d, remaining)


def _get_first(iterable):
    iterable = list(iterable)
    first = iterable.pop(0)
    return first, iterable


def unwrap(pykube_object):
    return pykube_object.obj


def _compare_dict_path(k8s_obj1, k8s_obj2, path):
    return _get_dict_path(k8s_obj1, path) == _get_dict_path(k8s_obj2, path)


def compare_data(k8s_obj1, k8s_obj2, key):
    return _compare_dict_path(k8s_obj1, k8s_obj2, _get_data_path(key))
