#!/usr/bin/python3

from pykube import KubeConfig, HTTPClient, Ingress
from time import sleep
import sys
import logging

SERVICE_ACCOUNT_PATH="/var/run/secrets/kubernetes.io/serviceaccount"
NAMESPACE_FILE=SERVICE_ACCOUNT_PATH + "/namespace"

def main():
    kube_config = get_kube_config()
    api_client = HTTPClient(kube_config)
    namespace = get_namespace()
    while (True):
        ingress_objs = fetch_all_ingress_objects(api_client, namespace)
        print(ingress_objs)
        sleep(60)


def fetch_all_ingress_objects(api_client, namespace):
    try:
        return list(Ingress.objects(api_client).filter(namespace=namespace))
    except Exception as exception:
        logging.exception(exception)
        logging.info("Failed to fetch Ingress objects from k8s API server.")
        return []



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


if __name__ == "__main__":
    main()