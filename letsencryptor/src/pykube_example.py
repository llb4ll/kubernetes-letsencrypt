#!/usr/bin/python3

from pykube import KubeConfig, HTTPClient, Ingress
from time import sleep
import sys
import logging
import pprint
import subprocess

INGRESS_NAME_LETSENCRYPTOR = "letsencryptor"

logging.basicConfig(level=logging.INFO)

SERVICE_ACCOUNT_PATH="/var/run/secrets/kubernetes.io/serviceaccount"
NAMESPACE_FILE=SERVICE_ACCOUNT_PATH + "/namespace"

prettyprint = pprint.PrettyPrinter().pprint



def main():
    kube_config = get_kube_config()
    api_client = HTTPClient(kube_config)
    namespace = get_namespace()
    logging.info("Letsencryptor's starting for namespace {}".format(namespace))
    while (True):
        ingress = fetch_ingress_object(api_client, namespace)
        if ingress is not None:
            refresh_ingress(ingress)
        sleep(10)


def fetch_ingress_object(api_client, namespace):
    try:
        for ingress in Ingress.objects(api_client).filter(namespace=namespace):
            if ingress.name == INGRESS_NAME_LETSENCRYPTOR:
                return ingress
    except Exception as exception:
        logging.exception(exception)
        logging.info("Failed to fetch Ingress objects in namespace {}".format(namespace))
        return None
    logging.info("Failed to find ingress controller in namespace {} with name {}".format(namespace, INGRESS_NAME_LETSENCRYPTOR))
    return None


def get_hosts(ingress):
    rules = ingress.obj['spec']['rules']
    return (rule['host'] for rule in rules)


def renew_letsencrypt(host_list):
    subprocess.call([
        "letsencrypt",
        "certonly",
        "--non-interactive",
        "--agree-tos",
        "--email=\"{}\".format(EMAIL)",
        "--standalone",
        "--standalone-supported-challenges=http-01",
        "--rsa-key-size=2048",
        "--keep-until-expiring",
        "--domains=\"{}\"".format(host_list),
        "--test-cert"
    ])



def refresh_ingress(ingress):
    hosts = get_hosts(ingress)
    host_list = ", ".join(hosts)   
    renew_letsencrypt(host_list)
    




def get_kube_config():
    if (len(sys.argv) > 1):
        return KubeConfig.from_file(sys.argv[1])
    else:
        logging.info("Using service account from kubernetes secrets")
        return KubeConfig.from_service_account()


def get_namespace():
    try:
        with open(NAMESPACE_FILE) as namespace_file:
            namespace = namespace_file.read()
            logging.info("Using namespace {} read from {}".format(namespace, NAMESPACE_FILE))
            return namespace
    except Exception as exception:
        logging.exception(exception)
    logging.info("Fallback to default namespace")
    return "default"


def prettyprint_iter(iterable):
    for item in iterable:
        prettyprint(item.__dict__)


if __name__ == "__main__":
    main()