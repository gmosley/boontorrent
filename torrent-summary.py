from pathlib import Path
from pprint import pprint
import libtorrent as lt

torrent_path = Path('torrents/')

def human_readable_size(size, decimal_places=2):
    for unit in ['B','KB','MB','GB','TB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f}{unit}"

def human_path(path):
    return '/'.join([f.decode(errors='ignore') for f in path])

for torrent_file in torrent_path.iterdir():
    if not torrent_file.name.endswith('.torrent'): continue
    with torrent_file.open('rb') as f:
        print(torrent_file)
        torrent = lt.bdecode(f.read())

        info = torrent[b'info']

        if b'name.utf-8' in info:
            torrent_name = info[b'name.utf-8'].decode()
        else:
            torrent_name = info[b'name'].decode()

        print(torrent_name)

        num_files = 1
        size = 0

        if b'length' in info:
            num_files = 1
            size = info[b'length']
            print('  {} - {}'.format(
                info[b'name'].decode(),
                human_readable_size(size))
            )
        else:
            num_files = 0
            for f in info[b'files']:
                num_files += 1
                size += f[b'length']
                print('  {} - {}'.format(
                    human_path(f[b'path']),
                    human_readable_size( f[b'length']))
                )
        print()

        # print('{} - {} ({})'.format(
        #     torrent_name, human_readable_size(size), num_files))
