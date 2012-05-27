#! /usr/bin/python
#
# This sucks down all my RSS feeds and spits out articles from the
# last 24 hours out to text files in the current directory.
#
# Author: Vivek Haldar <vh@vivekhaldar.com>

import argparse
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from threading import Thread
import feedparser
import output_file


# Fetch each RSS feed in a thread by itself, so that we can grab all of them in
# parallel.
class Fetcher(Thread):
    def __init__(self, rss_url, articles, days):
        super(Fetcher, self).__init__()
        self._rss_url = rss_url
        self._articles = articles
        self._days = days

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
            now = datetime.now ()
            pub_date = datetime(pub.tm_year, pub.tm_mon, pub.tm_mday,
                                pub.tm_hour, pub.tm_min)
            daydelta = timedelta(days = self._days)
            if (now - pub_date) < daydelta:
                print '   ', e.title
                if 'content' in e.keys():
                    body = e.content[0].value
                else:
                    body = e.summary
                plain_text = BeautifulSoup(body).get_text()
                self._articles[f.feed.title].append((e.title, plain_text))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("days", help='Fetch articles going back this many days',
                        type=int)
    args = parser.parse_args()
    print 'Fetching the last %d days' % args.days

    # Read subscriptions from other file.
    subscriptions = eval(open('subscriptions.py').read())

    # This is a map: feed_title -> list of articles
    articles = {}
    threads = []
    for s in subscriptions:
        t = Fetcher(s, articles, args.days)
        threads.append(t)
        t.start()

    # Join
    for t in threads:
        t.join(30.0)  # 30 s timeout.

    print "OK, got all the feeds..."

    # OK, now we have the dict with all the content... ditch it out to files.
    output_file.OutputFile(articles).output()
