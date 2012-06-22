"""Tests for the python utilities for accessing the Captricity APIs"""

import random
import unittest
import urllib2
import simplejson as json

from client import Client, parse_date_string

TEST_API_KEY = '1234'

TEST_FORM_IMAGE_PATH= 'Example-Form-Page-1.png'

class TestClient(unittest.TestCase):

    def setUp(self):
        self.endpoint = 'http://127.0.0.1:8000/api/backbone/schema'
        self.schema = json.loads(urllib2.urlopen(self.endpoint).read())

    def test_client_connection(self):
        i = 0
        resource1 = self.schema['resources'][i]
        while not resource1['supported']:
            i += 1
            resource1 = self.schema['resources'][i]

        client = Client(api_token=TEST_API_KEY, endpoint=self.endpoint)
        self.assertEqual(client._generate_url('^/api/shreddr/job/(?P<id>[\d]+)$', [666]), '/api/shreddr/job/666')
        self.assertEqual(client._generate_url('^/api/shreddr/tinker/(?P<id>[\d]+)/(?P<donkey>[^/]+)/$', [666, 'poundcake']), '/api/shreddr/tinker/666/poundcake/')
        self.assertEqual(client._generate_url('^/(?P<id>[\d]+)/moon/(?P<donkey>[^/]+)$', [666, 'poundcake']), '/666/moon/poundcake')
        self.assertTrue(hasattr(client, 'read_' + resource1['name']))
        jobs = client.read_jobs()
        self.assertTrue(len(jobs) > 0)
        self.assertTrue(jobs[0])
        created = parse_date_string(jobs[0]['created'])
        self.assertTrue(created.year >= 2011)
        job = client.read_job(jobs[0]['id'])

        job = client.update_job(job['id'], {'name':'Fancy Job'})
        self.assertEqual(job['name'], 'Fancy Job')
        job = client.read_job(jobs[0]['id'])
        self.assertEqual(job['name'], 'Fancy Job')
        job = client.update_job(job['id'], {'name':'Schmancy Job'})
        self.assertEqual(job['name'], 'Schmancy Job')

        client2 = Client(api_token='bogus-api-key', endpoint=self.endpoint)
        with self.assertRaises(IOError): client2.read_jobs()

        job = client.read_jobs(params={'status':'setup'})[0]
        current_iset_count = job['instance_set_count']
        iset = client.create_instance_sets(job['id'], {'name':'test_iset'})
        for i in range(iset['sheet_count']):
            inst = client.create_iset_instance(iset['id'], i, {'image' : open(TEST_FORM_IMAGE_PATH)})
        job = client.read_job(job['id'])
        self.assertEqual(job['instance_set_count'], current_iset_count + 1)
        instance_set = client.read_instance_set(iset['id'])
        self.assertTrue(instance_set.get('created', None) != None, 'Instance set has no created attribute %s' % instance_set)
        self.assertEqual(len(client.read_incomplete_instance_sets(job['id'])), 0)

    def test_non_json_resource(self):
        client = Client(api_token=TEST_API_KEY, endpoint=self.endpoint)
        jobs = client.read_jobs()
        self.assertTrue(len(jobs) > 0)
        completed_jobs = [job for job in jobs if job['status'] == 'completed']
        if len(completed_jobs) == 0:
            print 'There are no completed jobs so I can not test data-sets.'
            return
        completed_job = completed_jobs[0]
        datasets = client.read_datasets(completed_job['id'])
        self.assertTrue(len(datasets) > 0)
        dataset = client.read_dataset(datasets[0]['id'], accept='text/csv')
        self.assertTrue(dataset)
        self.assertTrue(dataset.find('page1') != -1)

if __name__ == '__main__': unittest.main()
