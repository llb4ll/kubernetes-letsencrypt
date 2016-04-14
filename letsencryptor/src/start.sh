#!/bin/sh

echo Starting letsencryptor
# Unbuffered mode to allow stdout loggind
python3 -u pykube_example.py
