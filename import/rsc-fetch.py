#!/usr/bin/python

import urllib, re, sys, glob, os

base = 'http://calm.shakespeare.org.uk'
dir = '../data/rsc/'

def fetch_url(url, file):
    if os.path.exists(file):
        r = open(file).read()
    else:
        r = urllib.urlopen(url).read()
        open(file, 'w').write(r)
    return r

def fetch_year(year):
    print "Fetching %s..." % year
    url = 'http://calm.shakespeare.org.uk/dserve/dserve.exe?dsqCmd=SearchBuild.tcl&dsqIni=Dserve.ini&dsqApp=Archive&dsqDb=Performance&srch_UserInteger1=' + str(year)
    file = '%sdataYear/%s' % (dir, year)
    return fetch_url(url, file)

for year in range(1879, 2010):
    # Fetch page 1
    r = fetch_year(year)

    # Check for Next pages
    m = re.search('<a class="navbar" href="([^"]*)">\s*\[Next\]\s*', r)
    if m:
        url = '%s%s' % (base, m.group(1).replace('&amp;', '&'))
        file = '%sdataYear/%s-2' % (dir, year)
        print "  Fetching page 2..."
        fetch_url(url, file)
    if year == 1985 or year == 1988:
        file = '%sdataYear/%s-3' % (dir, year)
        url = "%s/dserve/dserve.exe?dsqIni=Dserve.ini&dsqApp=Archive&dsqCmd=Overview.tcl&dsqDb=Performance&dsqSearch=(UserInteger1='%s')&dsqPos=2&dsqNum=50&PF=No" % (base, year)
        print "  Fetching page 3..."
        fetch_url(url, file)

    # Productions

#<td class="OverviewKey">
#<a href="/dserve/dserve.exe?dsqIni=Dserve.ini&amp;dsqApp=Archive&dsqCmd=Show.tcl&dsqDb=Performance&dsqPos=0&dsqSearch=(UserInteger1='1879')" class="OverviewKey">
#VIEW...</a>
#</td>
#<td class="OverviewCellPressNight">23/04/1879
#</td>
#<td class="OverviewCellTitle">Much Ado About Nothing
#</td>
#<td class="OverviewCellVenue">Shakespeare Memorial Theatre, Stratford-upon-Avon
#</td>

    m = re.findall('<tr>\s*<td class="OverviewKey">\s*<a href="([^"]*)" class="OverviewKey">\s*.*?\s*</a>\s*</td>\s*<td class="OverviewCellPressNight">\s*(.*?)\s*</td>\s*<td class="OverviewCellTitle">\s*(.*?)\s*</td>\s*<td class="OverviewCellVenue">\s*(.*?)\s*</td>', r)
    if not m:
        print "%s HAS NO PRODUCTIONS" % year
    for production in m:
        pos, year = re.search("Pos=(\d+).*?'(\d{4})'", production[0]).groups()
        url = '%s%s' % (base, production[0].replace('&amp;', '&'))
        #press = production[1]
        #title = production[2]
        #venue = production[3]
        #print year, pos, url #, press, title, venue
        if os.path.exists('%sdataProds/%s-%s' % (dir, year, pos)):
            continue
        file = '%sdataProds/%s-%s' % (dir, year, pos)
        fetch_url(url, file)

