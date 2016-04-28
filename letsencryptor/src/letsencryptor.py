#!/usr/bin/python3

import time
import logging
import pretty
from letsencrypt_wrapper import LetsEncrypt
import kubernetes_wrapper as k8s

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("letsencryptor")

SECRET_DATA_CERT_PEM = "tls.crt"
SECRET_DATA_KEY_PEM = "tls.key"

class Letsencryptor(object):
    kubernetes_polling_delay = 30

    def __init__(self, letsencrypt=None, kubernetes=None):
        self.letsencrypt = letsencrypt
        if self.letsencrypt is None:
            self.letsencrypt = LetsEncrypt()
        self.kubernetes = kubernetes
        if self.kubernetes is None:
            self.kubernetes = k8s.Kubernetes.create_from_secrets()

    def refresh_cert(self):
        """
        Parses the ingress object retrieved from the k8s api. Calls letsencrypt to renew the the certificate if required.
        Updates ingress object if letsencrypted generated a new cert.
        """
        pykube_ingress = self.kubernetes.fetch_pykube_ingress()
        if not pykube_ingress:
            # No matching ingress object found. Error has already been logged. Nothing else to do.
            return
        hosts = k8s.get_hosts_from_pykube_ingress(pykube_ingress)
        host_list = ", ".join(hosts)
        if not host_list:
            log.info("Empty host_list. Nothing to do.")
            return
        log.info("Found ingress object with hosts {}. Running Let's Encrypt. ".format(host_list))
        cert_pem, key_pem = self.run_letsencrypt(host_list)
        if not cert_pem or not key_pem:
            log.warn("Can't find certificate created by Let's Encrypt.")
            return
        self.update_ingress(pykube_ingress, cert_pem, key_pem)

    def run_letsencrypt(self, host_list):
        self.letsencrypt.renew_letsencrypt(host_list)
        cert_pem = self.letsencrypt.get_current_fullchain_cert(host_list)
        key_pem = self.letsencrypt.get_current_private_key(host_list)
        return cert_pem, key_pem

    def main(self):

        namespace = self.kubernetes.namespace
        logging.info("Letsencryptor running for namespace {}".format(namespace))

        while (True):
            self.refresh_cert()
            time.sleep(self.kubernetes_polling_delay)

    def _set_secret_name_and_tag(self, secret_obj):
        tag = _create_timestamp()
        secret_name = k8s.set_name(secret_obj, k8s.SECRET_BASENAME + "-" + tag)
        k8s.set_label(secret_obj, k8s.SECRET_LABEL, tag)
        log.info("Creating secret {} with label {}={}".format(secret_name, k8s.SECRET_LABEL, tag))
        return secret_name

    def _log_secrets(self):
        secrets = self.kubernetes.fetch_pykube_secrets()
        for s in secrets:
            log.info(pretty.format(s.obj))
        log.info("Found {} secrets: {}".format(len(secrets), ",".join((s.name for s in secrets))))

    def update_ingress(self, pykube_ingress, cert_pem, key_pem):
        new_secret = {}
        k8s.set_data(new_secret, SECRET_DATA_CERT_PEM, cert_pem)
        k8s.set_data(new_secret, SECRET_DATA_KEY_PEM, key_pem)
        old_secret = k8s.unwrap(self.kubernetes.fetch_pykube_secret_from_pykube_ingress(pykube_ingress))
        if k8s.compare_data(new_secret, old_secret, SECRET_DATA_CERT_PEM) and k8s.compare_data(new_secret, old_secret, SECRET_DATA_KEY_PEM):
            log.info("Found existing secret {}. TLS Data matches. No update required.".format(k8s.get_name(old_secret)))
        else:
            secret_name = self._set_secret_name_and_tag(new_secret)
            self.kubernetes.create_secret(new_secret)
            k8s.set_tls_secret_name(k8s.unwrap(pykube_ingress), secret_name)
            pykube_ingress.update()
            log.info("Updated ingress object {} with secret {}".format(pykube_ingress.name, secret_name))


def _create_timestamp():
    return time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())


if __name__ == "__main__":
    Letsencryptor().main()