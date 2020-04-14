#!/usr/bin/env bash

DIRECTORY=$(python -c 'import site; print(site.getsitepackages()[0])')/notebook/static/components

cp -a ./ipywidgets_extra/ipywidgets_extra_libs $DIRECTORY/
