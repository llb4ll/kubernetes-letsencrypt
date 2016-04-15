#!/usr/bin/python3

from time import sleep
import logging
import pretty
from letsencrypt_wrapper import LetsEncrypt
from kubernetes_wrapper import Kubernetes, get_hosts_from_pykube_ingress

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("letsencryptor")

class Letsencryptor(object):
    kubernetes_polling_delay = 30

    def __init__(self, letsencrypt=None, kubernetes=None):
        self.letsencrypt = letsencrypt
        if self.letsencrypt is None:
            self.letsencrypt = LetsEncrypt()
        self.kubernetes = kubernetes
        if self.kubernetes is None:
            self.kubernetes = Kubernetes.create_from_secrets()

    def refresh_ingress(self, ingress):
        hosts = get_hosts_from_pykube_ingress(ingress)
        host_list = ", ".join(hosts)
        log.info("Found ingress object with hosts: " + host_list)
        secrets = self.kubernetes.fetch_secret_objects()
        log.info("Found {} secrets: {}".format(len(secrets), ",".join((s.name for s in secrets))))
        for s in secrets:
            log.info(pretty.format(s.obj))
        LetsEncrypt().renew_letsencrypt(host_list)

    def main(self):
        namespace = self.kubernetes.namespace
        logging.info("Letsencryptor running for namespace {}".format(namespace))

        cert = self.letsencrypt.get_cert()
        logging.info("Cert found: {}".format(cert))

        while (True):
            pykube_ingress = self.kubernetes.fetch_ingress_object()
            if pykube_ingress is not None:
                self.refresh_ingress(pykube_ingress)
            sleep(self.kubernetes_polling_delay)


if __name__ == "__main__":
    Letsencryptor().main()