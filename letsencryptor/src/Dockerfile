FROM debian:jessie-backports

RUN apt-get update && apt-get install -y -t jessie-backports --no-install-recommends bash letsencrypt openssl python-pip

RUN pip install pykube

ADD pykube_example.py /pykube_example.py

ENTRYPOINT ["python", "-u", "/pykube_example.py"]
