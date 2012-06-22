"""
A quick example of uploading instances to a job with a multi-page document.
You will have to update the following constants for this to work on your box:
    API_TOKEN
    ENDPOINT
    IMAGE_PATH
    TARGET_JOB_ID
"""
import sys
import argparse

from client import Client

#------------UPDATE THE FOUR CONSTANTS BELOW

# Token for a user on your box
API_TOKEN = "1569df5c3d624054b8f3ba6b513f0bc3"

# API endpoint address
ENDPOINT = "http://localhost:8000/api/backbone/schema"

# Path to an image file
IMAGE_PATH = '/Users/nickj/Desktop/jalbert-page1.jpg'

# ID of a job of your user with at least on sheet
TARGET_JOB_ID = 2


def main():
    client = Client(api_token=API_TOKEN, endpoint=ENDPOINT)

    # Create a new instance set in the target job
    iset = client.create_instance_sets(TARGET_JOB_ID, {'name':'test_iset'})
    iset_id = iset['id']
    print 'Created InstanceSet %s in Job %s' % (iset_id, TARGET_JOB_ID)

    # Upload (the same) image for each page of the instance set
    for page_number in range(iset['sheet_count']):
        payload = {'image':open(IMAGE_PATH), 'image_name':'test_instance'}
        inst = client.create_iset_instance(iset_id, page_number, payload)
        print '\tUploaded Instance %s as page %s of InstanceSet %s' % (
                inst['id'],
                page_number,
                iset_id)


if __name__ == '__main__': main()
