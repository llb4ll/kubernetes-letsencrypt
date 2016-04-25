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

    def fetch_ingress_object(self, name=INGRESS_NAME):
        try:
            for ingress in Ingress.objects(self.api_client).filter(namespace=self.namespace):
                if ingress.name == name:
                    return ingress
        except Exception as exception:
            log.exception(exception)
            log.info("Failed to fetch Ingress objects in namespace {}".format(self.namespace))
            return None
        log.info("Failed to find ingress controller in namespace {} with name {}".format(self.namespace, name))
        return None

    def fetch_secret_objects(self, label=SECRET_LABEL):
        return list(Secret.objects(self.api_client).filter(selector=label, namespace=self.namespace))

    def create_secret(self, secret_obj):
        self.set_namespace(secret_obj)
        pykube_secret = Secret(self.api_client, secret_obj)
        pykube_secret.create()
        return pykube_secret

    def set_namespace(self, k8s_obj):
        set_namespace(k8s_obj, self.namespace)


def _sanitize_name(name):
    return str(name).lower()


def set_name(k8s_obj, name):
    name = _sanitize_name(name)
    _set_dict_path(k8s_obj, ['metadata', 'name'], name)
    return name


def set_namespace(k8s_obj, namespace):
    _set_dict_path(k8s_obj, ['metadata', 'namespace'], namespace)


def set_label(k8s_obj, key, val):
    _set_dict_path(k8s_obj, ['metadata', 'labels', key], val)


def get_hosts_from_pykube_ingress(ingress):
    rules = ingress.obj['spec']['rules']
    return (rule['host'] for rule in rules)


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
    path = copy(path)
    first = path.pop(0)
    if len(path) == 0:
        dict[first] = value
    else:
        dict[first] = dict.get(first, {})
        _set_dict_path(dict[first], path, value)



