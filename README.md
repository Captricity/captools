# THIS MODULE HAS BEEN DEPRECATED

The Captricity API Python Client is deprecated due to the proliferation of good
API Client builders (e.g [`slumber`](https://github.com/samgiles/slumber)) and
great REST client libraries (e.g [`requests`](https://github.com/requests/requests))
that make an official client library unnecessary for most cases.

Note that although this module is officially deprecated, the functionality will be supported
for as long as Captricity supports the v1 API. However, Captricity has no intention
of supporting `captools` beyond the v1 API.


# Captricity API Python Client

This is a Python client for the Captricity API

## Pip Installation of the Captricity Python Client

If you use the pip package manager, the following will install the Captricity API Client:
    
    pip install captricity-python-client

## Manual Installation of the Captricity Python Client

<a href="https://github.com/Captricity/captools/zipball/master" target="_blank">Download the zipped package</a> or clone the repository using git if you haven't done so already:

    git clone git@github.com:Captricity/captools.git

captools comes with a setup.py, which makes it easy to install into your python environment:
    
    cd captools
    python setup.py install

You should now be able to import captools.api in your python environment.

## Quickstart

Please see the <a href="https://shreddr.captricity.com/developer/quickstart/">Captricity API Quickstart guide</a> for a short hands-on introduction to using this client with the Captricity API.  

## License
This is licensed under the MIT license. See LICENSE.txt.
