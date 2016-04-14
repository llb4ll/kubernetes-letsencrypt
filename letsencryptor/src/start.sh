#!/bin/sh

echo Starting letsencryptor
# Unbuffered mode to allow stdout loggind
PYTHONUNBUFFERED=0 python2 -u pykube_example.py
