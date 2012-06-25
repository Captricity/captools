import urllib
import webbrowser
import urlparse
import BaseHTTPServer
import SocketServer
import re

from util import generate_request_access_signature


_API_TOKEN = ""

class CallbackHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        global _API_TOKEN
        parsed_query = urlparse.parse_qs(re.sub(r'^/\?', '', self.path))
        if 'request-granted' in parsed_query:
            _API_TOKEN = parsed_query['token'][0]
            body = "Request granted: Your API token is %s" % _API_TOKEN
        else:
            body = "Request denied: could not obtain API token. Did you click 'Deny Access' when prompted to grant access?"
        self.send_response(200, 'OK')
        self.send_header('Content-type', 'html')
        self.end_headers()
        self.wfile.write("<html><head><title>Captricity API Token</title></head><body>%s</body></html>" % body)

class ThirdPartyApplication(object):
    def __init__(self, third_party_id, secret_key, endpoint='https://shreddr.captricity.com', port=None):
        self.third_party_id = third_party_id
        self.secret_key = secret_key
        self.endpoint = endpoint
        self.port = 0 if port is None else port

    def get_account_access_request_url(self, return_url):
        login_url = self.endpoint + '/accounts/request-access/'
        params = {
                'return-url': return_url,
                'third-party-id': self.third_party_id,
        }
        params['signature'] = generate_request_access_signature(
                params, 
                self.secret_key)
        login_url += '?' + urllib.urlencode(params)
        return login_url

    def manually_authorize_application(self):
        # First find out what port is free, in case we are letting the os choose port (self.port = 0)
        server = SocketServer.TCPServer(('', self.port), CallbackHandler)
        selected_port = server.server_address[1]

        callback_url = "http://localhost:" + str(selected_port)
        login_url = self.get_account_access_request_url(callback_url)

        webbrowser.open(login_url)

        server.handle_request()

        return _API_TOKEN
 
