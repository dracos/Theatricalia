#!/usr/bin/python

from difflib import SequenceMatcher
import heapq

possibilities = ['Schmidt']
word = 'Smith'
cutoff = 0.6
n = 2000

result = []
s = SequenceMatcher()
s.set_seq2(word)
for x in possibilities:
    s.set_seq1(x)
    if s.real_quick_ratio() >= cutoff and \
       s.quick_ratio() >= cutoff and \
       s.ratio() >= cutoff:
       result.append((s.ratio(), x))

# Move the best scorers to head of list
result = heapq.nlargest(n, result)
print result
