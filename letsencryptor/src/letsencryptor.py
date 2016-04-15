#!/usr/bin/python3

from time import sleep
import logging
from letsencrypt_wrapper import LetsEncrypt
from kubernetes_wrapper import Kubernetes, get_hosts_from_pykube_ingress


logging.basicConfig(level=logging.INFO)


class Letsencryptor(object):
    kubernetes_polling_delay = 30

    def __init__(self, letsencrypt=None, kubernetes=None):
        self.letsencrypt = letsencrypt
        if self.letsencrypt is None:
            self.letsencrypt = LetsEncrypt()
        self.kubernetes = kubernetes
        if self.kubernetes is None:
            self.kubernetes = Kubernetes.create_from_secrets()

    def refresh_ingress(ingress):
        hosts = get_hosts_from_pykube_ingress(ingress)
        host_list = ", ".join(hosts)
        LetsEncrypt().renew_letsencrypt(host_list)

    def main(self):
        namespace = self.kubernetes.namespace
        logging.info("Letsencryptor running for namespace {}".format(namespace))
        while (True):
            pykube_ingress = self.kubernetes.fetch_ingress_object()
            if pykube_ingress is not None:
                self.refresh_ingress(pykube_ingress)
            sleep(self.kubernetes_polling_delay)


if __name__ == "__main__":
    Letsencryptor().main()