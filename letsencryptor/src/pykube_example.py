#!/usr/bin/python3

from pykube import KubeConfig, HTTPClient, Ingress
from time import sleep
import sys
import logging
import pprint

SERVICE_ACCOUNT_PATH="/var/run/secrets/kubernetes.io/serviceaccount"
NAMESPACE_FILE=SERVICE_ACCOUNT_PATH + "/namespace"

prettyprint = pprint.PrettyPrinter().pprint


def main():
    print("Letsencryptor reached first print statement")
    logging.info("Letsencryptor's first log message")
    kube_config = get_kube_config()
    api_client = HTTPClient(kube_config)
    namespace = get_namespace()
    create_ingress_object(api_client, namespace)
    while (True):
        ingress_objs = fetch_all_ingress_objects(api_client, namespace)
        prettyprint_iter(ingress_objs)
        sleep(10)


def fetch_all_ingress_objects(api_client, namespace):
    try:
        return list(Ingress.objects(api_client).filter(namespace=namespace))
    except Exception as exception:
        logging.exception(exception)
        logging.info("Failed to fetch Ingress objects from k8s API server.")
        return []


def create_ingress_object(api_client, namespace):
    ingress = {
        'metadata':  {
                'name': 'letsencryptor-https-test',
                'namespace': namespace},
        'spec': {
            "backend": {
                "serviceName": "server-minefield",
                "servicePort": 8080
            },
            'rules': [{
                'host': 'demo.cg.ts.egym.coffee',
                'https': {
                    'paths': [
                        {
                            'backend': {
                                'serviceName': 'server-minefield',
                                'servicePort': 8080},
                            'path': '/'}]}}]}}
    print("Creating ingress object with this structure: ")
    prettyprint(ingress)
    pykube_ingress = Ingress(api_client, ingress)
    pykube_ingress.create()
    print("Created ingress object with this structure: ")
    prettyprint(pykube_ingress.obj)





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