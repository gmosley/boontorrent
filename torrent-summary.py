from pathlib import Path
from pprint import pprint
import libtorrent as lt

torrent_path = Path('torrents/')

for torrent_file in torrent_path.iterdir():
    if not torrent_file.name.endswith('.torrent'): continue
    with torrent_file.open('rb') as f:
        torrent = lt.bdecode(f.read())
        info = torrent[b'info']

        if b'name.utf-8' in info:
            torrent_name = info[b'name.utf-8'].decode()
        else:
            torrent_name = info[b'name'].decode()

        print(torrent_name)

        # print(info.keys())
        # if b'files' in torrent[b'info']:
        #     pprint(info[b'files'])

