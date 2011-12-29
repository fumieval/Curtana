#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="Curtana",
    version="0.1.0",
    description="Twitter Client for Chosen One",
    license="BSD",
    keywords="Twitter",
    url="http://botis.org/wiki/Curtana",
    packages=find_packages(),
    install_requires = ["oauth2>=1.5", "tweepy>=1.7"],
    include_package_data=True,
)