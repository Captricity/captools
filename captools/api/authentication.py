"""
A simple utility for obtaining an API token from Captricity to use with the Captricity python client.

Assumes that you already registered an application on Captricity.

Note that this requires interaction with a web browser.
See https://shreddr.captricity.com/developer/#authentication for more information on how users are authenticated for the Captricity API.
"""
import argparse
import webbrowser
import urllib
import urlparse
import BaseHTTPServer
import SocketServer
import re

from util import generate_request_access_signature

API_TOKEN = ""

class CallbackHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        global API_TOKEN
        parsed_query = urlparse.parse_qs(re.sub(r'^/\?', '', self.path))
        if 'request-granted' in parsed_query:
            API_TOKEN = parsed_query['token'][0]
            body = "Request granted: Your API token is %s" % API_TOKEN
        else:
            body = "Request denied: could not obtain API token. Did you click 'Deny Access' when prompted to grant access?"
        self.send_response(200, 'OK')
        self.send_header('Content-type', 'html')
        self.end_headers()
        self.wfile.write("<html><head><title>Captricity API Token</title></head><body>%s</body></html>" % body)

def main():
    parser = argparse.ArgumentParser(description='Authenticate user and obtain an API token to access the Captricity API. Assumes that you have already registered an application on Captricity.\nSee https://shreddr.captricity.com/developer/#register for more info.')
    parser.add_argument('--endpoint', required=True, help='The URL to the API server you are accessing, like https://shreddr.captricity.com')
    parser.add_argument('--client-id', required=True, help='Client ID for a registered third party application on Captricity.')
    parser.add_argument('--client-secret-key', required=True, help='Client Secret Key for a registered third party application on Captricity.')
    parser.add_argument('--port', default=8765, help='Port number for listening to the callback request')
    args = parser.parse_args()

    # Generate login url, with callback as localhost with specified port number (default 8765)
    login_url = args.endpoint + "/accounts/request-access/"
    callback_url = "http://localhost:" + str(args.port)
    params = {
            'return-url' : callback_url,
            'third-party-id' : args.client_id
    }
    params['signature'] = generate_request_access_signature(params, args.client_secret_key)
    login_url += '?' + urllib.urlencode(params)

    webbrowser.open(login_url)

    SocketServer.TCPServer(('', int(args.port)), CallbackHandler).handle_request()

    print 'Your API token is:', API_TOKEN

if __name__ == '__main__': main()


