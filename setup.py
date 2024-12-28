import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="portfolio",
    version="0.0.1",
    author="Nicholas Etuk",
    author_email="nick_etuk@hotmail.com",
    description=("Portfolio tracker for crypto assets"),
    license="",
    keywords="crypto portfolio",
    url="http://asterlan.com",
    # packages=find_packages(","),
    packages=["portfolio"],
    long_description=read("README.md"),
    classifiers=[],
)
