# Copyright (C) 2012 Vivek Haldar
#
# Take in a dict containing fetched RSS data, and output to printable files in
# the current directory.
#
# Dict looks like:
# feed_title -> [list of articles]
# each article has (title, body).
#
# Author: Vivek Haldar <vh@vivekhaldar.com>

import codecs
import escpos
from datetime import datetime

import output

class OutputPrn(output.Output):
    def output(self):
        articles = self._articles
        for f in articles:
            prn = escpos.Escpos('%s.prn' %f)
            for a in articles[f]:
                title, body = a
                # Cut body down to 100 words.
                short_body = ' '.join(body.split()[:100])
                prn.bigtext(f + '\n')
                prn.bigtext(title + '\n')
                prn.text(body)
                prn.text('\n\n\n')
                prn.flush()
