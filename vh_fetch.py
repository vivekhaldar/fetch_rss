#! /usr/bin/python
#
# This sucks down all my RSS feeds and spits out articles from the
# last 24 hours out to text files in the current directory.
#
# Author: Vivek Haldar <vh@vivekhaldar.com>

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from threading import Thread
import codecs
import feedparser

oneday = timedelta(days = 1)
twoday = timedelta(days = 2)
threeday = timedelta(days = 3)
sevenday = timedelta(days = 7)
now = datetime.now ()

# Fetch each RSS feed in a thread by itself, so that we can grab all of them in
# parallel.
class Fetcher(Thread):
    def __init__(self, rss_url, articles):
        super(Fetcher, self).__init__()
        self._rss_url = rss_url
        self._articles = articles

    def run(self):
        s = self._rss_url
        print s
        try:
            self.fetch()
        except Exception as e:
            print '== error==', e

    def fetch(self):
        f = feedparser.parse(s)
        print f.feed.title
        self._articles[f.feed.title] = []
        for e in f.entries:
            if 'published_parsed' in e.keys():
                pub = e.published_parsed
            else:
                pub = e.updated_parsed
            pub_date = datetime(pub.tm_year, pub.tm_mon, pub.tm_mday,
                                pub.tm_hour, pub.tm_min)
            if (now - pub_date) < twoday:
                print '   ', e.title
                if 'content' in e.keys():
                    body = e.content[0].value
                else:
                    body = e.summary
                plain_text = BeautifulSoup(body).get_text()
                self._articles[f.feed.title].append((e.title, plain_text))

if __name__ == '__main__':
    # Read subscriptions from other file.
    subscriptions = eval(open('subscriptions.py').read())

    # This is a map: feed_title -> list of articles
    articles = {}
    threads = []
    for s in subscriptions:
        t = Fetcher(s, articles)
        threads.append(t)
        t.start()

    # Join
    for t in threads:
        t.join()

    print "OK, got all the feeds..."

    # OK, now we have the dict with all the content... ditch it out to files.
    for f in articles:
        for a in articles[f]:
            title, body = a
            filename = now.strftime('%m_%d_%Y') + '_' + f + '_' + title + '.txt'
            # Remove '/' from filenames
            filename = filename.replace('/', '_')
            fh = codecs.open(filename, encoding='utf-8', mode='w+')
            fh.write(body)
            fh.close()
