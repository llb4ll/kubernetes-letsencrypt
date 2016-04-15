FROM debian:jessie-backports

RUN apt-get update && apt-get install -y -t jessie-backports --no-install-recommends bash letsencrypt openssl python-pip

RUN pip install pykube

ADD *.py /

ENV PYKUBE_KUBERNETES_SERVICE_HOST=kubernetes.default.svc.cluster.local
RUN ["python", "-u", "/smoke_test.py"]
EXPOSE 8080
ENTRYPOINT ["python", "-u", "/letsencryptor.py"]
