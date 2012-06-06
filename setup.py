#!/usr/bin/env python

from setuptools import setup

setup(
    name='TastyAuth',
    version='0.1.0',
    description='Extremely tasty social authentication, for Google, Twitter and Facebook.',
    author='Alberto Granzotto (vrde)',
    author_email='agranzot@gmail.com',
    url='https://github.com/vrde/TastyAuth',

    packages=[
        'tastyauth',
        'tastyauth.tornado',
    ],

    install_requires=[
        'webob',
    ],
)

