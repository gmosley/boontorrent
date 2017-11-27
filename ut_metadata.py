import libtorrent
import time
from collections import Counter
import os

seen = set()
handles = set()

port = 40363

session = libtorrent.session()
session.listen_on(port, port)
session.set_alert_mask(libtorrent.alert.category_t.dht_notification | libtorrent.alert.category_t.error_notification)

session.add_dht_router("router.utorrent.com", 6881)
session.add_dht_router("router.bittorrent.com", 6881)
session.add_dht_router("dht.transmissionbt.com", 6881)

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
        # elif type(alert) != libtorrent.dht_outgoing_get_peers_alert:
        #     print('<other> {}'.format(alert))

    time.sleep(1)

    to_remove = set()
    for handle in handles:
        if (handle.has_metadata()):
            info = handle.get_torrent_info()
            print('<ut_metainfo> {}'.format(info.name()))
            f = open(info.name() + '.torrent', 'wb')
            f.write(libtorrent.bencode(
                libtorrent.create_torrent(info).generate()))
            f.close()
            to_remove.add(handle)

    for handle in to_remove:
        session.remove_torrent(handle)

    handles -= to_remove

# info_hash = '1488d454915d860529903b61adb537012a0fe7c8'
# magnet = "magnet:?xt=urn:btih:" + info_hash
# print(magnet)
# save_path = os.path.join(os.path.abspath(os.path.curdir), 'test.torrent')

# torrent_params = {
#     'save_path': save_path,
#     'paused': False,
#     # 'auto_managed': False,
#     # 'upload_mode': True,
#     'url': info_hash
# }
#
# h = session.add_torrent(torrent_params)
#
# # while not t.has_metadata():
# #     time.sleep(1)
# s = h.status()
# while (not s.is_seeding):
#         s = h.status()
#         print(session.pop_alert())
#         state_str = ['queued', 'checking', 'downloading metadata', \
#                 'downloading', 'finished', 'seeding', 'allocating']
#         print '%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s' % \
#                 (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
#                 s.num_peers, state_str[s.state])
#
#         time.sleep(1)
#
#
#
# info = t.get_torrent_info()
# print(info)
# session.remove_torrent(t)
# session.pause()
