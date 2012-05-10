#! /usr/bin/python
#
# This sucks down all my RSS feeds and spits out articles from the
# last 24 hours out to text files in the current directory.
#
# Author: Vivek Haldar <vh@vivekhaldar.com>

import feedparser
#import nltk
import codecs
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

SUBSCRIPTIONS = [
    'http://11011110.livejournal.com/data/rss',
    'http://feeds.feedburner.com/JDBentley',
    'http://feeds2.feedburner.com/blogspot/smartbear',
    'http://feeds.feedburner.com/advicetowriters/yirX',
    'http://feeds.feedburner.com/jamesaltucher',
    'http://blog.arc90.com/feed/',
    'http://www.asymco.com/feed/',
    'http://www.brepettis.com/blog/atom.xml',
    'http://www.antipope.org/charlie/blog-static/atom.xml',
    'http://feeds.feedburner.com/codeascraft',
    'http://www.collisiondetection.net/index.rdf',
    'http://cacm.acm.org/blogs/blog-cacm.rss',
    'http://www.contemplativecomputing.org/atom.xml',
    'http://craphound.com/?feed=rss2',
    'http://blogs.law.harvard.edu/doc/feed/',
    'http://www.rushkoff.com/blog/atom.xml',
    'http://feeds.feedburner.com/EmbeddedInAcademia',
    'http://www.ftrain.com/xml/feed/rss.xml',
    'http://googleappsscript.blogspot.com/feeds/posts/default',
    'http://grammarist.com/feed/',
    'http://rjlipton.wordpress.com/feed',
    'http://infovegan.com/index.xml',
    'http://feeds.feedburner.com/ICringely',
    'http://interconnected.org/home/;atom',
    'http://www.neverworkintheory.org/?feed=rss2',
    'http://feeds.feedburner.com/JamesFallows',
    'http://around.com/feed',
    'http://blog.empathybox.com/rss',
    'http://jeffjonas.typepad.com/jeff_jonas/atom.xml',
    'http://johnpavlus.wordpress.com/feed/',
    'http://john.jubjubs.net/feed/',
    'http://www.kadavy.net/home/feed/',
    'http://lessig.org/blog/index.xml',
    'http://nickcrocker.com/feed/',
    'http://thisblogisaploy.blogspot.com/feeds/posts/default',
    'http://raganwald.posterous.com/rss.xml',
    'http://www.randsinrepose.com/index.xml',
    'http://www.ribbonfarm.com/feed/',
    'http://blogs.suntimes.com/ebert/atom.xml',
    'http://feeds.splatf.com/splatf',
    'http://www.storytellingwithdata.com/feeds/posts/default',
    'http://herbsutter.com/feed/',
    'http://tagide.com/blog/feed/',
    'http://teemingmultitudes.blogspot.com/feeds/posts/default',
    'http://thebigblogtheory.wordpress.com/feed/',
    'http://www.thedelhiwalla.com/feed/',
    'http://www.johndcook.com/blog/feed/',
    'http://feeds.feedburner.com/scienceblogs/wDAM',
    'http://thelastpsychiatrist.com/atom.xml',
    'http://feeds.feedburner.com/longnow',
    'http://feeds.feedburner.com/thetechnium',
    'http://third-bit.com/blog/feed',
    'http://log.amitshah.net/feed/?pk_campaign=RSS&amp;pk_kwd=site',
    'http://feeds.feedburner.com/tweetagewasteland',
    'http://blog.vivekhaldar.com/rss',
    'http://matt-welsh.blogspot.com/feeds/posts/default',
    'http://websitesforwriters.net/rss',
    'http://feeds.feedburner.com/WeekendSherpa',
    'http://whatever.scalzi.com/feed/',
    'http://www.wired.com/wiredscience/category/frontal-cortex/feed',
    'http://ethicist.blogs.nytimes.com/feed/',
    'http://feeds.feedburner.com/DilbertDailyStrip',
    'http://feeds.feedburner.com/typepad/ihdT',
    'http://www.gapingvoid.com/index.rdf',
    'http://indexed.blogspot.com/feeds/posts/default',
    'http://www.savagechickens.com/blog/atom.xml',
    'http://feeds2.feedburner.com/AVc',
    'http://www.allthingsdistributed.com/atom.xml',
    'http://feeds.feedburner.com/CodeSoftly',
    'http://blogs.msdn.com/devdev/rss.xml',
    'http://www.freedom-to-tinker.com/?feed=rss2',
    'http://glinden.blogspot.com/feeds/posts/default',
    'http://jeremy.zawodny.com/blog/atom.xml',
    'http://blogs.sun.com/jrose/feed/entries/atom',
    'http://feeds.feedburner.com/julianbrownerecent',
    'http://www.mattcutts.com/blog/feed/',
    'http://michaelfeathers.typepad.com/michael_feathers_blog/index.rdf',
    'http://googleblog.blogspot.com/atom.xml',
    'http://www.tbray.org/ongoing/ongoing.atom',
    'http://radar.oreilly.com/atom.xml',
    'http://joegrossberg.com/paulgraham.rss',
    'http://blog.penelopetrunk.com/feed/',
    'http://feeds.feedburner.com/PresentationZen',
    'http://gbracha.blogspot.com/feeds/posts/default',
    'http://feeds.feedburner.com/roughtype/unGc',
    'http://www.schneier.com/blog/index.rdf',
    'http://www.scottberkun.com/feed',
    'http://scripting.com/rss.xml',
    'http://feeds2.feedburner.com/Stevenberlinjohnsoncom',
    'http://blogs.sun.com/bmc/feed/entries/atom',
    'http://wadler.blogspot.com/atom.xml',
    'http://www.bluebytesoftware.com/blog/SyndicationService.asmx/GetRss',
    'http://minimsft.blogspot.com/atom.xml',
    ]

oneday = timedelta(days = 1)
twoday = timedelta(days = 2)
threeday = timedelta(days = 3)
sevenday = timedelta(days = 7)
now = datetime.now ()

# This is a map: feed_title -> list of articles
articles = {}
for s in SUBSCRIPTIONS:
    print s
    try:
        f = feedparser.parse(s)
        print f.feed.title
        articles[f.feed.title] = []
        for e in f.entries:
            if 'published_parsed' in e.keys():
                pub = e.published_parsed
            else:
                pub = e.updated_parsed
            pub_date = datetime(pub.tm_year, pub.tm_mon, pub.tm_mday, pub.tm_hour, pub.tm_min)
            if (now - pub_date) < oneday:
                print '   ', e.title
                if 'content' in e.keys():
                    body = e.content[0].value
                else:
                    body = e.summary
                #plain_text = nltk.clean_html(body)
                plain_text = BeautifulSoup(body).get_text()
                articles[f.feed.title].append((e.title, plain_text))
    except Exception as e:
        print '== error==', e


# OK, now we have the dict with all the content... ditch it out to files...
for f in articles:
    for a in articles[f]:
        title, body = a
        filename = now.strftime('%m_%d_%Y') + '_' + f + '_' + title + '.txt'
        # Remove '/' from filenames
        filename = filename.replace('/', '_')
        fh = codecs.open(filename, encoding='utf-8', mode='w+')
        fh.write(body)
        fh.close()

