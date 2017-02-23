# dyndns

After moving my personal domains over to Amazon and Route53, I wanted to
do dynamic DNS updates for a few names in my domains.  Unfortunately, Amazon
doesn't support TSIG, and doesn't have a very simple API for trivial Route53
updates, so I whipped up a small tool with Python and AWS Lambda.

This dynamic DNS system requires an AWS Lambda as well as an API Gateway
configured to serve the Lambda.  The `ddupdate` program will communicate
to the API Gateway, and transmit several options about the pending update.
The list of options includes a security token - essentially, a shared secret
for updating a particular hostname/zone ID combination.
