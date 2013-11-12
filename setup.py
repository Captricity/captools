#!/usr/bin/env python

from distutils.core import setup

LONG_DESCRIPTION = open('README.md', 'r').read()

setup(name='captricity-python-client',
        version='0.18',
        description='Python client to access Captricity API',
        url='https://github.com/Captricity/captools',
        author='Captricity, Inc',
        author_email='support@captricity.com',
        classifiers=[
            "Programming Language :: Python",
            "License :: OSI Approved :: MIT License",
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
        ],
        long_description = LONG_DESCRIPTION,
        packages=['captools', 'captools.api'],
        package_data={'captools.api': ['img/*.png']})
