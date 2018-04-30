import boto3
import json
import uuid

from pathlib import Path
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk

s3_client = boto3.client('s3')
print("STARTED")
def parse_lat_lon(r):
    if 'location' in r['peers'][0]:
        location = r['peers'][0]['location']
        if 'latitude' in location and 'longitude' in location:
            return {
                'lat': location['latitude'],
                'lon': location['longitude']
            }


def data_iterable(data_file):
    # for data_file in data_files:
    with open(data_file, 'r') as f:
        for line in f:
            r = json.loads(line)
            if r['type'] != 'resolve' or 'name' not in r:
                continue

            body = {
                'name': r['name'],
                'infohash': r['infohash'],
                'files': r['files'],
                'size': r['size']
            }
            if 'location' in r['peers'][0]:
                location = r['peers'][0]['location']
                body['subdivision'] = location.get('subdivision', None)
                body['city'] = location.get('city', None)
                body['country'] = location.get('country', None)
            loc = parse_lat_lon(r)
            if loc:
                body['location'] = loc
            yield {
                '_op_type': 'index',
                '_index': 'torrents',
                '_type': '_doc',
                '_id': r['infohash'],
                '_source': body
            }

def lambda_handler(event, context):
    for record in event["Records"]:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key'] 
        download_path = str(uuid.uuid4())
        s3_client.download_file(bucket, key, download_path)
        es = Elasticsearch()
        es.indices.delete(index='torrents', ignore=[404]) #pylint: disable=E1123

        es.indices.create(
            index='torrents',
            body=json.load(open('schema.json'))
        )
        
        for _, item in streaming_bulk(es, data_iterable(download_path), chunk_size=500, max_retries=2):
            print(item)

event = {  
   "Records":[  
      {  
         "s3":{  
            "bucket":{  
               "name":"boontorrent-kinesis",
            },
            "object":{  
               "key":"2018/04/09/21/boonlog-firehose-1-2018-04-09-21-00-40-8d3bf19a-daa0-4e2c-a34d-50a0a2860efa",
            }
         }
      }
   ]
}
lambda_handler(event, None)