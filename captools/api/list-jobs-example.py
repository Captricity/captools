"""
An example application which uses Captricity's python client to list all of an account's jobs.
"""
import sys
import argparse

from client import Client

def main():
    parser = argparse.ArgumentParser(description='List your Captricity jobs.')
    parser.add_argument('--endpoint', required=True, help='the URL to the API definition resource, like https://shreddr.captricity.com/api/backbone/schema')
    parser.add_argument('--apitoken', required=True, help='the api token associated with your Captricity account')
    args = parser.parse_args()

    client = Client(api_token=args.apitoken, endpoint=args.endpoint)
    jobs = client.read_jobs()
    for job in jobs:
        print job['name']
        print '\tstatus:', job['status']
        print '\t    id:', job['id']
if __name__ == '__main__': main()
