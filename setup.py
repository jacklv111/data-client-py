# coding: utf-8

"""
    data client 

"""

import configparser

from setuptools import find_packages, setup

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

def __get_install_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        reqs = [x.strip() for x in f.read().splitlines()]
    reqs = [x for x in reqs if not x.startswith("#")]
    return reqs

config = configparser.ConfigParser()
config.read('setup.cfg')

setup(
    name=config['metadata']['name'],
    version=config['metadata']['version'],
    description="data client",
    author_email="",
    url="",
    data_files=[
        ("data_client/utils/config/config_file", ["data_client/utils/config/config_file/config.ini"]),
        ("requirements", ["requirements.txt"]),
        ('setup.cfg', ['setup.cfg'])
    ],
    keywords=["data client"],
    install_requires=__get_install_requirements(),
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'aifsctl = data_client.cli.main:aifsctl',
        ],
    },
    long_description="""\
    data client # noqa: E501
    """
)
