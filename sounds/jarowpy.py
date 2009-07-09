# Copyright Roger Binns <rogerb@rogerbinns.com>
#
# This file is under the BitPim license.
#
# Alternatively you can use it under any OSI certified license as listed
# at http://www.opensource.org/licenses/alphabetical
#
# Jaro/Winkler string match algorithm.  There is a native C
# implementation in this directory as well.  There is an excellent
# paper on the "quality" of various string matching algorithms at
# http://www.isi.edu/info-agents/workshops/ijcai03/papers/Cohen-p.pdf
# as well as Java implementations by the same authors at
# http://secondstring.sf.net
#
# Most implementations make copies of the source strings, scribble '*'
# all over the copies, and will compute the entire commonchars even if
# the lengths won't match early on.
#
# My version uses a bitset to track which chars have been seen when
# looking for the common ones, won't give misleading results if '*' is
# present in the string and various other goodness.
#
# The general algorithm is as follows:
#
#   - Compute the matching characters from s1 in s2.  The range
#     searched is half of the length of the shortest string on either
#     side of the current position.  Characters should only be matched
#     once (we use a bitset to mark matched chars - many
#     implementations make a copied string and replace the characters
#     with '*'
# 
#   - Repeat the process with s2 in s1
#
#   - If the matching chars are zero or different length, then return
#     zero.
#
#   - Do the math as show below, which also takes into account how
#     different the two match strings are (transitions)
#
#   - The Winkler addition gives a bonus for how many characters at
#     the begining of both strings are the same since most strings
#     that are the same have misspellings later in the string.
#
# Note that if you want caseless comparison then the strings should be
# converted beforehand. It isn't efficient to do it in this code.
#
# This implementation treats all characters equally.  A refinement is
# partial scores for similar characters (such as 'i' and 'y' or 'b'
# and 'd').  That requires training on a body of strings so we don't
# bother.


def jarow(s1, s2, winkleradjust=1):
    if len(s1)==0 or len(s2)==0: return 0
    if s1==s2: return 1
    halflen=min(len(s1)/2+1, len(s2)/2+1)

    s1pos=0
    s1seenins2=[0]*len(s2)
    s2pos=0
    s2seenins1=[0]*len(s1)
    transpositions=0
    commonlen=0

    while s1pos<len(s1) or s2pos<len(s2):
        # find the next common char from s1 in s2
        s1char=None
        while s1pos<len(s1):
            c=s1[s1pos]
            for i in xrange(max(0,s1pos-halflen), min(len(s2),s1pos+halflen)):
                if s1seenins2[i]: continue
                if c==s2[i]:
                    s1char=c
                    s1seenins2[i]=1
                    break
            s1pos+=1
            if s1char is not None:
                break
        # find the next common char from s2 in s1
        s2char=None
        while s2pos<len(s2):
            c=s2[s2pos]
            for i in xrange(max(0,s2pos-halflen), min(len(s1),s2pos+halflen)):
                if s2seenins1[i]: continue
                if c==s1[i]:
                    s2char=c
                    s2seenins1[i]=1
                    break
            s2pos+=1
            if s2char is not None:
                break

        if s1char==None and s2char==None:
            break
        if s1char!=None and s2char==None:
            return 0
        if s1char==None and s2char!=None:
            return 0
        commonlen+=1
        if s1char!=s2char:
            transpositions+=1

    if commonlen==0: return 0
    transpositions/=2
    dist=commonlen/float(len(s1)) + commonlen/float(len(s2)) + (commonlen-transpositions)/float(commonlen)
    dist/=3.0

    if winkleradjust:
        for common in range(min(len(s1)+1, len(s2)+1, winkleradjust)):
            if common>=len(s1) or common>=len(s2): break
            if s1[common]!=s2[common]:
                break
        dist = dist + common * 0.1 * (1-dist)

    return dist
