from pathlib import Path
from pprint import pprint
import libtorrent as lt
from sklearn import metrics
import sys

torrents_path = Path('torrents-new')
adult_words = ['xxx', 'porn', 'anal', 'cock']

def get_torrent_name(torrent_file):
    with open(torrent_file, 'rb') as f:
        torrent = lt.bdecode(f.read())
        info = torrent[b'info']

        if b'name.utf-8' in info:
            torrent_name = info[b'name.utf-8'].decode()
        else:
            torrent_name = info[b'name'].decode()
        
        return torrent_name

def print_torrent(infohash):
    torrent_file = Path(torrents_path, infohash + '.torrent')
    print(get_torrent_name(torrent_file))

def read_labels(labels_filename):
    infohashes = []
    labels = []
    with open(labels_filename, 'r') as f:
        for line in f:
            infohash, label = line.strip().split(' ')
            infohashes.append(infohash)
            labels.append(int(label))
    return infohashes, labels


def normalize_name(name):
    return name.lower().replace('.', ' ')

infohashes, labels = read_labels('adult-labels.txt')
y_pred = []

for infohash in infohashes:
    torrent_file = Path(torrents_path, infohash + '.torrent')
    name = normalize_name(get_torrent_name(torrent_file))
    pred = 1 if any(w in name for w in adult_words) else 0
    y_pred.append(pred)

print('\n---False Positives---')
for infohash, truth, pred in zip(infohashes, labels, y_pred):
    if truth == 0 and pred == 1:
        print_torrent(infohash)

print('\n---True Negatives----')
for infohash, truth, pred in zip(infohashes, labels, y_pred):
    if truth == 1 and pred == 0:
        print_torrent(infohash)

print()
print(metrics.accuracy_score(labels, y_pred))
print(metrics.f1_score(labels, y_pred))