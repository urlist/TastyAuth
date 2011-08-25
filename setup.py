#!/usr/bin/env python

from setuptools import setup

setup(
    name='TastyAuth',
    version='0.1.0',
    description='Extremely tasty social authentication, for Google, Twitter and Facebook.',
    author='Alberto Granzotto (vrde)',
    author_email='vrde@tastybrain.org',
    url='https://hg.tastybra.in/private/tastyauth',

    packages=['tastyauth'],

    install_requires=[
        'webob',
    ]
)

