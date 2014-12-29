"""
Utilites for accessing the Captricity APIs

NOTE: Methods which start with an underscore (_) are for internal use only and WILL change.
      Do not write your code against them.

"""
import new
import types
import random
import urllib
import httplib 
import urlparse
import traceback
import mimetypes
import json
from itertools import groupby
from hashlib import sha256
from urllib import urlencode
from datetime import datetime

API_TOKEN_HEADER_NAME = 'Captricity-API-Token'
API_VERSION_HEADER_NAME = 'Captricity-API-Version'
CLIENT_VERSION = '0.01'
USER_AGENT = 'Captricity Python Client %s' % CLIENT_VERSION

class Client(object):
    """
    A network client for the Captricity third-party API.
    This class will fetch the API description from the endpoint URL and dynamically create methods for accessing the API.
    So, once you instantiate the Client you will be able to call cliend.read_job() even though you won't see that method defined below.

    To see a list of all of the api related methods that this client offers, do the following:
    client = Client('your api token', 'http://host/api/backbone/schreddr')
    client.print_help()
    """
    def __init__(self, api_token, endpoint="https://shreddr.captricity.com/api/backbone/schema", version=None):
        """
        endpoint must be the full url to the API schema document, like `http://127.0.0.1:8000/api/backbone/schema'
        api_token is the unique string associated with your account's profile which allows API access
        """
        self.api_token = api_token
        self.endpoint = endpoint
        self.parsed_endpoint = urlparse.urlparse(self.endpoint)
        self.api_version = version 
        schema_url = self.parsed_endpoint.path
        if version: schema_url = schema_url + '?version=' + version
        self.schema = self._get_data(schema_url)
        self.api_version = self.schema['version']

        for resource in self.schema['resources']:
            if "GET" in resource['allowed_request_methods']:
                read_callable = _generate_read_callable(resource['name'], resource['display_name'], resource['arguments'], resource['regex'], resource['doc'], resource['supported'])
                setattr(self, read_callable.__name__, new.instancemethod(read_callable, self, self.__class__))
            if "PUT" in resource['allowed_request_methods']:
                update_callable = _generate_update_callable(resource['name'], resource['display_name'], resource['arguments'], resource['regex'], resource['doc'], resource['supported'], resource['put_syntaxes'])
                setattr(self, update_callable.__name__, new.instancemethod(update_callable, self, self.__class__))
            if "POST" in resource['allowed_request_methods']:
                create_callable = _generate_create_callable(resource['name'], resource['display_name'], resource['arguments'], resource['regex'], resource['doc'], resource['supported'], resource['post_syntaxes'], resource['is_action'])
                setattr(self, create_callable.__name__, new.instancemethod(create_callable, self, self.__class__))
            if "DELETE" in resource['allowed_request_methods']:
                delete_callable = _generate_delete_callable(resource['name'], resource['display_name'], resource['arguments'], resource['regex'], resource['doc'], resource['supported'])
                setattr(self, delete_callable.__name__, new.instancemethod(delete_callable, self, self.__class__))

    def print_help(self):
        """Prints the api method info to stdout for debugging."""
        keyfunc = lambda x: (x.resource_name, x.__doc__.strip())
        resources = groupby(sorted(filter(lambda x: (hasattr(x, 'is_api_call') and x.is_api_call and x.is_supported_api), [getattr(self, resource) for resource in dir(self)]), key=keyfunc), key=keyfunc)
        for resource_desc, resource_methods in resources:
            print resource_desc[0]
            print '\t', resource_desc[1]
            print
            print '\t', 'Available methods:'
            for r in resource_methods:
                method_header = r.__name__ + '('
                if r._get_args:
                    method_header += ','.join(r._get_args)
                if r._put_or_post_args:
                    put_or_post_args = [arg['name'] for arg in reduce(lambda x, y: x+y, r._put_or_post_args.values())]
                    method_header += ',{' +  ','.join(put_or_post_args) + '}'
                method_header += ')'
                method_desc = ""
                if r.__name__.startswith('create'):
                    method_desc = 'Corresponding API call: POST to ' + r._resource_uri
                if r.__name__.startswith('update'):
                    method_desc = 'Corresponding API call: PUT to ' + r._resource_uri
                if r.__name__.startswith('read'):
                    method_desc = 'Corresponding API call: GET to ' + r._resource_uri
                if r.__name__.startswith('delete'):
                    method_desc = 'Corresponding API call: DELETE to ' + r._resource_uri

                print '\t\t', method_header, ' - ', method_desc
            print

    def _construct_request(self):
        """
        Utility for constructing the request header and connection
        """
        if self.parsed_endpoint.scheme == 'https':
            conn = httplib.HTTPSConnection(self.parsed_endpoint.netloc)
        else:
            conn = httplib.HTTPConnection(self.parsed_endpoint.netloc)
        head = {
            "Accept" : "application/json",
            "User-Agent": USER_AGENT,
            API_TOKEN_HEADER_NAME: self.api_token,
        }
        if self.api_version in ['0.1', '0.01a']:
            head[API_VERSION_HEADER_NAME] = self.api_version
        return conn, head

    def _delete_resource(self, url):
        """
        DELETEs the resource at url
        """
        conn, head = self._construct_request()
        conn.request("DELETE", url, "", head)
        resp = conn.getresponse()
        self._handle_response_errors('DELETE', url, resp)

    def _get_data(self, url, accept=None):
        """
        GETs the resource at url and returns the raw response
        If the accept parameter is not None, the request passes is as the Accept header
        """
        if self.parsed_endpoint.scheme == 'https':
            conn = httplib.HTTPSConnection(self.parsed_endpoint.netloc)
        else:
            conn = httplib.HTTPConnection(self.parsed_endpoint.netloc)
        head = {
            "User-Agent": USER_AGENT,
            API_TOKEN_HEADER_NAME: self.api_token,
        }
        if self.api_version in ['0.1', '0.01a']:
            head[API_VERSION_HEADER_NAME] = self.api_version
        if accept: head['Accept'] = accept
        conn.request("GET", url, "", head)
        resp = conn.getresponse()
        self._handle_response_errors('GET', url, resp)
        content_type = resp.getheader('content-type')
        if 'application/json' in content_type:
            return json.loads(resp.read())
        return resp.read()

    def _put_or_post_multipart(self, method, url, data):
        """
        encodes the data as a multipart form and PUTs or POSTs to the url
        the response is parsed as JSON and the returns the resulting data structure
        """
        fields = []
        files = []
        for key, value in data.items():
            if type(value) == file:
                files.append((key, value.name, value.read()))
            else:
                fields.append((key, value))
        content_type, body = _encode_multipart_formdata(fields, files)
        if self.parsed_endpoint.scheme == 'https':
            h = httplib.HTTPS(self.parsed_endpoint.netloc)
        else:
            h = httplib.HTTP(self.parsed_endpoint.netloc)
        h.putrequest(method, url)
        h.putheader('Content-Type', content_type)
        h.putheader('Content-Length', str(len(body)))
        h.putheader('Accept', 'application/json')
        h.putheader('User-Agent', USER_AGENT)
        h.putheader(API_TOKEN_HEADER_NAME, self.api_token)
        if self.api_version in ['0.1', '0.01a']:
            h.putheader(API_VERSION_HEADER_NAME, self.api_version)
        h.endheaders()
        h.send(body)
        errcode, errmsg, headers = h.getreply()
        if errcode not in [200, 202]: raise IOError('Response to %s to URL %s was status code %s: %s' % (method, url, errcode, h.file.read()))
        return json.loads(h.file.read())

    def _put_or_post_json(self, method, url, data):
        """
        urlencodes the data and PUTs it to the url
        the response is parsed as JSON and the resulting data type is returned
        """
        if self.parsed_endpoint.scheme == 'https':
            conn = httplib.HTTPSConnection(self.parsed_endpoint.netloc)
        else:
            conn = httplib.HTTPConnection(self.parsed_endpoint.netloc)
        head = {
            "Content-Type" : "application/json",
            "Accept" : "application/json",
            "User-Agent": USER_AGENT,
            API_TOKEN_HEADER_NAME: self.api_token,
        }
        if self.api_version in ['0.1', '0.01a']:
            head[API_VERSION_HEADER_NAME] = self.api_version
        conn.request(method, url, json.dumps(data), head)
        resp = conn.getresponse()
        self._handle_response_errors(method, url, resp)
        return json.loads(resp.read())

    def _generate_url(self, regex, arguments):
        """
        Uses the regex (of the type defined in Django's url patterns) and the arguments to return a relative URL
        For example, if the regex is '^/api/shreddr/job/(?P<id>[\d]+)$' and arguments is ['23'] then return would be '/api/shreddr/job/23'
        """
        regex_tokens = _split_regex(regex)
        result = ''
        for i in range(len(arguments)):
            result = result + str(regex_tokens[i]) + str(arguments[i])
        if len(regex_tokens) > len(arguments): result += regex_tokens[-1]
        return result
        #return '%s://%s/%s' % (self.parsed_endpoint.scheme, self.parsed_endpoint.netloc, result)

    def _handle_response_errors(self, method, url, response):
        if response.status in [200, 202]:
            return
        raise IOError('Response to %s to URL %s was status code %s: %s' % (
                       method, url, response.status, response.read()))

    def read_example_job(self):
        '''
        Convenience method for pulling out the example job.  Used in the
        Captricity API Quickstart.
        '''
        for job in self.read_jobs():
            if job['is_example']:
                return job

    def launch_job(self, job_id):
        '''
        Convenience method for launching a job.  We use POST for actions
        outside of HTTP verbs (job launch in this case).
        '''
        assert self.api_version.lower() in ['0.01a', '0.1'], 'This method is only supported in BETA (0.01) and ALPHA (0.01a) versions'
        try:
            self.create_job(job_id, {'submit_job_action':True})
        except ValueError:
            pass
        return self.read_job(job_id)

