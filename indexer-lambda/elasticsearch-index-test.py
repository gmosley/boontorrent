import json
from pathlib import Path
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk


data_path = Path('2018')
data_files = (x for x in data_path.glob('**/*') if x.is_file())

es = Elasticsearch()

es.indices.delete(index='torrents', ignore=[404]) #pylint: disable=E1123

es.indices.create(
    index='torrents',
    body=json.load(open('schema.json'))
)

def parse_lat_lon(r):
    if 'location' in r['peers'][0]:
        location = r['peers'][0]['location']
        if 'latitude' in location and 'longitude' in location:
            return {
                'lat': location['latitude'],
                'lon': location['longitude']
            }


def data_iterable():
    for data_file in data_files:
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

failed = 0
success = 0

for ok, item in streaming_bulk(es, data_iterable(), chunk_size=500, max_retries=2):
    # go through request-reponse pairs and detect failures
    if not ok:
        failed += 1
    else:
        success += 1

print("DONE")
print("failed", failed)
print("success", success)