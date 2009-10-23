#!/usr/bin/python

import urllib, re, sys, glob, os, time, random

base = 'http://worthing.nationaltheatre.org.uk'
dir = '../data/national/'

def fetch_url(url, file):
    if os.path.exists(file):
        r = open(file).read()
    else:
        r = urllib.urlopen(url).read()
        open(file, 'w').write(r)
    return r

def fetch_year(year):
    print "Fetching %s..." % year
    url = '%s/Dserve/dserve.exe?&dsqIni=Dserve.ini&dsqApp=Archive&dsqDb=Performance&dsqCmd=overview.tcl&dsqSearch=%%28OriginalDate=%%27%s%%27%%29&dsqNum=200' % (base, year)
    file = '%syears/%s' % (dir, year)
    return fetch_url(url, file)

for year in range(1963, 2007):
    r = fetch_year(year)

    m = re.findall('<tr>\s*<td class="OverviewKey">\s*<a href="([^"]*)" class="OverviewKey">\s*.*?\s*</a>\s*</td>\s*<td class="OverviewCell">\s*(.*?)\s*</td>\s*<td class="OverviewCell">\s*(.*?)\s*</td>\s*<td class="OverviewCell">\s*(.*?)\s*</td>', r)
    if not m:
        print "%s HAS NO PRODUCTIONS" % year
    for production in m:
        pos, year = re.search("Pos=(\d+).*?'(\d{4})'", production[0]).groups()
        url = '%s%s' % (base, production[0].replace('&amp;', '&'))
        #press = production[1]
        #title = production[2]
        #venue = production[3]
        #print year, pos, url #, press, title, venue
        file = '%sproductions/%s-%s' % (dir, year, pos)
        if os.path.exists(file):
            continue
        fetch_url(url, file)
        print "  Fetched %s" % pos
        time.sleep(1+random.random()-0.5)

