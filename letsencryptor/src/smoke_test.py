from unittest import TestCase, main
from letsencryptor import LetsEncrypt

class SmokeTest(TestCase):
    """
    Verifies that the requirements to run letsencryptor are fulfilled.
    In particular, ensures that Python packages and the letsencrypt binary is available.
    """

    def test_letsencrypt_bin(self):
        """
        Tests will fail if letsencrypt binary is not available or not functional
        :return:
        """
        lets_encrypt = LetsEncrypt()
        lets_encrypt.get_version()

if __name__ == "__main__":
    main()