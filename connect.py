#!/usr/local/bin/python

import urllib2, argparse, pprint, sys, ConfigParser


parser = argparse.ArgumentParser(description='Update DNS record dynamically')
parser.add_argument('fqdn', type=str, nargs=1, help='DNS record to update')
parser.add_argument('-u', '--url', nargs=1, type=str,
                    help='URL for the AWS API Gateway to use for updates')
parser.add_argument('-t', '--token', nargs=1, type=str,
                    help='Security token')
parser.add_argument('-4', '--ipv4', nargs=1, type=str,
                    help='IPv4 address to advertise (rather than autodetect)')
parser.add_argument('-6', '--ipv6', nargs=1, type=str,
                    help='IPv6 address to advertise (will not be autodetected)')
parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',
                    help='Display verbose results from the server')
parser.add_argument('-f', '--config', nargs=1, type=str, dest='config',
                    help='Specify a config file with default options')
parser.add_argument('-l', '--ttl', nargs=1, type=int, dest='ttl',
                    help='TTL for the injected DNS record')

args = parser.parse_args()

vargs = vars(args)

if vargs['config'] != None:
    conffile = [ vargs['config'] ]
else:
    conffile = ['/usr/local/etc/dyndns.conf', '/etc/dyndns.con']

config = ConfigParser.RawConfigParser()
for f in conffile:
    config.read(f)

for host in vargs['fqdn']:
    query_args = ['fqdn','token','ipv4','ipv6', 'ttl']

    # fqdn is fixed (it's the host we're iterating on).  The rest can come
    # from either the command line (vargs) or the config file, or be None
    # if no value is provided.
    arghash = {'fqdn': host}
    for item in ['url'] + query_args[1:]:
        if vargs[item] != None:
            arghash[item] = vargs[item]
        else:
            try:
                arghash[item] = config.get(host, item)
            except Exception, e:
                arghash[item] = None

    # Since token and url can come from a config file or command line, we
    # need to validate we have these for this host.
    if arghash['token'] == None:
        print "Missing security token for " + host
        sys.exit(1)
    if arghash['url'] == None:
        print "Missing URL for " + host
        sys.exit(2)

    # Collect non-null arguments to be passed via query string, and format
    # the query string appropriately.
    qstring = reduce(lambda x, y: x + '&' + y,  \
                list(map(lambda x: x + '=' + str(arghash[x]), \
                list(filter(lambda x: arghash[x] != None, query_args)) )) )

    try:
        u = urllib2.urlopen(arghash['url'] + '?' + qstring)
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
