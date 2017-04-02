#!/usr/bin/env python
import requests
import os
import shutil
from datetime import datetime


def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


url = 'http://argus.feralhosting.com/poriented/pmgr/avail.php'
r = requests.get(url)
j = r.json()
print datetime.now()

for f in j:
    fq = find(f['file'], '/media/sdaj1/poriented/share/media/deluge/completed')
    if fq is None:
        print 'still loading ', format(f['nFile']), '.'
    else:
        nSz = os.path.getsize(fq)
        np = '/media/sdaj1/poriented/share/media/plex'
        for d in f['nPath']:
            tp = os.path.join(np, d)
            if not os.path.isdir(tp):
                os.makedirs(tp)

            np = tp

        if os.path.exists(os.path.join(np, f['nFile'])):
            cSz = os.path.getsize(os.path.join(np, f['nFile']))
        else:
            cSz = 0

        if nSz > cSz:
            shutil.move(fq, os.path.join(np, f['nFile']))
        else:
            os.remove(fq)

        nf = find(f['nFile'], np)
        print np