def parse_date_string(date_string):
    """Converts the date strings created by the API (e.g. '2012-04-06T19:11:33.032') and returns an equivalent datetime instance."""
    return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f")


def _encode_multipart_formdata(fields, files):
    """
    Create a multipart encoded form for use in PUTing and POSTing.

    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------A_vEry_UnlikelY_bouNdary_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append(str('Content-Disposition: form-data; name="%s"' % key))
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append(str('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename)))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    """Use the python mimetypes to determine a mime type, or return application/octet-stream"""
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

def _generate_read_callable(name, display_name, arguments, regex, doc, supported):
    """Returns a callable which conjures the URL for the resource and GETs a response"""
    def f(self, *args, **kwargs):
        url = self._generate_url(regex, args)
        if 'params' in kwargs: url += "?" + urllib.urlencode(kwargs['params'])
        return self._get_data(url, accept=(kwargs.get('accept')))
    f.__name__ = str('read_%s' % name)
    f.__doc__ = doc
    f._resource_uri = regex
    f._get_args = arguments
    f._put_or_post_args = None 
    f.resource_name = display_name
    f.is_api_call = True
    f.is_supported_api = supported
    return f

def _generate_update_callable(name, display_name, arguments, regex, doc, supported, put_arguments):
    """Returns a callable which conjures the URL for the resource and PUTs data"""
    def f(self, *args, **kwargs):
        for key, value in args[-1].items():
            if type(value) == file:
                return self._put_or_post_multipart('PUT', self._generate_url(regex, args[:-1]), args[-1])
        return self._put_or_post_json('PUT', self._generate_url(regex, args[:-1]), args[-1])
    f.__name__ = str('update_%s' % name)
    f.__doc__ = doc
    f._resource_uri = regex
    f._get_args = arguments
    f._put_or_post_args = put_arguments
    f.resource_name = display_name
    f.is_api_call = True
    f.is_supported_api = supported
    return f

def _generate_create_callable(name, display_name, arguments, regex, doc, supported, post_arguments, is_action):
    """Returns a callable which conjures the URL for the resource and POSTs data"""
    def f(self, *args, **kwargs):
        for key, value in args[-1].items():
            if type(value) == file:
                return self._put_or_post_multipart('POST', self._generate_url(regex, args[:-1]), args[-1])
        return self._put_or_post_json('POST', self._generate_url(regex, args[:-1]), args[-1])
    if is_action:
        f.__name__ = str(name)
    else:
        f.__name__ = str('create_%s' % name)
    f.__doc__ = doc
    f._resource_uri = regex
    f._get_args = arguments
    f._put_or_post_args = post_arguments
    f.resource_name = display_name
    f.is_api_call = True
    f.is_supported_api = supported
    return f

def _generate_delete_callable(name, display_name, arguments, regex, doc, supported):
    def f(self, *args, **kwargs):
        return self._delete_resource(self._generate_url(regex, args))
    f.__name__ = str('delete_%s' % name)
    f.__doc__ = doc
    f._resource_uri = regex
    f._get_args = arguments
    f._put_or_post_args = None
    f.resource_name = display_name
    f.is_api_call = True
    f.is_supported_api = supported
    return f

def _split_regex(regex):
    """
    Return an array of the URL split at each regex match like (?P<id>[\d]+)
    Call with a regex of '^/foo/(?P<id>[\d]+)/bar/$' and you will receive ['/foo/', '/bar/']
    """
    if regex[0] == '^': regex = regex[1:]
    if regex[-1] == '$': regex = regex[0:-1]
    results = []
    line = ''
    for c in regex:
        if c == '(':
            results.append(line)
            line = ''
        elif c == ')':
            line = ''
        else:
            line = line + c
    if len(line) > 0: results.append(line)
    return results
