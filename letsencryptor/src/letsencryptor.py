#!/usr/bin/python3

import time
import logging
import pretty
from letsencrypt_wrapper import LetsEncrypt
import kubernetes_wrapper as k8s

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
            self.kubernetes = k8s.Kubernetes.create_from_secrets()

    def refresh_ingress(self, ingress):
        hosts = k8s.get_hosts_from_pykube_ingress(ingress)
        host_list = ", ".join(hosts)
        log.info("Found ingress object with hosts {}. Running Let's Encrypt. ".format(host_list))
        LetsEncrypt().renew_letsencrypt(host_list)
        self._log_secrets()

    def main(self):

        namespace = self.kubernetes.namespace
        logging.info("Letsencryptor running for namespace {}".format(namespace))

        cert = self.letsencrypt.get_current_letsencrypt_entity("demo.cg.lg.ts.egym.coffee", "fullchain")
        logging.info("Cert found: {}".format(cert))

        while (True):
            pykube_ingress = self.kubernetes.fetch_ingress_object()
            if pykube_ingress is not None:
                self.refresh_ingress(pykube_ingress)
            time.sleep(self.kubernetes_polling_delay)

    def _create_test_secret(self):
        secret_obj = {}
        tag = _create_timestamp()
        k8s.set_name(secret_obj, k8s.SECRET_BASENAME + "-" + tag)
        k8s.set_label(secret_obj, k8s. SCERET_LABEL, tag)
        self.kubernetes.create_secret(secret_obj)

    def _log_secrets(self):
        secrets = self.kubernetes.fetch_secret_objects()
        for s in secrets:
            log.info(pretty.format(s.obj))
        log.info("Found {} secrets: {}".format(len(secrets), ",".join((s.name for s in secrets))))


def _create_timestamp():
    return time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())


if __name__ == "__main__":
    Letsencryptor().main()