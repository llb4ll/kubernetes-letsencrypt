import letsencryptor
from kubernetes_fake import Kubernetes
from letsencrypt_fake import Letsencrypt
from unittest import TestCase, main


class LetsencryptorTest(TestCase):
    def setUp(self):
        self.letsencrypt = Letsencrypt()
        self.kubernetes = Kubernetes()
        self.letsencryptor = letsencryptor.Letsencryptor(kubernetes=self.kubernetes, letsencrypt=self.letsencrypt)

    def testFoo(self):
        self.letsencryptor.main()


if __name__ == "__main__":
    main()