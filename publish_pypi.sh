#!/bin/bash

set -e

rm -rf ./dist || echo "No previous build"
python setup.py sdist
twine upload -u $PYPI_TOKEN -p $PYPI_PWD --skip-existing dist/*
