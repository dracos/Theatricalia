#!/usr/bin/python

import urllib, time, random, re, os

for n in range(1700,2009):
    file = '../data/bristol/years/%s.html' % n
    if not os.path.exists(file):
        continue
    print n
    fp = open(file)
    list = fp.read()
    fp.close()

    m = re.search('<table border="1" width="100%"[^>]*>(.*?)</table>(?s)', list)
    table = m.group(1)
    rows = re.findall('<tr[^>]*>(.*?)</tr>(?s)', table)
    for row in rows:
        if re.search('<th>', row): continue
        play, theatre, season, notes, search_link, details_link = re.findall('<td[^>]*>\s*(.*?)\s*</td>(?s)', row)
        # season is always n-(n+1)
        m = re.search('href="([^>]*?)">', search_link)
        search_link = m.group(1).replace('&amp;', '&').replace('\n', '').replace(' ', '%20')
        m = re.search('href="([^>]*?unique_key=(\d+)[^>]*?)">', details_link)
        details_link = m.group(1).replace('&amp;', '&').replace('\n', '').replace(' ', '%20').replace('#', '%23')
        id = m.group(2)
        print ' ', id, play, theatre
        if os.path.exists('../data/bristol/productions/%s' % id):
            continue
        fp = urllib.urlopen('http://www.bristol.ac.uk/theatrecollection/search/' + details_link)
        details = fp.read()
        fp.close()
        fp = open('../data/bristol/productions/%s' % id, 'w')
        fp.write(details)
        fp.close()
        time.sleep(0.25+random.random()/2)

    #time.sleep(1+random.random()-0.5)


