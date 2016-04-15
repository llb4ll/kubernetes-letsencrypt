import subprocess

class LetsEncrypt(object):
    def __init__(self):
        self.letsencrypt_bin = "letsencrypt"

    def renew_letsencrypt(self, host_list):
        subprocess.call([
            self.letsencrypt_bin,
            "certonly",
            "--non-interactive",
            "--agree-tos",
            "--email=\"{}\".format(EMAIL)",
            "--standalone",
            "--standalone-supported-challenges=http-01",
            "--rsa-key-size=2048",
            "--keep-until-expiring",
            "--domains=\"{}\"".format(host_list),
            "--test-cert"
        ])

    def get_version(self):
        subprocess.call([
            self.letsencrypt_bin,
            "--version"
        ])

    def get_cert(self):
        file = open('/etc/letsencrypt/live/fullchain.pem', 'r')
        return file.read()
        file.close()

    def get_key(self):
        file = open('/etc/letsencrypt/live/privkey.pem', 'r')
        return file.read()
        file.close()


if __name__ == "__main__":
    LetsEncrypt().get_version();
