import boto3
import json
import uuid
import io

from pathlib import Path
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk

s3_client = boto3.client('s3')
def parse_lat_lon(r):
    if 'location' in r['peers'][0]:
        location = r['peers'][0]['location']
        if 'latitude' in location and 'longitude' in location:
            return {
                'lat': location['latitude'],
                'lon': location['longitude']
            }


def data_iterable(file_obj):
    # for data_file in data_files:
    for line in file_obj:
        r = json.loads(line)
        if r['type'] != 'resolve' or 'name' not in r:
            continue

        body = {
            'name': r['name'],
            'infohash': r['infohash'],
            'files': r['files'],
            'size': r['size'],
            'timestamp': r['timestamp']
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
        file_obj = io.BytesIO()
        s3_client.download_fileobj(bucket, key, file_obj)
        file_obj.seek(0)
        es = Elasticsearch(['https://vpc-boontorrent-giarxt7zrugwle2okjyqc67b6m.us-east-1.es.amazonaws.com'])
        successes = 0
        falures = 0
        s3_client.upload_fileobj(io.BytesIO(key.encode()), "boontorrent-dump", "latest.txt", ExtraArgs={'ACL': 'public-read'})
        for success, _ in streaming_bulk(es, data_iterable(file_obj), chunk_size=500, max_retries=2):
            if success:
                successes += 1
            else:
                falures += 1

        return successes, falures


# event = {
#    "Records":[  
#       {  
#          "s3":{  
#             "bucket":{  
#                "name":"boontorrent-kinesis",
#             },
#             "object":{  
#                "key":"2018/04/09/21/boonlog-firehose-1-2018-04-09-21-00-40-8d3bf19a-daa0-4e2c-a34d-50a0a2860efa",
#             }
#          }
#       }
#    ]
# }
# lambda_handler(event, None)