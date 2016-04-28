import subprocess
import logging

DATA_PATH = '/etc/letsencrypt/live'
LETSENCRYPT_PORT = 8080
DEFAULT_EMAIL = "letsencyptor@example.net"
FULLCHAIN = "fullchain"
PRIVKEY = "privkey"

class LetsEncrypt(object):
    def __init__(self, email=DEFAULT_EMAIL, port=LETSENCRYPT_PORT, data_path=DATA_PATH):
        self.letsencrypt_bin = "letsencrypt"
        self.email = email
        self.port = port
        self.data_path = data_path

    def renew_letsencrypt(self, host_list):
        logging.info("Calling letsencrypt for hosts {} trying challenge at port {} with notification email {}.".format(host_list, self.port, self.email))
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

    def get_current_letsencrypt_entity(self, host_name, entity):
        file_name = self._get_filename(host_name, entity)
        try:
            with open(file_name, 'r') as file:
                return file.read()
        except IOError:
            logging.warn("File {} could not be opened.".format(file_name))
        else:
            logging.warn("Unexpected error when trying to read file.")
        return

    def _get_filename(self, host_name, entity):
        return '{}/{}/{}.pem'.format(self.data_path, host_name, entity)

    def get_current_fullchain_cert(self, host_list):
        return self.get_current_letsencrypt_entity(host_list, FULLCHAIN)

    def get_current_private_key(self, host_list):
        return self.get_current_letsencrypt_entity(host_list, PRIVKEY)


if __name__ == "__main__":
    LetsEncrypt().get_version()
