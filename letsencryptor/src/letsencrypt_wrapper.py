import subprocess
import logging

LETSENCRYPT_PORT = 8080
DEFAULT_EMAIL = "letsencyptor@example.net"


class LetsEncrypt(object):
    def __init__(self, email=DEFAULT_EMAIL, port=LETSENCRYPT_PORT):
        self.letsencrypt_bin = "letsencrypt"
        self.email = email
        self.port = port

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
        file_name='/etc/letsencrypt/live/{}/{}.pem'.format(host_name, entity)
        try:
            with open(file_name, 'r') as file:
                file_content = file.read()
                file.close()
                return file_content
        except IOError:
            logging.warn("File {} could not be opened.".format(file_name))
        else:
            logging.warn("Unexpectad error when trying to read file.")
        return


if __name__ == "__main__":
    LetsEncrypt().get_version();
