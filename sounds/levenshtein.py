#!/usr/bin/python

import re

def damerau(s1, s2):
	d = {}
	lens1 = len(s1)
	lens2 = len(s2)
	for i in range(0, lens1+1):
		d[(i-1,-1)] = i
	for j in range(1, lens2+1):
		d[(-1,j-1)] = j
	for i in range(0, lens1):
		for j in range(0, lens2):
			cost = s1[i] != s2[j] and 1 or 0
			d[(i,j)] = min(d[(i-1,j)]+1, d[(i,j-1)]+1, d[(i-1,j-1)]+cost)
			if i>0 and j>0 and s1[i]==s2[j-1] and s1[i-1]==s2[j]:
				d[(i,j)] = min(d[(i,j)], d[(i-2,j-2)]+cost)
	return 1 - (d[(lens1-1,lens2-1)] + 0.0) / max(lens1, lens2)

def qnum(s1, s2):
	#s1 = re.sub('[aeiouy ]', '', s1.lower())
	#s2 = re.sub('[aeiouy ]', '', s2.lower())
	s1 = '#' + s1 + '$'
	s2 = '#' + s2 + '$'
	lens1 = len(s1)
	lens2 = len(s2)
	hits = 0
	s1q = [ s1[i:i+2] for i in range(0, lens1-1) ]
	s2q = [ s2[i:i+2] for i in range(0, lens2-1) ]
	for s in s1q:
		if s2.find(s) >= 0:
			hits += 1
	for s in s2q:
		if s1.find(s) >= 0:
			hits += 1
	return (hits + 0.0) / (lens1 + lens2 - 2)

if __name__ == '__main__' :
	print(qnum('Anthony Share', 'Antony Sher'))
	print(qnum('Chuk Iwuji', 'Chuck Iwugee'))
	#import sys
	#line = 'foo'
	#while line:
	#	line = sys.stdin.readline().strip()
	#	print(line, damerau(line.lower(), 'Antony Sher'.lower()))

