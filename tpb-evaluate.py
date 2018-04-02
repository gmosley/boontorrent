import boto3
from botocore.exceptions import ClientError
from bs4 import BeautifulSoup
import urllib.parse
import requests

s3 = boto3.client('s3')

def check_exists(infohash):
    try:
        s3.head_object(Bucket='boontorrent', Key=infohash + '.torrent')
        return True
    except ClientError:
        return False


# any piratebay search results url works
tpb_url = r'https://thepiratebay.org/search/game%20of%20thrones/0/99/0'
tpb_url = r'https://thepiratebay.org/top/201'
tpb_url = r'https://thepiratebay.org/top/all'

r = requests.get(tpb_url)
r.raise_for_status()

html_doc = r.content

found = 0
total = 0

soup = BeautifulSoup(html_doc, 'html.parser')
results_table = soup.find('table', id='searchResult')
for row in results_table.findAll('tr')[1:]:
    total += 1
    name = row.find('div', class_='detName').get_text().strip()
    magnet_href = row.select_one("a[href*=magnet]")['href']
    magnet = urllib.parse.parse_qs(magnet_href)
    
    infohash = magnet['magnet:?xt'][0].split(':')[-1].upper()
    name = magnet['dn'][0]

    exists = check_exists(infohash)
    if exists:
        found += 1

    print('{} ({})'.format(name, exists))

print('found {}/{}'.format(found, total))