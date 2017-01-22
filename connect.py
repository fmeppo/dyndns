#!/usr/local/bin/python

import urllib2, sys

url = sys.argv[1]
hostname = sys.argv[2]
authtok = sys.argv[3]

try:
    u = urllib2.urlopen(url + '?host=' + hostname + '&auth=' + authtok)
    data = u.read()
    print data
    u.close()
except urllib2.HTTPError, e:
    print "HTTP error: " + str(e)
except urllib2.URLError, e:
    print "Network error: " + str(e)
