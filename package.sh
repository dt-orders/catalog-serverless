#!/bin/bash
set -eo pipefail
rm -rf build-layers
mkdir build-layers
cd src
pip3 install --target ../build-layers/python -r requirements.txt
cd ../build-layers
zip -r -9 ../package/catalog-python-prereq.zip ./python/*
cd ../src/findByNameContains
zip -9 ../../package/findByNameContains.zip lambda_function.py
cd ../../src/ServerlessDBActions
zip -9 ../../package/ServerlessDBActions.zip lambda_function.py

