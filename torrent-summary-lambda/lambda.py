import bencoder
import boto3
import io
import json
import sys

s3_client = boto3.client('s3')

def summarize_torrent(torrent_obj, infohash):
    torrent = bencoder.decode(torrent_obj.read())
    output = {}
    info = torrent[b'info']
    output["infohash"] = infohash
    if b'name.utf-8' in info:
        output["name"] = info[b'name.utf-8'].decode()
    else:
        output["name"] = info[b'name'].decode()

    num_files = 1
    size = 0

    if b'length' in info:
        output["num_files"] = 1
        output["size"] = info[b'length']
    else:
        num_files = 0
        files = []
        for f in info[b'files']:
            num_files += 1
            size += f[b'length']
            files.append({"size": f[b'length'], "path": [f.decode(errors='ignore') for f in f[b'path']]})            
        output["size"] = size
        output["num_files"] = num_files
        output["files"] = files
    return output

def lambda_handler(event, context):
    if "infohash" not in event:
        return {
            "StatusCode": 400, 
            "Error": "event must contain infohash key"
        }
    
    infohash = event["infohash"].upper()

    file_obj = io.BytesIO()
    s3_client.download_fileobj("boontorrent", "{}.torrent".format(infohash), file_obj)
    file_obj.seek(0)
    return summarize_torrent(file_obj, infohash)

event = {"infohash":"C8FF22309BA88B9CC47C99F72B9A05993286A621"}
print(json.dumps(lambda_handler(event, None), indent=2))
