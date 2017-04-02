#!/usr/bin/env python
import requests
import os
import shutil
import inspect
import logging


def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


def function_logger(file_level, console_level=None):
    function_name = inspect.stack()[1][3]
    logger = logging.getLogger(function_name)
    logger.setLevel(logging.DEBUG)  # By default, logs all messages

    if console_level is not None:
        ch = logging.StreamHandler()  # StreamHandler logs to console
        ch.setLevel(console_level)
        ch_format = logging.Formatter('%(asctime)s - %(message)s')
        ch.setFormatter(ch_format)
        logger.addHandler(ch)

    fh = logging.FileHandler("{0}.log".format(function_name))
    fh.setLevel(file_level)
    fh_format = logging.Formatter(
        '%(asctime)s - %(lineno)d - %(levelname)-8s - %(message)s')
    fh.setFormatter(fh_format)
    logger.addHandler(fh)

    return logger


class AvailableMedia():
    """docstring for AvailableMedia"""
    dscanned = {'scanned': 0, 'skipped': 0, 'moved': 0}

    def __init__(self, console_level=logging.INFO, url=None):
        self.logger = function_logger(console_level)
        durl = 'http://argus.feralhosting.com/poriented/pmgr/avail.php'
        self.url = url if url is not None else durl
        self.logger.debug('set url to "%s"' % self.url)
        self.scanned = {'scanned': 0, 'skipped': 0, 'moved': 0}
        self.parse_avail()

    def __str__(self):
        return str(self.dscanned) if not hasattr(
            self, 'scanned') else str(self.scanned)

    def parse_avail(self):
        jreq = None
        try:
            req = requests.get(self.url)
            jreq = req.json()
        except Exception as e:
            self.logger.error("Request from %s failed with error: %s" % (
                self.url, str(e)))
        if jreq is None:
            return False
        self.scanned['scanned'] = len(jreq)
        for media_file in jreq:
            fq = find(
                media_file['file'],
                '/media/sdaj1/poriented/share/media/deluge/completed')
            if fq is None:
                self.scanned['skipped'] += 1
                self.logger.info('still loading %s.' % str(
                    media_file['nFile']))
            else:
                nSz = os.path.getsize(fq)
                np = '/media/sdaj1/poriented/share/media/plex'
                spec_fldr = media_file['nFile'].split('.')
                spec_fldr = spec_fldr if len(spec_fldr) < 2 else spec_fldr[:-1]
                n_fldr = media_file['nPath']
                n_fldr.extend(spec_fldr)
                for d in media_file['nPath']:
                    tp = os.path.join(np, d)
                    if not os.path.isdir(tp):
                        os.makedirs(tp)
                np = tp
            if os.path.exists(os.path.join(np, media_file['file'])):
                cSz = os.path.getsize(os.path.join(np, media_file['file']))
            else:
                cSz = 0
            if nSz > cSz:
                shutil.move(fq, os.path.join(np, media_file['file']))
                self.scanned['moved'] += 1
            else:
                self.scanned['skipped'] += 1
                os.remove(fq)
            nf = find(media_file['file'], np)
            self.logger.info(str(nf))


if __name__ == '__main__':
    check_files = AvailableMedia()
    print(check_files)
