#!/usr/bin/env python
# -*-coding:utf8-*-

from setuptools import setup
import ovalparser

setup(
    name="ovalparser",
    version=ovalparser.version,
    packages=['ovalparser', 'ovalparser/object_parser', 'ovalparser/state_parser', 'ovalparser/utils'],
    install_requires=['lxml'],

    author="axtx",
    author_email="security@bjca.org.cn",
    description="This is ovalparser Package",
    license='AXTX 2015, All Rights Reserved',
    keywords="oval",
)