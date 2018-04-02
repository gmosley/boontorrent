import json
from pathlib import Path
from elasticsearch import Elasticsearch

data_path = Path('2018/03/22')
data_files = [x for x in data_path.glob('**/*') if x.is_file()]

es = Elasticsearch()

es.indices.delete(index='torrents', ignore=[404])

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

for data_file in data_files:
    print(data_file)
    with open(data_file, 'r') as f:
        for line in f:
            r = json.loads(line)
            if r['type'] == 'resolve' and 'name' in r:
                body = {
                    'name': r['name'],
                    'infohash': r['infohash'],
                    'files': r['files'],
                    'size': r['size']
                }
                loc = parse_lat_lon(r)
                if loc:
                    body['location'] = loc

                es.index(index='torrents', doc_type='_doc', id=r['infohash'], body=body)