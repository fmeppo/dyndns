#!/usr/local/bin/python

import urllib2, argparse, pprint, sys, ConfigParser


parser = argparse.ArgumentParser(description='Update DNS record dynamically')
parser.add_argument('fqdn', type=str, nargs=1, help='DNS record to update')
parser.add_argument('-u', '--url', nargs=1, type=str, required=True,
                    help='URL for the AWS API Gateway to use for updates')
parser.add_argument('-t', '--token', nargs=1, type=str, required=True,
                    help='Security token')
parser.add_argument('-4', '--ipv4', nargs=1, type=str,
                    help='IPv4 address to advertise (rather than autodetect)')
parser.add_argument('-6', '--ipv6', nargs=1, type=str,
                    help='IPv6 address to advertise (will not be autodetected)')
parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',
                    help='Display verbose results from the server')
parser.add_argument('-f', '--config', nargs=1, type=str, dest='config',
                    help='Specify a config file with default options')

args = parser.parse_args()

vargs = vars(args)

if vargs['config'] != None:
    conffile = [ vargs['config'] ]
else:
    conffile = ['/usr/local/etc/dyndns.conf', '/etc/dyndns.con']

config = ConfigParser.RawConfigParser()
for f in conffile:
    config.read(f)

query_args = ['fqdn','token','ipv4','ipv6']

arghash = {}
for item in query_args:
    if vargs[item] != None:
        arghash[item] = vargs[item]
    else:
        try:
            arghash[item] = config.get(vargs['fqdn'], item)
        except Exception, e:
            arghash[item] = None

qstring = reduce(lambda x, y: x + '&' + y,  \
            list(map(lambda x: x + '=' + str(vargs[x][0]), \
            list(filter(lambda x: vargs[x] != None, query_args)) )) )

try:
    u = urllib2.urlopen(args.url[0] + '?' + qstring)
    data = u.read()
    u.close()
except urllib2.HTTPError, e:
    print "HTTP error: " + str(e)
    sys.exit(1)
except urllib2.URLError, e:
    print "Network error: " + str(e)
    sys.exit(2)
except ValueError, e:
    print "Invalid URL: " + args.url[0]
    sys.exit(3)

if args.verbose:
    print data

if u.getcode() == 200:
    # Success!
    sys.exit(0)
else:
    print "Failed to set DNS records."
    sys.exit(1)
