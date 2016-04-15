from pykube import Ingress, KubeConfig, HTTPClient, Secret
import logging


log = logging.getLogger("Kubenertes")

SCERET_LABEL_LETSENCRYPTOR = "letsencryptor-tls"
INGRESS_NAME_LETSENCRYPTOR = "letsencryptor"
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

    def fetch_ingress_object(self, name=INGRESS_NAME_LETSENCRYPTOR):
        try:
            for ingress in Ingress.objects(self.api_client).filter(namespace=self.namespace):
                if ingress.name == self.ingress_name:
                    return ingress
        except Exception as exception:
            log.exception(exception)
            log.info("Failed to fetch Ingress objects in namespace {}".format(self.namespace))
            return None
        log.info("Failed to find ingress controller in namespace {} with name {}".format(self.namespace, name))
        return None

    def fetch_secret_objects(self, label=SCERET_LABEL_LETSENCRYPTOR):
        return list(Secret.objects(self.api_client).filter(label=label, namespace=self.namespace))


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

def get_hosts_from_pykube_ingress(ingress):
    rules = ingress.obj['spec']['rules']
    return (rule['host'] for rule in rules)


