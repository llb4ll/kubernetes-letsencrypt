import subprocess

LETSENCRYPT_PORT = 8080
DEFAULT_EMAIL = "letsencyptor@example.net"


class LetsEncrypt(object):
    def __init__(self, email=DEFAULT_EMAIL, port=LETSENCRYPT_PORT):
        self.letsencrypt_bin = "letsencrypt"
        self.email = email
        self.port = port

    def renew_letsencrypt(self, host_list):
        subprocess.call([
            self.letsencrypt_bin,
            "certonly",
            "--non-interactive",
            "--agree-tos",
            "--email={}".format(self.email),
            "--standalone",
            "--standalone-supported-challenges=http-01",
            "--http-01-port=" + str(self.port),
            "--rsa-key-size=2048",
            "--keep-until-expiring",
            "--domains={}".format(host_list),
            "--test-cert"
        ])

    def get_version(self):
        subprocess.call([
            self.letsencrypt_bin,
            "--version"
        ])

if __name__ == "__main__":
    LetsEncrypt().get_version();