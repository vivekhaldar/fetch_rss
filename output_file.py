# Copyright (C) 2012 Vivek Haldar
#
# Take in a dict containing fetched RSS data, and output to text files in the
# current directory.
#
# Dict looks like:
# feed_title -> [list of articles]
# each article has (title, body).
#
# Author: Vivek Haldar <vh@vivekhaldar.com>

import codecs
from datetime import datetime

import output

class OutputFile(output.Output):
    def output(self):
        articles = self._articles
        now = datetime.now ()
        for f in articles:
            for a in articles[f]:
                title, body = a
                numwords = '%05d' % len(body.split())
                # Cut feed title down to 2 words.
                short_feed_name = ' '.join(f.split()[:2])
                filename = numwords + '_' + short_feed_name + '_' + title + '.txt'
                # Remove '/' from filenames
                filename = filename.replace('/', '_')
                fh = codecs.open(filename, encoding='utf-8', mode='w+')
                fh.write(f + '\n')
                fh.write(title + '\n')
                fh.write(body)
                fh.close()
