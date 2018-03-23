import json
from pathlib import Path
from elasticsearch import Elasticsearch

data_path = Path('2018/03/22')
data_files = [x for x in data_path.glob('**/*') if x.is_file()]

es = Elasticsearch()

for data_file in data_files:
    print(data_file)
    with open(data_file, 'r') as f:
        for line in f:
            r = json.loads(line)
            if r['type'] == 'resolve' and 'name' in r:
                body = {'name': r['name'], 'infohash': r['infohash']}
                es.index(index='torrents', doc_type='_doc', id=r['infohash'], body=body)