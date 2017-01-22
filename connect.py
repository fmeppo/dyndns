#!/usr/local/bin/python

import urllib2, argparse, pprint


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

args = parser.parse_args()

vargs = vars(args)
query_args = ['fqdn','token','ipv4','ipv6']
qstring = reduce(lambda x, y: x + '&' + y,  \
            list(map(lambda x: x + '=' + str(vargs[x][0]), \
            list(filter(lambda x: vargs[x] != None, query_args)) )) )

try:
    u = urllib2.urlopen(args.url[0] + '?' + qstring)
    data = u.read()
    print data
    u.close()
except urllib2.HTTPError, e:
    print "HTTP error: " + str(e)
except urllib2.URLError, e:
    print "Network error: " + str(e)
except ValueError, e:
    print "Invalid URL: " + args.url[0]
