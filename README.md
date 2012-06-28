# Captricity API Python Client

This is a Python client for the Captricity API

## Requirements

The Captricity Python client requires the <a href="http://simplejson.readthedocs.org/en/latest/index.html" target="_blank">```simplejson``` library</a>.  If you use the pip package manager, you can install the ```simplejson``` library as follows:

    pip install simplejson
    
Alternatively, you can <a href="https://github.com/simplejson/simplejson/zipball/master" target="_blank">download the source</a> or git clone it using the following command:

    git clone git://github.com/simplejson/simplejson.git
    
In the top level of the of the directoyr, run: 

    python setup.py install
    
You should be able to execute the following from the python interactive interpreter without error when the package is successfully installed:

    $ python
    >>> import simplejson
    >>>

## Pip Installation of the Captricity Python Client

If you use the pip package manager, the following will install the Captricity API Client:
    
    pip install https://github.com/Captricity/captools/tarball/master 

## Manual Installation of the Captricity Python Client

<a href="https://github.com/Captricity/captools/zipball/master" target="_blank">Download the zipped package</a> or clone the repository using git if you haven't done so already:

    git clone git@github.com:Captricity/captools.git

captools comes with a setup.py, which makes it easy to install into your python environment:
    
    cd captools
    python setup.py install

You should now be able to import captools.api in your python environment.

## Quickstart

Please see the <a href="https://shreddr.captricity.com/developer/quickstart/">Captricity API Quickstart guide</a> for a short hands-on introduction to using this client with the Captricity API.  

## Example Applications

Check out the <a href="https://github.com/Captricity/captricity-cloud-io">Captricity Cloud IO application</a> for an example of using this library in a webapp.

## License
This is licensed under the MIT license. See LICENSE.txt.
