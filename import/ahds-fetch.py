#!/usr/bin/python

import urllib2, cookielib, time, sys, random, glob, re
random.seed()
urlopen = urllib2.urlopen
Request = urllib2.Request
cj = cookielib.LWPCookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

for n in range(1,67):
	print n
	if n==1:
		fp = urlopen('http://ahds.ac.uk/ahdscollections/docroot/birminghamrep/birminghamrepsearch.do')
	else:
		fp = urlopen('http://ahds.ac.uk/ahdscollections/docroot/birminghamrep/birminghamrepsearch.do?currentPage=%d&requiredPage=%d' % (n-1, n))
	list = fp.read()
	fp.close()
	fp = open('../data/ahds/lists/%d' % n, 'w')
	fp.write(list)
	fp.close()
	time.sleep(1+random.random()-0.5)

# Get a cookie
#fp = urlopen('http://ahds.ac.uk/ahdscollections/docroot/birminghamrep/birminghamrepsearch.do')
#fp.read()
#fp.close()

	m = re.search('<table width="90%" cellpadding="5" cellspacing="0" class="table01">(.*?)</table>(?s)', list)
	table = m.group(1)
	rows = re.findall('<tr[^>]*>(.*?)</tr>(?s)', table)
	for row in rows:
		play, author, director, designer, theatre, first, last = re.findall('<td[^>]*>\s*(.*?)\s*</td>(?s)', row)
		if play=='<b>Play</b>':
			continue
		m = re.match('<a href="birminghamrepdetails\.do\?id=(\d+)">(.*?)</a>', play)
		if not m:
			raise Exception, row
		id, play = m.groups()
		print id, play, author, director, designer, theatre, first, last
		fp = urlopen('http://ahds.ac.uk/ahdscollections/docroot/birminghamrep/birminghamrepdetails.do?id=%s' % id)
		details = fp.read()
		fp.close()
		fp = open('../data/ahds/details/%s' % id, 'w')
		fp.write(details)
		fp.close()
		time.sleep(2+random.random()-0.5)

