FROM ubuntu:15.10

RUN apt-get -y update && apt-get install -y python3-pip python-pip
RUN pip3 install pykube
RUN pip2 install letsencrypt

ADD pykube_example.py /pykube_example.py
ADD start.sh /start.sh

ENTRYPOINT ["/start.sh"]
