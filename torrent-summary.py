from pathlib import Path
from pprint import pprint
import libtorrent as lt
import sys


def human_readable_size(size, decimal_places=2):
    for unit in ['B','KB','MB','GB','TB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f}{unit}"

def human_path(path):
    return '/'.join([f.decode(errors='ignore') for f in path])

def classify(torrent_file):
    infohash = torrent_file.name.split('.')[0]
    print()
    print(infohash)
    summarize_torrent(torrent_file)
    result = input('[y/n/q]')
    if result == 'q':
        exit()

    label = 1 if result == 'y' else 0

    with open('classify.txt', 'a') as f:
        f.write('{} {}\n'.format(infohash, label))

def summarize_torrent(torrent_file):
    print(torrent_file)
    with open(torrent_file, 'rb') as f:
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

if __name__ == '__main__':
    print
    if len(sys.argv) < 2:
        print('usage python3 torrent-summary.py <torrent(s)>')
        exit(1)
    
    for arg in sys.argv[1:]:
        p = Path(arg)
        if not p.exists():
            print('{} not found'.format(p))
        elif p.is_dir():
            for torrent_file in p.iterdir():
                if torrent_file.name.endswith('.torrent'):
                    # summarize_torrent(torrent_file)
                    classify(torrent_file)
        else:
            summarize_torrent(p)
    