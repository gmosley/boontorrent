import time
import btdht
import binascii
from collections import Counter

infohashes = Counter()

class DHTCrawler(btdht.DHT_BASE):
    def on_get_peers_query(self, query):
        try:
            info_hash = query[b'info_hash']
            ip_port = '{}:{}'.format(query.addr[0], query.addr[1])
            print('<get_peers> {:21} {}'.format(ip_port, binascii.hexlify(info_hash)))
            infohashes[info_hash] += 1
        except KeyError:
            pass

dht = DHTCrawler(bind_port=40363, debuglvl=0)
dht.register_message(b'get_peers')
routing_table = dht.root

dht.start()

while True:
    time.sleep(30)
    stats = routing_table.stats()
    print('<dht_info> {} nodes ({} good), {} infohashes ({} unique)'
          .format(stats[0], stats[1], sum(infohashes.values()), len(infohashes)))