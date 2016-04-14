FROM python:3

RUN pip install pykube
ADD pykube_example.py /pykube_example.py
ADD start.sh /start.sh

ENTRYPOINT ["/start.sh"]
