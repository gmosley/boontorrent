# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import libtorrent
import time
import os
import binascii
from termcolor import colored

seen = set()
handles = set()
meta_info_count = 0

# port = 40363
port = 6881

session = libtorrent.session()
session.listen_on(port, port)
session.set_alert_mask(
    libtorrent.alert.category_t.dht_notification | libtorrent.alert.category_t.error_notification | libtorrent.alert.category_t.performance_warning)

session_settings = session.settings()
session_settings.connection_speed = 80
session_settings.peer_connect_timeout = 5
session.set_settings(session_settings)

session.add_dht_router("router.utorrent.com", 6881)
session.add_dht_router("router.bittorrent.com", 6881)
session.add_dht_router("dht.transmissionbt.com", 6881)

# start with the default settings and make some modifications
dht_settings = session.get_dht_settings()
dht_settings.dht_upload_rate_limit = 12000
dht_settings.upload_rate_limit = 0
dht_settings.download_rate_limit = 0
dht_settings.restrict_routing_ips = True

session.set_dht_settings(dht_settings)
print('max_dht_items {}, max_torrents {}'.format(dht_settings.max_dht_items, dht_settings.max_torrents))

print('starting dht with node id {}'.format(binascii.hexlify(session.dht_state()['node-id'])))
session.start_dht()


def get_params_for_info_hash(info_hash):
    save_path = os.path.join(os.path.abspath(os.path.curdir), str(info_hash) + '.torrent')

    torrent_params = {
        'save_path': save_path,
        'paused': False,
        'auto_managed': False,
        'upload_mode': True,
        'file_priorities': [0] * 1000,
        'info_hash': info_hash.to_bytes()
    }
    return torrent_params


state_str = ['queued', 'checking', 'downloading metadata',
             'downloading', 'finished', 'seeding', 'allocating']

while True:
    time.sleep(1)
    alerts = session.pop_alerts()
    for alert in alerts:
        if type(alert) == libtorrent.dht_get_peers_alert:
            pass
            print(u'<dht_get_peers> ' + colored(u'{}'.format(alert.info_hash), "blue"))
            if alert.info_hash not in seen:
                handles.add(session.add_torrent(get_params_for_info_hash(alert.info_hash)))
                seen.add(alert.info_hash)
        elif type(alert) == libtorrent.dht_announce_alert:
            print(u'<dht_announce>' + colored(u' {}:{} {}'.format(alert.ip, alert.port, alert.info_hash), "yellow"))
            if alert.info_hash not in seen:
                handles.add(session.add_torrent(get_params_for_info_hash(alert.info_hash)))
                seen.add(alert.info_hash)
        elif type(alert) != libtorrent.dht_outgoing_get_peers_alert:
            print(u'<other>' + colored(u' {}'.format(alert), "magenta"))

    print(u'<info> {} nodes in routing table, {} infohashes collected, retrieving {} metadata ({} retrieved)'
        .format(len(session.dht_state()['nodes']), len(seen), len(handles), meta_info_count))

    to_remove = set()
    for handle in handles:
        status = handle.status()
        if status.has_metadata:
            info = handle.get_torrent_info()
            print('<ut_metadata> ' + colored('{}'.format(info.name().decode("utf-8", "ignore")), "green"))
            f = open(info.name().decode("utf-8", "ignore") + '.torrent', 'wb')
            f.write(libtorrent.bencode(
                libtorrent.create_torrent(info).generate()))
            f.close()
            meta_info_count += 1
            # current_time = int(time.time())
            # print('<metadata_stats> time={} prio={} ({} {})'
            #       .format(current_time - handle.status().added_time, handle.status().queue_position, status.num_peers, status.list_peers))
            to_remove.add(handle)
        # else:
        #     pass
        # print('{} - {} peers ({} connected), prio {}, {} {:2}%'
        #       .format(status.info_hash, status.list_peers, status.num_peers, status.queue_position, state_str[status.state], status.progress * 100))
        else:
            current_time = int(time.time())
            status = handle.status()
            time_spent = current_time - status.added_time
            if time_spent > 30:
                to_remove.add(handle)

    for handle in to_remove:
        session.remove_torrent(handle)

    handles -= to_remove
