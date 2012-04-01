# Copyright (C) 2011 Peter Teichman

import datetime
import os
import re
import time

class IrssiLogFile:
    def __init__(self, path):
        self._path = path

        self._fd = open(path, 'r')
        self._linenum = 0

    def set_now(self, date):
        self._now = datetime.datetime.strptime(date, "%a %b %d %H:%M:%S %Y")

    def update_time(self, time_str):
        t = time.strptime(time_str, "%H:%M")
        self._now = self._now.replace(hour=t.tm_hour, minute=t.tm_min,
                                      second=0)

    def update_date(self, date_str):
        self._now = datetime.datetime.strptime(date_str, "%a %b %d %Y")

    def items(self):
        for line in self._fd.xreadlines():
            self._linenum += 1
            line = line.strip()

            # handle some special lines
            m = re.match("^--- Log opened (.*)", line)
            if m:
                self.set_now(m.group(1))
                continue

            m = re.match("^--- Day changed (.*)", line)
            if m:
                self.update_date(m.group(1))
                continue

            m = re.match("^--- Log closed (.*)", line)
            if m:
                # do nothing
                continue

            # parse the current time, update self._now
            m = re.match("^(\d\d:\d\d) (.*)", line)
            if not m:
                print "Unrecogized line format:", line
                continue

            self.update_time(m.group(1))

            msg = m.group(2)
            if msg.startswith("-!-"):
                # skip join/part info
                continue

            msg = unicode(msg.strip(), "utf-8", errors="replace")

            # detect speaker
            speaker = None

            m = re.search("^<(\S+)>", msg)
            if m:
                speaker = m.group(1)
            else:
                m = re.search("^\* (\S+)", msg)
                if m:
                    speaker = m.group(1)

            if msg.startswith("!") or msg.startswith("-"):
                # server message
                continue

            if speaker is None:
                raise Exception(msg)

            speaker = speaker.strip("_")

            yield (unicode("yasty"), unicode("#yasty"), self._now,
                   unicode(speaker), msg, unicode(self._path), self._linenum)

class IrssiLogIndexer:
    def __init__(self, index):
        self._index = index

    def index_file(self, path):
        print path
        log_file = IrssiLogFile(path)

        network = os.path.basename(os.path.dirname(path))

        # Strip any numerals from the end of the network name
        stripped = network.strip("0123456789")
        if stripped:
            network = stripped

        channel = os.path.basename(path).split(".")[0]

        writer = self._index.writer()
        for msg in log_file.items():
            writer.add_document(network=unicode(network),
                                channel=unicode(channel), when=msg[2],
                                speaker=msg[3], content=msg[4], file=msg[5],
                                line=msg[6])

        writer.commit()
