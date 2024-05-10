# -*- coding: utf-8 -*-

# Python 3

import time
import requests
from requests.compat import urljoin
import json

AIRTABLE_API_URL = "https://api.airtable.com/v0/"

# Utility function to create dictionary from airtable results
def keyed_result(json, key, result = None):

	# Only row row of data per key will be returned, so only unique key/value pairs!

	if result is None:
		result = {}

	for r in json["records"]:
		row = r["fields"]
		row['rec_id']=r['id']
		result[row[key]]=row

	return(result)



# Utility function to create dictionary from airtable results
def keyed_results(json, key, result = None):

        # supports a list of results for each key
        # used when a key is not unique

        if result is None:
                result = {}

        for r in json["records"]:
                row = r["fields"]
                row['rec_id']=r['id']
                if row[key] not in result:
                        result[row[key]]=[]
                result[row[key]].append(row)

        return result



# Class used to ensure we don't go over the rate limit with Airtable
class Throttle:

	def __init__(self, transactions, secs=1.0):
		self.max_transactions = transactions
		self.duration = secs
		self.queue = []
		self.tolerance = .1

	def next(self):
		waiting = True
		while waiting:
			self.queue = [recent for recent in self.queue if (recent+self.duration+self.tolerance) > time.monotonic()]
			if len(self.queue) < self.max_transactions:
				waiting = False
				self.queue.append(time.monotonic())
			else:
				oldest = self.queue[0]
				current = time.monotonic()
				elapsed = current - oldest
				pause = self.duration - elapsed + self.tolerance
				time.sleep(pause)

class UpdateBatch(object):
      
    def __init__(self):
          
        self.batches = []
        self.in_batch = 0
        self.total_batches = -1
        self.batch_count = 0
        self.records = 0

    def append(self, rec_id, field_data):
          
        if self.in_batch == 0 or self.in_batch == 10:
            self.batches.append({ 'records' : [] })
            self.in_batch = 0
            self.total_batches = self.total_batches + 1
            self.batch_count = self.batch_count + 1
        
        rec = {}

        rec['id'] = rec_id

        rec['fields'] = field_data

        self.batches[self.total_batches]['records'].append(rec)
        self.in_batch = self.in_batch + 1 
        self.records = self.records + 1


class AirtableConnection(object):
	
    def __init__(self, secret, base):
        self.api = AIRTABLE_API_URL
        self.base = base
        self.header = { 'Authorization' : f'Bearer {secret}'}
        self.limiter = Throttle(5,1.0) # Set Airtable rate limiter to 5 transactions per second max.


    def table_url(self, tablename):
        return f"{self.api}{self.base}/{tablename}"



    # Delete a bunch of rec-ids from Airtable base
    def delete(self, tablename, recid_list):

        # if the queue is empty we are done!

        if len(recid_list) < 1:
            return
	    
	    # deletes one records at a time, might not be optimal...

        for r in range(0, len(recid_list)):

            id = recid_list[r]
            delete_url = urljoin(self.table_url(tablename)+"/",id)
            self.limiter.next()
            response = requests.delete(delete_url, headers = self.header)
	    

    def update(self, tablename, rec_id, field_data):
        
        payload = { 'records' : [] }

        rec = {}

        rec['id'] = rec_id

        rec['fields'] = field_data

        payload['records'].append(rec)

        update_url = self.table_url(tablename)

        self.limiter.next()

        response = requests.patch(update_url, headers = self.header, json = payload)


    def updates(self, tablename : str, update_batch : UpdateBatch):

        for batch in update_batch.batches:
          
            update_url = self.table_url(tablename)

            self.limiter.next()

            response = requests.patch(update_url, headers = self.header, json = batch)


    def fetch(self, tablename, options = None):

        fetch_url = self.table_url(tablename)
        get_more  = True
        offset = None
        result = None

        while get_more:

            if offset is not None:
                if options is not None:
                    options['offset'] = offset
                else:
                    options = { 'offset' : offset }
                
            self.limiter.next()

            if options is not None:

                response = requests.get(
                    fetch_url,
                    headers = self.header,
                    params = options  
                )
            else:
                response = requests.get(
                    fetch_url,
                    headers = self.header
                )

            get_more = False

            data = response.json()

            if result is None:
                    result = data
            else:
                    result['records'] = result['records'] + data['records']                


            if "offset" in data:

                get_more = True
                offset = data['offset']

        return result
