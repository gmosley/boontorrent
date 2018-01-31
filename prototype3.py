import libtorrent as lt
from pprint import pprint
import time
import os
import binascii
from termcolor import colored


# we can view default settings with lt.default_settings()

alert_mask = (
    lt.alert.category_t.dht_notification |
    lt.alert.category_t.error_notification |
    lt.alert.category_t.performance_warning |
    lt.alert.category_t.stats_notification
    # lt.alert.category_t.dht_operation_notification
)

# other DHT routers:
#  router.utorrent.com:6881
#  router.bittorrent.com:6881
#  dht.transmissionbt.com:6881
#  dht.libtorrent.org:25401

session_settings = {
    'listen_interfaces': '0.0.0.0:40363', # port 40363 is for Graham's VPN.
    'alert_mask': alert_mask,
    'dht_bootstrap_nodes': 'router.utorrent.com:6881'
}

session = lt.session(session_settings)
# TODO: is there a way to create a paused session so we can change dht settings
#       before starting?
# gmosley: see https://www.libtorrent.org/reference-Core.html#set_dht_storage()
session.pause()

# TODO: re-read documentation and make sure these settings are correct
# session_settings = session.settings()
# session_settings.connection_speed = 80
# session_settings.peer_connect_timeout = 5
# session.set_settings(session_settings)

# start with the default settings and make some modifications
dht_settings = session.get_dht_settings()
# pprint(dir(dht_settings))
# pprint(dht_settings.aggressive_lookups)
# pprint(dht_settings.max_peers)
# pprint(dht_settings.extended_routing_table)

# TODO: re-read documentation and make sure these settings are correct
dht_settings.dht_upload_rate_limit = 12000
dht_settings.upload_rate_limit = 0
dht_settings.download_rate_limit = 0
dht_settings.restrict_routing_ips = True

session.set_dht_settings(dht_settings)

# TODO: read docs session.post_session_stats(). We can get the names of each 
#       field from lt.session_stats_metrics()

for alert in session.pop_alerts():
#    if type(alert) == lt.log_alert:
#        continue
    
    print('alert: ' + alert.what(), flush=True)
    print(alert.message(), flush=True)

initial_state = session.save_state()
#dht_node_id = initial_state[b'dht state'][b'node-id']
#print('dht node id {}'.format(binascii.hexlify(dht_node_id).decode()))
#print('max_dht_items {}, max_torrents {}'.format(
#    dht_settings.max_dht_items, dht_settings.max_torrents))

def get_params_for_info_hash(info_hash):
    save_path = os.path.join(
        os.path.abspath(os.path.curdir), str(info_hash) + '.torrent')

    flags = (
        lt.add_torrent_params_flags_t.flag_upload_mode |
        lt.add_torrent_params_flags_t.flag_update_subscribe
    )

    # TODO: do we want to enable stop when ready? 
    # https://www.libtorrent.org/reference-Core.html#stop_when_ready()

    torrent_params = {
        'flags': flags,
        'save_path': save_path,
        'info_hash': info_hash.to_bytes()
    }
    return torrent_params


session.resume()
time.sleep(5)

seen = set()
handles = set()
meta_info_count = 0

state_str = ['queued', 'checking', 'downloading metadata', 
             'downloading', 'finished', 'seeding', 'allocating']

while True:
    print('checking for alerts', flush=True)
    alerts = session.pop_alerts()
    for alert in alerts:
        print('({}) {}'.format(alert.what(), alert.message()), flush=True)
        if type(alert) == lt.portmap_error_alert:
            print(alert.message(), flush=True)
        elif (type(alert) in [lt.dht_announce_alert, lt.dht_get_peers_alert]) and alert.info_hash not in seen:
            seen.add(alert.info_hash)
            torrent_params = get_params_for_info_hash(alert.info_hash)
            handles.add(session.add_torrent(torrent_params))
            
    # TODO: https://www.libtorrent.org/reference-Core.html#post_torrent_updates()
    to_remove = set()
    for handle in handles:
        status = handle.status()
        if (status.has_metadata):
            metadata = status.torrent_file
            print('<ut_metadata> {} ({})'.format(metadata.name(), handle.info_hash()), flush=True)
            with open(metadata.name() + '.torrent', 'wb') as f:
                f.write(lt.bencode(lt.create_torrent(metadata).generate()))
            meta_info_count += 1
            to_remove.add(handle)
        else:
            print('{} - {} peers ({} connected), prio {}, {} {:2}%'
                  .format(status.info_hash, status.list_peers, status.num_peers, status.queue_position, state_str[status.state], status.progress * 100), flush=True)

    for handle in to_remove:
        session.remove_torrent(handle)

    handles -= to_remove

    time.sleep(10)
