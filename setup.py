#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="Curtana",
    version="0.3.0",
    description="Twitter Client for Chosen One",
    license="BSD",
    keywords="Twitter",
    url="http://botis.org/Curtana",
    packages=find_packages(),
    install_requires = ["oauth2>=1.5", "twython>=2.0", "readline>=6"],
    include_package_data=True,
)
