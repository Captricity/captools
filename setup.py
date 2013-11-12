#!/usr/bin/env python

from distutils.core import setup

LONG_DESCRIPTION = '''
Captricity API Python Client
----------------------------

This is a Python client for the Captricity API

Pip Installation of the Captricity Python Client
------------------------------------------------

If you use the pip package manager, the following will install the Captricity API Client:
    
    pip install captricity-python-client

Manual Installation of the Captricity Python Client
---------------------------------------------------

`Download the zipped package <https://github.com/Captricity/captools/zipball/master>` or clone the repository using git if you haven't done so already:

    git clone git@github.com:Captricity/captools.git

captools comes with a setup.py, which makes it easy to install into your python environment:
    
    cd captools
    python setup.py install

You should now be able to import captools.api in your python environment.

Quickstart
----------

Please see the `Captricity API Quickstart guide <https://shreddr.captricity.com/developer/quickstart/>` for a short hands-on introduction to using this client with the Captricity API.  

License
-------
This is licensed under the MIT license. See LICENSE.txt.'''

setup(name='captricity-python-client',
        version='0.19',
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
