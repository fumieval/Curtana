#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="Curtana",
    version="0.2.1",
    description="Twitter Client for Chosen One",
    license="BSD",
    keywords="Twitter",
    url="http://botis.org/wiki/Curtana",
    packages=find_packages(),
    install_requires = ["oauth2>=1.5", "twython>=1.4", "readline>=6"],
    include_package_data=True,
)
