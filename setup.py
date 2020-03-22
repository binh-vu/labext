import os
import shutil
import sys
import urllib.request
from setuptools import setup, find_packages


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

setup(name="ipywidgets_extra",
      version='1.0.0',
      packages=find_packages(),
      description="Extra widgets for Jupyter Lab",
      long_description=long_description,
      long_description_content_type='text/markdown',
      author="Binh Vu",
      author_email="binh@toan2.com",
      url="https://github.com/binh-vu/ipywidgets_extra",
      python_requires='>3.6',
      license="MIT",
      install_requires=['ujson', 'IPython'],
      package_data={'': ['*.so', '*.pyd']})
