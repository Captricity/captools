"""
An example application which uses Captricity's python client to upload images to a job.
"""
import sys
import argparse
import math

from client import Client

def main():
    parser = argparse.ArgumentParser(description='List your Captricity jobs.')
    parser.add_argument('--endpoint', required=True, help='the URL to the API definition resource, like https://shreddr.captricity.com/api/backbone/schema')
    parser.add_argument('--apitoken', required=True, help='the api token associated with your Captricity account')
    parser.add_argument('--job', required=True, type=int, help='the ID number for the job resource')
    parser.add_argument('image', type=file, nargs='+', help='image files which you would like to upload')

    args = parser.parse_args()

    # Creating the client will fetch the API descriptor and set up the api methods
    client = Client(api_token=args.apitoken, endpoint=args.endpoint)

    # Fetch the job to make sure that it exists and to get its display name
    job = client.read_job(args.job)
    print 'Uploading images to job "%s"' % job['name']

    # We need to group the instance images into instance sets. To do so, we need to find the page count of the form that is used for the job
    # We take advantage of the fact that the job's document resource metadata is included in the metadata for the job
    page_count = job['document']['sheet_count']

    # Once we know the page count, we will process the image list in batches, grouping them into image sets
    # Note that we assume the images were provided in the correct order
    for i in range(int(math.ceil(len(args.image) / float(page_count)))):
        # For each group of images in an image set, we create the instance set on the captricity server first.
        # We will also name the image sets by the first image in the set
        # Also store the new instance set so we know which one to post images to
        iset = client.create_instance_sets(job['id'], {'name': args.image[i].name})
        print 'Uploading image set', i
        # We will then upload each image to the image set in order until the image set is full
        for page_number, image in enumerate(args.image[i*page_count:(i*page_count)+page_count]):
            print '\t', image.name
            client.create_iset_instance(iset['id'], page_number, {'image' : image, 'image_name' : image.name})

if __name__ == '__main__': main()
