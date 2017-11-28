import libtorrent
import time
import os
import binascii

seen = set()
handles = set()
meta_info_count = 0

port = 40363

session = libtorrent.session()
session.listen_on(port, port)
session.set_alert_mask(libtorrent.alert.category_t.dht_notification | libtorrent.alert.category_t.error_notification)

session.add_dht_router("router.utorrent.com", 6881)
session.add_dht_router("router.bittorrent.com", 6881)
session.add_dht_router("dht.transmissionbt.com", 6881)
session.add_dht_router("dht.libtorrent.org", 25401)

# start with the default settings and make some modifications
dht_settings = session.get_dht_settings()
dht_settings.aggressive_lookups = True
dht_settings.extended_routing_table = True
dht_settings.max_dht_items = 3000
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
        'info_hash': info_hash.to_bytes()
    }
    return torrent_params


while True:
    alerts = session.pop_alerts()
    for alert in alerts:
        if type(alert) == libtorrent.dht_get_peers_alert:
            print('<dht_get_peers> {}'.format(alert.info_hash))
            if (alert.info_hash not in seen):
                handles.add(session.add_torrent(get_params_for_info_hash(alert.info_hash)))
                seen.add(alert.info_hash)
        elif type(alert) == libtorrent.dht_announce_alert:
            print('<dht_announce> {}:{} {}'.format(alert.ip, alert.port, alert.info_hash))
            if (alert.info_hash not in seen):
                handles.add(session.add_torrent(get_params_for_info_hash(alert.info_hash)))
                seen.add(alert.info_hash)
        elif type(alert) != libtorrent.dht_outgoing_get_peers_alert:
            print('<other> {}'.format(alert))

    time.sleep(1)
    print('<info> {} nodes in routing table, {} infohashes collected, retrieving {} metainfos ({} retrieved)'
          .format(len(session.dht_state()['nodes']), len(seen), len(handles), meta_info_count))

    to_remove = set()
    for handle in handles:
        if (handle.has_metadata()):
            info = handle.get_torrent_info()
            print('<ut_metainfo> {}'.format(info.name()))
            f = open(info.name() + '.torrent', 'wb')
            f.write(libtorrent.bencode(
                libtorrent.create_torrent(info).generate()))
            f.close()
            meta_info_count += 1
            to_remove.add(handle)

    for handle in to_remove:
        session.remove_torrent(handle)

    handles -= to_remove
