import os
from unittest import TestCase, main
from letsencryptor import LetsEncrypt
from kubernetes_wrapper import SERVICE_ACCOUNT_PATH, NAMESPACE_FILE, TOKEN_FILE, Kubernetes

ENV_SERVICE_HOST = 'KUBERNETES_SERVICE_HOST'
ENV_SERVICE_PORT = 'KUBERNETES_SERVICE_PORT'


class SmokeTest(TestCase):
    """
    Verifies that the requirements to run letsencryptor are fulfilled.
    In particular, ensures that Python packages and the letsencrypt binary is available.
    """

    def test_letsencrypt_bin(self):
        """
        Tests will fail if letsencrypt binary is not available or not functional
        """
        lets_encrypt = LetsEncrypt()
        lets_encrypt.get_version()

    def test_kube_config(self):
        os.environ[ENV_SERVICE_HOST] = os.environ.get(ENV_SERVICE_HOST, "localhost")
        os.environ[ENV_SERVICE_PORT] = os.environ.get(ENV_SERVICE_HOST, "8888")
        os.makedirs(SERVICE_ACCOUNT_PATH)
        namespace = "test-namespace"
        token = "test-token"
        self.write_line_to_test_file(NAMESPACE_FILE, namespace)
        self.write_line_to_test_file(TOKEN_FILE, token)
        kubernetes = Kubernetes.create_from_secrets()
        self.assertEqual(kubernetes.namespace, namespace)
        # clean up
        os.remove(NAMESPACE_FILE)
        os.remove(TOKEN_FILE)

    def write_line_to_test_file(self, filename, content):
        if os.path.isfile(filename):
            raise RuntimeWarning("File {} exists, will not overwrite".format(filename))
        with open(filename, 'w') as f:
            f.writelines(content)


if __name__ == "__main__":
    main()