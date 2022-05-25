#!/bin/sh
docker run --rm \
    -v /"$PWD"://var/task \
    lambci/lambda:build-python3.8 \
    bash -c "\
    mkdir -p site-packages && \
    pip install -r requirements.txt -t site-packages && \
    echo 'pip install completed!!'
    "
