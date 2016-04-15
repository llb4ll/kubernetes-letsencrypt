FROM debian:jessie-backports

RUN apt-get update && apt-get install -y -t jessie-backports --no-install-recommends bash letsencrypt openssl python-pip

RUN pip install pykube

ADD *.py /

RUN ["python", "-u", "/smoke_test.py"]
ENTRYPOINT ["python", "-u", "/letsencryptor.py"]
